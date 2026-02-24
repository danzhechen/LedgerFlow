# Rules CR/DR flip — what we flip and what we checked

## Currently flipped in code

We **flip CR and DR** (one swap) when the journal entry’s **`old_type`** contains:

- **押金** (deposit), or  
- **ol-d** (case-insensitive), e.g. `OL-D`, `OL-D&OL助学金`

So these types are handled with a flip:

| type in 账目分类明细 | Meaning | Rule in sheet (before flip) | After flip |
|----------------------|--------|-----------------------------|------------|
| OL-D | Deposit refund (we pay back 押金) | CR 银行存款, DR 应付OL押金 | DR 银行存款, CR 应付OL押金 ✓ |
| OL押金 | Deposit | CR 银行存款, DR 应付OL押金 | same flip ✓ |
| OL-D&OL助学金 | Deposit + scholarship | CR 银行存款, DR 应付OL押金 / 应付OL奖助 | same flip ✓ |

So 账目分类明细 can keep these rules as written; the code applies the flip so the ledger is correct.

---

## Other types we checked (no flip added)

From **journal_to_ledger** we looked at types that look like “pay back” or “refund” and compared rule sides to accounting meaning.

### 还款 (repayment)

- **Rule:** CR=银行存款, DR=短期借款  
- **Meaning:** We repay the loan → cash out (CR 银行存款), liability down (DR 短期借款).  
- **Verdict:** Rule is already in the correct direction. **No flip.**

### 借款还款 (loan repayment)

- **Rule:** CR=短期借款, DR=银行存款  
- **Meaning:** Same as 还款: cash out, loan down. CR 短期借款 (reduce liability), DR 银行存款 (cash out).  
- **Verdict:** Correct. **No flip.**

### 退税 (tax refund)

- **Rule:** CR=应付税款, DR=银行存款  
- **Meaning:** We receive tax refund → cash in (DR 银行存款), tax payable down (CR 应付税款).  
- **Verdict:** Correct. **No flip.**

### 书院-助学金 (scholarship)

- **Rule:** CR=银行存款, DR=应付SC奖助  
- **Meaning:** We pay scholarship → cash out, liability down.  
- **Verdict:** Correct. **No flip.**

---

## If you see wrong signs in the report

1. Run the diagnostic:  
   `python scripts/check_income_expense_cr_dr.py --sheet 2023`  
   and check which 收入/支出 accounts have “⚠️ check CR/DR in rules”.

2. If a **specific `old_type`** (e.g. a new 退还 type, or a variant of 押金/还款) shows the wrong sign, we can add it to the flip list in code. The check is here:

   **`src/veritas_accounting/rules/applicator.py`**  
   - Look for `is_deposit_refund = "押金" in ot or "ol-d" in ot.lower()`.  
   - Add another condition, e.g. `or "还款" in ot` or a new keyword you want to flip.

3. Alternatively we could move the list to config (e.g. a set of `old_type` substrings that trigger a flip) so you can extend it without code changes.

---

## Summary

- **Flipped today:** 押金, ol-d (covers OL-D, OL押金, OL-D&OL助学金).  
- **Checked, no flip:** 还款, 借款还款, 退税, 书院-助学金.  
- If you have another type where the rule is “written the opposite way” in 账目分类明细, tell me the **exact `old_type`** (or a unique substring) and we can add it to the flip list or make the list configurable.
