# Error Handling Guide

Complete guide to understanding, interpreting, and fixing errors in veritas-accounting.

## Table of Contents

- [Error Types](#error-types)
- [Error Severity Levels](#error-severity-levels)
- [Error Report Structure](#error-report-structure)
- [Common Errors](#common-errors)
- [How to Fix Errors](#how-to-fix-errors)
- [Error Message Format](#error-message-format)

## Error Types

Errors are categorized into four main types:

### 1. Data Errors (`data_error`)

Errors related to input data quality:
- Missing required columns
- Invalid data types
- Invalid value ranges
- Null values in required fields
- Duplicate entries

**Example:**
```
📊 [ERROR] (Row: 5, Entry: JE-005): Year must be between 2000 and 2100 (got: 1999)
   Field: year
   Value: 1999
   💡 Check that 'year' field has a valid year value between 2000 and 2100
```

### 2. Rule Errors (`rule_error`)

Errors related to mapping rules:
- Invalid rule syntax
- Rule condition errors
- Account code not found
- Rule conflicts

**Example:**
```
📋 [ERROR] (Rule: R-042): Invalid rule condition syntax
   Condition: old_type == "OL" and
   💡 Fix the rule condition syntax - check for missing values or operators
```

### 3. Transformation Errors (`transformation_error`)

Errors during journal → ledger transformation:
- Amount mismatch
- Account code validation failure
- Rule application failure
- Data loss during transformation

**Example:**
```
🔄 [ERROR] (Entry: JE-123): Amount mismatch in transformation
   Journal amount: 1000.00
   Ledger total: 950.00
   💡 Check that mapping rules correctly handle amount distribution
```

### 4. Output Errors (`output_error`)

Errors in generated output:
- Invalid ledger structure
- Hierarchy totals don't balance
- Missing required fields in output
- Output validation failures

**Example:**
```
📤 [ERROR]: Hierarchy totals don't balance
   Level 3 total: 5000.00
   Level 4 sum: 4800.00
   💡 Review transformation logic for missing entries
```

## Error Severity Levels

Errors are assigned severity levels to help prioritize fixes:

### Critical (`critical`)

**Impact:** Processing cannot continue, data corruption risk

**Examples:**
- File corruption
- Transformation failure
- Data loss

**Action:** Must fix before proceeding

### Error (`error`)

**Impact:** Invalid data or rule, processing blocked

**Examples:**
- Missing required columns
- Invalid data types
- Rule syntax errors

**Action:** Fix before processing

### Warning (`warning`)

**Impact:** Potential issue, processing continues

**Examples:**
- Unmatched entries (no rules match)
- Unusual values
- Optional field missing

**Action:** Review and fix if needed

### Info (`info`)

**Impact:** Informational only, no action needed

**Examples:**
- Processing statistics
- Configuration notes

**Action:** None required

## Error Report Structure

The error report Excel file (`error_report.xlsx`) contains multiple sheets:

### Summary Sheet

**Overview Statistics:**
- Total errors by type
- Total errors by severity
- Validation summary
- Transformation summary

**Status Indicators:**
- 🟢 Green: All clear
- 🟡 Yellow: Warnings present
- 🔴 Red: Errors found

### Errors Sheet

**Detailed Error List:**
- Row Number
- Entry ID
- Rule ID
- Field Name
- Error Type
- Severity
- Error Message
- Actual Value
- Expected Value
- Requires Review

**Color Coding:**
- Red: Critical/Error severity
- Yellow: Warning severity
- Green: Info severity

### Transformations Sheet

**Transformation Log:**
- Entry ID
- Timestamp
- Source Description
- Source Amount
- Applied Rules
- Generated Ledger Entries
- No Match flag

### Validation Sheet

**Validation Results:**
- Overall Status
- Entries Processed
- Valid Entries
- Errors Found
- Warnings Found
- Overall Confidence

### Auto-Fixes Sheet

**Auto-Fix Suggestions:**
- Entry ID
- Field Name
- Original Value
- Suggested Value
- Confidence Level
- Approval Status
- Fix Description

## Common Errors

### Error: "Missing required columns"

**Problem:** Your Excel file doesn't have the required columns.

**Solution:**
1. Check column names match exactly (case-sensitive)
2. Verify required columns: `entry_id`, `year`, `description`, `old_type`, `amount`, `date`
3. Check for typos or extra spaces in column names
4. See [Example Files](../examples/) for correct format

**Example Fix:**
```
Before: Year, Description, Type, Amount, Date
After:  year, description, old_type, amount, date
```

### Error: "Invalid date format"

**Problem:** Date values can't be parsed.

**Solution:**
1. Use standard date formats: `YYYY-MM-DD`, `YYYY/MM/DD`, `MM/DD/YYYY`
2. Ensure dates are in date format in Excel (not text)
3. Check for invalid dates (e.g., Feb 30, invalid month/day combinations)
4. Remove any time components if not needed

**Example Fix:**
```
Before: "2024/1/15 10:30:00" (text with time)
After:  2024-01-15 (date format)
```

### Error: "Year must be between 2000 and 2100"

**Problem:** Year value is outside valid range.

**Solution:**
1. Check year values are integers between 2000 and 2100
2. Verify no typos (e.g., 1999 instead of 2024)
3. Check for text values instead of numbers

**Example Fix:**
```
Before: 1999 (too old)
After:  2024 (valid)
```

### Error: "Invalid amount format"

**Problem:** Amount values can't be converted to numbers.

**Solution:**
1. Ensure amounts are numeric (not text)
2. Remove currency symbols ($, ¥, etc.)
3. Use decimal point (.) not comma (,) for decimals
4. Check for empty cells in amount column

**Example Fix:**
```
Before: "$1,000.00" (text with currency symbol)
After:  1000.00 (numeric)
```

### Error: "Rule condition syntax error"

**Problem:** Mapping rule condition has invalid syntax.

**Solution:**
1. Check rule-engine syntax:
   - Use `==` for equality (not `=`)
   - Use `and`, `or`, `not` for logical operators
   - Quote string values: `old_type == "OL"`
2. Verify field names match JournalEntry fields
3. Check for missing operators or values

**Example Fix:**
```
Before: old_type = OL (missing quotes and wrong operator)
After:  old_type == "OL" (correct syntax)
```

### Error: "Account code not found in hierarchy"

**Problem:** Rule references account code that doesn't exist.

**Solution:**
1. Verify account code exists in account hierarchy
2. Check for typos in account codes
3. Ensure account hierarchy file is loaded
4. Update rule to use correct account code

**Example Fix:**
```
Before: account_code: "A99" (doesn't exist)
After:  account_code: "A1" (valid account code)
```

### Error: "No matching rules found"

**Problem:** Journal entry doesn't match any mapping rules.

**Solution:**
1. Review entry data (old_type, year, etc.)
2. Check if rule conditions match entry values
3. Add new rule if needed
4. Verify rule priority allows rule to be applied

**Example:**
```
Entry: old_type="NEW_TYPE", year=2024
Rules: old_type=="OL", old_type=="CR"
Result: No match (NEW_TYPE not covered by rules)
Fix: Add rule for NEW_TYPE or update entry old_type
```

## How to Fix Errors

### Step 1: Review Error Report

1. Open `error_report.xlsx` in Excel
2. Check "Summary" sheet for overview
3. Review "Errors" sheet for details
4. Note error types and severity

### Step 2: Prioritize Fixes

**Priority Order:**
1. Critical errors (must fix)
2. Data errors (block processing)
3. Rule errors (affect transformation)
4. Warnings (review if needed)

### Step 3: Fix Errors

**For Data Errors:**
- Fix input Excel file
- Correct data types
- Fill missing values
- Remove duplicates

**For Rule Errors:**
- Fix rule syntax
- Update account codes
- Correct rule conditions
- Test rules before using

**For Transformation Errors:**
- Review transformation logic
- Check rule application
- Verify account hierarchy
- Review audit trail

### Step 4: Re-run Processing

After fixing errors:
```bash
veritas-accounting process --input fixed_journal.xlsx --rules fixed_rules.xlsx
```

### Step 5: Verify Fixes

- Check new error report
- Verify no critical/error level issues
- Review transformation results
- Confirm output files are correct

## Error Message Format

Error messages follow a consistent format:

```
[ICON] [SEVERITY] (Location): Error Message
   Field: field_name
   Value: actual_value
   💡 Quick fix hint
```

**Components:**
- **Icon**: Error type indicator (📊 data, 📋 rule, 🔄 transformation, 📤 output)
- **Severity**: ERROR, WARNING, CRITICAL, INFO
- **Location**: Row number, Entry ID, Rule ID
- **Error Message**: Description of what went wrong
- **Field**: Which field has the error
- **Value**: What value caused the error
- **Quick Fix Hint**: Actionable guidance

**Example:**
```
📊 [ERROR] (Row: 10, Entry: JE-010): Year must be between 2000 and 2100
   Field: year
   Value: 1999
   💡 Check that 'year' field has a valid year value between 2000 and 2100
```

## Getting Help

If you encounter errors you can't fix:

1. **Check Error Report**: Detailed information in `error_report.xlsx`
2. **Review Documentation**: See [Troubleshooting Guide](./troubleshooting.md)
3. **Validate Input**: Use `validate` command to check files
4. **Check Examples**: See [Example Files](../examples/) for correct formats
5. **Review Audit Trail**: Check `audit_trail.xlsx` for transformation details

---

**Next:** See [Troubleshooting Guide](./troubleshooting.md) for common issues and solutions.
