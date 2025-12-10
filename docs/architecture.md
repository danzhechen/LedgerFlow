# Architecture

## Executive Summary

This architecture defines a standalone Python application for Excel-native accounting automation. The system processes 691+ journal entries through 194 mapping rules, transforming them into hierarchical ledger structures with complete transparency and validation. Built with Python 3.11+, pandas, openpyxl, Pydantic, and a rule engine, the architecture emphasizes type safety, comprehensive validation, and Excel-native workflows.

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Python Runtime | Python 3.11 | 3.11.x | All epics | Stable, excellent performance, full type hint support, 5+ years support |
| Package Manager | pip + pyproject.toml | Latest | Epic 1 | Standard Python packaging, supports modern dependency management |
| Data Processing | pandas | 3.0.0 | Epic 2, 3, 4, 5, 6 | Industry standard for Excel data manipulation, excellent performance |
| Excel I/O | openpyxl | 3.1.3 | Epic 1, 2, 6 | Full formatting control, UTF-8 support, preserves Excel structure |
| Data Validation | Pydantic | 2.12 | Epic 1, 2, 3, 4 | Type-safe models, automatic validation, excellent error messages |
| Rule Engine | rule-engine | 3.5.0 | Epic 3 | Supports conditional logic, one-to-many mappings, efficient evaluation |
| CLI Framework | Click | Latest | Epic 7 | Mature, composable, excellent for complex CLIs, environment variable support |
| Configuration | Pydantic Settings | 2.12 | Epic 7 | Type-safe config, YAML/JSON/env var support, validation |
| Testing | pytest | Latest | All epics | Industry standard, excellent fixtures, clear test structure |
| Logging | Python logging | Standard | All epics | Built-in, structured logging support, file + console output |
| Code Quality | ruff + mypy | Latest | All epics | Fast linting, type checking, modern Python tooling |
| Project Structure | src-layout | N/A | Epic 1 | Modern Python packaging, clear separation of concerns |

## Project Structure

```
veritas-accounting/
├── pyproject.toml              # Project metadata, dependencies, build config
├── README.md                    # Project overview, quick start
├── .gitignore                   # Python gitignore patterns
├── .python-version              # Python version (3.11)
├── src/
│   └── veritas_accounting/
│       ├── __init__.py
│       ├── __main__.py          # CLI entrypoint
│       ├── cli/
│       │   ├── __init__.py
│       │   └── commands.py      # Click command definitions
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py      # Pydantic Settings configuration
│       ├── models/
│       │   ├── __init__.py
│       │   ├── journal.py       # JournalEntry Pydantic model
│       │   ├── ledger.py        # LedgerEntry Pydantic model
│       │   ├── rule.py          # MappingRule Pydantic model
│       │   └── account.py       # Account hierarchy model
│       ├── excel/
│       │   ├── __init__.py
│       │   ├── reader.py        # Excel file reading (openpyxl + pandas)
│       │   └── writer.py        # Excel file writing with formatting
│       ├── validation/
│       │   ├── __init__.py
│       │   ├── input_validator.py    # Input data validation
│       │   ├── transformation_validator.py  # Transformation validation
│       │   └── output_validator.py   # Output data validation
│       ├── rules/
│       │   ├── __init__.py
│       │   ├── engine.py        # Rule engine integration
│       │   ├── applicator.py    # Rule application logic
│       │   └── validator.py    # Rule structure validation
│       ├── transformation/
│       │   ├── __init__.py
│       │   ├── journal_to_ledger.py  # Core transformation logic
│       │   └── aggregator.py   # Quarterly aggregation
│       ├── audit/
│       │   ├── __init__.py
│       │   ├── trail.py        # Audit trail tracking
│       │   └── exporter.py     # Audit trail export
│       ├── reporting/
│       │   ├── __init__.py
│       │   ├── error_report.py # Excel error report generation
│       │   ├── ledger_output.py # Ledger Excel output
│       │   └── quarterly_report.py # Quarterly aggregation reports
│       └── utils/
│           ├── __init__.py
│           ├── logging.py      # Logging configuration
│           └── exceptions.py   # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_excel_io.py
│   │   ├── test_validation.py
│   │   ├── test_rules.py
│   │   └── test_transformation.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   └── test_rule_application.py
│   └── fixtures/
│       ├── sample_journal.xlsx
│       ├── sample_rules.xlsx
│       └── expected_output.xlsx
├── docs/
│   ├── getting-started.md
│   ├── user-manual.md
│   ├── rule-management.md
│   ├── error-handling.md
│   └── troubleshooting.md
├── examples/
│   ├── journal_entries_sample.xlsx
│   ├── mapping_rules_sample.xlsx
│   └── README.md
└── .venv/                       # Virtual environment (gitignored)
```

## Epic to Architecture Mapping

| Epic | Module/Component | Key Files |
|------|------------------|-----------|
| Epic 1: Foundation | Project setup, Excel I/O, data models | `src/veritas_accounting/excel/`, `src/veritas_accounting/models/`, `pyproject.toml` |
| Epic 2: Input Processing | Excel reading, validation | `src/veritas_accounting/excel/reader.py`, `src/veritas_accounting/validation/input_validator.py` |
| Epic 3: Rule Engine | Rule evaluation, transformation | `src/veritas_accounting/rules/`, `src/veritas_accounting/transformation/` |
| Epic 4: Validation | Multi-layer validation | `src/veritas_accounting/validation/` |
| Epic 5: Audit Trail | Transformation tracking | `src/veritas_accounting/audit/` |
| Epic 6: Output Generation | Excel report generation | `src/veritas_accounting/reporting/` |
| Epic 7: User Interface | CLI interface, configuration | `src/veritas_accounting/cli/`, `src/veritas_accounting/config/` |
| Epic 8: Documentation | User guides | `docs/` |
| Epic 9: Rule Versioning | Rule management | `src/veritas_accounting/rules/` (extended) |

## Technology Stack Details

### Core Technologies

**Python 3.11**
- Runtime: Python 3.11.x (verified stable, excellent performance)
- Type hints: Full support for modern type annotations
- Performance: 10-60% faster than 3.10 for this workload
- Support: Security updates until October 2026+

**pandas 3.0.0**
- Purpose: Excel data manipulation, DataFrame operations
- Key features: Excel reading/writing, data transformation, aggregation
- Integration: Works seamlessly with openpyxl for Excel I/O

**openpyxl 3.1.3**
- Purpose: Excel file reading/writing with full formatting control
- Key features: UTF-8 support, formatting preservation, Chinese text handling
- Integration: Used by pandas for Excel engine, direct use for formatting

**Pydantic 2.12**
- Purpose: Type-safe data models, automatic validation
- Key features: Validation, serialization, error messages, Settings management
- Models: JournalEntry, LedgerEntry, MappingRule, Account, Config

**rule-engine 3.5.0**
- Purpose: Evaluate conditional logic in mapping rules
- Key features: Condition evaluation, field references, logical operators
- Integration: Wrapped in custom RuleEvaluator class

**Click (Latest)**
- Purpose: CLI framework for command-line interface
- Key features: Command composition, help generation, environment variables
- Commands: `process`, `validate`, `version`

### Integration Points

1. **Excel I/O → Data Models**: pandas reads Excel → Pydantic models validate
2. **Data Models → Rule Engine**: JournalEntry → rule-engine evaluates conditions
3. **Rule Engine → Transformation**: Matching rules → LedgerEntry generation
4. **Transformation → Validation**: LedgerEntry → multi-layer validation
5. **Validation → Reporting**: Validation results → Excel error reports
6. **Audit Trail → All Components**: All transformations tracked in audit trail

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Patterns

**Module/File Naming:**
- Use snake_case for all file and module names: `journal_to_ledger.py`, `input_validator.py`
- Match module name to primary class when single class: `reader.py` contains `ExcelReader`
- Use plural for collections: `models/` contains multiple model files

**Class Naming:**
- Use PascalCase for classes: `JournalEntry`, `ExcelReader`, `RuleApplicator`
- Suffix with purpose: `*Reader`, `*Writer`, `*Validator`, `*Transformer`, `*Generator`

**Function/Variable Naming:**
- Use snake_case: `read_journal_entries()`, `apply_rules()`, `validate_input()`
- Use descriptive verbs: `read_`, `write_`, `validate_`, `transform_`, `generate_`

**Constant Naming:**
- Use UPPER_SNAKE_CASE: `DEFAULT_OUTPUT_DIR`, `MAX_ENTRIES_PER_BATCH`

### Structure Patterns

**Test Organization:**
- Co-locate tests with source: `tests/unit/` mirrors `src/veritas_accounting/`
- Use `conftest.py` for shared fixtures
- Test file naming: `test_<module_name>.py`

**Component Organization:**
- Organize by feature/domain: `excel/`, `rules/`, `transformation/`, `validation/`
- Keep related functionality together: All Excel I/O in `excel/` module
- Shared utilities in `utils/` module

**Import Organization:**
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports: `from veritas_accounting.models.journal import JournalEntry`

### Format Patterns

**Error Response Format:**
```python
{
    "error_type": "ValidationError",
    "message": "Human-readable error message",
    "field": "field_name",
    "value": "actual_value",
    "expected": "expected_value",
    "location": {"file": "journal.xlsx", "row": 42, "entry_id": "JE-123"}
}
```

**Logging Format:**
- Structured logging with context: `logger.info("Processing entry", extra={"entry_id": "JE-123", "rule_count": 5})`
- Log levels: DEBUG (development), INFO (normal flow), WARNING (issues), ERROR (failures), CRITICAL (system failure)

**Date/Time Format:**
- Internal: Use `datetime` objects, ISO 8601 strings for serialization
- Display: User-friendly format in reports: "2024-01-15" or "Q1 2024"

### Communication Patterns

**Exception Handling:**
- Custom exceptions inherit from domain base: `VeritasAccountingError`
- Specific exceptions: `ValidationError`, `RuleError`, `TransformationError`, `ExcelIOError`
- Always include context in exception messages

**Function Return Patterns:**
- Validation functions: Return `(result, errors)` tuple
- Processing functions: Return structured result objects
- Use Result/Either pattern for operations that can fail

### Lifecycle Patterns

**Processing Flow:**
1. Load → Validate → Transform → Validate → Generate Output
2. Each stage collects errors, continues processing when possible
3. Fail-fast only on critical errors (file not found, invalid config)

**Error Recovery:**
- Continue processing after non-critical errors
- Collect all errors, report at end
- Provide actionable error messages

**State Management:**
- Immutable data models (Pydantic models)
- Transformations create new objects, never modify input
- Audit trail tracks all state changes

### Location Patterns

**File Paths:**
- Input files: User-specified or config default
- Output files: `{output_dir}/ledger_{timestamp}.xlsx`, `{output_dir}/error_report_{timestamp}.xlsx`
- Config files: `config.yaml` in project root or user-specified path

**Log Files:**
- Default: `logs/veritas_accounting_{timestamp}.log`
- Configurable via settings

### Consistency Patterns

**Date Formatting:**
- Internal: `datetime` objects
- Excel output: "YYYY-MM-DD" format
- Reports: "Q1 2024" for quarters

**Number Formatting:**
- Internal: Python `Decimal` for financial amounts (precision)
- Excel output: Currency format with 2 decimals
- Reports: Formatted as currency

**Error Messages:**
- User-friendly language (no stack traces)
- Include: What went wrong, where, how to fix
- Support English (primary), Chinese if needed

## Consistency Rules

### Naming Conventions

- **Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Prefix with `_` (single underscore)

### Code Organization

- **One class per file** when class is substantial (>100 lines)
- **Group related functions** in same module
- **Keep modules focused** (single responsibility)
- **Use `__init__.py`** to expose public API

### Error Handling

- **Custom exceptions** for domain errors
- **Structured error objects** with context
- **Continue processing** when possible (collect errors)
- **Fail-fast** only on critical errors
- **User-friendly messages** (no technical jargon in user-facing errors)

### Logging Strategy

- **Structured logging** with context (entry_id, rule_id, etc.)
- **Log levels**: DEBUG (dev), INFO (flow), WARNING (issues), ERROR (failures)
- **Dual output**: Console (INFO+) and file (DEBUG+)
- **Log rotation**: Daily log files, keep 30 days
- **Format**: `{timestamp} {level} {module} {message} {context}`

## Data Architecture

### Data Models

**JournalEntry (Pydantic Model)**
```python
class JournalEntry(BaseModel):
    entry_id: str
    year: int
    description: str
    old_type: str
    amount: Decimal
    date: datetime
    # Optional fields as needed
```

**LedgerEntry (Pydantic Model)**
```python
class LedgerEntry(BaseModel):
    entry_id: str
    account_code: str
    account_path: str  # Full hierarchy path
    amount: Decimal
    date: datetime
    description: str
    source_entry_id: str  # Link back to JournalEntry
    rule_applied: str  # Rule ID that generated this entry
```

**MappingRule (Pydantic Model)**
```python
class MappingRule(BaseModel):
    rule_id: str
    condition: str  # rule-engine expression
    old_type: Optional[str]
    new_type: Optional[str]
    account_code: str
    priority: int
    # One-to-many support
    generates_multiple: bool = False
```

**Account (Pydantic Model)**
```python
class Account(BaseModel):
    code: str
    name: str
    level: int  # 1-4
    parent_code: Optional[str]
    full_path: str  # "Level1/Level2/Level3/Level4"
```

### Data Flow

1. **Input**: Excel file → pandas DataFrame → Pydantic JournalEntry models
2. **Rule Application**: JournalEntry → rule-engine evaluation → Matching rules
3. **Transformation**: JournalEntry + Rules → LedgerEntry generation
4. **Validation**: LedgerEntry → Multi-layer validation → Validated entries
5. **Output**: LedgerEntry → pandas DataFrame → Excel file with formatting
6. **Audit Trail**: All transformations → AuditTrail records → Export

### Data Relationships

- **JournalEntry 1:N LedgerEntry** (one-to-many via rules)
- **MappingRule 1:N LedgerEntry** (one rule can generate multiple entries)
- **Account 1:N LedgerEntry** (hierarchical account structure)
- **TransformationRecord** links JournalEntry → Rules → LedgerEntry

## API Contracts

### CLI Interface

**Command: `veritas-accounting process`**
```bash
veritas-accounting process \
  --input journal.xlsx \
  --rules rules.xlsx \
  --output ./output \
  --config config.yaml
```

**Arguments:**
- `--input` (required): Path to journal entries Excel file
- `--rules` (optional): Path to mapping rules Excel file (default: config)
- `--output` (optional): Output directory (default: `./output`)
- `--config` (optional): Configuration file path
- `--verbose` (flag): Enable debug logging

**Response:**
- Exit code 0: Success
- Exit code 1: Validation errors (check error report)
- Exit code 2: Processing errors (check logs)

### Configuration File Format (YAML)

```yaml
input:
  journal_file: "journal.xlsx"
  rules_file: "rules.xlsx"
  account_hierarchy_file: "accounts.xlsx"

output:
  directory: "./output"
  ledger_filename: "ledger_{timestamp}.xlsx"
  error_report_filename: "error_report_{timestamp}.xlsx"

validation:
  level: "strict"  # strict | lenient
  auto_fix_enabled: false

logging:
  level: "INFO"  # DEBUG | INFO | WARNING | ERROR
  file: "logs/veritas_accounting.log"
```

### Internal API Patterns

**Function Signatures:**
```python
def read_journal_entries(file_path: Path) -> tuple[list[JournalEntry], list[ValidationError]]:
    """Returns (entries, errors) tuple"""

def apply_rules(entry: JournalEntry, rules: list[MappingRule]) -> list[LedgerEntry]:
    """Returns list of generated ledger entries"""

def validate_output(ledger_entries: list[LedgerEntry]) -> ValidationResult:
    """Returns structured validation result"""
```

## Security Architecture

**Data Protection:**
- No network access (standalone tool)
- Input files read-only (never modified)
- Original data preserved alongside processed data
- Audit trail for compliance

**Error Handling:**
- No sensitive data in error messages
- File paths sanitized in logs
- Exception messages user-friendly (no stack traces to users)

**Validation:**
- Input validation prevents malicious data
- Rule validation prevents invalid transformations
- Output validation ensures data integrity

## Performance Considerations

**Processing Optimization:**
- Rule compilation: Compile rules once, reuse for all entries
- Batch processing: Process entries in batches if memory constrained
- Efficient Excel I/O: Use pandas for bulk operations, openpyxl for formatting
- Target: 691 entries in < 5 minutes

**Memory Management:**
- Stream processing for large files (if needed)
- Clear intermediate data structures
- Efficient DataFrame operations

**Caching:**
- Compiled rules cached in memory
- Account hierarchy loaded once
- No persistent caching (stateless processing)

## Deployment Architecture

**Deployment Model:**
- Standalone Python application
- No server/infrastructure required
- Local execution on user's machine
- Virtual environment for isolation

**Distribution:**
- Installable via pip: `pip install veritas-accounting`
- Or: Clone repository, install dependencies
- Requirements: Python 3.11+, dependencies in pyproject.toml

**Environment:**
- Python virtual environment (`.venv/`)
- Dependencies managed via `pyproject.toml`
- No external services required

## Development Environment

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for version control)
- Text editor/IDE (VS Code, PyCharm, etc.)

### Setup Commands

```bash
# Clone repository (if applicable)
git clone <repository-url>
cd veritas-accounting

# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run application
veritas-accounting --help
```

## Architecture Decision Records (ADRs)

### ADR-001: Python 3.11 Selection
**Decision**: Use Python 3.11 as the runtime version.  
**Rationale**: Stable release with excellent performance improvements, full type hint support, and long-term support. Better than 3.10 for performance, more stable than 3.12 for production use.  
**Alternatives Considered**: Python 3.10 (slower), Python 3.12 (newer, less battle-tested)  
**Status**: Accepted

### ADR-002: Click for CLI Framework
**Decision**: Use Click instead of argparse or Typer for CLI interface.  
**Rationale**: Mature, composable, excellent for complex CLIs. Supports environment variables, nested commands, and has better error handling than argparse. More stable than Typer.  
**Alternatives Considered**: argparse (verbose, limited features), Typer (newer, less mature)  
**Status**: Accepted

### ADR-003: Pydantic for Data Validation
**Decision**: Use Pydantic 2.x for all data models and validation.  
**Rationale**: Type-safe models, automatic validation, excellent error messages. Integrates well with type hints. Settings management built-in.  
**Alternatives Considered**: Manual validation (error-prone), dataclasses (no validation)  
**Status**: Accepted

### ADR-004: rule-engine for Rule Evaluation
**Decision**: Use rule-engine library for evaluating mapping rule conditions.  
**Rationale**: Supports complex conditional logic, efficient evaluation, handles field references and logical operators. Fits the 194-rule requirement perfectly.  
**Alternatives Considered**: Custom parser (complex, error-prone), simpleruleengine (less features)  
**Status**: Accepted

### ADR-005: openpyxl for Excel Formatting
**Decision**: Use openpyxl directly for formatting, pandas for data operations.  
**Rationale**: openpyxl provides full formatting control (required for FR11), UTF-8 support for Chinese text, preserves Excel structure. pandas handles data efficiently, openpyxl handles formatting.  
**Alternatives Considered**: pandas only (limited formatting), xlsxwriter (write-only)  
**Status**: Accepted

### ADR-006: src-layout Project Structure
**Decision**: Use src-layout (src/veritas_accounting/) instead of flat structure.  
**Rationale**: Modern Python packaging standard, clear separation, better for distribution, prevents import issues.  
**Alternatives Considered**: Flat structure (simpler but less professional)  
**Status**: Accepted

### ADR-007: Immutable Data Models
**Decision**: All Pydantic models are immutable (frozen=True where appropriate).  
**Rationale**: Prevents accidental mutations, ensures data integrity, makes transformations explicit. Original data always preserved.  
**Alternatives Considered**: Mutable models (easier but error-prone)  
**Status**: Accepted

### ADR-008: Multi-layer Validation Strategy
**Decision**: Implement validation at input, transformation, and output stages.  
**Rationale**: Catches errors early, ensures 100% accuracy requirement, provides comprehensive error reporting. Each stage validates different aspects.  
**Alternatives Considered**: Single validation point (less thorough)  
**Status**: Accepted

---

_Generated by BMAD Decision Architecture Workflow v1.0_  
_Date: 2025-01-27_  
_For: dan_
