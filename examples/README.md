# Example Files

This directory contains example Excel files showing the correct format for veritas-accounting input and output files.

## Files

### journal_entries_sample.xlsx

Example journal entries file showing:
- Required columns: `entry_id`, `year`, `description`, `old_type`, `amount`, `date`
- Optional columns: `quarter`, `notes`
- Correct data types and formats
- Example data values

**Use this as a template** for creating your journal entries file.

### mapping_rules_sample.xlsx

Example mapping rules file showing:
- Required columns: `rule_id`, `condition`, `account_code`, `priority`
- Optional columns: `old_type`, `new_type`, `description`, `generates_multiple`
- Rule condition syntax examples
- Priority ordering examples

**Use this as a template** for creating or editing your mapping rules file.

### account_hierarchy_sample.xlsx

Example account hierarchy file showing:
- 4-level hierarchical structure
- Account codes and names
- Parent-child relationships
- Full path structure

**Use this as a template** if you need to create an account hierarchy file.

### ledger_output_sample.xlsx

Example ledger output file showing:
- What the output looks like after processing
- Ledger entry structure
- Account hierarchy organization
- Source entry and rule references

**Use this as a reference** to understand what output files will contain.

## Usage

1. **Copy example files** to use as templates
2. **Replace example data** with your actual data
3. **Maintain column structure** (column names and order)
4. **Follow data type requirements** (numbers, dates, strings)
5. **Validate files** before processing:
   ```bash
   veritas-accounting validate --input your_journal.xlsx --rules your_rules.xlsx
   ```

## Notes

- Example files use realistic but anonymized data
- All dates are in 2024 for consistency
- Account codes follow the hierarchy structure
- Rule conditions demonstrate common patterns

## Documentation

For complete documentation, see:
- [Getting Started Guide](../docs/getting-started.md)
- [User Manual](../docs/user-manual.md)
- [Rule Management Guide](../docs/rule-management.md)
