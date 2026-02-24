# TOTAL row and net worth — why the final row has Net = 0

## What the final row is

In **Account Summary (by Year)** (and by Quarter), the **last row** is labeled **TOTAL**. It shows:

- **CR Amount** = sum of every account’s CR for that year  
- **DR Amount** = sum of every account’s DR for that year  
- **Net Amount** = sum of every account’s Net for that year  

So the TOTAL row is the **grand total over all accounts**, not “net worth.”

---

## Why Net in the TOTAL row is 0 (and why that’s correct)

In **double-entry accounting**:

- Every transaction has **equal** debits and credits (same amount on both sides).
- So across the **whole** ledger:
  - **Total CR (all accounts) = Total DR (all accounts)**  
- Therefore:
  - **Sum of (Net per account) = Sum(CR) − Sum(DR) = 0**

So if we’re calculating CR and DR correctly, the **TOTAL row’s Net column will be 0** (or very close, e.g. rounding). That is **correct** and means the books balance. It is a **sanity check**, not a mistake.

---

## Net worth (权益) is not the same as TOTAL Net

**Net worth** (权益 / equity) is:

- **Assets − Liabilities**, or  
- The balance of **equity / 权益** accounts.

So:

- **Net worth** = balance of a **subset** of accounts (equity side), not the sum of **every** account’s net.
- Net worth is **not** always 0; it is the organization’s equity at a point in time.

The **TOTAL** row is “sum of all nets” → **should be 0**.  
**Net worth** is “equity balance” → **in general is not 0**.

If you want to see **net worth** in the report, that would be a **separate** row or section (e.g. “权益” or “Net worth” = subtotal of equity accounts), not the grand TOTAL row.

---

## Quarterly Report: TOTAL and Result rows

In the **Quarterly Report** sheet, for each quarter you see:

- **Qx YYYY TOTAL** — Sum of CR, DR, and **Net = DR − CR** over all accounts. For a balanced ledger this Net is **0**.
- **Qx YYYY Result (收入−支出)** — Σ(CR − DR) for **收入** (4xxx) and **支出** (5xxx) only. This **should equal** the reference 小结 **期末总净资产 − 期初总净资产** (e.g. 2023 Q1 = -11,624.88; 2023 Q2 = 377,451.98; 2024 Q1–Q3 combined = 110,528.38).
- **Qx YYYY Result (支出−收入)** — Same magnitude, opposite sign: −(收入−支出).
- **Qx YYYY Result (权益)** — Sum of Net for **权益** (3xxx). Change in equity over the quarter.

### If Result (收入−支出) has the **opposite sign** to 小结 期末−期初

Then the mapping rules are likely assigning **CR/DR the wrong way** for 收入 vs 支出:

- For **收入** (e.g. 捐赠收入, 学费收入): the **收入** account should be **CR** when money comes in (正数交易).
- For **支出** (e.g. 组委工资, 讲师工资): the **支出** account should be **DR** when money goes out.

Check the rules file (e.g. journal_to_ledger or 账目分类明细_ledger_rules): each rule pair should have **CR** on the 收入 or 资产 side and **DR** on the 支出 or 资产 side for normal payments. Fix any rules that have these swapped so that the computed Result (收入−支出) matches 小结 in both sign and magnitude. Do **not** rely on negating the number in the report; fix the source data.

**Diagnostic script:** Run `python scripts/check_income_expense_cr_dr.py --sheet 2023` (or `--sheet 2024`) to list CR/DR totals per 收入 and 支出 account. Any row marked "⚠️ check CR/DR in rules" has the wrong side (e.g. 支出 with only CR); fix that account’s rules.

### 2024 Q1–Q3 sum vs reference 110,528.38

The reference 小结 期末−期初 for **2024 Q1–Q3** (one number for the whole period) should equal the **sum** of our 2024 Q1 + Q2 + Q3 **Result (收入−支出)**. If our sum is far off (e.g. ~300k instead of 110k), check:

- Whether 2024 has different scope or extra/missing entries vs the reference.
- One quarter (e.g. Q2) dominating due to wrong account type or double-count; inspect that quarter’s Ledger Entries and rules.

---

## Summary

| Row / concept        | Meaning                         | Expected value   |
|----------------------|----------------------------------|------------------|
| **TOTAL (Account Summary by Year)** | Sum of all accounts' CR, DR, Net | Net = 0 (balance) |
| **Qx YYYY TOTAL (Quarterly Report)** | DR − CR for that quarter (all accounts) | 0 (balanced) |
| **Qx YYYY Result (收入−支出)** | Σ(CR−DR) for 收入+支出; should = 小结 期末−期初 | e.g. 2023 Q1 -11,624.88; 2024 Q1–Q3 sum 110,528.38 |
| **Qx YYYY Result (支出−收入)** | −(收入−支出) | Opposite sign |
| **Qx YYYY Result (权益)** | Sum of Net for 权益 accounts | Change in equity |
| **Net worth / 权益** | Equity (e.g. Assets - Liabilities) | Not necessarily 0 |

Correct CR/DR in rules → Result (收入−支出) matches 小结 期末−期初. If the sign is wrong, fix the mapping rules (收入=CR, 支出=DR for normal flows), not the report.
