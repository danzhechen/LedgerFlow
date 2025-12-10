# Getting Started with veritas-accounting

This guide will help you get started with veritas-accounting, from installation to your first successful processing run.

## Table of Contents

- [Installation](#installation)
- [First Run](#first-run)
- [Basic Workflow](#basic-workflow)
- [Next Steps](#next-steps)

## Installation

### Prerequisites

- **Python 3.11 or higher** - Check your version:
  ```bash
  python3 --version
  ```
- **pip** (Python package manager) - Usually comes with Python

### Step 1: Clone or Download

If you have the repository:
```bash
git clone <repository-url>
cd veritas-accounting
```

Or download and extract the project files to a directory.

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates the project dependencies:

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
# Install the package and dependencies
pip install -e .

# Or install from requirements (if available)
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check that the CLI is available
veritas-accounting --version

# Or using Python module
python -m veritas_accounting --version
```

You should see version `0.1.0` or similar.

## First Run

### Prepare Your Files

Before running, you need:

1. **Journal Entries Excel File** - Your input data
   - Required columns: `entry_id`, `year`, `description`, `old_type`, `amount`, `date`
   - Optional columns: `quarter`, `notes`
   - See [Example Files](../examples/) for format

2. **Mapping Rules Excel File** (optional if using default)
   - Required columns: `rule_id`, `condition`, `account_code`, `priority`
   - Optional columns: `old_type`, `new_type`, `description`, `generates_multiple`
   - See [Rule Management Guide](./rule-management.md) for details

3. **Account Hierarchy File** (optional)
   - Used for hierarchical organization and validation
   - Can be Excel, YAML, or JSON format

### Basic Command

```bash
veritas-accounting process --input journal.xlsx --rules rules.xlsx --output ./output
```

This will:
1. Read your journal entries
2. Apply mapping rules
3. Generate ledger output
4. Create error reports
5. Export audit trail

### What You'll See

```
📖 Reading journal entries...
   ✓ Read 691 journal entries
📋 Reading mapping rules...
   ✓ Loaded 194 mapping rules
✅ Validating input data...
   ✓ Input validation passed
🔄 Applying mapping rules and transforming entries...
   ✓ Generated 1250 ledger entries
📊 Generating reports...
   ✓ Generated ledger output: ./output/ledger_output.xlsx
   ✓ Generated quarterly report: ./output/quarterly_report.xlsx
   ✓ Generated error report: ./output/error_report.xlsx
   ✓ Exported audit trail: ./output/audit_trail.xlsx

✅ Processing complete!
📁 Output files saved to: /path/to/output
```

## Basic Workflow

### 1. Prepare Input Files

Ensure your journal entries Excel file has the correct format:
- Required columns present
- Data types correct (year as number, amount as number, date as date)
- No empty required fields

### 2. Run Processing

```bash
veritas-accounting process --input your_journal.xlsx --rules your_rules.xlsx
```

### 3. Review Error Report

Check the error report Excel file:
- Open `error_report.xlsx` in Excel
- Review the "Summary" sheet for overview
- Check "Errors" sheet for any issues
- Review "Transformations" sheet to see what happened

### 4. Use Output Files

- **ledger_output.xlsx** - Your transformed ledger entries
- **quarterly_report.xlsx** - Quarterly aggregation summaries
- **error_report.xlsx** - Complete error and transformation log
- **audit_trail.xlsx** - Full audit trail for compliance

## Next Steps

Now that you've completed your first run:

1. **Learn More:**
   - Read the [User Manual](./user-manual.md) for complete feature reference
   - Check [Configuration Guide](./configuration.md) for advanced options
   - Review [Error Handling Guide](./error-handling.md) for troubleshooting

2. **Customize:**
   - Create a configuration file (see [Configuration Guide](./configuration.md))
   - Update mapping rules (see [Rule Management Guide](./rule-management.md))
   - Set up account hierarchy

3. **Troubleshoot:**
   - If you encounter errors, see [Troubleshooting Guide](./troubleshooting.md)
   - Check error reports for detailed information
   - Review validation messages

## Common First-Time Issues

### "File not found" Error

**Problem:** The system can't find your input file.

**Solution:**
- Use absolute paths: `--input /full/path/to/journal.xlsx`
- Or relative paths from current directory: `--input ./data/journal.xlsx`
- Check file permissions (must be readable)

### "Missing required columns" Error

**Problem:** Your Excel file doesn't have the required columns.

**Solution:**
- Check column names match exactly (case-sensitive)
- See [Example Files](../examples/) for correct format
- Required columns: `entry_id`, `year`, `description`, `old_type`, `amount`, `date`

### "Invalid date format" Error

**Problem:** Date values can't be parsed.

**Solution:**
- Use standard date formats: `YYYY-MM-DD`, `YYYY/MM/DD`, `MM/DD/YYYY`
- Ensure dates are in date format in Excel (not text)
- Check for invalid dates (e.g., Feb 30)

## Getting Help

- **Documentation:** See `docs/` folder for complete guides
- **Examples:** Check `examples/` folder for sample files
- **Error Reports:** Always check error_report.xlsx for detailed information
- **CLI Help:** Run `veritas-accounting --help` or `veritas-accounting process --help`

## Quick Reference

```bash
# Process journal entries
veritas-accounting process --input journal.xlsx --rules rules.xlsx --output ./output

# Validate input files only
veritas-accounting validate --input journal.xlsx --rules rules.xlsx

# Use configuration file
veritas-accounting process --config config.yaml

# Enable verbose logging
veritas-accounting process --input journal.xlsx --verbose
```

---

**Ready to dive deeper?** Continue to the [User Manual](./user-manual.md) for complete feature documentation.
