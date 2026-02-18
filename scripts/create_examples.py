"""Script to create example Excel files for documentation."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd

from veritas_accounting.excel.writer import ExcelWriter


def create_journal_entries_example(output_path: Path) -> None:
    """Create example journal entries Excel file."""
    data = [
        {
            "entry_id": "JE-001",
            "year": 2024,
            "description": "Payment received from customer",
            "old_type": "OL",
            "amount": 1000.00,
            "date": datetime(2024, 1, 15),
            "quarter": 1,
            "notes": "Q1 payment",
        },
        {
            "entry_id": "JE-002",
            "year": 2024,
            "description": "Expense payment for services",
            "old_type": "CR",
            "amount": 500.00,
            "date": datetime(2024, 2, 20),
            "quarter": 1,
            "notes": None,
        },
        {
            "entry_id": "JE-003",
            "year": 2024,
            "description": "Large payment received",
            "old_type": "OL",
            "amount": 5000.00,
            "date": datetime(2024, 3, 10),
            "quarter": 1,
            "notes": "Large transaction",
        },
        {
            "entry_id": "JE-004",
            "year": 2024,
            "description": "Quarterly expense",
            "old_type": "DR",
            "amount": 750.00,
            "date": datetime(2024, 3, 31),
            "quarter": 1,
            "notes": "Q1 expense",
        },
        {
            "entry_id": "JE-005",
            "year": 2024,
            "description": "Regular payment",
            "old_type": "OL",
            "amount": 250.00,
            "date": datetime(2024, 4, 5),
            "quarter": 2,
            "notes": None,
        },
    ]

    df = pd.DataFrame(data)
    writer = ExcelWriter()
    writer.write_file(df, output_path, sheet_name="Journal Entries")


def create_mapping_rules_example(output_path: Path) -> None:
    """Create example mapping rules Excel file."""
    data = [
        {
            "rule_id": "R-001",
            "condition": 'old_type == "OL"',
            "account_code": "A1",
            "priority": 10,
            "old_type": "OL",
            "description": "Map OL entries to A1",
            "generates_multiple": False,
        },
        {
            "rule_id": "R-002",
            "condition": 'old_type == "CR"',
            "account_code": "B2",
            "priority": 10,
            "old_type": "CR",
            "description": "Map CR entries to B2",
            "generates_multiple": False,
        },
        {
            "rule_id": "R-003",
            "condition": 'old_type == "OL" and amount > 1000',
            "account_code": "A1-1",
            "priority": 15,
            "old_type": "OL",
            "description": "Map large OL entries (>1000) to A1-1",
            "generates_multiple": False,
        },
        {
            "rule_id": "R-004",
            "condition": 'old_type == "DR"',
            "account_code": "C3",
            "priority": 10,
            "old_type": "DR",
            "description": "Map DR entries to C3",
            "generates_multiple": False,
        },
        {
            "rule_id": "R-005",
            "condition": 'old_type == "OL" and year == 2024',
            "account_code": "A1",
            "priority": 12,
            "old_type": "OL",
            "description": "Map 2024 OL entries to A1",
            "generates_multiple": False,
        },
    ]

    df = pd.DataFrame(data)
    writer = ExcelWriter()
    writer.write_file(df, output_path, sheet_name="Mapping Rules")


def create_account_hierarchy_example(output_path: Path) -> None:
    """Create example account hierarchy Excel file."""
    data = [
        {
            "code": "A1",
            "name": "Level 1 Account 1",
            "level": 1,
            "parent_code": None,
            "full_path": "Level1/Account1",
        },
        {
            "code": "A1-1",
            "name": "Level 2 Account 1-1",
            "level": 2,
            "parent_code": "A1",
            "full_path": "Level1/Account1/Level2/Account1-1",
        },
        {
            "code": "A1-1-1",
            "name": "Level 3 Account 1-1-1",
            "level": 3,
            "parent_code": "A1-1",
            "full_path": "Level1/Account1/Level2/Account1-1/Level3/Account1-1-1",
        },
        {
            "code": "B2",
            "name": "Level 1 Account 2",
            "level": 1,
            "parent_code": None,
            "full_path": "Level1/Account2",
        },
        {
            "code": "B2-1",
            "name": "Level 2 Account 2-1",
            "level": 2,
            "parent_code": "B2",
            "full_path": "Level1/Account2/Level2/Account2-1",
        },
        {
            "code": "C3",
            "name": "Level 1 Account 3",
            "level": 1,
            "parent_code": None,
            "full_path": "Level1/Account3",
        },
    ]

    df = pd.DataFrame(data)
    writer = ExcelWriter()
    writer.write_file(df, output_path, sheet_name="Account Hierarchy")


def create_ledger_output_example(output_path: Path) -> None:
    """Create example ledger output Excel file."""
    data = [
        {
            "entry_id": "LE-001",
            "account_code": "A1",
            "account_path": "Level1/Account1",
            "level": 1,
            "description": "Payment received from customer",
            "amount": 1000.00,
            "date": datetime(2024, 1, 15),
            "quarter": 1,
            "year": 2024,
            "source_entry_id": "JE-001",
            "rule_applied": "R-001",
        },
        {
            "entry_id": "LE-002",
            "account_code": "B2",
            "account_path": "Level1/Account2",
            "level": 1,
            "description": "Expense payment for services",
            "amount": 500.00,
            "date": datetime(2024, 2, 20),
            "quarter": 1,
            "year": 2024,
            "source_entry_id": "JE-002",
            "rule_applied": "R-002",
        },
        {
            "entry_id": "LE-003",
            "account_code": "A1-1",
            "account_path": "Level1/Account1/Level2/Account1-1",
            "level": 2,
            "description": "Large payment received",
            "amount": 5000.00,
            "date": datetime(2024, 3, 10),
            "quarter": 1,
            "year": 2024,
            "source_entry_id": "JE-003",
            "rule_applied": "R-003",
        },
    ]

    df = pd.DataFrame(data)
    writer = ExcelWriter()
    writer.write_file(df, output_path, sheet_name="Ledger Entries")


def main() -> None:
    """Create all example files."""
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    print("Creating example files...")

    # Create journal entries example
    journal_path = examples_dir / "journal_entries_sample.xlsx"
    create_journal_entries_example(journal_path)
    print(f"✓ Created: {journal_path}")

    # Create mapping rules example
    rules_path = examples_dir / "mapping_rules_sample.xlsx"
    create_mapping_rules_example(rules_path)
    print(f"✓ Created: {rules_path}")

    # Create account hierarchy example
    hierarchy_path = examples_dir / "account_hierarchy_sample.xlsx"
    create_account_hierarchy_example(hierarchy_path)
    print(f"✓ Created: {hierarchy_path}")

    # Create ledger output example
    ledger_path = examples_dir / "ledger_output_sample.xlsx"
    create_ledger_output_example(ledger_path)
    print(f"✓ Created: {ledger_path}")

    # Create README for examples
    readme_path = examples_dir / "README.md"
    readme_content = """# Example Files

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
"""
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"✓ Created: {readme_path}")

    print("\n✅ All example files created successfully!")
    print(f"📁 Location: {examples_dir.absolute()}")


if __name__ == "__main__":
    main()








