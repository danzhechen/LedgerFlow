# Yearly validation against reference account books

This describes how to validate that the pipeline output matches your existing **Veritas China Account book** yearly numbers (2020–2024).

## Inputs

- **Journal:** `examples/journal_entry_2020_2024.xlsx` (sheets: 2020, 2021, 2022, 2023, 2024)
- **Rules:** e.g. `账目分类明细_ledger_rules.xlsx`
- **Account hierarchy:** e.g. `账目分类明细.xlsx`
- **Reference files (expected results):**
  - 2020: e.g. `2020Veritas China Account book.xlsx`
  - 2021: `2021Veritas China Account book.xlsx`
  - 2022: `2022Veritas China Account book.xlsx`
  - 2023: `2023Veritas China Account book.xlsx`
  - 2024: `2024Veritas China Account book (1).xlsx` (or `2024Veritas China Account book.xlsx`)

## What is compared

- **Our output:** The unified report’s **“Account Summary (by Year)”** sheet (per-year CR, DR, Net per account).
- **Reference:** The same structure from each year’s Veritas China Account book file.
- Comparison is by **Ledger ID** (or first column in the reference). Amounts are compared with a small **tolerance** (default 0.01).

## Run validation

### 1. Run pipeline for all years

From the project root:

```bash
python scripts/process_multi_sheet.py \
  --input examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细_ledger_rules.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --output ./output
```

This writes one report per year under `output/2020/`, `output/2021/`, … `output/2024/` (each with `ledger_output.xlsx`).

### 2. Compare against reference files

Point the script at your reference files (Downloads or a copy in the repo):

```bash
python scripts/validate_yearly_against_reference.py \
  --journal examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细_ledger_rules.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --output ./output \
  --reference-2020 "/Users/JerryChen/Downloads/2020Veritas China Account book.xlsx" \
  --reference-2021 "/Users/JerryChen/Downloads/2021Veritas China Account book.xlsx" \
  --reference-2022 "/Users/JerryChen/Downloads/2022Veritas China Account book.xlsx" \
  --reference-2023 "/Users/JerryChen/Downloads/2023Veritas China Account book.xlsx" \
  --reference-2024 "/Users/JerryChen/Downloads/2024Veritas China Account book (1).xlsx"
```

Or put all reference files in one directory and use:

```bash
python scripts/validate_yearly_against_reference.py ... --reference-dir /path/to/reference_books
```

The script will look for files named `2020.xlsx`, `2020Veritas China Account book.xlsx`, or `2020Veritas China Account book (1).xlsx` (and similarly for 2021–2024).

You can skip re-running the pipeline and only compare existing output:

```bash
python scripts/validate_yearly_against_reference.py ... --no-run-pipeline
```

### 3. Environment variables

Instead of `--reference-YYYY` you can set:

- `REFERENCE_2020`, `REFERENCE_2021`, `REFERENCE_2022`, `REFERENCE_2023`, `REFERENCE_2024`

each to the full path of the corresponding Excel file.

### 4. Tolerance

Use `--tolerance 0.01` (default) or another value if your reference rounding differs.

### 5. 2024 has no Q4 data (align validation)

When the reference 2024 file only contains **Q1–Q3** (no Q4), validation should compare like-with-like. The script does this by default:

- **2024** is compared to the reference column **2024Q1-Q3** (not full-year 2024).
- **2020–2023** use the reference column with that year (e.g. `2020`, `2021`, …).

Override with:

- `--year-label "2024FY"` to use one column label for all years.
- `--year-labels "2020:2020,2021:2021,2022:2022,2023:2023,2024:2024Q1-Q3"` to set each year’s column explicitly.

### 6. Type mapping (fewer no-match entries)

If the **account hierarchy** file is 账目分类明细.xlsx and it has a sheet named **journal**, the pipeline uses that sheet as an OLD→NEW type map: raw journal **Type** (e.g. 工资, 书院, OL) is mapped to the rule **old_type** (e.g. 支出SC组委, 支出SC运营, T-收入OL) before applying rules. That reduces “no matching rule” entries. No extra config is needed when using 账目分类明细.xlsx as the hierarchy file. If a (year, type) pair is missing in the sheet (e.g. 2024), the pipeline falls back to the same type in earlier years (2023, 2022, …) so 2024 entries still benefit from 2022/2023 mappings.

## Reference file format

The script tries to auto-detect columns in the reference Excel:

- **Account / Ledger ID:** “Ledger ID”, “Account”, “账户”, “Code”, “科目代码”, or first column
- **CR:** “CR Amount”, “CR”, “Credit”, “贷方”
- **DR:** “DR Amount”, “DR”, “Debit”, “借方”
- **Net:** “Net Amount”, “Net”, “余额”, “Balance”

If your files use different headers, you can extend the detection in `scripts/yearly_validation_helpers.py` (`get_yearly_numbers_from_reference`) or add a `column_map` option to the script (see docstring in the helper).

## Expense vs income (e.g. 8月工资 vs 余利宝收益)

- **Salary/wages (8月工资)** are an **expense**: we paid people. They should be compared to our **expense account** (e.g. **组委工资**), **not** to 银行存款. The pipeline creates correct double-entry: CR 银行存款 (cash out) and DR 组委工资 (expense). In the Account Summary, 组委工资 shows a **negative net** (expense).
- **Income (e.g. 余利宝收益)** shows as **positive net** (income accounts are CR-heavy).
- So 8月工资 and 余利宝收益 have **opposite signs** in the report (expense negative, income positive). The validation script matches reference rows like "a-1-2 8月工资" or "8月工资" to our **组委工资** account (see `REFERENCE_NAME_ALIASES` in `scripts/yearly_validation_helpers.py`).

## 押金 (deposit refund) — CR/DR flip

When we **pay other people back** 押金 (e.g. **OL-d** = deposit refund), 账目分类明细 is correct but the rule sides are written the opposite way. The pipeline **flips CR and DR** for these entries so the ledger is correct: journal `old_type` containing **押金** or **ol-d** (case-insensitive) triggers one flip. So 押金-related rules in 账目分类明细 can stay as-is; the code applies the flip automatically.

## Pytest (optional)

- **Pipeline only (no reference):**  
  Run the integration test that processes sheet “2024” and checks that the report contains an “Account Summary (by Year)” with 2024 data:

  ```bash
  pytest tests/integration/test_yearly_validation.py::test_journal_2020_2024_sheet_2024_pipeline -v
  ```

- **With reference (optional):**  
  If `REFERENCE_2024` is set and points to the 2024 account book file, this test runs the pipeline for 2024 and compares yearly numbers:

  ```bash
  REFERENCE_2024="/Users/JerryChen/Downloads/2024Veritas China Account book (1).xlsx" \
  pytest tests/integration/test_yearly_validation.py::test_yearly_validation_against_reference_if_provided -v
  ```

## Exit code

- `validate_yearly_against_reference.py` exits with **0** if all compared years match within tolerance.
- It exits with **1** if there are differences (and prints the first 15 per year).

---

# How to check the final result and see how different they are

This section is a **step-by-step guide** to: (1) where your “final result” lives, (2) how to run the check, and (3) how to read and interpret differences.

## 1. Where is the final result?

After the pipeline runs, the **final result** for each year is a single Excel workbook:

| Path | Contents |
|------|----------|
| `output/2020/ledger_output.xlsx` | 2020 report |
| `output/2021/ledger_output.xlsx` | 2021 report |
| … | … |
| `output/2024/ledger_output.xlsx` | 2024 report |

Each workbook has these sheets:

- **Ledger Entries** – Every transformed entry (DR/CR, signed amount, account).
- **Account Summary (by Year)** – Totals by year (this is what we compare to the reference).
- **Account Summary (by Quarter)** – Totals by quarter.
- **Quarterly Report** – Quarterly breakdown.
- **Audit & Review** – Audit trail and review info (including entries with no matching rule).

So when we say “final result,” we mean these `ledger_output.xlsx` files, and the **main comparison** is done on the **Account Summary (by Year)** sheet (and, for the reference, the **报表小结FY** sheet when using `--reference-format summary_fy`).

## 2. How to run the check (quick version)

From the project root, with reference files in e.g. `~/Downloads/`:

```bash
.venv/bin/python scripts/validate_yearly_against_reference.py \
  --journal examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细_ledger_rules.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --output ./output \
  --reference-dir "/Users/JerryChen/Downloads"
```

This will:

1. Run the pipeline for sheets 2020–2024 (unless you use `--no-run-pipeline`).
2. For each year that has a reference file, compare our **Account Summary (by Year)** to the reference **报表小结FY** column for that year (2024 uses **2024Q1-Q3** by default).
3. Print a short summary: ✓ if everything matches, ❌ and a list of differences if not.

So “checking the final result” = running this script and reading its output.

## 3. How to interpret “how different they are”

The script prints **one line per difference**. Each line is:

`<account/category> | <message>`

### Types of messages

| Message pattern | Meaning |
|-----------------|--------|
| `net: ours=X, ref=Y` | Same category in both; **numbers differ**. Ours = X, reference = Y. Check rounding, missing/extra entries, or mapping. |
| `Category not in reference (or add alias)` | We have this category (and a non‑zero amount), but the reference has no matching row. Either the reference doesn’t use this line, or you need to add a **name alias** (e.g. 组委工资 ↔ 讲师组委工资) in `yearly_validation_helpers.py`. |
| `In reference only (no matching our category)` | Reference has this category with a non‑zero amount, but we don’t have a matching account name. Our report may be missing a category or use a different name (alias can fix the latter). |

So “how different they are” = **count of these lines** and **size of the number gaps** (e.g. `ours - ref`) when the message is `net: ours=X, ref=Y`.

### Tolerance

- Differences **smaller than** `--tolerance` (default **0.01**) are **ignored** and not reported.
- So “different” = difference **greater than** 0.01 (or whatever you pass).

### See all differences (not just the first 15)

The script only prints the **first 15** differences per year. To see **all** of them, redirect output to a file and open it:

```bash
.venv/bin/python scripts/validate_yearly_against_reference.py \
  --journal examples/journal_entry_2020_2024.xlsx \
  --rules 账目分类明细_ledger_rules.xlsx \
  --account-hierarchy 账目分类明细.xlsx \
  --output ./output \
  --reference-dir "/Users/JerryChen/Downloads" \
  2>&1 | tee validation_report.txt
```

Then open `validation_report.txt` and search for `❌` and the lines below it to see every reported difference.

## 4. Manual spot-check in Excel (optional)

If you want to compare by eye:

1. Open **our** report: `output/2024/ledger_output.xlsx` → sheet **Account Summary (by Year)**. Filter or scroll to the year (e.g. 2024).
2. Open the **reference** file (e.g. 2024 Veritas China Account book) → sheet **报表小结FY**.
3. For 2024, use the column **2024Q1-Q3** in the reference (since there’s no Q4).
4. Match rows by **category name** (and use the same aliases as in the script if names differ, e.g. 组委工资 vs 讲师组委工资).
5. Compare the **net** (or single amount) column: our value vs reference value.

That gives you a direct view of “how different they are” for each line.

### Comparing with the reference 小结 (期初/期末总净资产)

If your reference has a **小结** with rows **期初总净资产** and **期末总净资产** by quarter:

- **期末总净资产 − 期初总净资产** should match our **Quarterly Report** row **"Qx YYYY Result (收入−支出)"** (Net column). Examples: 2023 Q1 = **-11,624.88**; 2023 Q2 = **377,451.98**; **2024 Q1–Q3 combined** = **110,528.38** (sum our 2024 Q1 + Q2 + Q3 Result (收入−支出)).
- If our number has the **opposite sign** to the 小结, the mapping rules likely have CR/DR swapped for 收入 vs 支出: 收入 should be **CR** and 支出 **DR** for normal positive transactions. Fix the rules file (see **total-row-and-net-worth.md**), not the report.
- If 2024 Q1+Q2+Q3 sum is far from 110,528.38 (e.g. ~300k), check 2024 scope and one quarter dominating (e.g. Q2).

## 5. Summary checklist

- [ ] Pipeline has been run (so `output/2020/` … `output/2024/` each contain `ledger_output.xlsx`).
- [ ] Reference files are in place and pointed to (e.g. `--reference-dir` or `--reference-2024` etc.).
- [ ] Run `validate_yearly_against_reference.py`; read the script output.
- [ ] If there are differences: read each line (net difference vs “not in reference” vs “in reference only”); optionally redirect to `validation_report.txt` to see all.
- [ ] Optionally open our **Account Summary (by Year)** and reference **报表小结FY** in Excel for a manual spot-check.
