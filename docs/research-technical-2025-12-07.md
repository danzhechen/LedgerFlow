# Technical Research Report: Accounting Automation System

**Project:** veritas-accounting  
**Research Type:** Technical/Architecture Research  
**Date:** 2025-12-07  
**Researcher:** Analyst Agent  
**Research Focus:** Excel processing, rule engines, data validation, accounting automation

---

## Executive Summary

This technical research evaluates technologies and approaches for building an accounting automation system that processes 691+ journal entries through 194 mapping rules to generate quarterly ledger reports. The system prioritizes **correctness**, **maximum automation**, and **Excel as the main tool**.

**Key Findings:**
- **Excel Processing:** Combined pandas + openpyxl approach optimal (pandas for data, openpyxl for formatting)
- **Rule Engine:** Lightweight rule engine libraries (rule-engine, simpleruleengine) suitable for 194 mapping rules
- **Data Validation:** Pydantic + Pandantic for type-safe validation with pandas DataFrames
- **Architecture:** Python-based pipeline with Excel-native interfaces

**Top Recommendation:** Python + pandas + openpyxl + Pydantic + rule-engine library

---

## 1. Technical Requirements and Constraints

### Functional Requirements
- Process 691+ journal entries efficiently
- Apply 194 mapping rules with conditional logic (one-to-many mappings)
- Transform journal → ledger with hierarchical structure (4 levels, 25 accounts)
- Generate quarterly aggregations
- Preserve Excel formatting and structure
- Handle Chinese text encoding

### Non-Functional Requirements
- **Performance:** Process 691 entries in < 5 minutes
- **Correctness:** 100% accuracy in transformations (critical for accounting)
- **Maintainability:** Easy to update 194 mapping rules
- **Usability:** Excel-native workflow (no learning curve)
- **Reliability:** Robust error handling and validation

### Constraints
- **Technology:** Python (already selected)
- **Interface:** Excel files (input and output)
- **Team Skills:** Intermediate Python level
- **Timeline:** 6-7 weeks for MVP
- **Budget:** Open source preferred

---

## 2. Technology Options Evaluated

### 2.1 Excel Processing Libraries

#### Option A: pandas (Primary Data Processing)
**Overview:** Powerful data manipulation library optimized for large datasets

**Current Status (2025):**
- Mature and widely adopted
- Excellent for data analysis and transformation
- Efficient DataFrame operations

**Technical Characteristics:**
- **Architecture:** Columnar data structures (DataFrames)
- **Performance:** Optimized for large datasets, vectorized operations
- **Scalability:** Handles large files efficiently with chunking
- **Integration:** Works with openpyxl as engine

**Developer Experience:**
- **Learning Curve:** Moderate (familiar to data scientists)
- **Documentation:** Excellent, extensive examples
- **Tooling:** Rich ecosystem, Jupyter integration
- **Testing:** Well-supported testing patterns

**Operations:**
- **Deployment:** Pure Python, no external dependencies
- **Monitoring:** Standard Python logging
- **Performance:** Can process 691 entries in seconds

**Ecosystem:**
- Extensive library ecosystem
- Strong community support
- Commercial support available

**Limitations:**
- Limited Excel formatting control
- Requires openpyxl for .xlsx files
- Less intuitive for Excel-specific features

**Sources:**
- [plus2net.com - pandas vs openpyxl comparison](https://www.plus2net.com/python/openpyxl-pandas.php)
- [hassanagmir.com - Excel automation best practices](https://hassanagmir.com/blogs/excel-with-python-mastering-automation-2-1)

**Verdict:** ✅ **RECOMMENDED** for data processing and transformation

---

#### Option B: openpyxl (Excel Formatting and Structure)
**Overview:** Comprehensive Excel file manipulation library with full formatting support

**Current Status (2025):**
- Actively maintained
- Full support for Excel 2010+ formats (.xlsx, .xlsm, .xltx, .xltm)
- Extensive formatting capabilities

**Technical Characteristics:**
- **Architecture:** Cell-level operations, workbook/worksheet model
- **Performance:** Slower for large datasets (cell-by-cell processing)
- **Scalability:** Use `read_only=True` mode for large files
- **Integration:** Works as pandas engine

**Developer Experience:**
- **Learning Curve:** Moderate (Excel object model familiarity helps)
- **Documentation:** Good, comprehensive API reference
- **Tooling:** Standard Python tooling
- **Testing:** Straightforward testing

**Operations:**
- **Deployment:** Pure Python, no Excel installation required
- **Monitoring:** Standard Python logging
- **Performance:** Optimized with read_only mode for large files

**Ecosystem:**
- Good community support
- Regular updates
- Compatible with pandas

**Strengths:**
- ✅ Full Excel formatting control
- ✅ Preserves Excel structure perfectly
- ✅ Handles charts, macros, styles
- ✅ Chinese text encoding support

**Limitations:**
- Slower for pure data processing (use pandas for that)
- More verbose for simple data operations

**Sources:**
- [plus2net.com - openpyxl capabilities](https://www.plus2net.com/python/openpyxl-pandas.php)
- [hakibenita.com - Fast Excel processing](https://hakibenita.com/fast-excel-python)

**Verdict:** ✅ **RECOMMENDED** for Excel formatting and structure preservation

---

#### Option C: xlwings (Excel Application Integration)
**Overview:** Bridge between Python and Excel application, enables VBA-like automation

**Current Status (2025):**
- Active development
- Requires Excel installation
- Real-time Excel interaction

**Technical Characteristics:**
- **Architecture:** COM automation, Excel object model
- **Performance:** Dependent on Excel application responsiveness
- **Scalability:** Not optimal for large batch processing
- **Integration:** Direct Excel application control

**Limitations:**
- ❌ Requires Excel installation (not suitable for server environments)
- ❌ Performance overhead from Excel application
- ❌ Not ideal for automated batch processing
- ❌ Platform-dependent (Windows/Mac specific)

**Verdict:** ❌ **NOT RECOMMENDED** - Overkill for this use case, adds complexity

---

### 2.2 Rule Engine Libraries

#### Option A: rule-engine
**Overview:** Lightweight, optionally typed expression language for matching Python objects

**Current Status (2025):**
- Version 2.4.1 (as of research)
- Active maintenance
- Pure Python implementation

**Technical Characteristics:**
- **Architecture:** Expression-based rule evaluation
- **Performance:** Fast evaluation, compiled expressions
- **Features:** Type hinting, regex support, datetime handling
- **Syntax:** Custom grammar, readable rules

**Developer Experience:**
- **Learning Curve:** Low to moderate
- **Documentation:** Good examples
- **Rule Definition:** Declarative, readable syntax

**Use Case Fit:**
- ✅ Well-suited for 194 mapping rules
- ✅ Supports conditional logic
- ✅ Can handle one-to-many mappings
- ✅ Easy to load from Excel/config

**Example Rule:**
```python
rule = Rule('old_type == "OL" and year == 2022') -> 'T-收入OL'
```

**Sources:**
- [pypi.org - rule-engine library](https://pypi.org/project/rule-engine/2.4.1/)

**Verdict:** ✅ **RECOMMENDED** - Good fit for mapping rule engine

---

#### Option B: simpleruleengine
**Overview:** Framework for declaratively specifying rules with chaining support

**Current Status (2025):**
- Version 2.0.0
- Active development
- Rule chaining capabilities

**Technical Characteristics:**
- **Architecture:** Decision/score-based rules
- **Performance:** Efficient rule evaluation
- **Features:** Rule chaining, dynamic decision-making
- **Syntax:** Declarative rule specification

**Use Case Fit:**
- ✅ Supports complex rule logic
- ✅ Rule chaining for conditional mappings
- ✅ Good for one-to-many scenarios

**Verdict:** ✅ **ALTERNATIVE** - Also suitable, slightly more complex

---

#### Option C: light-rule-engine
**Overview:** Simple, pure Python library inspired by Django's Q object

**Current Status (2025):**
- Version 1.1.1
- Lightweight implementation
- Nested rule support

**Technical Characteristics:**
- **Architecture:** Nested logical conditions
- **Performance:** Simple and fast
- **Features:** Complex logical conditions, dictionary evaluation

**Use Case Fit:**
- ✅ Simple and lightweight
- ✅ Good for basic conditional logic
- ⚠️ May be limited for complex 194-rule scenarios

**Verdict:** ⚠️ **CONSIDER** - Simpler but may lack features for complex mappings

---

### 2.3 Data Validation Frameworks

#### Option A: Pydantic + Pandantic
**Overview:** Type-safe data validation using Python type hints, extended for pandas

**Current Status (2025):**
- Pydantic v2 (latest)
- Pandantic for DataFrame validation
- Industry standard for data validation

**Technical Characteristics:**
- **Architecture:** Schema-based validation
- **Performance:** Fast validation, compiled validators
- **Features:** Type hints, automatic validation, detailed error messages
- **Integration:** Works seamlessly with pandas DataFrames

**Developer Experience:**
- **Learning Curve:** Low (uses standard Python type hints)
- **Documentation:** Excellent, comprehensive
- **Error Messages:** Detailed, actionable validation errors

**Use Case Fit:**
- ✅ Perfect for journal entry validation
- ✅ Type-safe data models
- ✅ Detailed validation error reporting
- ✅ Integrates with pandas DataFrames

**Example:**
```python
class JournalEntry(BaseModel):
    year: int
    description: str
    old_type: str
    new_type: Optional[str] = None
```

**Sources:**
- [docs.pydantic.dev - Pydantic validation](https://docs.pydantic.dev/latest/errors/errors/)
- [pandantic-rtd.readthedocs.io - Pandantic for DataFrames](https://pandantic-rtd.readthedocs.io/)

**Verdict:** ✅ **HIGHLY RECOMMENDED** - Best fit for validation requirements

---

#### Option B: PyDataValidator
**Overview:** Flexible library for data validation processes

**Current Status (2025):**
- Active development
- Comprehensive validation tools

**Technical Characteristics:**
- **Architecture:** Flexible validation framework
- **Features:** Data cleaning, consistency checks

**Verdict:** ⚠️ **ALTERNATIVE** - Less mature than Pydantic, fewer features

---

## 3. Comparative Analysis

### Excel Processing Comparison

| Dimension | pandas | openpyxl | xlwings |
|-----------|--------|----------|---------|
| **Data Processing** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Excel Formatting** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance (Large Files)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Excel-Native** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Dependencies** | Low | Low | High (Excel required) |
| **Best For** | Data analysis | Formatting | Excel integration |

**Recommendation:** Use **pandas + openpyxl** combination
- pandas for data processing and transformation
- openpyxl for reading/writing with formatting preservation

### Rule Engine Comparison

| Dimension | rule-engine | simpleruleengine | light-rule-engine |
|-----------|-------------|------------------|-------------------|
| **Complexity Support** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Conditional Logic** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **194 Rules Support** | ✅ Yes | ✅ Yes | ⚠️ Limited |

**Recommendation:** **rule-engine** for balance of features and simplicity

### Data Validation Comparison

| Dimension | Pydantic + Pandantic | PyDataValidator |
|-----------|---------------------|-----------------|
| **Type Safety** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Pandas Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Error Messages** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Maturity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Community** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Recommendation:** **Pydantic + Pandantic** - Industry standard, excellent pandas integration

---

## 4. Recommended Technology Stack

### Primary Stack

1. **Python 3.8+** - Base language
2. **pandas** - Data processing and transformation
3. **openpyxl** - Excel file I/O with formatting
4. **Pydantic** - Data validation and type safety
5. **Pandantic** - DataFrame validation
6. **rule-engine** - Mapping rule evaluation

### Supporting Libraries

- **logging** - Error tracking and audit trails
- **pathlib** - File path handling
- **typing** - Type hints for code clarity
- **dataclasses** - Data models (alternative to Pydantic for simple cases)

### Architecture Pattern

**Hybrid Approach:**
- Use pandas for data manipulation (fast, efficient)
- Use openpyxl for Excel I/O (formatting preservation)
- Combine both: pandas processes data → openpyxl writes formatted output

**Performance Optimization:**
- pandas: Use chunking for very large files (not needed for 691 entries)
- openpyxl: Use `read_only=True` for reading large files
- Rule engine: Compile rules once, reuse for all entries

---

## 5. Implementation Recommendations

### Phase 1: Foundation
- Set up Python project with pandas + openpyxl
- Create data models with Pydantic
- Implement Excel file reader (pandas with openpyxl engine)

### Phase 2: Rule Engine
- Load 194 rules from Excel into rule-engine format
- Implement rule evaluation logic
- Handle one-to-many mappings

### Phase 3: Validation
- Implement Pydantic models for Journal, Ledger, Rules
- Use Pandantic for DataFrame validation
- Create comprehensive validation pipeline

### Phase 4: Transformation
- Build pandas-based transformation pipeline
- Apply rules using rule-engine
- Generate quarterly aggregations

### Phase 5: Output
- Use openpyxl to write formatted Excel output
- Preserve Excel structure and formatting
- Generate error report Excel file

---

## 6. Risk Mitigation

### Identified Risks

1. **Excel Format Complexity**
   - **Risk:** Complex Excel structure may not be fully preserved
   - **Mitigation:** Use openpyxl for all Excel I/O, test with actual file early
   - **Contingency:** Manual format template if needed

2. **194 Rules Complexity**
   - **Risk:** Rule engine may not handle all conditional logic
   - **Mitigation:** Start with simple rules, test incrementally
   - **Contingency:** Hybrid approach (rule-engine + custom Python logic)

3. **Performance with 691 Entries**
   - **Risk:** Processing may be slower than expected
   - **Mitigation:** Optimize with pandas vectorization, profile early
   - **Contingency:** Add parallel processing if needed (deferred per plan)

4. **Chinese Text Encoding**
   - **Risk:** Encoding issues with Chinese characters
   - **Mitigation:** Use UTF-8 encoding, test with actual data
   - **Contingency:** Explicit encoding handling in openpyxl

---

## 7. Next Steps

1. **Proof of Concept (Week 1)**
   - Set up environment with recommended stack
   - Test Excel file reading with actual `账目分类明细.xlsx`
   - Validate Chinese text handling

2. **Rule Engine Prototype (Week 2)**
   - Load sample rules into rule-engine
   - Test rule evaluation on sample entries
   - Validate one-to-many mapping logic

3. **Validation Framework (Week 2-3)**
   - Implement Pydantic models
   - Test validation on sample data
   - Create error reporting structure

---

## 8. References and Sources

### Excel Processing
- [plus2net.com - pandas vs openpyxl comparison](https://www.plus2net.com/python/openpyxl-pandas.php)
- [hassanagmir.com - Excel automation best practices](https://hassanagmir.com/blogs/excel-with-python-mastering-automation-2-1)
- [hakibenita.com - Fast Excel processing techniques](https://hakibenita.com/fast-excel-python)

### Rule Engines
- [pypi.org - rule-engine library](https://pypi.org/project/rule-engine/2.4.1/)
- [pypi.org - simpleruleengine](https://pypi.org/project/simpleruleengine/2.0.0/)
- [pypi.org - light-rule-engine](https://pypi.org/project/light-rule-engine/1.1.1/)

### Data Validation
- [docs.pydantic.dev - Pydantic validation](https://docs.pydantic.dev/latest/errors/errors/)
- [pandantic-rtd.readthedocs.io - Pandantic for DataFrames](https://pandantic-rtd.readthedocs.io/)
- [pypi.org - PyDataValidator](https://pypi.org/project/py-data-validator/)

### Accounting Automation
- [udemy.com - Python automation for Excel and accounting](https://www.udemy.com/course/advanced-python-automation-for-excel-and-accounting/)
- [elba-tech.com - Automating Excel with Python](https://www.elba-tech.com/automating-excel-with-python/)

---

## 9. Architecture Decision Record (ADR)

### ADR-001: Excel Processing Library Selection

**Status:** Accepted

**Context:**
Need to process Excel files (read journal entries, mapping rules, ledger structure) and generate formatted Excel output while preserving structure and formatting.

**Decision Drivers:**
- Excel-native workflow requirement
- Format preservation critical
- Performance with 691 entries
- Chinese text encoding support
- Ease of maintenance

**Considered Options:**
1. pandas only
2. openpyxl only
3. pandas + openpyxl (hybrid)
4. xlwings

**Decision:**
Use **pandas + openpyxl hybrid approach**
- pandas for data processing and transformation
- openpyxl for Excel I/O with formatting preservation

**Consequences:**

**Positive:**
- Best of both worlds (performance + formatting)
- Industry-standard approach
- Excellent documentation and community support
- No external dependencies (Excel installation not required)

**Negative:**
- Need to understand both libraries
- Slightly more complex than single-library approach
- Requires careful coordination between libraries

**Neutral:**
- Learning curve for both libraries (moderate)

---

### ADR-002: Rule Engine Selection

**Status:** Accepted

**Context:**
Need to evaluate and apply 194 mapping rules with conditional logic (one-to-many mappings, many-to-one aggregations).

**Decision Drivers:**
- 194 rules complexity
- Conditional logic requirements
- Maintainability (rules in Excel/config)
- Performance with 691 entries

**Considered Options:**
1. rule-engine
2. simpleruleengine
3. light-rule-engine
4. Custom Python logic

**Decision:**
Use **rule-engine library** for primary rule evaluation, with custom Python logic for complex cases.

**Consequences:**

**Positive:**
- Declarative rule definition
- Good performance
- Supports complex conditional logic
- Easy to load from Excel/config

**Negative:**
- Learning curve for rule syntax
- May need custom logic for edge cases

**Neutral:**
- Rule versioning and testing framework needed

---

### ADR-003: Data Validation Framework Selection

**Status:** Accepted

**Context:**
Need comprehensive data validation for journal entries, mapping rules, and ledger output with detailed error reporting.

**Decision Drivers:**
- Type safety requirements
- pandas DataFrame integration
- Detailed error messages
- Accounting correctness critical

**Considered Options:**
1. Pydantic + Pandantic
2. PyDataValidator
3. Custom validation

**Decision:**
Use **Pydantic + Pandantic** for all data validation.

**Consequences:**

**Positive:**
- Type-safe data models
- Excellent pandas integration
- Detailed, actionable error messages
- Industry standard approach

**Negative:**
- Additional dependency
- Learning curve for type hints

**Neutral:**
- Validation performance is excellent

---

**Research Complete** ✅

**Next Workflow:** Product Brief (recommended) or PRD (required)
