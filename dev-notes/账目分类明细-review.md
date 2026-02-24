# 账目分类明细 — structure and how we use it

## Your clarification

- **Each table has an OLD section and a NEW section.**  
  OLD = how things were described before (and the **year**). NEW = what we want to use **in the future**.
- **ledger_old and ledger_new tabs** = naming rules and how we organize different rules.

---

## Structure (as read from 账目分类明细.xlsx)

### 1. **journal** (OLD → NEW type)

| Section | Columns | Meaning |
|--------|---------|--------|
| OLD | year, 摘要, type | Raw journal: year, description, **type** as entered in the past |
| NEW | type | **Standardized type** we use going forward |

- Example: (2022, 工资) → 支出SC组委; (2022, OL) → T-收入OL.
- **Used today:** Yes. We load this as a type mapping and apply it before rules (with year fallback when a year has no row).

### 2. **journal_to_ledger** (OLD → NEW type + CR/DR ledgers)

| Section | Columns | Meaning |
|--------|---------|--------|
| OLD | year, type, cr_ledger, dr_ledger | Per-year old type and old ledger names (e.g. 銀行存款1002, OL收入4301) |
| NEW | type, cr_ledger, dr_ledger, description | **Standardized** type and **ledger_new** account names for CR and DR |

- One row per (year, old type) mapping to one NEW (type, cr_ledger, dr_ledger).  
- **Same (year, type) can appear in multiple rows** with different NEW (type, cr, dr) — e.g. 2022 工资 → 支出SC组委, 支出SC讲师, or 组委工资 (all CR 银行存款).
- **Used today:** No. We use **账目分类明细_ledger_rules.xlsx** instead (separate file). So the **single source of truth** for “which CR/DR ledgers” is currently the _ledger_rules file, not the journal_to_ledger sheet.

### 3. **ledger_new** (target chart, no year)

| Columns | Meaning |
|---------|--------|
| ledger name, ledger ID, #1–#4, 备注 | **One** chart of accounts we use **going forward**. No year column. |

- Examples: 银行存款 1100, 收入OL 4300, 组委工资 5010.
- **Used today:** Yes. We load this as the **account hierarchy** (sheet name `ledger_new`).

### 4. **ledger_old** (per-year old naming)

| Columns | Meaning |
|---------|--------|
| year, ledger name, ledger ID | **Old** ledger names/IDs **per year** (how things were named/organized before). |

- Examples: 2021 core讲师工资 5501; 2022 OL收入 4301.
- **Used today:** No. We never read this in the pipeline.

---

## Summary: what we use today

| Source | Used? | How |
|--------|--------|-----|
| 账目分类明细.xlsx **journal** | Yes | OLD type → NEW type (with year fallback). |
| 账目分类明细.xlsx **ledger_new** | Yes | Account hierarchy (names + IDs). |
| 账目分类明细.xlsx **journal_to_ledger** | No | Rules come from 账目分类明细_ledger_rules.xlsx. |
| 账目分类明细.xlsx **ledger_old** | No | Not read. |

So we **do not** yet “fully use” **journal_to_ledger** or **ledger_old**.

---

## Mismatch found

- **收入SCOL** appears in **journal_to_ledger** (NEW side) as a ledger name, but **not** in **ledger_new**.
- Our rules (in _ledger_rules.xlsx) can reference 收入SCOL, so the validator complains “account 收入SCOL does not exist in hierarchy”.
- **Resolved:** 收入SCOL is added by the pipeline when loading ledger_new if missing (code 4250).

---

## Decisions (from your answers)

1. **Multiple NEW rows** → Use **摘要** (description). Rows with a keyword in column Unnamed: 12 get that keyword in the condition and higher priority; when several rows have no keyword, only the first is used per (year, type).

2. **Single source of rules** → 账目分类明细.xlsx is the main rules file; when the same file is used for rules and hierarchy, rules load from **journal_to_ledger**.   
   (Removed old question.) Should the pipeline **build mapping rules from journal_to_ledger** (NEW columns) when the hierarchy file is 账目分类明细.xlsx, so that 账目分类明细 is the single source of truth and we can phase out (or generate) 账目分类明细_ledger_rules.xlsx? Or do you prefer to keep _ledger_rules.xlsx as the main rules file and only “align” it with journal_to_ledger manually?

3. **收入SCOL**  
   → Add as new category (pipeline adds it to hierarchy when missing).

4. **ledger_old**  
   → Reference and test only; not used in the main pipeline.

**Hierarchy file** = the Excel that contains the chart of accounts (ledger_new sheet). 账目分类明细.xlsx is both hierarchy and rules source.
