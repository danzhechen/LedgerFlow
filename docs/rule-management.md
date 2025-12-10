# Rule Management Guide

Complete guide to editing and managing the 194 mapping rules in Excel.

## Table of Contents

- [Rule File Format](#rule-file-format)
- [Rule Syntax](#rule-syntax)
- [Rule Examples](#rule-examples)
- [Rule Validation](#rule-validation)
- [Rule Testing](#rule-testing)
- [Common Rule Errors](#common-rule-errors)
- [Best Practices](#best-practices)

## Rule File Format

### Excel Structure

Mapping rules are stored in Excel files (`.xlsx` format) with the following structure:

**Required Columns:**
- `rule_id` (string): Unique identifier for the rule (e.g., "R-001", "R-042")
- `condition` (string): Rule-engine expression (e.g., `old_type == "OL"`)
- `account_code` (string): Target account code in hierarchy (e.g., "A1", "B2-3")
- `priority` (integer): Rule priority/order (higher priority = applied first, e.g., 10, 5, 1)

**Optional Columns:**
- `old_type` (string): Source journal entry type (for reference/documentation)
- `new_type` (string): Target ledger account type (for reference/documentation)
- `description` (string): Human-readable description (supports Chinese text)
- `generates_multiple` (boolean): Whether rule generates multiple ledger entries (true/false)

### Example Rule File

| rule_id | condition | account_code | priority | old_type | description | generates_multiple |
|---------|-----------|--------------|----------|----------|-------------|-------------------|
| R-001 | old_type == "OL" | A1 | 10 | OL | Map OL entries to A1 | false |
| R-002 | old_type == "CR" and year == 2024 | B2 | 5 | CR | Map 2024 CR entries to B2 | false |
| R-003 | old_type == "OL" and amount > 1000 | A1-1 | 8 | OL | Map large OL entries to A1-1 | false |

### Column Name Flexibility

The system recognizes these column name variations:
- `rule_id`: "Rule ID", "RULE_ID", "id", "ID"
- `condition`: "Condition", "CONDITION"
- `account_code`: "Account Code", "ACCOUNT_CODE", "account"
- `priority`: "Priority", "PRIORITY", "order"
- `old_type`: "Old Type", "OLD_TYPE", "source_type"
- `new_type`: "New Type", "NEW_TYPE", "target_type"
- `description`: "Description", "DESCRIPTION", "desc"
- `generates_multiple`: "Generates Multiple", "GENERATES_MULTIPLE", "one_to_many"

## Rule Syntax

Rules use the **rule-engine** library syntax for conditions.

### Basic Comparisons

**Equality:**
```python
old_type == "OL"           # String equality
year == 2024               # Number equality
amount == 1000.00          # Decimal equality
```

**Inequality:**
```python
old_type != "CR"           # Not equal
year != 2023               # Not equal
```

**Comparisons:**
```python
amount > 1000              # Greater than
amount >= 1000             # Greater than or equal
amount < 5000              # Less than
amount <= 5000             # Less than or equal
```

### Logical Operators

**AND:**
```python
old_type == "OL" and year == 2024
old_type == "CR" and amount > 1000
```

**OR:**
```python
old_type == "OL" or old_type == "CR"
year == 2023 or year == 2024
```

**NOT:**
```python
not old_type == "OL"
not (year == 2023 and old_type == "CR")
```

**Combined:**
```python
(old_type == "OL" or old_type == "CR") and year == 2024
old_type == "OL" and (amount > 1000 or amount < 100)
```

### Available Fields

You can reference these JournalEntry fields in conditions:

- `entry_id` (string): Entry identifier
- `year` (integer): Year (2000-2100)
- `description` (string): Description text
- `old_type` (string): Original account type
- `amount` (decimal): Financial amount
- `date` (datetime): Entry date
- `quarter` (integer, optional): Quarter (1-4)
- `notes` (string, optional): Additional notes

### Date Comparisons

**Date Fields:**
```python
date == "2024-01-15"       # Exact date match
year == 2024               # Year comparison
quarter == 1               # Quarter comparison
```

**Date Ranges:**
```python
year >= 2024 and year <= 2025
quarter == 1 or quarter == 2
```

### String Operations

**Exact Match:**
```python
old_type == "OL"           # Case-sensitive
description == "Payment"   # Exact string match
```

**Note:** String comparisons are case-sensitive. "OL" ≠ "ol"

## Rule Examples

### Example 1: Simple Type Mapping

**Rule:** Map all "OL" entries to account "A1"

| rule_id | condition | account_code | priority | description |
|---------|-----------|--------------|----------|-------------|
| R-001 | old_type == "OL" | A1 | 10 | Map OL entries to A1 |

**How it works:**
- Matches any journal entry where `old_type` equals "OL"
- Generates ledger entry with account code "A1"
- Applied with priority 10 (higher priority = applied first)

### Example 2: Conditional Mapping with Year

**Rule:** Map "CR" entries from 2024 to account "B2"

| rule_id | condition | account_code | priority | description |
|---------|-----------|--------------|----------|-------------|
| R-002 | old_type == "CR" and year == 2024 | B2 | 5 | Map 2024 CR entries to B2 |

**How it works:**
- Matches entries where `old_type` is "CR" AND `year` is 2024
- Only applies to 2024 entries
- Other years' CR entries won't match

### Example 3: Amount-Based Mapping

**Rule:** Map large "OL" entries (>1000) to different account

| rule_id | condition | account_code | priority | description |
|---------|-----------|--------------|----------|-------------|
| R-003 | old_type == "OL" and amount > 1000 | A1-1 | 8 | Map large OL entries to A1-1 |

**How it works:**
- Matches "OL" entries with amount greater than 1000
- Smaller amounts won't match
- Applied with priority 8

### Example 4: Multiple Conditions

**Rule:** Map entries matching multiple criteria

| rule_id | condition | account_code | priority | description |
|---------|-----------|--------------|----------|-------------|
| R-004 | (old_type == "OL" or old_type == "CR") and year == 2024 and amount >= 500 | C3 | 7 | Map 2024 OL/CR entries >= 500 to C3 |

**How it works:**
- Matches entries where:
  - `old_type` is "OL" OR "CR"
  - AND `year` is 2024
  - AND `amount` is >= 500

### Example 5: One-to-Many Mapping

**Rule:** Generate multiple ledger entries from one journal entry

| rule_id | condition | account_code | priority | generates_multiple | description |
|---------|-----------|--------------|----------|-------------------|-------------|
| R-005 | old_type == "OL" | A1 | 10 | true | Map OL to A1 (one-to-many) |

**How it works:**
- When `generates_multiple` is `true`, rule can generate multiple ledger entries
- Used for complex mappings that split amounts across accounts
- Requires special handling in rule application logic

## Rule Validation

### What Gets Validated

1. **Structure Validation:**
   - Required columns present
   - Column names recognized
   - Data types correct

2. **Syntax Validation:**
   - Rule condition syntax is valid
   - Field names exist in JournalEntry
   - Operators are valid

3. **Logic Validation:**
   - Account codes exist in hierarchy (if hierarchy provided)
   - Rule priority is valid (positive integer)
   - No conflicting rules (same condition → different results)

### Validation Errors

**Common Validation Errors:**

1. **"Missing required column: rule_id"**
   - Solution: Add `rule_id` column to Excel file

2. **"Invalid rule condition syntax"**
   - Solution: Check condition syntax, use `==` not `=`, quote strings

3. **"Field 'invalid_field' not found in JournalEntry"**
   - Solution: Use valid field names (entry_id, year, description, old_type, amount, date, quarter, notes)

4. **"Account code 'XYZ' not found in hierarchy"**
   - Solution: Use valid account codes from hierarchy, check for typos

### Validating Rules

**Before Processing:**
```bash
veritas-accounting validate --input journal.xlsx --rules rules.xlsx
```

**Check Validation Results:**
- Review validation output
- Fix any syntax errors
- Verify account codes
- Test with sample data

## Rule Testing

### Step 1: Validate Rule Syntax

```bash
veritas-accounting validate --rules rules.xlsx
```

### Step 2: Test with Sample Data

Create a small test journal file with entries that should match your rules:
- Include entries with various `old_type` values
- Test different year values
- Test different amount ranges

### Step 3: Process Test Data

```bash
veritas-accounting process --input test_journal.xlsx --rules rules.xlsx --output ./test_output
```

### Step 4: Review Results

- Check error report for rule application issues
- Review transformation log
- Verify ledger entries are generated correctly
- Check account code mappings

### Step 5: Iterate

- Fix any issues found
- Update rules as needed
- Re-test until correct

## Common Rule Errors

### Error: "Invalid rule condition syntax"

**Problem:** Condition has syntax errors.

**Common Mistakes:**
- Using `=` instead of `==` for equality
- Missing quotes around string values
- Invalid operators
- Missing parentheses

**Examples:**

❌ **Wrong:**
```
old_type = OL                    # Missing quotes and wrong operator
old_type == "OL" and year = 2024 # Wrong operator for year
old_type == "OL" or "CR"         # Missing field reference
```

✅ **Correct:**
```
old_type == "OL"                 # Correct syntax
old_type == "OL" and year == 2024 # Correct operators
old_type == "OL" or old_type == "CR" # Correct field references
```

### Error: "Field 'xyz' not found in JournalEntry"

**Problem:** Condition references non-existent field.

**Solution:**
- Use only valid JournalEntry fields:
  - `entry_id`, `year`, `description`, `old_type`, `amount`, `date`, `quarter`, `notes`
- Check for typos in field names
- Verify field names match exactly (case-sensitive)

### Error: "Account code 'XYZ' not found in hierarchy"

**Problem:** Rule references account code that doesn't exist.

**Solution:**
- Verify account code exists in account hierarchy
- Check for typos (e.g., "A1" vs "A-1")
- Ensure account hierarchy file is loaded
- Use valid account codes from hierarchy

### Error: "Rule priority must be positive integer"

**Problem:** Priority value is invalid.

**Solution:**
- Use positive integers (1, 2, 10, 100)
- Higher numbers = higher priority (applied first)
- Don't use negative numbers or decimals

## Best Practices

### 1. Use Descriptive Rule IDs

**Good:**
- `R-OL-2024-A1`: Clear what the rule does
- `R-CR-LARGE-B2`: Descriptive identifier

**Avoid:**
- `R-001`: Not descriptive
- `rule1`: Not following convention

### 2. Add Descriptions

Always include descriptions to document what rules do:
- Helps future maintenance
- Explains rule purpose
- Supports Chinese text for bilingual teams

### 3. Organize by Priority

**Priority Strategy:**
- Specific rules: Higher priority (10, 20, 30)
- General rules: Lower priority (1, 2, 3)
- Default/catch-all: Lowest priority (1)

**Example:**
```
Priority 20: old_type == "OL" and year == 2024 and amount > 1000  # Very specific
Priority 10: old_type == "OL" and year == 2024                     # Specific
Priority 5:  old_type == "OL"                                      # General
Priority 1:  True                                                   # Catch-all
```

### 4. Test Rules Incrementally

- Add one rule at a time
- Test after each addition
- Verify it works as expected
- Document any special cases

### 5. Use Comments in Excel

Add Excel comments to explain complex rules:
- Right-click cell → Insert Comment
- Explain rule logic
- Document special cases
- Note any assumptions

### 6. Version Control

- Keep rule files in version control
- Document rule changes
- Track rule history
- Test before deploying changes

### 7. Validate Before Using

Always validate rules before processing:
```bash
veritas-accounting validate --rules rules.xlsx
```

## Rule Maintenance

### Adding New Rules

1. **Identify Need:**
   - Find unmatched entries
   - Identify new entry types
   - Review error reports

2. **Create Rule:**
   - Add row to rules Excel file
   - Write condition
   - Set account code
   - Assign priority

3. **Test Rule:**
   - Validate syntax
   - Test with sample data
   - Verify results

4. **Deploy:**
   - Update rules file
   - Re-run processing
   - Verify output

### Updating Existing Rules

1. **Identify Rule:**
   - Find rule by rule_id
   - Review current condition
   - Understand what needs to change

2. **Update Rule:**
   - Modify condition or account_code
   - Update description if needed
   - Adjust priority if necessary

3. **Test Changes:**
   - Validate updated rule
   - Test with affected entries
   - Verify no regressions

4. **Deploy:**
   - Update rules file
   - Re-run processing
   - Review results

### Removing Rules

1. **Identify Rule:**
   - Find rule to remove
   - Check if it's still needed
   - Verify no dependencies

2. **Remove Rule:**
   - Delete row from Excel file
   - Or mark as inactive (if supported)

3. **Test:**
   - Verify entries still match
   - Check for unmatched entries
   - Review error reports

## Rule File Management

### Backup Rules

Always backup rule files before making changes:
```bash
cp rules.xlsx rules_backup_2024-01-15.xlsx
```

### Version Control

Track rule changes:
- Use Git or similar
- Commit rule changes
- Document changes in commit messages
- Tag rule versions

### Rule Documentation

Document complex rules:
- Add Excel comments
- Maintain rule documentation
- Explain business logic
- Note special cases

---

**Next Steps:**
- See [Example Files](../examples/) for sample rule files
- Review [User Manual](./user-manual.md) for complete reference
- Check [Error Handling Guide](./error-handling.md) for rule error troubleshooting
