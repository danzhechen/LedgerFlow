# Configuration Guide

Complete guide to configuring veritas-accounting for your needs.

## Table of Contents

- [Configuration Sources](#configuration-sources)
- [Configuration File Format](#configuration-file-format)
- [Configuration Options](#configuration-options)
- [Environment Variables](#environment-variables)
- [CLI Arguments](#cli-arguments)
- [Priority Order](#priority-order)
- [Examples](#examples)

## Configuration Sources

veritas-accounting supports multiple configuration sources with a clear priority order:

1. **Command-line arguments** (highest priority)
2. **Configuration file** (YAML format)
3. **Environment variables**
4. **Default values** (lowest priority)

Settings from higher priority sources override lower priority ones.

## Configuration File Format

Configuration files use YAML format (`.yaml` or `.yml` extension).

### Basic Structure

```yaml
input:
  journal_file: "path/to/journal.xlsx"
  rules_file: "path/to/rules.xlsx"
  account_hierarchy_file: "path/to/hierarchy.xlsx"

output:
  directory: "./output"
  ledger_file: "ledger_output.xlsx"
  quarterly_report_file: "quarterly_report.xlsx"
  error_report_file: "error_report.xlsx"
  audit_trail_file: "audit_trail.xlsx"

validation:
  level: "strict"  # or "lenient"
  auto_fix_enabled: false
  require_review: true

processing:
  parallel_processing: false
  chunk_size: null
```

### File Location

Place configuration files anywhere and reference them:
```bash
veritas-accounting process --config /path/to/config.yaml
```

Or use a default location (if supported):
- `./config.yaml`
- `~/.veritas-accounting/config.yaml`

## Configuration Options

### Input Configuration

**`input.journal_file`** (required)
- Type: String (file path)
- Description: Path to journal entries Excel file
- Example: `"journal.xlsx"` or `"/absolute/path/to/journal.xlsx"`

**`input.rules_file`** (optional)
- Type: String (file path) or null
- Description: Path to mapping rules Excel file
- Default: None (must be provided via CLI or config)

**`input.account_hierarchy_file`** (optional)
- Type: String (file path) or null
- Description: Path to account hierarchy file (Excel, YAML, or JSON)
- Default: None

### Output Configuration

**`output.directory`** (optional)
- Type: String (directory path)
- Description: Output directory for generated files
- Default: `"./output"`

**`output.ledger_file`** (optional)
- Type: String (filename)
- Description: Name of ledger output Excel file
- Default: `"ledger_output.xlsx"`

**`output.quarterly_report_file`** (optional)
- Type: String (filename)
- Description: Name of quarterly report Excel file
- Default: `"quarterly_report.xlsx"`

**`output.error_report_file`** (optional)
- Type: String (filename)
- Description: Name of error report Excel file
- Default: `"error_report.xlsx"`

**`output.audit_trail_file`** (optional)
- Type: String (filename)
- Description: Name of audit trail export file
- Default: `"audit_trail.xlsx"`

### Validation Configuration

**`validation.level`** (optional)
- Type: String (`"strict"` or `"lenient"`)
- Description: Validation strictness level
- Default: `"strict"`
- Options:
  - `"strict"`: All validation checks, errors block processing
  - `"lenient"`: Warnings only, processing continues

**`validation.auto_fix_enabled`** (optional)
- Type: Boolean
- Description: Enable auto-fix suggestions for validation errors
- Default: `false`

**`validation.require_review`** (optional)
- Type: Boolean
- Description: Require review for all errors before proceeding
- Default: `true`

### Processing Configuration

**`processing.parallel_processing`** (optional)
- Type: Boolean
- Description: Enable parallel processing (future feature)
- Default: `false`

**`processing.chunk_size`** (optional)
- Type: Integer or null
- Description: Chunk size for batch processing
- Default: `null` (no chunking)

## Environment Variables

Set environment variables for automation and CI/CD:

**Input Variables:**
- `VERITAS_JOURNAL_FILE`: Journal entries file path
- `VERITAS_RULES_FILE`: Mapping rules file path
- `VERITAS_ACCOUNT_HIERARCHY_FILE`: Account hierarchy file path

**Output Variables:**
- `VERITAS_OUTPUT_DIR`: Output directory (default: `./output`)
- `VERITAS_LEDGER_FILE`: Ledger output filename
- `VERITAS_QUARTERLY_REPORT_FILE`: Quarterly report filename
- `VERITAS_ERROR_REPORT_FILE`: Error report filename
- `VERITAS_AUDIT_TRAIL_FILE`: Audit trail filename

**Validation Variables:**
- `VERITAS_VALIDATION_LEVEL`: Validation level (`strict` or `lenient`)
- `VERITAS_AUTO_FIX_ENABLED`: Enable auto-fix (`true` or `false`)
- `VERITAS_REQUIRE_REVIEW`: Require review (`true` or `false`)

**Processing Variables:**
- `VERITAS_PARALLEL_PROCESSING`: Enable parallel processing (`true` or `false`)
- `VERITAS_CHUNK_SIZE`: Chunk size for batch processing (integer)

### Example: Setting Environment Variables

**On macOS/Linux:**
```bash
export VERITAS_JOURNAL_FILE="journal.xlsx"
export VERITAS_RULES_FILE="rules.xlsx"
export VERITAS_OUTPUT_DIR="./output"
export VERITAS_VALIDATION_LEVEL="strict"
```

**On Windows (Command Prompt):**
```cmd
set VERITAS_JOURNAL_FILE=journal.xlsx
set VERITAS_RULES_FILE=rules.xlsx
set VERITAS_OUTPUT_DIR=./output
```

**On Windows (PowerShell):**
```powershell
$env:VERITAS_JOURNAL_FILE="journal.xlsx"
$env:VERITAS_RULES_FILE="rules.xlsx"
$env:VERITAS_OUTPUT_DIR="./output"
```

## CLI Arguments

CLI arguments have the highest priority and override all other sources.

**Input Arguments:**
- `--input, -i`: Journal entries file path
- `--rules, -r`: Mapping rules file path
- `--account-hierarchy, -a`: Account hierarchy file path

**Output Arguments:**
- `--output, -o`: Output directory

**Validation Arguments:**
- `--validation-level`: Validation level (`strict` or `lenient`)
- `--auto-fix`: Enable auto-fix suggestions (flag)

**Other Arguments:**
- `--config, -c`: Configuration file path
- `--verbose, -v`: Enable verbose logging (flag)

## Priority Order

Configuration values are merged in this order (later sources override earlier):

1. **Default values** (built into the system)
2. **Environment variables** (if set)
3. **Configuration file** (if provided)
4. **CLI arguments** (if provided)

**Example:**
```bash
# Environment variable sets output directory
export VERITAS_OUTPUT_DIR="./env_output"

# Config file sets output directory
# config.yaml: output.directory: "./config_output"

# CLI argument overrides both
veritas-accounting process --input journal.xlsx --output ./cli_output
# Result: Uses ./cli_output (CLI argument wins)
```

## Examples

### Example 1: Basic Configuration File

**`config.yaml`:**
```yaml
input:
  journal_file: "data/journal_entries.xlsx"
  rules_file: "data/mapping_rules.xlsx"

output:
  directory: "./results"
  ledger_file: "my_ledger.xlsx"

validation:
  level: "strict"
```

**Usage:**
```bash
veritas-accounting process --config config.yaml
```

### Example 2: Environment Variables

**Set variables:**
```bash
export VERITAS_JOURNAL_FILE="journal.xlsx"
export VERITAS_RULES_FILE="rules.xlsx"
export VERITAS_OUTPUT_DIR="./output"
export VERITAS_VALIDATION_LEVEL="lenient"
```

**Usage:**
```bash
veritas-accounting process
# Uses environment variables automatically
```

### Example 3: CLI Override

**Config file sets defaults, CLI overrides:**
```bash
# config.yaml has output.directory: "./default_output"
veritas-accounting process --config config.yaml --output ./custom_output
# Uses ./custom_output (CLI argument overrides config file)
```

### Example 4: Complete Configuration

**`production_config.yaml`:**
```yaml
input:
  journal_file: "/data/accounting/journal_entries.xlsx"
  rules_file: "/data/accounting/mapping_rules.xlsx"
  account_hierarchy_file: "/data/accounting/account_hierarchy.xlsx"

output:
  directory: "/data/accounting/output"
  ledger_file: "ledger_output.xlsx"
  quarterly_report_file: "quarterly_report.xlsx"
  error_report_file: "error_report.xlsx"
  audit_trail_file: "audit_trail.xlsx"

validation:
  level: "strict"
  auto_fix_enabled: false
  require_review: true

processing:
  parallel_processing: false
  chunk_size: null
```

**Usage:**
```bash
veritas-accounting process --config production_config.yaml
```

## Validation

Configuration is validated when loaded:

- **File paths**: Checked for existence (if files are specified)
- **Value types**: Validated (strings, integers, booleans)
- **Value ranges**: Checked (e.g., validation level must be "strict" or "lenient")
- **Required fields**: Journal file is required

**Error Messages:**
If configuration is invalid, you'll see clear error messages:
```
❌ Configuration errors:
   • File does not exist: journal.xlsx
   • Invalid validation level: invalid_value (must be 'strict' or 'lenient')
```

## Best Practices

1. **Use Configuration Files for Production**
   - Store configuration in version control
   - Use different configs for different environments
   - Document configuration choices

2. **Use Environment Variables for CI/CD**
   - Set sensitive values via environment variables
   - Use CI/CD system's secret management
   - Avoid hardcoding paths in scripts

3. **Use CLI Arguments for One-Time Runs**
   - Quick testing and development
   - Override specific settings
   - Interactive use

4. **Validate Before Running**
   - Use `validate` command to check input files
   - Review configuration before processing
   - Test with small datasets first

---

**Next Steps:**
- See [User Manual](./user-manual.md) for complete feature reference
- Check [Error Handling Guide](./error-handling.md) for troubleshooting
- Review [Rule Management Guide](./rule-management.md) for rule configuration
