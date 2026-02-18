# User Manual

Complete reference guide for all veritas-accounting features and capabilities.

## Table of Contents

- [Overview](#overview)
- [CLI Commands](#cli-commands)
- [Input Files](#input-files)
- [Output Files](#output-files)
- [Configuration](#configuration)
- [Processing Workflow](#processing-workflow)
- [Validation](#validation)
- [Error Handling](#error-handling)
- [Advanced Features](#advanced-features)

## Overview

veritas-accounting is an Excel-native accounting automation system that transforms journal entries through mapping rules to generate hierarchical ledger structures with complete transparency and validation.

### Key Concepts

- **Journal Entries**: Source accounting data (input)
- **Mapping Rules**: Transformation rules that map journal entries to ledger accounts
- **Ledger Entries**: Transformed output data organized by account hierarchy
- **Account Hierarchy**: 4-level hierarchical account structure (25 accounts)
- **Audit Trail**: Complete record of all transformations for traceability

## CLI Commands

### `process` Command

Process journal entries through mapping rules to generate ledger output.

**Usage:**
```bash
veritas-accounting process [OPTIONS]
```

**Required Options:**
- `--input, -i PATH`: Path to journal entries Excel file (required)

**Optional Options:**
- `--rules, -r PATH`: Path to mapping rules Excel file
- `--account-hierarchy, -a PATH`: Path to account hierarchy file
- `--output, -o PATH`: Output directory (default: `./output`)
- `--config, -c PATH`: Configuration file path (YAML format)
- `--validation-level {strict|lenient}`: Validation level
- `--auto-fix`: Enable auto-fix suggestions
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Basic usage
veritas-accounting process --input journal.xlsx --rules rules.xlsx

# With custom output directory
veritas-accounting process --input journal.xlsx --output ./my_output

# Using configuration file
veritas-accounting process --config my_config.yaml

# With verbose logging
veritas-accounting process --input journal.xlsx --verbose
```

**Output:**
- `ledger_output.xlsx` - Ledger entries organized by hierarchy
- `quarterly_report.xlsx` - Quarterly aggregation summaries
- `error_report.xlsx` - Comprehensive error and transformation report
- `audit_trail.xlsx` - Complete audit trail export

### `validate` Command

Validate input files and mapping rules without processing.

**Usage:**
```bash
veritas-accounting validate [OPTIONS]
```

**Options:**
- `--input, -i PATH`: Path to journal entries Excel file (required)
- `--rules, -r PATH`: Path to mapping rules Excel file

**Example:**
```bash
veritas-accounting validate --input journal.xlsx --rules rules.xlsx
```

**Output:**
- Validation status messages
- List of validation errors (if any)
- File format verification

## Input Files

### Journal Entries File

**Format:** Excel (.xlsx)

**Required Columns:**
- `entry_id` (string): Unique identifier for each entry
- `year` (integer): Year of the entry (2000-2100)
- `description` (string): Description of the entry (supports Chinese text)
- `old_type` (string): Original account type/category
- `amount` (number): Financial amount (decimal)
- `date` (date): Date of the entry (YYYY-MM-DD format)

**Optional Columns:**
- `quarter` (integer): Quarter number (1-4)
- `notes` (string): Additional notes or comments

**Column Name Flexibility:**
The system recognizes multiple column name variations:
- `entry_id`: "Entry ID", "ENTRY_ID", "id", "ID", "编号"
- `year`: "Year", "YEAR", "年份"
- `description`: "Description", "DESCRIPTION", "描述", "说明"
- `old_type`: "Old Type", "OLD_TYPE", "type", "Type", "TYPE", "类型"
- `amount`: "Amount", "AMOUNT", "金额"
- `date`: "Date", "DATE", "日期"

**Example:**
| entry_id | year | description | old_type | amount | date | quarter |
|----------|------|-------------|----------|--------|------|----------|
| JE-001 | 2024 | Payment received | OL | 1000.00 | 2024-01-15 | 1 |
| JE-002 | 2024 | Expense payment | CR | 500.00 | 2024-02-20 | 1 |

### Mapping Rules File

**Format:** Excel (.xlsx)

**Required Columns:**
- `rule_id` (string): Unique identifier for the rule
- `condition` (string): Rule-engine expression (e.g., `old_type == "OL"`)
- `account_code` (string): Target account code in hierarchy
- `priority` (integer): Rule priority/order (higher = applied first)

**Optional Columns:**
- `old_type` (string): Source journal entry type
- `new_type` (string): Target ledger account type
- `description` (string): Human-readable rule description
- `generates_multiple` (boolean): Whether rule generates multiple ledger entries

**Condition Syntax:**
Uses rule-engine library syntax:
- Comparisons: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical operators: `and`, `or`, `not`
- Field references: `old_type`, `year`, `amount`, `date`, etc.

**Example:**
| rule_id | condition | account_code | priority | description |
|---------|-----------|--------------|----------|------------|
| R-001 | old_type == "OL" | A1 | 10 | Map OL entries to A1 |
| R-002 | old_type == "CR" and year == 2024 | B2 | 5 | Map 2024 CR entries to B2 |

### Account Hierarchy File

**Format:** Excel (.xlsx), YAML (.yaml), or JSON (.json)

**Structure:**
- 4-level hierarchical structure
- 25 accounts total
- Each account has: code, name, level, parent_code, full_path

**Excel Format:**
| code | name | level | parent_code | full_path |
|------|------|-------|-------------|-----------|
| A1 | Level 1 Account 1 | 1 | | Level1/Account1 |
| A1-1 | Level 2 Account 1-1 | 2 | A1 | Level1/Account1/Level2/Account1-1 |

## Output Files

### Ledger Output (`ledger_output.xlsx`)

**Sheets:**
1. **Ledger Entries** - All ledger entries organized by account hierarchy
   - Columns: Entry ID, Account Code, Account Path, Level, Description, Amount, Date, Quarter, Year, Source Entry ID, Rule Applied
   - Color-coded by hierarchy level
   - Filters and sorting enabled

2. **Summary** - Hierarchical totals by level
   - Level 1-4 summaries
   - Total amounts and entry counts per level

### Quarterly Report (`quarterly_report.xlsx`)

**Sheets:**
1. **Quarterly Totals** - Aggregated totals by account and quarter
   - Organized by quarter (Q1, Q2, Q3, Q4)
   - Color-coded by quarter
   - Quarter totals included

2. **Hierarchy Summary** - Totals at each hierarchy level
   - Level 1-4 summaries
   - Account counts and totals

3. **Statistics** - Summary statistics and metrics
   - Total entries, total amount
   - Unique accounts, unique quarters
   - Quarter breakdown

### Audit Trail (`audit_trail.xlsx`)

**Purpose:** Complete audit trail for compliance, record-keeping, and technical debugging.

**Sheets:**
1. **Metadata** - Audit trail metadata
   - User, system version, rule version
   - Processing timestamps
   - Summary statistics

2. **Transformations** - All transformation records
   - Source entries, applied rules, generated entries
   - Timestamps and metadata

3. **Rules** - All applied rules
   - Rule details and usage counts

4. **Entries** - All journal and ledger entries
   - Complete entry data

5. **Relationships** - Links between entries and rules
   - Journal entry → Rule → Ledger entry relationships

### Review Preview (`review_preview.xlsx`)

**Purpose:** User-friendly preview and review system for accountants to quickly identify and review problematic entries before finalizing the output.

**Sheets:**

1. **Review Dashboard** - Summary and quick overview
   - Summary statistics (total entries, entries needing review)
   - Issues breakdown by type and severity
   - Quick action guide
   - Color-coded status indicators

2. **Preview Table** - Complete ledger entries preview
   - All transformed ledger entries in table format (preview of final output)
   - Visual status flags (✓ OK, ⚠ Warning, ✗ Critical, ! Error, ℹ Info)
   - Color-coded rows:
     - Green: No issues
     - Yellow: Warnings
     - Orange: Errors
     - Red: Critical issues
     - Blue: Informational items
   - Review reason column explaining why entry needs attention
   - Filterable and sortable

3. **Comparison View** - Side-by-side Journal → Ledger comparison
   - Original journal entries on the left
   - Transformed ledger entries on the right
   - Visual arrow (→) showing transformation
   - Color-coded by status
   - Shows one-to-many relationships (one journal entry → multiple ledger entries)

4. **Flagged Entries** - Only entries requiring review
   - Filtered view showing only problematic entries
   - Sorted by severity (critical → error → warning → info)
   - Action needed column with specific guidance
   - Issue type and reason for each flag

**Key Features:**
- **Visual Flags:** Icons and colors make it easy to spot issues at a glance
- **Preview of Final Output:** See exactly what the ledger will look like
- **Problem Identification:** Automatically flags:
  - Entries with no matching rules
  - Validation errors and warnings
  - Unusual amounts (statistical outliers)
  - Missing account codes
  - Multiple rules applied (potential conflicts)
- **Actionable Guidance:** Each flagged entry includes specific action needed
- **Excel-Native:** Works entirely in Excel - no special tools needed

**How to Use:**
1. Start with the **Review Dashboard** to get an overview
2. Review the **Preview Table** to see all entries with visual flags
3. Use **Comparison View** to verify transformations are correct
4. Focus on **Flagged Entries** sheet to address issues
5. After review, use the final ledger output file

## Configuration

See [Configuration Guide](./configuration.md) for complete configuration documentation.

**Quick Reference:**
- Configuration file: YAML format
- Environment variables: `VERITAS_*` prefix
- CLI arguments: Highest priority
- Defaults: Sensible out-of-the-box defaults

## Processing Workflow

### Step-by-Step Process

1. **Input Reading**
   - Read journal entries from Excel
   - Read mapping rules from Excel
   - Read account hierarchy (if provided)

2. **Validation**
   - Validate input data structure
   - Validate data types and values
   - Validate mapping rules syntax
   - Check business rules

3. **Transformation**
   - Apply mapping rules to journal entries
   - Generate ledger entries
   - Track transformations in audit trail

4. **Output Generation**
   - Generate ledger output Excel
   - Generate quarterly aggregation report
   - Generate error report
   - Export audit trail

5. **Review**
   - Review error report for issues
   - Check transformation log
   - Verify output files

### Status Messages

During processing, you'll see progress messages:
- 📖 Reading journal entries...
- 📋 Reading mapping rules...
- ✅ Validating input data...
- 🔄 Applying mapping rules...
- 📊 Generating reports...
- ✅ Processing complete!

## Validation

### Validation Levels

- **Strict** (default): All validation checks enabled, errors block processing
- **Lenient**: Warnings only, processing continues with warnings

### Validation Checks

1. **Structure Validation**
   - Required columns present
   - Column names recognized
   - Data types correct

2. **Value Validation**
   - Year range: 2000-2100
   - Amount format: Valid decimal
   - Date format: Valid date
   - Quarter range: 1-4

3. **Business Rule Validation**
   - No duplicate entries
   - Account codes exist in hierarchy
   - Rule conditions are valid

4. **Transformation Validation**
   - All entries have matching rules (or explicit no-match)
   - Amounts balance correctly
   - Account codes are valid

## Error Handling

See [Error Handling Guide](./error-handling.md) for complete error handling documentation.

**Key Points:**
- All errors are collected (non-fail-fast)
- Errors are categorized by type and severity
- Error reports provide detailed context
- Actionable guidance for fixing errors

## Advanced Features

### Configuration Files

Use YAML configuration files for complex setups:
```yaml
input:
  journal_file: "journal.xlsx"
  rules_file: "rules.xlsx"
output:
  directory: "./output"
validation:
  level: "strict"
  auto_fix_enabled: false
```

### Environment Variables

Set environment variables for automation:
```bash
export VERITAS_JOURNAL_FILE="journal.xlsx"
export VERITAS_RULES_FILE="rules.xlsx"
export VERITAS_OUTPUT_DIR="./output"
```

### Audit Trail

Complete transformation tracking:
- Source entries preserved
- Applied rules recorded
- Generated entries linked
- Timestamps and metadata

### Error Reports

Comprehensive error reporting:
- Multiple sheets for different views
- Color-coded severity levels
- Detailed context and guidance
- Original data preserved

---

**Need help?** See [Troubleshooting Guide](./troubleshooting.md) for common issues and solutions.








