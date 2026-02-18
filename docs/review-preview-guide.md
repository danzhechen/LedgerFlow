# Review Preview System - User Guide

## Overview

The Review Preview System is a user-friendly replacement for the technical audit trail system. It provides accountants with a visual, Excel-based preview of transformed ledger entries with clear flags for entries that need review.

## Why This is Better Than the Old Audit System

### Old Audit System Problems

1. **Too Technical**: The audit trail was designed for developers, not accountants
   - Programmatic views (entry-by-entry, rule-by-rule)
   - JSON/CSV exports requiring technical knowledge
   - No visual preview of the final output

2. **Separate from Output**: Error reports were separate files
   - Had to cross-reference between multiple files
   - No side-by-side comparison
   - Difficult to see the "big picture"

3. **No Visual Flags**: Had to manually scan through data
   - No color coding
   - No icons or status indicators
   - Hard to spot issues quickly

4. **Not Actionable**: Showed what happened, but not what to do
   - Technical error messages
   - No guidance on how to fix issues
   - No prioritization of problems

### New Review Preview System Benefits

1. **Visual Preview**: See the final ledger output before finalizing
   - Complete table of all ledger entries
   - Exactly what will be in the final output
   - Easy to spot issues at a glance

2. **Visual Flags**: Color-coded and icon-based status indicators
   - ✓ Green = OK (no issues)
   - ⚠ Yellow = Warning (review recommended)
   - ✗ Red = Critical (must fix)
   - ! Orange = Error (needs attention)
   - ℹ Blue = Info (informational)

3. **Side-by-Side Comparison**: Journal → Ledger transformation visible
   - See original journal entry
   - See transformed ledger entry(s)
   - Verify transformations are correct

4. **Focused Review**: Flagged entries sheet shows only problems
   - Sorted by severity
   - Action needed column with specific guidance
   - No need to scan through all entries

5. **Excel-Native**: Works entirely in Excel
   - No special tools needed
   - Familiar interface
   - Filterable and sortable

6. **Actionable Guidance**: Each flagged entry includes:
   - What the problem is
   - Why it's flagged
   - What action is needed

## Review Preview Report Structure

The `review_preview.xlsx` file contains 4 sheets:

### 1. Review Dashboard

**Purpose:** Quick overview and summary

**Contents:**
- Summary statistics
  - Total journal entries processed
  - Total ledger entries generated
  - Entries needing review
  - Breakdown by severity (critical, error, warning, info)
- Issues by type
  - No matching rule
  - Validation errors
  - Validation warnings
  - Unusual amounts
  - Missing accounts
  - Multiple rules applied
- Quick action guide
  - Links to other sheets
  - Recommended review workflow

**When to Use:**
- Start here to get an overview
- Check if there are critical issues
- Understand the scope of review needed

### 2. Preview Table

**Purpose:** Complete preview of all ledger entries (the final output)

**Contents:**
- All transformed ledger entries in table format
- Visual status column (icons)
- Color-coded rows by status
- Review reason column (explains why flagged)
- All ledger entry fields:
  - Entry ID, Ledger ID, Account Code, Account Path
  - Description, Amount, Date
  - Quarter, Year, Source Entry ID, Rule Applied

**When to Use:**
- Review all entries to see final output
- Spot-check entries visually
- Use filters to focus on specific accounts or dates
- Verify amounts and account codes

**Visual Indicators:**
- Green rows = OK, no issues
- Yellow rows = Warning, review recommended
- Orange rows = Error, needs attention
- Red rows = Critical, must fix
- Blue rows = Info, informational

### 3. Comparison View

**Purpose:** Side-by-side comparison of Journal → Ledger transformation

**Contents:**
- Left side: Original journal entry
  - Entry ID, Description, Amount, Date, Type
- Arrow (→) showing transformation
- Right side: Transformed ledger entry(s)
  - Entry ID, Account Code, Account Path
  - Amount, Date, Rule Applied, Quarter, Year
- Color-coded by status
- Shows one-to-many relationships (one journal → multiple ledger entries)

**When to Use:**
- Verify transformations are correct
- Check that amounts match
- Verify account codes are correct
- Understand how journal entries were split

**Special Cases:**
- "NO MATCH" in red = Journal entry had no matching rule
- Multiple ledger entries = One journal entry split into multiple accounts

### 4. Flagged Entries

**Purpose:** Focused view of only entries needing review

**Contents:**
- Only entries with issues (filtered view)
- Sorted by severity (critical → error → warning → info)
- Status icon and severity level
- Entry details (account, amount, date, etc.)
- Issue type (what kind of problem)
- Reason (why it's flagged)
- Action needed (what to do about it)

**When to Use:**
- Focus on fixing problems
- Prioritize by severity
- Follow action guidance
- Track progress as you fix issues

**Action Types:**
- "Review journal entry and add/update mapping rule" (no match)
- "Fix data error in journal entry" (validation error)
- "Review warning - may need correction" (validation warning)
- "Verify amount is correct" (unusual amount)
- "Verify account code or update hierarchy" (missing account)
- "Review rule priority - may need adjustment" (multiple rules)

## Issue Types and What They Mean

### 1. No Matching Rule
**Severity:** Error  
**Meaning:** Journal entry didn't match any mapping rule  
**Action:** Review the journal entry description/type and either:
- Add a new mapping rule
- Update an existing rule to match this entry
- Verify the entry is correct

### 2. Validation Error
**Severity:** Error/Critical  
**Meaning:** Data validation failed (missing field, invalid type, etc.)  
**Action:** Fix the data error in the journal entry:
- Check required fields are present
- Verify data types are correct
- Check value ranges

### 3. Validation Warning
**Severity:** Warning  
**Meaning:** Data quality issue (unusual value, potential problem)  
**Action:** Review the warning:
- May be correct but unusual
- May need correction
- Use judgment to decide

### 4. Unusual Amount
**Severity:** Warning  
**Meaning:** Amount is statistically unusual (very large or very small)  
**Action:** Verify the amount is correct:
- Check for data entry errors
- Verify it's not a typo
- Confirm it's intentional

### 5. Missing Account
**Severity:** Warning  
**Meaning:** Account code not found in account hierarchy  
**Action:** Verify the account code:
- Check for typos
- Verify account exists in hierarchy
- Update account hierarchy if needed

### 6. Multiple Rules
**Severity:** Info  
**Meaning:** Multiple mapping rules matched the same entry  
**Action:** Review rule priority:
- May be intentional (rule priority working)
- May need rule adjustment
- Verify the correct rule was applied

## Recommended Review Workflow

1. **Start with Review Dashboard**
   - Check summary statistics
   - Identify critical issues
   - Understand scope

2. **Review Preview Table**
   - Scan visually for issues (color-coded)
   - Use filters to focus on specific accounts/dates
   - Verify amounts and account codes

3. **Use Comparison View**
   - Verify transformations are correct
   - Check journal → ledger mapping
   - Spot-check entries

4. **Focus on Flagged Entries**
   - Address critical issues first
   - Work through errors
   - Review warnings
   - Check info items

5. **Fix Issues**
   - Update journal entries if needed
   - Add/update mapping rules
   - Fix account hierarchy
   - Re-run processing

6. **Final Review**
   - Check Preview Table again
   - Verify all critical issues resolved
   - Proceed with final ledger output

## Tips for Effective Review

1. **Use Filters**: Excel filters make it easy to focus on specific issues
   - Filter by status (critical, error, warning)
   - Filter by account code
   - Filter by date range

2. **Sort by Severity**: In Flagged Entries sheet, entries are already sorted by severity
   - Critical issues first
   - Then errors
   - Then warnings
   - Finally info items

3. **Color Coding**: Visual indicators make scanning faster
   - Red = Stop and fix immediately
   - Orange = Needs attention
   - Yellow = Review recommended
   - Green = OK
   - Blue = Informational

4. **Action Column**: Each flagged entry has specific guidance
   - Follow the action needed
   - Don't guess what to do

5. **Comparison View**: Use this to verify transformations
   - Check amounts match
   - Verify account codes
   - Understand one-to-many splits

## Integration with Processing Pipeline

The Review Preview report is automatically generated during processing:

```bash
veritas-accounting process --input journal.xlsx --rules rules.xlsx
```

**Output Files:**
- `ledger_output.xlsx` - Final ledger output (use this after review)
- `review_preview.xlsx` - Review preview (use this for review)
- `error_report.xlsx` - Detailed error report (technical)
- `audit_trail.xlsx` - Complete audit trail (technical)

**Workflow:**
1. Run processing
2. Review `review_preview.xlsx`
3. Fix issues if needed
4. Re-run processing
5. Use `ledger_output.xlsx` as final output

## Comparison: Old vs New

| Feature | Old Audit System | New Review Preview |
|---------|-----------------|-------------------|
| **Target User** | Developers | Accountants |
| **Format** | JSON/CSV/Excel (technical) | Excel (user-friendly) |
| **Visual Flags** | None | Color-coded + icons |
| **Preview** | No | Yes (complete table) |
| **Comparison** | Separate files | Side-by-side |
| **Actionable** | Technical errors | Specific guidance |
| **Focus** | All data | Flagged entries |
| **Usability** | Requires technical knowledge | Excel-native, intuitive |

## Summary

The Review Preview System provides accountants with:
- ✅ **Visual preview** of final ledger output
- ✅ **Clear flags** for problematic entries
- ✅ **Side-by-side comparison** of transformations
- ✅ **Focused review** of only issues
- ✅ **Actionable guidance** for each problem
- ✅ **Excel-native** workflow

This makes the review process much faster and more effective than the old technical audit trail system.
