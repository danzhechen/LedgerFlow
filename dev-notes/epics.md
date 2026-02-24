# veritas-accounting - Epic Breakdown

**Author:** dan  
**Date:** 2025-01-27  
**Project Level:** Medium  
**Target Scale:** Internal Tool / Business Process Automation

---

## Overview

This document provides the complete epic and story breakdown for veritas-accounting, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

---

## Functional Requirements Inventory

**Input Processing (FR1-FR5):**
- FR1: The system MUST accept Excel files containing journal entries (691+ entries per quarter)
- FR2: The system MUST validate journal entry structure (required columns, data types, value ranges)
- FR3: The system MUST read 194 mapping rules from Excel files or configuration
- FR4: The system MUST validate mapping rule structure and logic
- FR5: The system MUST handle Chinese text encoding in input files

**Rule Application & Transformation (FR6-FR11):**
- FR6: The system MUST apply all 194 mapping rules automatically to journal entries (no manual lookup required)
- FR7: The system MUST handle conditional logic in mapping rules (if-then-else conditions)
- FR8: The system MUST support one-to-many mappings (one journal entry → multiple ledger entries)
- FR9: The system MUST transform journal entries → ledger structure with hierarchical organization (4 levels, 25 accounts)
- FR10: The system MUST generate quarterly aggregations from ledger entries
- FR11: The system MUST preserve Excel formatting and structure in output files

**Validation & Error Detection (FR12-FR17):**
- FR12: The system MUST validate input data before processing (structure, completeness, data types)
- FR13: The system MUST validate transformation logic during processing (rule application, mapping correctness)
- FR14: The system MUST validate output data after processing (completeness, consistency, accuracy)
- FR15: The system MUST detect and flag all errors for human review
- FR16: The system MUST provide detailed error messages explaining what went wrong and why
- FR17: The system MUST support auto-fix suggestions with review flags (expert approves all fixes)

**Transparency & Audit Trail (FR18-FR22):**
- FR18: The system MUST track all transformations in a complete audit trail
- FR19: The system MUST generate Excel error reports showing all changes and issues
- FR20: The system MUST make all transformations visible and reviewable
- FR21: The system MUST show validation results and confidence indicators
- FR22: The system MUST preserve original data alongside processed data for comparison

**Output & Reporting (FR23-FR26):**
- FR23: The system MUST generate ledger output in Excel format with preserved formatting
- FR24: The system MUST generate quarterly aggregation reports
- FR25: The system MUST generate comprehensive error reports in Excel format
- FR26: The system MUST support export of audit trail data

**Rule Management (FR27-FR29):**
- FR27: The system MUST allow rules to be edited in Excel files (no code changes required)
- FR28: The system MUST validate rule syntax and logic before application
- FR29: The system MUST support rule versioning (track rule changes over time)

**User Experience (FR30-FR33):**
- FR30: The system MUST provide clear, actionable error messages
- FR31: The system MUST use Excel-native workflow (familiar interface, no new tools to learn)
- FR32: The system MUST provide simple process flow: input → process → review → output
- FR33: The system MUST be operable by non-expert users after brief training (< 2 hours)

**Developer Tool Specific Requirements:**
- FR-EXCEL1: The system MUST read journal entries from Excel files (standard .xlsx format)
- FR-EXCEL2: The system MUST read 194 mapping rules from Excel files or configuration files
- FR-EXCEL3: The system MUST write ledger output to Excel files with preserved formatting
- FR-EXCEL4: The system MUST generate Excel error reports with clear formatting and explanations
- FR-EXCEL5: The system MUST support Chinese text encoding in Excel files
- FR-API1: The system MUST provide a Python script/application entrypoint
- FR-API2: The system MUST support configuration via Excel-based rule files, configuration files (YAML/JSON), and command-line arguments
- FR-API3: The system MUST provide clear error messages and exceptions
- FR-INST1: The system MUST be installable via standard Python package managers
- FR-INST2: The system MUST have clear installation instructions and dependency management
- FR-INST3: The system MUST work in standard Python environments
- FR-DOC1: The system MUST provide usage documentation, rule management guide, error handling guide, and troubleshooting guide
- FR-DOC2: The system MUST include example Excel files

**Total: 33 core FRs + 13 developer tool FRs = 46 functional requirements**

---

## Epic Structure Summary

**Epic 1: Foundation & Project Setup**
- Establishes project infrastructure, core dependencies, and basic Excel I/O capabilities
- **FR Coverage:** FR-INST1, FR-INST2, FR-INST3, FR-DOC1 (foundation), FR-EXCEL1 (basic reading)

**Epic 2: Input Processing & Validation**
- Handles reading and validating journal entries and mapping rules from Excel
- **FR Coverage:** FR1, FR2, FR3, FR4, FR5, FR-EXCEL1, FR-EXCEL2, FR-EXCEL5, FR12

**Epic 3: Rule Engine & Transformation Core**
- Implements rule evaluation engine and journal → ledger transformation logic
- **FR Coverage:** FR6, FR7, FR8, FR9, FR10, FR13, FR27, FR28

**Epic 4: Validation & Error Detection**
- Comprehensive validation pipeline and error detection system
- **FR Coverage:** FR14, FR15, FR16, FR17, FR21

**Epic 5: Transparency & Audit Trail**
- Complete audit trail tracking and transformation visibility
- **FR Coverage:** FR18, FR19, FR20, FR22, FR26

**Epic 6: Output Generation & Reporting**
- Excel output generation with formatting preservation and error reports
- **FR Coverage:** FR11, FR23, FR24, FR25, FR-EXCEL3, FR-EXCEL4

**Epic 7: User Interface & Experience**
- CLI interface, configuration management, and user-friendly error messaging
- **FR Coverage:** FR30, FR31, FR32, FR33, FR-API1, FR-API2, FR-API3

**Epic 8: Documentation & Examples**
- Complete documentation and example files for users
- **FR Coverage:** FR-DOC1, FR-DOC2

**Epic 9: Rule Management & Versioning**
- Advanced rule management features (versioning, change tracking)
- **FR Coverage:** FR29

---

## FR Coverage Map

**Epic 1 (Foundation):** FR-INST1, FR-INST2, FR-INST3, FR-DOC1 (foundation), FR-EXCEL1 (basic)
**Epic 2 (Input Processing):** FR1, FR2, FR3, FR4, FR5, FR-EXCEL1, FR-EXCEL2, FR-EXCEL5, FR12
**Epic 3 (Rule Engine):** FR6, FR7, FR8, FR9, FR10, FR13, FR27, FR28
**Epic 4 (Validation):** FR14, FR15, FR16, FR17, FR21
**Epic 5 (Audit Trail):** FR18, FR19, FR20, FR22, FR26
**Epic 6 (Output):** FR11, FR23, FR24, FR25, FR-EXCEL3, FR-EXCEL4
**Epic 7 (User Interface):** FR30, FR31, FR32, FR33, FR-API1, FR-API2, FR-API3
**Epic 8 (Documentation):** FR-DOC1, FR-DOC2
**Epic 9 (Rule Versioning):** FR29

---

## Epic 1: Foundation & Project Setup

**Goal:** Establish the project infrastructure, core dependencies, development environment, and basic Excel I/O capabilities that enable all subsequent development work.

### Story 1.1: Project Structure & Core Dependencies

As a **developer**,
I want **a well-organized project structure with core dependencies installed**,
So that **I have a solid foundation for building the accounting automation system**.

**Acceptance Criteria:**

**Given** a new Python project directory
**When** I set up the project structure
**Then** the project has:
- Standard Python package structure (`src/veritas_accounting/` or similar)
- `pyproject.toml` or `requirements.txt` with core dependencies (pandas, openpyxl, Pydantic, rule-engine)
- Virtual environment setup instructions
- Basic README.md with project overview
- `.gitignore` for Python projects
- Basic logging configuration

**And** all dependencies can be installed via `pip install -r requirements.txt` or `poetry install`

**Prerequisites:** None (this is the first story)

**Technical Notes:**
- Use Python 3.8+ (specify in pyproject.toml or requirements.txt)
- Core dependencies: pandas, openpyxl, Pydantic, rule-engine, pathlib (standard library)
- Project structure should separate: data models, rule engine, Excel I/O, validation, transformation, CLI
- Set up basic logging to file and console

---

### Story 1.2: Basic Excel File Reading

As a **developer**,
I want **basic Excel file reading capability using openpyxl**,
So that **I can read journal entries and mapping rules from Excel files**.

**Acceptance Criteria:**

**Given** an Excel file (.xlsx format) with data
**When** I use the Excel reader module
**Then** the system can:
- Read Excel files using openpyxl with UTF-8 encoding support
- Handle Chinese text encoding correctly
- Read data from specified worksheets
- Return data as pandas DataFrame or structured data format
- Provide clear error messages if file is missing, corrupted, or has invalid format

**And** the reader handles:
- Missing files gracefully (FileNotFoundError with clear message)
- Corrupted files (openpyxl exceptions caught and re-raised with context)
- Empty worksheets (returns empty DataFrame)
- Multiple worksheets (can specify which sheet to read)

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Use openpyxl for Excel reading (preserves formatting, handles .xlsx)
- Use pandas `read_excel()` with openpyxl engine for data processing
- Set encoding to UTF-8 for Chinese text support
- Create `ExcelReader` class or module with methods: `read_file(path)`, `read_sheet(path, sheet_name)`
- Wrap openpyxl exceptions in custom exceptions with user-friendly messages

---

### Story 1.3: Basic Excel File Writing

As a **developer**,
I want **basic Excel file writing capability using openpyxl**,
So that **I can write ledger output and error reports to Excel files**.

**Acceptance Criteria:**

**Given** structured data (DataFrame or list of dictionaries)
**When** I use the Excel writer module
**Then** the system can:
- Write data to Excel files (.xlsx format) using openpyxl
- Create new Excel files or overwrite existing ones
- Write to specified worksheets
- Preserve basic formatting (column widths, header row styling)
- Handle Chinese text encoding correctly

**And** the writer:
- Creates directory structure if output path doesn't exist
- Handles write permissions errors gracefully
- Provides clear error messages for invalid data formats

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Use openpyxl for Excel writing (full formatting control)
- Create `ExcelWriter` class or module with methods: `write_file(data, path)`, `write_sheet(data, path, sheet_name)`
- Use pandas `to_excel()` with openpyxl engine for DataFrame writing, then enhance with openpyxl for formatting
- Set UTF-8 encoding for Chinese text
- Basic formatting: auto-adjust column widths, bold header row

---

### Story 1.4: Core Data Models with Pydantic

As a **developer**,
I want **type-safe data models using Pydantic**,
So that **I can validate journal entries, mapping rules, and ledger entries with clear error messages**.

**Acceptance Criteria:**

**Given** raw data from Excel files
**When** I create data model instances
**Then** the system:
- Defines Pydantic models for: JournalEntry, MappingRule, LedgerEntry, AccountHierarchy
- Validates data types automatically (int, str, float, date, etc.)
- Provides detailed validation error messages showing which field failed and why
- Handles optional fields correctly
- Supports Chinese text in string fields

**And** validation errors include:
- Field name that failed
- Expected type vs actual type
- Value that caused the error
- Clear message explaining the issue

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Create `models.py` or `data_models.py` with Pydantic BaseModel classes
- Models: `JournalEntry`, `MappingRule`, `LedgerEntry`, `Account`, `TransformationAudit`
- Use Pydantic validators for custom validation logic (e.g., date ranges, account code formats)
- Define Field() with descriptions for better error messages
- Use `Optional[]` for fields that may be missing
- Consider using `pandantic` for DataFrame validation if needed

---

## Epic 2: Input Processing & Validation

**Goal:** Read and validate journal entries and mapping rules from Excel files, ensuring data quality before processing begins.

### Story 2.1: Journal Entry Excel Reader

As an **accounting operator**,
I want **the system to read journal entries from my Excel file**,
So that **I can process 691+ entries automatically without manual data entry**.

**Acceptance Criteria:**

**Given** an Excel file containing journal entries
**When** I provide the file path to the system
**Then** the system:
- Reads the Excel file using the Excel reader from Epic 1
- Identifies the correct worksheet (by name or first sheet)
- Parses rows into JournalEntry data models
- Handles expected columns: year, description, old_type, amount, date (exact column names TBD based on actual file structure)
- Returns a list of validated JournalEntry objects
- Provides clear error if required columns are missing

**And** the system handles:
- Empty rows (skips them)
- Header row (identifies and skips)
- Chinese text in description and type fields
- Different date formats (standardizes to datetime objects)
- Missing optional fields (uses None or default values)

**Prerequisites:** Story 1.2 (Excel reading), Story 1.4 (data models)

**Technical Notes:**
- Create `JournalEntryReader` class that uses ExcelReader and JournalEntry model
- Column mapping: Map Excel column names to JournalEntry model fields (flexible mapping for different file formats)
- Date parsing: Use pandas `to_datetime()` with multiple format attempts
- Error handling: Collect all validation errors and report them together (don't fail on first error)
- Return structured result: `(entries: List[JournalEntry], errors: List[ValidationError])`

---

### Story 2.2: Journal Entry Structure Validation

As an **accounting operator**,
I want **the system to validate journal entry structure and data quality**,
So that **I catch data issues before processing begins**.

**Acceptance Criteria:**

**Given** journal entries read from Excel
**When** the system validates the entries
**Then** the system checks:
- Required columns are present (year, description, old_type, amount)
- Data types are correct (year is integer, amount is numeric, date is valid date)
- Value ranges are valid (year is reasonable, amount is not null, dates are in valid range)
- No duplicate entries (based on key fields - TBD: what makes an entry unique?)
- All entries have required fields populated (no nulls in required columns)

**And** validation errors are:
- Collected and reported together (not fail-fast)
- Categorized by error type (missing column, invalid type, invalid value, duplicate)
- Include row numbers and field names for easy fixing
- Written to a validation error report

**Prerequisites:** Story 2.1 (journal entry reader)

**Technical Notes:**
- Create `JournalEntryValidator` class using Pydantic validation
- Use Pydantic validators for custom checks (date ranges, amount ranges, etc.)
- Validation checks:
  - Structure: Required columns present
  - Types: Use Pydantic type validation
  - Values: Custom validators for business rules (e.g., year between 2020-2030, amount > 0)
  - Uniqueness: Check for duplicates based on composite key (year + description + date?)
- Return validation result: `(valid_entries: List[JournalEntry], errors: List[ValidationError])`
- Each ValidationError should have: row_number, field_name, error_type, error_message, actual_value

---

### Story 2.3: Mapping Rules Excel Reader

As an **accounting operator**,
I want **the system to read 194 mapping rules from my Excel file**,
So that **rules can be edited in Excel without code changes**.

**Acceptance Criteria:**

**Given** an Excel file containing mapping rules
**When** I provide the file path to the system
**Then** the system:
- Reads the Excel file using the Excel reader
- Identifies the mapping rules worksheet
- Parses rows into MappingRule data models
- Handles expected columns: condition, old_type, new_type, account_code, priority (exact structure TBD)
- Returns a list of validated MappingRule objects
- Provides clear error if rule structure is invalid

**And** the system handles:
- Rule conditions in various formats (simple equality, conditional logic, regex patterns)
- One-to-many mappings (one rule → multiple ledger entries)
- Rule priority/ordering (rules may need to be applied in specific order)
- Chinese text in rule descriptions and account names

**Prerequisites:** Story 1.2 (Excel reading), Story 1.4 (data models)

**Technical Notes:**
- Create `MappingRuleReader` class
- Rule structure (TBD based on actual format):
  - Condition: String expression (e.g., "old_type == 'OL' and year == 2022")
  - Old type: Source journal entry type
  - New type: Target ledger account type
  - Account code: Target account in hierarchy (4 levels, 25 accounts)
  - Priority: Rule application order
- Use rule-engine library syntax for condition parsing (or custom parser)
- Validate rule syntax during reading (catch invalid conditions early)
- Return structured result: `(rules: List[MappingRule], errors: List[ValidationError])`

---

### Story 2.4: Mapping Rule Structure Validation

As an **accounting operator**,
I want **the system to validate mapping rule structure and logic**,
So that **I catch rule errors before they cause processing failures**.

**Acceptance Criteria:**

**Given** mapping rules read from Excel
**When** the system validates the rules
**Then** the system checks:
- Rule syntax is valid (condition expressions can be parsed)
- Required fields are present (condition, old_type or new_type, account_code)
- Rule conditions reference valid fields (no typos in field names)
- Account codes exist in account hierarchy (4 levels, 25 accounts)
- No conflicting rules (same condition → different results without priority)
- Rule priority is valid (unique priorities or clear conflict resolution)

**And** validation errors are:
- Collected and reported together
- Categorized by error type (syntax error, missing field, invalid reference, conflict)
- Include rule numbers/IDs for easy fixing
- Written to a validation error report

**Prerequisites:** Story 2.3 (mapping rules reader), Story 3.1 (account hierarchy - if needed for validation)

**Technical Notes:**
- Create `MappingRuleValidator` class
- Syntax validation: Use rule-engine library to parse and validate condition expressions
- Field reference validation: Check that condition fields match JournalEntry model fields
- Account code validation: Load account hierarchy and verify codes exist
- Conflict detection: Identify rules with same condition but different results
- Priority validation: Ensure priority values are unique or conflict resolution is clear
- Return validation result: `(valid_rules: List[MappingRule], errors: List[ValidationError])`

---

### Story 2.5: Chinese Text Encoding Support

As an **accounting operator**,
I want **the system to handle Chinese text correctly in Excel files**,
So that **I can use Chinese descriptions and account names without encoding issues**.

**Acceptance Criteria:**

**Given** Excel files with Chinese text
**When** the system reads or writes files
**Then** the system:
- Reads Chinese characters correctly (no garbled text, no encoding errors)
- Writes Chinese characters correctly to output files
- Preserves Chinese text in all transformations
- Handles Chinese text in error messages and reports

**And** the system:
- Uses UTF-8 encoding consistently
- Handles both simplified and traditional Chinese
- Works on Windows, Mac, and Linux systems
- Provides clear error messages if encoding issues occur

**Prerequisites:** Story 1.2 (Excel reading), Story 1.3 (Excel writing)

**Technical Notes:**
- Ensure openpyxl uses UTF-8 encoding (default in openpyxl 3.0+)
- Set encoding explicitly in file operations: `open(file, encoding='utf-8')`
- Test with actual Chinese text from `账目分类明细.xlsx`
- Use `chardet` library if needed to detect encoding of input files
- In pandas: `read_excel(engine='openpyxl')` handles UTF-8 correctly
- In error messages: Use Unicode strings, ensure console/terminal supports UTF-8

---

## Epic 3: Rule Engine & Transformation Core

**Goal:** Implement the core rule evaluation engine and journal → ledger transformation logic that automates the 194 mapping rules.

### Story 3.1: Account Hierarchy Model

As a **developer**,
I want **a data model for the account hierarchy (4 levels, 25 accounts)**,
So that **I can organize ledger entries into the correct account structure**.

**Acceptance Criteria:**

**Given** the account hierarchy structure (4 levels, 25 accounts)
**When** I create the account model
**Then** the system:
- Defines Account model with: code, name, level (1-4), parent_code, full_path
- Loads account hierarchy from configuration or Excel file
- Validates account codes are unique
- Validates parent-child relationships are valid (no circular references)
- Provides methods to find accounts by code, get full path, get children

**And** the model:
- Supports hierarchical queries (get all accounts under a parent)
- Validates account codes match expected format (TBD: format of account codes)
- Handles Chinese account names

**Prerequisites:** Story 1.4 (data models)

**Technical Notes:**
- Create `Account` Pydantic model with hierarchical structure
- Account structure: 4 levels (e.g., Level 1: Major category, Level 2: Category, Level 3: Subcategory, Level 4: Account)
- 25 total accounts across all levels
- Store hierarchy in tree structure or flat list with parent references
- Create `AccountHierarchy` class with methods: `get_account(code)`, `get_children(parent_code)`, `get_full_path(code)`
- Load from Excel file or YAML/JSON config file
- Validate no circular references in parent-child relationships

---

### Story 3.2: Rule Engine Integration

As a **developer**,
I want **to integrate the rule-engine library for evaluating mapping rule conditions**,
So that **I can apply conditional logic from the 194 mapping rules**.

**Acceptance Criteria:**

**Given** a mapping rule with a condition expression
**When** I evaluate the rule against a journal entry
**Then** the system:
- Parses the condition expression using rule-engine syntax
- Evaluates the condition against journal entry data
- Returns True if condition matches, False otherwise
- Handles complex conditions (AND, OR, comparisons, string matching)
- Provides clear error messages if condition syntax is invalid

**And** the rule engine:
- Supports field references (e.g., `old_type`, `year`, `amount`)
- Supports comparison operators (==, !=, <, >, <=, >=)
- Supports logical operators (AND, OR, NOT)
- Supports string matching (contains, starts_with, regex - if needed)
- Handles null/None values correctly

**Prerequisites:** Story 2.3 (mapping rules reader), Story 1.4 (data models)

**Technical Notes:**
- Use `rule-engine` library (or `simpleruleengine` as alternative)
- Create `RuleEvaluator` class that wraps rule-engine
- Convert JournalEntry to dictionary for rule evaluation: `entry.dict()`
- Rule syntax examples:
  - Simple: `old_type == "OL"`
  - Complex: `old_type == "OL" and year == 2022 and amount > 1000`
- Error handling: Catch rule-engine exceptions and convert to user-friendly messages
- Performance: Compile rules once, reuse compiled rules for all entries (691 entries × 194 rules = many evaluations)

---

### Story 3.3: Rule Application Logic

As a **developer**,
I want **to apply mapping rules to journal entries automatically**,
So that **all 194 rules are evaluated without manual lookup**.

**Acceptance Criteria:**

**Given** a journal entry and a list of validated mapping rules
**When** I apply the rules to the entry
**Then** the system:
- Evaluates each rule's condition against the journal entry
- Finds all matching rules (may be multiple matches)
- Applies rule priority if multiple rules match (highest priority first, or all if one-to-many)
- Generates ledger entries based on matching rules
- Returns list of generated ledger entries (may be multiple for one-to-many mappings)

**And** the system:
- Handles one-to-many mappings (one journal entry → multiple ledger entries)
- Applies rules in priority order (if priority specified)
- Tracks which rules were applied (for audit trail)
- Handles cases where no rules match (flags for review)

**Prerequisites:** Story 3.2 (rule engine), Story 2.4 (rule validation)

**Technical Notes:**
- Create `RuleApplicator` class
- Algorithm:
  1. For each journal entry:
    2. Evaluate all rules against entry
    3. Collect matching rules
    4. Sort by priority (if specified)
    5. Apply rules (may generate multiple ledger entries)
    6. Return list of ledger entries
- One-to-many: One rule may specify multiple account codes or generate multiple ledger entries
- No match handling: Flag entry for manual review, log warning
- Performance: Optimize rule evaluation (compile rules once, use efficient matching)

---

### Story 3.4: Journal to Ledger Transformation

As an **accounting operator**,
I want **journal entries automatically transformed into ledger structure**,
So that **I don't have to manually map journal → ledger**.

**Acceptance Criteria:**

**Given** journal entries and applied mapping rules
**When** the system transforms entries to ledger structure
**Then** the system:
- Creates ledger entries with hierarchical account structure (4 levels, 25 accounts)
- Maps journal entry data to ledger entry fields (amount, date, description, account code)
- Organizes entries by account hierarchy
- Preserves all original journal entry information (for audit trail)
- Generates ledger entries in correct format for quarterly aggregation

**And** the transformation:
- Handles one-to-many mappings correctly (one journal → multiple ledger entries)
- Maintains data integrity (amounts balance, dates preserved, descriptions copied)
- Links ledger entries back to source journal entries (for traceability)

**Prerequisites:** Story 3.3 (rule application), Story 3.1 (account hierarchy)

**Technical Notes:**
- Create `JournalToLedgerTransformer` class
- Transformation logic:
  1. For each journal entry:
    2. Apply rules to get target account codes
    3. Create ledger entry for each target account
    4. Copy relevant data (amount, date, description)
    5. Set account code and hierarchy path
    6. Link back to source journal entry (entry_id)
- Ledger entry structure: account_code, account_path, amount, date, description, source_entry_id, rule_applied
- Data integrity: Ensure amounts are correctly allocated in one-to-many cases
- Preserve original: Keep journal entry data alongside ledger entry for audit

---

### Story 3.5: Quarterly Aggregation

As an **accounting operator**,
I want **quarterly aggregations generated automatically from ledger entries**,
So that **I get summary reports without manual calculation**.

**Acceptance Criteria:**

**Given** ledger entries for a quarter
**When** the system generates quarterly aggregations
**Then** the system:
- Groups ledger entries by account code and quarter
- Calculates totals for each account (sum of amounts)
- Organizes aggregations by account hierarchy (4 levels)
- Generates summary at each hierarchy level (Level 1 totals, Level 2 totals, etc.)
- Preserves quarterly period information (Q1, Q2, Q3, Q4, year)

**And** the aggregation:
- Handles multiple quarters in same dataset (if processing multiple quarters)
- Provides drill-down capability (can see details behind totals)
- Validates totals balance correctly (accounting equation checks)

**Prerequisites:** Story 3.4 (journal to ledger transformation)

**Technical Notes:**
- Create `QuarterlyAggregator` class
- Use pandas groupby for efficient aggregation:
  - Group by: account_code, quarter, year
  - Aggregate: sum(amount), count(entries)
- Generate hierarchical totals:
  - Level 4: Individual account totals
  - Level 3: Sum of Level 4 accounts
  - Level 2: Sum of Level 3 accounts
  - Level 1: Sum of Level 2 accounts
- Output format: DataFrame or structured data with hierarchy preserved
- Validation: Check accounting equation (debits = credits, if applicable)

---

## Epic 4: Validation & Error Detection

**Goal:** Implement comprehensive validation pipeline and error detection system that ensures 100% accuracy and catches all issues before they impact financial reports.

### Story 4.1: Input Data Validation Pipeline

As an **accounting operator**,
I want **comprehensive input data validation before processing**,
So that **I catch data quality issues early**.

**Acceptance Criteria:**

**Given** journal entries and mapping rules loaded from Excel
**When** the system validates input data
**Then** the system performs:
- Structure validation (required columns, data types - from Epic 2)
- Business rule validation (year ranges, amount ranges, date validity)
- Completeness validation (no nulls in required fields)
- Consistency validation (dates are in same quarter, amounts are reasonable)
- Cross-reference validation (account codes in rules exist in hierarchy)

**And** validation results:
- Are collected and reported together (not fail-fast)
- Include severity levels (error, warning, info)
- Provide actionable error messages (what's wrong, how to fix)
- Are written to validation report Excel file

**Prerequisites:** Story 2.2 (journal validation), Story 2.4 (rule validation)

**Technical Notes:**
- Create `InputValidationPipeline` class
- Validation stages:
  1. Structure validation (Pydantic models)
  2. Business rule validation (custom validators)
  3. Completeness validation (null checks)
  4. Consistency validation (cross-field checks)
  5. Reference validation (foreign key checks)
- Return validation result: `(is_valid: bool, errors: List[ValidationError], warnings: List[ValidationWarning])`
- Each error/warning: type, severity, message, field, value, row_number

---

### Story 4.2: Transformation Validation

As an **accounting operator**,
I want **validation during transformation to catch mapping errors**,
So that **I ensure rules are applied correctly**.

**Acceptance Criteria:**

**Given** journal entries being transformed to ledger entries
**When** the system validates the transformation
**Then** the system checks:
- All journal entries have matching rules (or flags unmatched entries)
- Rule application is correct (conditions match, results are valid)
- Ledger entries have valid account codes (exist in hierarchy)
- Amounts are preserved correctly (no data loss in transformation)
- One-to-many mappings are complete (all expected ledger entries created)

**And** validation errors:
- Are flagged immediately during transformation
- Include which journal entry failed, which rule was applied, what went wrong
- Are collected for error report

**Prerequisites:** Story 3.3 (rule application), Story 3.4 (transformation)

**Technical Notes:**
- Create `TransformationValidator` class
- Validation checks:
  - Rule match validation: Every journal entry has at least one matching rule (or explicit "no match" flag)
  - Rule correctness: Verify rule condition actually matches entry data
  - Account code validation: All generated account codes exist in hierarchy
  - Amount preservation: Sum of ledger entry amounts equals journal entry amount (for one-to-many)
  - Completeness: All expected ledger entries created (based on rule specifications)
- Real-time validation: Validate during transformation, don't wait until end
- Error collection: Collect errors but continue processing (don't fail-fast)

---

### Story 4.3: Output Data Validation

As an **accounting operator**,
I want **validation of final output data to ensure correctness**,
So that **I have confidence in the generated ledger and reports**.

**Acceptance Criteria:**

**Given** ledger entries and quarterly aggregations
**When** the system validates output data
**Then** the system checks:
- Completeness (all journal entries processed, no entries lost)
- Consistency (totals balance, hierarchy sums correctly)
- Accuracy (amounts match source, dates preserved, descriptions correct)
- Account structure (all account codes valid, hierarchy relationships correct)
- Quarterly totals (aggregations sum correctly at each level)

**And** validation includes:
- Accounting equation checks (if applicable: debits = credits)
- Balance checks (opening + transactions = closing)
- Cross-quarter consistency (if processing multiple quarters)

**Prerequisites:** Story 3.5 (quarterly aggregation), Story 4.2 (transformation validation)

**Technical Notes:**
- Create `OutputValidator` class
- Validation checks:
  - Completeness: Count journal entries in = count ledger entries out (accounting for one-to-many)
  - Consistency: Hierarchical totals sum correctly (Level 4 → Level 3 → Level 2 → Level 1)
  - Accuracy: Sample check - verify random entries match source data
  - Account structure: All account codes in ledger exist in hierarchy
  - Quarterly totals: Aggregations sum correctly, no double-counting
- Accounting validation: If applicable, check debits = credits, balance equations
- Return validation result: `(is_valid: bool, errors: List[ValidationError], summary: ValidationSummary)`

---

### Story 4.4: Error Detection & Flagging

As an **accounting operator**,
I want **all errors detected and flagged for review**,
So that **I don't miss any issues that could affect financial reports**.

**Acceptance Criteria:**

**Given** validation results from all stages (input, transformation, output)
**When** the system detects errors
**Then** the system:
- Collects all errors from all validation stages
- Categorizes errors by type (data error, rule error, transformation error, output error)
- Assigns severity levels (critical, error, warning, info)
- Flags errors for human review (all errors require review, no auto-ignore)
- Provides error context (which entry, which rule, what value, what expected)

**And** error detection:
- Has zero tolerance for undetected errors (100% error detection target)
- Provides actionable error messages (what's wrong, how to fix, where to look)
- Groups related errors (e.g., all errors for same journal entry)

**Prerequisites:** Story 4.1 (input validation), Story 4.2 (transformation validation), Story 4.3 (output validation)

**Technical Notes:**
- Create `ErrorDetector` class that aggregates errors from all validation stages
- Error types:
  - DataError: Invalid input data (missing field, wrong type, invalid value)
  - RuleError: Rule syntax error, rule doesn't match, rule conflict
  - TransformationError: Transformation failed, data loss, incorrect mapping
  - OutputError: Output invalid, totals don't balance, missing data
- Severity levels:
  - Critical: Data corruption, transformation failure, cannot proceed
  - Error: Invalid data, rule failure, needs correction
  - Warning: Potential issue, should review
  - Info: Informational, no action needed
- Error context: entry_id, rule_id, field_name, actual_value, expected_value, error_message
- Error grouping: Group by entry_id, rule_id, or error_type for easier review

---

### Story 4.5: Detailed Error Messages

As an **accounting operator**,
I want **detailed error messages explaining what went wrong and why**,
So that **I can fix issues quickly without guessing**.

**Acceptance Criteria:**

**Given** an error detected during processing
**When** the system generates an error message
**Then** the error message includes:
- Clear description of what went wrong (in plain language, not technical jargon)
- Explanation of why it's an error (what rule or validation failed)
- Specific details (which field, what value, what was expected)
- Location information (which journal entry, row number, which rule)
- Actionable guidance (how to fix the issue, what to check)

**And** error messages:
- Are user-friendly (no stack traces, no technical exceptions)
- Are in the user's language (English or Chinese, as appropriate)
- Provide examples when helpful (show correct format)
- Reference documentation when applicable (link to rule guide, data format guide)

**Prerequisites:** Story 4.4 (error detection)

**Technical Notes:**
- Create `ErrorMessageGenerator` class
- Error message template:
  - Title: Short summary (e.g., "Invalid account code in rule")
  - Description: What went wrong (e.g., "Rule #42 references account code 'XYZ' which doesn't exist")
  - Details: Specific values (e.g., "Rule: old_type == 'OL' → account_code 'XYZ', Account hierarchy has: A, B, C...")
  - Location: Where the error occurred (e.g., "Journal entry #123, Rule #42, Mapping rules file row 45")
  - Fix: How to fix (e.g., "Update rule #42 to use valid account code from hierarchy: A, B, or C")
- Use error message templates for consistency
- Support multiple languages (English primary, Chinese if needed)
- Include examples in error messages when helpful

---

### Story 4.6: Auto-Fix Suggestions with Review Flags

As an **accounting operator**,
I want **auto-fix suggestions for common errors with review flags**,
So that **I can approve fixes quickly while maintaining control**.

**Acceptance Criteria:**

**Given** errors detected during processing
**When** the system can suggest auto-fixes
**Then** the system:
- Identifies fixable errors (common patterns: typos, case mismatches, missing defaults)
- Suggests automatic fixes with confidence scores
- Flags all auto-fixes for expert review (no automatic application without approval)
- Shows what will be changed (before/after comparison)
- Allows expert to approve or reject each fix

**And** auto-fix suggestions:
- Are conservative (only suggest fixes with high confidence)
- Are transparent (show exactly what will change)
- Are reviewable (expert must approve before application)
- Include confidence scores (high/medium/low confidence in fix)

**Prerequisites:** Story 4.5 (error messages)

**Technical Notes:**
- Create `AutoFixSuggester` class
- Auto-fix patterns:
  - Typo correction: "OL" vs "0L" (suggest correct based on known types)
  - Case mismatch: "ol" vs "OL" (suggest standard case)
  - Missing default: Null value → suggest default based on context
  - Account code typo: "A1" vs "A-1" (suggest closest match from hierarchy)
- Confidence scoring:
  - High: Exact match found, very confident (e.g., "OL" typo → "OL")
  - Medium: Close match, somewhat confident (e.g., "A1" → "A-1" if only one close match)
  - Low: Multiple possibilities, not confident (don't suggest, flag for manual review)
- Review workflow: Generate fix suggestions → Expert reviews → Approve/reject → Apply approved fixes
- Store fix history: Track what was auto-fixed, who approved, when

---

### Story 4.7: Validation Results & Confidence Indicators

As an **accounting operator**,
I want **to see validation results and confidence indicators**,
So that **I know how confident I can be in the automated results**.

**Acceptance Criteria:**

**Given** processing results (ledger entries, aggregations)
**When** the system shows validation results
**Then** the system displays:
- Overall validation status (pass/fail/warning)
- Summary statistics (entries processed, errors found, warnings)
- Confidence scores for transformations (high/medium/low based on rule match quality)
- Validation coverage (what was validated, what wasn't)
- Quick status indicators (green/yellow/red for visual scanning)

**And** confidence indicators:
- Are based on rule match quality (exact match = high, fuzzy match = medium, no match = low)
- Are based on data quality (clean data = high, questionable data = low)
- Are aggregated at entry level and overall level
- Help expert prioritize review (review low-confidence entries first)

**Prerequisites:** Story 4.3 (output validation), Story 4.4 (error detection)

**Technical Notes:**
- Create `ValidationResults` class
- Confidence scoring:
  - Rule match: Exact match = 1.0, partial match = 0.7, no match = 0.0
  - Data quality: Clean data = 1.0, warnings = 0.7, errors = 0.0
  - Overall: Weighted average of rule match and data quality
- Display format:
  - Summary: "691 entries processed, 5 errors, 12 warnings, 98% confidence"
  - Per-entry: Show confidence score for each entry
  - Visual: Color coding (green = high confidence, yellow = medium, red = low)
- Include in error report Excel file as separate sheet or column

---

## Epic 5: Transparency & Audit Trail

**Goal:** Implement complete audit trail tracking and transformation visibility so operators can review and verify all automated changes.

### Story 5.1: Transformation Audit Trail

As an **accounting operator**,
I want **a complete audit trail of all transformations**,
So that **I can trace any output back to its source and verify correctness**.

**Acceptance Criteria:**

**Given** journal entries being transformed to ledger entries
**When** the system processes entries
**Then** the system tracks:
- Source journal entry (entry ID, original data)
- Applied mapping rules (rule ID, rule condition, rule result)
- Generated ledger entries (entry ID, account code, amount, date)
- Transformation timestamp (when transformation occurred)
- Transformation metadata (who ran it, which version of rules, which version of system)

**And** the audit trail:
- Links journal entries to ledger entries (one-to-many relationship preserved)
- Links ledger entries to applied rules (which rule generated which entry)
- Preserves original data alongside transformed data
- Is stored in structured format (can be exported, queried, analyzed)

**Prerequisites:** Story 3.4 (journal to ledger transformation), Story 3.3 (rule application)

**Technical Notes:**
- Create `AuditTrail` class to track transformations
- Audit trail structure:
  - TransformationRecord: entry_id, timestamp, user, system_version, rule_version
  - SourceEntry: journal entry data (preserve original)
  - AppliedRules: list of rules applied with results
  - GeneratedEntries: list of ledger entries created
- Store audit trail in memory during processing, write to file/database at end
- Format: JSON, CSV, or structured Excel (for easy review)
- Include in output: Audit trail file alongside ledger output

---

### Story 5.2: Excel Error Report Generation

As an **accounting operator**,
I want **an Excel error report showing all changes and issues**,
So that **I can review transformations and errors in familiar Excel format**.

**Acceptance Criteria:**

**Given** processing results with errors and transformations
**When** the system generates the error report
**Then** the system creates an Excel file with:
- Error summary sheet (total errors, errors by type, severity breakdown)
- Detailed errors sheet (each error with full context: entry, rule, field, value, message)
- Transformation log sheet (all transformations: source → target, rules applied)
- Validation results sheet (validation status, confidence scores, coverage)
- Auto-fix suggestions sheet (suggested fixes with confidence, approval status)

**And** the Excel report:
- Uses clear formatting (colors for severity, bold headers, organized layout)
- Is easy to navigate (multiple sheets, clear sheet names)
- Includes filters and sorting (filter by error type, sort by severity)
- Preserves Chinese text correctly
- Can be opened in Excel without issues

**Prerequisites:** Story 4.4 (error detection), Story 5.1 (audit trail), Story 1.3 (Excel writing)

**Technical Notes:**
- Create `ErrorReportGenerator` class
- Excel structure:
  - Sheet 1: "Summary" - Overview statistics, status indicators
  - Sheet 2: "Errors" - Detailed error list with all context
  - Sheet 3: "Transformations" - Transformation log (source → target)
  - Sheet 4: "Validation" - Validation results and confidence scores
  - Sheet 5: "Auto-Fixes" - Suggested fixes with approval workflow
- Use openpyxl for formatting:
  - Colors: Red for errors, yellow for warnings, green for success
  - Bold headers, auto-width columns, filters enabled
  - Freeze top row for easy scrolling
- Include hyperlinks if helpful (link errors to source entries)

---

### Story 5.3: Transformation Visibility

As an **accounting operator**,
I want **all transformations to be visible and reviewable**,
So that **I can see exactly what the system did and verify it's correct**.

**Acceptance Criteria:**

**Given** processed journal entries and generated ledger entries
**When** I review the transformations
**Then** I can see:
- Original journal entry data (preserved exactly as input)
- Which rules were applied (rule ID, condition, result)
- Generated ledger entries (what was created, account codes, amounts)
- Transformation path (journal entry → rule → ledger entry, with all steps visible)
- Comparison view (before/after, original vs transformed)

**And** visibility includes:
- Entry-by-entry view (see transformation for each journal entry)
- Rule-by-rule view (see what each rule produced)
- Summary view (overall transformation statistics)
- Export capability (export transformation log to Excel/CSV for external review)

**Prerequisites:** Story 5.1 (audit trail), Story 5.2 (error report)

**Technical Notes:**
- Create `TransformationViewer` class
- Views:
  - Entry view: Show journal entry → applied rules → ledger entries
  - Rule view: Show rule → matching entries → generated ledger entries
  - Summary view: Statistics, charts, overview
- Display format:
  - Console output: Formatted text showing transformations
  - Excel output: Transformation log sheet in error report
  - JSON/CSV: Structured data for programmatic access
- Include in error report Excel: "Transformations" sheet with full details

---

### Story 5.4: Original Data Preservation

As an **accounting operator**,
I want **original data preserved alongside processed data**,
So that **I can compare and verify transformations are correct**.

**Acceptance Criteria:**

**Given** journal entries being processed
**When** the system transforms entries
**Then** the system:
- Preserves original journal entry data (never modifies input)
- Stores original data alongside transformed data (in audit trail)
- Provides comparison view (original vs transformed side-by-side)
- Allows export of original data (can export original journal entries separately)

**And** data preservation:
- Is complete (all original fields preserved, no data loss)
- Is accessible (can view original data in error report, audit trail)
- Is immutable (original data never changes, only transformed data changes)

**Prerequisites:** Story 2.1 (journal entry reader), Story 5.1 (audit trail)

**Technical Notes:**
- Never modify input data, always create new objects for transformed data
- Store original data in audit trail: `original_entry: JournalEntry, transformed_entry: LedgerEntry`
- Include original data in error report: "Original Data" sheet showing input journal entries
- Comparison view: Side-by-side columns showing original vs transformed
- Export: Allow exporting original journal entries to separate Excel file if needed

---

### Story 5.5: Audit Trail Export

As an **accounting operator**,
I want **to export audit trail data for external analysis**,
So that **I can analyze transformations and maintain compliance records**.

**Acceptance Criteria:**

**Given** a complete audit trail from processing
**When** I export the audit trail
**Then** the system:
- Exports audit trail to Excel format (structured, easy to review)
- Exports audit trail to CSV format (for external tools, databases)
- Exports audit trail to JSON format (for programmatic access)
- Includes all audit trail data (transformations, rules, timestamps, metadata)
- Preserves data relationships (links between journal entries, rules, ledger entries)

**And** export formats:
- Are well-structured (clear columns, organized data)
- Are complete (no data loss in export)
- Are readable (formatted for human review in Excel)
- Are machine-readable (CSV/JSON for automation)

**Prerequisites:** Story 5.1 (audit trail), Story 1.3 (Excel writing)

**Technical Notes:**
- Create `AuditTrailExporter` class
- Export formats:
  - Excel: Multiple sheets (transformations, rules, entries, metadata)
  - CSV: Flat files with relationships preserved (entry_id, rule_id links)
  - JSON: Structured JSON with nested relationships
- Include metadata: system version, rule version, processing timestamp, user
- Preserve relationships: Use IDs to link journal entries → rules → ledger entries
- Make export part of standard output (always generate audit trail file)

---

## Epic 6: Output Generation & Reporting

**Goal:** Generate Excel output files with preserved formatting, comprehensive error reports, and quarterly aggregation reports that are ready for use.

### Story 6.1: Ledger Output Excel Generation

As an **accounting operator**,
I want **ledger output in Excel format with preserved formatting**,
So that **I can use the output directly in my accounting workflow**.

**Acceptance Criteria:**

**Given** transformed ledger entries
**When** the system generates ledger output
**Then** the system creates an Excel file with:
- Ledger entries organized by account hierarchy (4 levels)
- Proper Excel formatting (column widths, header styling, number formats)
- Chinese text displayed correctly
- Account hierarchy visible (indentation or grouping to show levels)
- Summary totals at each hierarchy level

**And** the Excel output:
- Preserves formatting from input (if applicable)
- Uses professional formatting (bold headers, proper alignment, number formats)
- Is easy to read and navigate (filters, sorting, clear structure)
- Can be opened in Excel without issues

**Prerequisites:** Story 3.4 (journal to ledger transformation), Story 1.3 (Excel writing)

**Technical Notes:**
- Create `LedgerOutputGenerator` class
- Excel structure:
  - Sheet 1: "Ledger Entries" - All ledger entries with account hierarchy
  - Sheet 2: "Summary" - Hierarchical totals (Level 1 → Level 4)
  - Formatting:
    - Bold headers, auto-width columns
    - Number formats for amounts (currency, decimals)
    - Indentation or grouping for hierarchy levels
    - Filters enabled for easy filtering
- Use openpyxl for full formatting control
- Organize by account hierarchy: Group entries by account code, show hierarchy levels

---

### Story 6.2: Quarterly Aggregation Report

As an **accounting operator**,
I want **quarterly aggregation reports in Excel format**,
So that **I get summary reports ready for financial reporting**.

**Acceptance Criteria:**

**Given** ledger entries for a quarter
**When** the system generates quarterly aggregation report
**Then** the system creates an Excel file with:
- Quarterly totals by account (sum of amounts for each account)
- Hierarchical organization (Level 1 → Level 4 totals)
- Quarter and year information (Q1 2024, Q2 2024, etc.)
- Summary statistics (total entries, total amount, account counts)
- Comparison view (if multiple quarters: compare Q1 vs Q2, etc.)

**And** the report:
- Uses clear formatting (professional, ready for presentation)
- Includes charts/graphs if helpful (visualization of totals)
- Is organized logically (by account hierarchy, by quarter)
- Can be used directly for financial reporting

**Prerequisites:** Story 3.5 (quarterly aggregation), Story 1.3 (Excel writing)

**Technical Notes:**
- Create `QuarterlyReportGenerator` class
- Excel structure:
  - Sheet 1: "Quarterly Totals" - Aggregated totals by account and quarter
  - Sheet 2: "Hierarchy Summary" - Totals at each hierarchy level
  - Sheet 3: "Statistics" - Summary statistics and metrics
- Formatting:
  - Professional formatting (ready for presentation)
  - Number formats (currency, percentages)
  - Charts if helpful (bar charts, pie charts for account distribution)
- Include comparison: If processing multiple quarters, show quarter-over-quarter comparison

---

### Story 6.3: Comprehensive Error Report Excel

As an **accounting operator**,
I want **a comprehensive error report in Excel format**,
So that **I can review all errors and transformations in one place**.

**Acceptance Criteria:**

**Given** processing results with errors, warnings, and transformations
**When** the system generates the error report
**Then** the system creates an Excel file (from Story 5.2) with all sheets:
- Error summary (overview, statistics)
- Detailed errors (all errors with full context)
- Transformation log (all transformations visible)
- Validation results (validation status, confidence scores)
- Auto-fix suggestions (suggested fixes with approval workflow)
- Original data (preserved input data for comparison)

**And** the error report:
- Is comprehensive (includes all information needed for review)
- Is well-formatted (easy to read, navigate, filter)
- Preserves Chinese text correctly
- Can be used for expert review and approval

**Prerequisites:** Story 5.2 (error report generation), Story 6.1 (Excel writing capabilities)

**Technical Notes:**
- Reuse `ErrorReportGenerator` from Story 5.2
- Ensure all sheets are included and well-formatted
- Make error report a standard output (always generated, even if no errors)
- Include "No Errors" message if processing was successful
- Format for easy review: Colors, filters, clear organization

---

### Story 6.4: Excel Formatting Preservation

As an **accounting operator**,
I want **Excel formatting preserved in output files**,
So that **output files look professional and match my organization's standards**.

**Acceptance Criteria:**

**Given** output Excel files (ledger, reports, error reports)
**When** the system writes files
**Then** the system preserves and applies:
- Column widths (auto-adjusted or specified widths)
- Cell formatting (number formats, date formats, text alignment)
- Header styling (bold, colors, borders)
- Row styling (alternating colors, borders if helpful)
- Chinese text formatting (proper fonts, encoding)

**And** formatting:
- Is consistent across all output files
- Is professional (ready for presentation, not raw data)
- Matches input formatting (if reading from formatted input files)
- Can be customized (formatting templates or configuration)

**Prerequisites:** Story 1.3 (Excel writing), Story 6.1 (ledger output), Story 6.2 (quarterly report)

**Technical Notes:**
- Use openpyxl for full formatting control (not just pandas to_excel)
- Formatting elements:
  - Column widths: Auto-adjust or set specific widths
  - Number formats: Currency, percentages, decimals
  - Date formats: Standard date formats
  - Cell styles: Bold, italic, colors, borders, alignment
  - Header row: Bold, background color, borders
- Create formatting templates or configuration for consistent styling
- Test with actual Excel files to ensure formatting looks correct

---

## Epic 7: User Interface & Experience

**Goal:** Provide a user-friendly CLI interface, configuration management, and clear error messaging that makes the system easy to use for non-expert operators.

### Story 7.1: Python CLI Entrypoint

As an **accounting operator**,
I want **a simple command-line interface to run the automation**,
So that **I can process my quarterly accounting with a single command**.

**Acceptance Criteria:**

**Given** the accounting automation system installed
**When** I run the CLI command
**Then** the system:
- Provides a command-line entrypoint (e.g., `veritas-accounting` or `python -m veritas_accounting`)
- Accepts required arguments: journal entry Excel file path
- Accepts optional arguments: mapping rules file path, output directory, configuration file
- Provides helpful usage information (`--help` flag)
- Shows clear error messages if arguments are invalid

**And** the CLI:
- Is easy to use (simple command, clear arguments)
- Provides helpful error messages (what's wrong, how to fix)
- Shows progress during processing (status messages, progress bar if long-running)
- Exits with appropriate status codes (0 for success, non-zero for errors)

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Create CLI using `argparse` or `click` library
- Command structure: `veritas-accounting process --input journal.xlsx --rules rules.xlsx --output ./output`
- Arguments:
  - Required: `--input` (journal entries file)
  - Optional: `--rules` (mapping rules file, default path), `--output` (output directory, default: current directory), `--config` (config file)
- Help text: Clear descriptions, examples, required vs optional
- Progress: Show status messages during processing (reading files, applying rules, generating output)
- Error handling: Catch exceptions, show user-friendly messages, exit with status codes

---

### Story 7.2: Configuration Management

As an **accounting operator**,
I want **to configure the system via Excel files, YAML/JSON config, or command-line arguments**,
So that **I can customize behavior without code changes**.

**Acceptance Criteria:**

**Given** configuration needs (rule file paths, output paths, validation settings)
**When** I configure the system
**Then** the system supports:
- Excel-based rule files (mapping rules in Excel, account hierarchy in Excel)
- Configuration files (YAML or JSON with settings: paths, validation options, output options)
- Command-line arguments (override config file settings)
- Environment variables (for sensitive settings if needed)
- Configuration merging (CLI args override config file, config file overrides defaults)

**And** configuration:
- Has sensible defaults (works out-of-the-box with minimal configuration)
- Is validated (check config file format, check file paths exist)
- Provides clear error messages if configuration is invalid
- Is documented (what options are available, what they do)

**Prerequisites:** Story 7.1 (CLI entrypoint)

**Technical Notes:**
- Create `Config` class using Pydantic for validation
- Configuration sources (priority order):
  1. Command-line arguments (highest priority)
  2. Configuration file (YAML/JSON)
  3. Environment variables
  4. Default values (lowest priority)
- Configuration options:
  - Input: journal_file_path, rules_file_path, account_hierarchy_path
  - Output: output_directory, output_file_names
  - Validation: validation_level (strict/lenient), auto_fix_enabled
  - Processing: parallel_processing (future), chunk_size
- Config file format: YAML or JSON, example:
  ```yaml
  input:
    journal_file: "journal.xlsx"
    rules_file: "rules.xlsx"
  output:
    directory: "./output"
  validation:
    level: "strict"
  ```
- Validate config: Check file paths exist, check format is valid

---

### Story 7.3: Clear Error Messages & User Guidance

As an **accounting operator**,
I want **clear, actionable error messages and user guidance**,
So that **I can fix issues quickly without technical expertise**.

**Acceptance Criteria:**

**Given** errors or issues during processing
**When** the system encounters problems
**Then** the system provides:
- User-friendly error messages (plain language, not technical jargon)
- Actionable guidance (what to do to fix the issue)
- Context information (which file, which entry, what value)
- Examples when helpful (show correct format, show expected structure)
- Links to documentation (reference guides, troubleshooting)

**And** error messages:
- Are consistent (same format, same style)
- Are helpful (not just "error occurred", but "error X in file Y, field Z, fix by doing W")
- Support multiple languages (English primary, Chinese if needed)
- Are logged appropriately (console for user, file for debugging)

**Prerequisites:** Story 4.5 (detailed error messages), Story 7.1 (CLI)

**Technical Notes:**
- Reuse `ErrorMessageGenerator` from Story 4.5
- Enhance for CLI context:
  - Console output: Formatted, colored if terminal supports it
  - File output: Detailed logs for debugging
  - User messages: Simplified, actionable
- Error message format:
  - Title: Short summary
  - Description: What went wrong
  - Location: Where (file, entry, field)
  - Fix: How to fix
  - Example: Show correct format if helpful
- Use color coding in console: Red for errors, yellow for warnings, green for success
- Include help text: `--help` flag shows usage, common errors, troubleshooting tips

---

### Story 7.4: Simple Process Flow

As an **accounting operator**,
I want **a simple process flow: input → process → review → output**,
So that **I can use the system without complex training**.

**Acceptance Criteria:**

**Given** the accounting automation system
**When** I use the system
**Then** the workflow is:
1. **Input:** Provide journal entries Excel file (and rules file if not using default)
2. **Process:** Run CLI command, system processes automatically
3. **Review:** Review error report Excel file (check errors, approve auto-fixes)
4. **Output:** Use ledger output and quarterly reports

**And** the process:
- Is linear and clear (no branching, no complex decisions)
- Has clear steps (each step is obvious, no ambiguity)
- Provides status feedback (know what's happening at each step)
- Has clear outputs (know what files are generated, where they are)

**Prerequisites:** Story 7.1 (CLI), Story 6.3 (error report), Story 6.1 (ledger output)

**Technical Notes:**
- Design workflow to be simple and linear
- Process flow:
  1. User provides input files
  2. User runs CLI command: `veritas-accounting process --input journal.xlsx`
  3. System processes (shows progress)
  4. System generates outputs (ledger.xlsx, error_report.xlsx, quarterly_report.xlsx)
  5. User reviews error report
  6. User uses outputs
- Status messages during processing:
  - "Reading journal entries..."
  - "Validating input data..."
  - "Applying mapping rules..."
  - "Generating ledger entries..."
  - "Validating output..."
  - "Generating reports..."
  - "Complete! Output files in ./output/"
- Make it obvious what to do next at each step

---

### Story 7.5: Non-Expert Usability

As a **future accounting operator (non-expert)**,
I want **the system to be operable after brief training (< 2 hours)**,
So that **I can take over accounting responsibilities without deep expertise**.

**Acceptance Criteria:**

**Given** a new operator with basic Excel knowledge
**When** they learn to use the system
**Then** they can:
- Understand the process flow (input → process → review → output)
- Run the CLI command correctly
- Interpret error reports and fix common issues
- Use the output files in their workflow
- Get help when needed (documentation, error messages guide them)

**And** usability includes:
- Clear documentation (getting started guide, user manual)
- Helpful error messages (guide them to solutions)
- Example files (see what input should look like)
- Troubleshooting guide (common issues and fixes)

**Prerequisites:** Story 7.4 (simple process flow), Story 8.1 (documentation)

**Technical Notes:**
- Focus on user experience for non-experts
- Documentation:
  - Getting started guide: Step-by-step, screenshots if helpful
  - User manual: Complete reference
  - Example files: Sample journal entries, sample rules
  - Troubleshooting: Common errors and fixes
- Error messages: Guide users to solutions, not just report problems
- Example: If error "Missing column 'year'", show example of correct format
- Make system forgiving: Provide defaults, suggest fixes, guide users

---

## Epic 8: Documentation & Examples

**Goal:** Provide complete documentation and example files that enable users to learn, use, and maintain the system effectively.

### Story 8.1: Usage Documentation

As an **accounting operator**,
I want **complete usage documentation**,
So that **I can learn how to use the system effectively**.

**Acceptance Criteria:**

**Given** the accounting automation system
**When** I need to learn how to use it
**Then** documentation includes:
- Getting started guide (installation, first run, basic usage)
- User manual (complete reference for all features)
- Configuration guide (how to configure, what options are available)
- Error handling guide (how to interpret errors, how to fix common issues)
- Troubleshooting guide (common problems and solutions)

**And** documentation:
- Is clear and well-organized (easy to find what you need)
- Includes examples (show actual commands, show example files)
- Is up-to-date (matches current system version)
- Is accessible (in docs/ folder, readable format)

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:**
- Create documentation in `docs/` folder
- Documentation files:
  - `README.md`: Project overview, quick start
  - `docs/getting-started.md`: Installation, first run, basic workflow
  - `docs/user-manual.md`: Complete reference, all features
  - `docs/configuration.md`: Configuration options, config file format
  - `docs/error-handling.md`: Error types, how to fix, troubleshooting
  - `docs/troubleshooting.md`: Common issues and solutions
- Use Markdown format, include code examples, include screenshots if helpful
- Keep documentation in sync with code (update when features change)

---

### Story 8.2: Rule Management Guide

As an **accounting operator**,
I want **documentation on how to edit and manage the 194 mapping rules**,
So that **I can update rules in Excel without code changes**.

**Acceptance Criteria:**

**Given** the need to update mapping rules
**When** I want to edit rules
**Then** documentation explains:
- Rule file format (Excel structure, required columns, data types)
- Rule syntax (how to write conditions, what operators are supported)
- Rule examples (show example rules, explain how they work)
- Rule validation (what makes a rule valid, common rule errors)
- Rule testing (how to test rules before using in production)

**And** the guide:
- Is practical (shows actual Excel examples)
- Is comprehensive (covers all rule features)
- Includes troubleshooting (common rule errors and fixes)
- Is accessible (in docs/ folder, easy to find)

**Prerequisites:** Story 2.3 (mapping rules reader), Story 8.1 (documentation)

**Technical Notes:**
- Create `docs/rule-management.md`
- Include:
  - Rule file structure: Excel columns, data types, required fields
  - Rule syntax: Condition expressions, operators, examples
  - Rule examples: Real examples from the 194 rules (anonymized if needed)
  - Rule validation: What's checked, error messages
  - Rule testing: How to test rules, validation workflow
- Include screenshots or examples of Excel rule file
- Show before/after examples of rule updates

---

### Story 8.3: Example Excel Files

As an **accounting operator**,
I want **example Excel files showing correct formats**,
So that **I know what my input files should look like**.

**Acceptance Criteria:**

**Given** the need to prepare input files
**When** I create journal entries or mapping rules files
**Then** example files show:
- Journal entry format (required columns, data types, example data)
- Mapping rule format (rule structure, condition syntax, example rules)
- Account hierarchy format (if hierarchy is in Excel, show structure)
- Expected output format (what ledger output looks like, what reports look like)

**And** example files:
- Are realistic (use realistic data, not just placeholders)
- Are complete (show all required fields, show optional fields)
- Include comments/notes (explain what each field is for)
- Are in `examples/` folder (easy to find and copy)

**Prerequisites:** Story 2.1 (journal entry reader), Story 2.3 (mapping rules reader), Story 6.1 (ledger output)

**Technical Notes:**
- Create `examples/` folder in project
- Example files:
  - `examples/journal_entries_sample.xlsx`: Sample journal entries with all required columns
  - `examples/mapping_rules_sample.xlsx`: Sample mapping rules with examples
  - `examples/account_hierarchy_sample.xlsx`: Sample account hierarchy (if in Excel)
  - `examples/ledger_output_sample.xlsx`: Example ledger output (what output looks like)
- Include comments in Excel files: Use Excel comments to explain fields
- Include README in examples folder: Explain what each file is for
- Use realistic but anonymized data (don't use real financial data)

---

## Epic 9: Rule Management & Versioning

**Goal:** Implement advanced rule management features including versioning and change tracking to support rule evolution over time.

### Story 9.1: Rule Versioning

As an **accounting operator**,
I want **rule versioning to track rule changes over time**,
So that **I can see rule history and revert to previous versions if needed**.

**Acceptance Criteria:**

**Given** mapping rules that may change over time
**When** I update rules
**Then** the system:
- Tracks rule versions (version number, timestamp, who changed, what changed)
- Stores rule history (can see all previous versions)
- Allows version comparison (see what changed between versions)
- Supports version rollback (revert to previous version if needed)
- Links processing runs to rule versions (audit trail shows which rule version was used)

**And** versioning:
- Is automatic (system tracks versions when rules are loaded)
- Is transparent (version info visible in audit trail, error reports)
- Is accessible (can view version history, can export version data)

**Prerequisites:** Story 2.3 (mapping rules reader), Story 5.1 (audit trail)

**Technical Notes:**
- Create `RuleVersionManager` class
- Version tracking:
  - Generate version ID: Hash of rule file content or timestamp-based version
  - Store version metadata: version_id, timestamp, file_hash, rule_count
  - Store version history: Keep previous versions (in memory during run, or in file/database)
- Version comparison: Compare rule files to detect changes (which rules added/removed/modified)
- Version in audit trail: Include rule_version in transformation records
- Storage: Store versions in JSON file or simple database (SQLite)
- Version format: Semantic versioning (1.0.0, 1.1.0) or timestamp-based (2025-01-27-v1)

---

## FR Coverage Matrix

**Epic 1 (Foundation):**
- FR-INST1, FR-INST2, FR-INST3 → Story 1.1
- FR-EXCEL1 (basic) → Story 1.2, Story 1.3
- FR-DOC1 (foundation) → Story 8.1

**Epic 2 (Input Processing):**
- FR1, FR-EXCEL1 → Story 2.1
- FR2, FR12 → Story 2.2
- FR3, FR-EXCEL2 → Story 2.3
- FR4 → Story 2.4
- FR5, FR-EXCEL5 → Story 2.5

**Epic 3 (Rule Engine):**
- FR6, FR7, FR8 → Story 3.2, Story 3.3
- FR9 → Story 3.1, Story 3.4
- FR10 → Story 3.5
- FR13 → Story 3.3, Story 4.2
- FR27, FR28 → Story 2.3, Story 2.4, Story 3.2

**Epic 4 (Validation):**
- FR14 → Story 4.3
- FR15 → Story 4.4
- FR16 → Story 4.5
- FR17 → Story 4.6
- FR21 → Story 4.7

**Epic 5 (Audit Trail):**
- FR18 → Story 5.1
- FR19 → Story 5.2
- FR20 → Story 5.3
- FR22 → Story 5.4
- FR26 → Story 5.5

**Epic 6 (Output):**
- FR11, FR-EXCEL3 → Story 6.1, Story 6.4
- FR23 → Story 6.1
- FR24 → Story 6.2
- FR25, FR-EXCEL4 → Story 6.3

**Epic 7 (User Interface):**
- FR30 → Story 7.3
- FR31, FR32 → Story 7.4
- FR33 → Story 7.5
- FR-API1 → Story 7.1
- FR-API2 → Story 7.2
- FR-API3 → Story 7.3

**Epic 8 (Documentation):**
- FR-DOC1 → Story 8.1, Story 8.2
- FR-DOC2 → Story 8.3

**Epic 9 (Rule Versioning):**
- FR29 → Story 9.1

**All 46 functional requirements are covered by at least one story.**

---

## Summary

This epic breakdown decomposes the 46 functional requirements from the PRD into 9 epics and 35+ stories. Each story is sized for single-session completion by a development agent and includes detailed BDD-style acceptance criteria.

**Epic Sequencing:**
1. **Epic 1 (Foundation)** - Must be completed first (infrastructure)
2. **Epic 2 (Input Processing)** - Can start after Epic 1 (depends on Excel I/O)
3. **Epic 3 (Rule Engine)** - Depends on Epic 2 (needs validated input)
4. **Epic 4 (Validation)** - Depends on Epic 3 (validates transformations)
5. **Epic 5 (Audit Trail)** - Depends on Epic 3 (tracks transformations)
6. **Epic 6 (Output)** - Depends on Epic 3, Epic 4, Epic 5 (generates final outputs)
7. **Epic 7 (User Interface)** - Can be developed in parallel with Epics 2-6 (CLI interface)
8. **Epic 8 (Documentation)** - Can be developed throughout (living documentation)
9. **Epic 9 (Rule Versioning)** - Depends on Epic 2, Epic 5 (advanced feature)

**Key Features:**
- Complete FR coverage (all 46 requirements mapped to stories)
- Detailed acceptance criteria (BDD-style, testable)
- Clear prerequisites (no forward dependencies)
- Technical implementation guidance (libraries, patterns, approaches)
- User-focused stories (accounting operator perspective)

**Next Steps:**
1. **UX Design** - Not applicable (Excel-native, no custom UI)
2. **Architecture** - Run `workflow create-architecture` to add technical design details
3. **Implementation** - Stories ready for development after architecture is complete

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

_This document will be updated after Architecture workflow to incorporate technical decisions and implementation details._








