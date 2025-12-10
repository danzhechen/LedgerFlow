# veritas-accounting - Product Requirements Document

**Author:** dan  
**Date:** 2025-01-27  
**Version:** 1.0

---

## Executive Summary

**Vision Alignment**

This product transforms Veritas's quarterly accounting process from a 5-10 hour manual task (dependent on a single expert) into a streamlined, accessible workflow that anyone can operate and maintain. The vision is to eliminate knowledge silos, reduce processing time by 80-90%, and ensure continuity of critical accounting operations through automation and clear documentation.

The system automates the complete workflow: processing 691+ journal entries, applying 194 mapping rules with conditional logic automatically, transforming journal → ledger with hierarchical structure, and generating quarterly aggregations—all while ensuring 100% accuracy through comprehensive validation and human oversight.

**What Makes This Special**

The unique value proposition is **Excel-native accounting automation with complete transparency and trust**. Unlike traditional accounting software that requires learning new tools, this system works entirely within Excel—the familiar interface users already know. The system provides complete transparency: showing exactly what transformations were made, comprehensive error reporting, and human oversight at every step.

The compelling moment for users is when they run the automation and see their 5-10 hour quarterly task complete in under an hour, with full visibility into every transformation and the confidence that comes from comprehensive validation and reviewable outputs.

---

## Project Classification

**Technical Type:** Internal Tool / Business Process Automation  
**Domain:** Accounting / Financial Operations  
**Complexity:** Medium

This is an **internal business process automation tool** designed to automate Veritas's quarterly accounting workflow. It provides an Excel-native interface for processing journal entries through mapping rules to generate ledger reports. The domain is accounting/financial operations, requiring high accuracy and auditability.

**Project Type Details:**
- **Form Factor:** Python script/application with Excel I/O
- **Target Users:** Accounting operators (current expert and future inheritors)
- **Integration Pattern:** Standalone tool, processes Excel files
- **Deployment:** Local Python environment, no infrastructure required

**Domain Context**

Accounting automation requires:
- **100% accuracy** in all transformations (critical for financial reporting)
- **Complete audit trail** for compliance and verification
- **Transparency** so operators can review and approve all changes
- **Error detection and reporting** to catch issues before they impact financial reports
- **Rule-based logic** that can be explicitly documented and maintained

---

## Success Criteria

**What Winning Looks Like**

Success for this product means the current accounting operator (PhD student) can reduce quarterly processing from **5-10 hours to < 1 hour**, while ensuring **100% accuracy** and enabling **any team member** to operate the system with confidence. Success means eliminating the single point of failure and ensuring operational continuity even when the expert is unavailable.

**Specific Success Metrics:**

1. **Time Savings:** 80-90% reduction in quarterly processing time (5-10 hours → < 1 hour)
2. **Accuracy:** 100% correct transformations for all 691+ journal entries
3. **Knowledge Transfer:** New operators can learn and use the system in < 2 hours (vs. weeks currently)
4. **Trust & Adoption:** Expert trusts system enough to use it for all quarterly processing within 3 months
5. **Operational Continuity:** Process continues successfully even when expert unavailable
6. **Error Detection:** 100% of errors caught and flagged for review

**Success means users experience [key value moment]:** Running the automation and seeing their quarterly accounting work complete in under an hour, with full confidence in the results through transparent reporting and comprehensive validation.

---

## Product Scope

### MVP - Minimum Viable Product

**Core Capabilities (Must Work for Product to Be Useful):**

1. **Excel Input Processing**
   - Read journal entries from Excel file (691+ entries)
   - Read 194 mapping rules from Excel/config
   - Validate input data structure and content

2. **Automated Rule Application**
   - Apply all 194 mapping rules automatically (no manual lookup)
   - Handle conditional logic and one-to-many mappings
   - Transform journal entries → ledger structure with hierarchical organization (4 levels, 25 accounts)

3. **Data Transformation**
   - Automate journal → ledger mapping (eliminates manual translation bottleneck)
   - Generate quarterly aggregations
   - Preserve Excel formatting and structure in output

4. **Validation & Error Detection**
   - Multi-layer validation (input, transformation, output)
   - Comprehensive error detection and reporting
   - Flag all issues for human review

5. **Transparency & Trust**
   - Complete audit trail (track all transformations)
   - Excel error report (reviewable, shows all changes)
   - Auto-fix with review flags (expert approves all fixes)
   - Validation results visible (confidence indicators)

6. **Excel-Native Interface**
   - Excel-based rule management (edit rules in Excel)
   - Excel input/output workflow (familiar interface)
   - Clear error messages (understand what went wrong)

**MVP Success Criteria:** 
- ✅ Processes 691 entries correctly
- ✅ Applies all 194 mapping rules automatically
- ✅ Reduces processing time from 5-10 hours to < 1 hour
- ✅ Expert can review and approve all transformations
- ✅ New operator can learn and use system in < 2 hours
- ✅ System is trusted for quarterly processing

### Growth Features (Post-MVP)

**Features That Make It Competitive:**

1. **Enhanced Rule Management**
   - Rule versioning and change tracking
   - Rule testing framework
   - Rule validation before application

2. **Advanced Error Handling**
   - Pattern learning from corrections (suggest fixes based on history)
   - Smart error grouping and prioritization
   - Automated fix suggestions with confidence scores

3. **Performance Optimization**
   - Parallel processing for large batches
   - Incremental processing (process only new/changed entries)
   - Caching of rule evaluations

4. **Integration & Automation**
   - Scheduled quarterly processing
   - Email notifications for completion/errors
   - Integration with other financial systems (if needed)

5. **Reporting & Analytics**
   - Historical processing reports
   - Rule usage analytics
   - Error trend analysis

### Vision (Future)

**Dream Version Capabilities:**

1. **Upstream Automation**
   - Bank statement → journal entry automation
   - Receipt/invoice → journal entry automation
   - Multi-source data integration

2. **Intelligent Processing**
   - Machine learning for pattern recognition
   - Automatic rule suggestion based on data patterns
   - Predictive error detection

3. **Advanced User Experience**
   - Web interface (if needed by stakeholders)
   - Interactive visualization of transformations
   - Real-time processing dashboard

4. **Enterprise Features**
   - Multi-organization support
   - Role-based access control
   - Advanced audit and compliance reporting

**Out of Scope (for initial release)**
- Bank statement → journal automation (deferred to future)
- Pattern learning from corrections (deferred to post-MVP)
- Web interface (Excel-native only for MVP)
- Multi-organization support (single organization focus)

---

## Domain-Specific Requirements

**Accounting Domain Considerations**

This system operates in the accounting/financial domain, which has specific requirements:

1. **Accuracy is Critical:**
   - 100% correctness in all transformations is non-negotiable
   - Financial reporting errors have serious consequences
   - Every transformation must be verifiable

2. **Audit Trail Required:**
   - Complete record of all transformations for compliance
   - Ability to trace any output back to source inputs
   - Version control for rules and processing logic

3. **Human Oversight:**
   - Expert review and approval of all automated changes
   - No "black box" processing—everything must be transparent
   - Clear error reporting for human decision-making

4. **Regulatory Compliance:**
   - Maintain data integrity throughout processing
   - Support audit requirements
   - Preserve original data alongside processed data

5. **Rule Complexity:**
   - 194 mapping rules with conditional logic
   - One-to-many mappings (one journal entry → multiple ledger entries)
   - Hierarchical account structure (4 levels, 25 accounts)

These domain requirements shape all functional and non-functional requirements below.

---

## Developer Tool Specific Requirements

**Excel Processing Interface**

- **FR-EXCEL1:** The system MUST read journal entries from Excel files (standard .xlsx format)
- **FR-EXCEL2:** The system MUST read 194 mapping rules from Excel files or configuration files
- **FR-EXCEL3:** The system MUST write ledger output to Excel files with preserved formatting
- **FR-EXCEL4:** The system MUST generate Excel error reports with clear formatting and explanations
- **FR-EXCEL5:** The system MUST support Chinese text encoding in Excel files

**Python API & Script Interface**

- **FR-API1:** The system MUST provide a Python script/application entrypoint that:
  - Accepts Excel file paths as input
  - Processes journal entries through mapping rules
  - Generates ledger output and error reports
- **FR-API2:** The system MUST support configuration via:
  - Excel-based rule files
  - Configuration files (YAML/JSON)
  - Command-line arguments
- **FR-API3:** The system MUST provide clear error messages and exceptions for common failure modes (invalid Excel format, missing rules, validation errors)

**Installation & Distribution**

- **FR-INST1:** The system MUST be installable via standard Python package managers (pip, poetry)
- **FR-INST2:** The system MUST have clear installation instructions and dependency management
- **FR-INST3:** The system MUST work in standard Python environments (no special infrastructure required)

**Documentation & Examples**

- **FR-DOC1:** The system MUST provide:
  - Usage documentation (how to run the automation)
  - Rule management guide (how to edit 194 rules)
  - Error handling guide (how to interpret and fix errors)
  - Troubleshooting guide
- **FR-DOC2:** The system MUST include example Excel files demonstrating:
  - Input journal entry format
  - Mapping rule format
  - Expected output format

---

## Functional Requirements

### Input Processing

- **FR1:** The system MUST accept Excel files containing journal entries (691+ entries per quarter)
- **FR2:** The system MUST validate journal entry structure (required columns, data types, value ranges)
- **FR3:** The system MUST read 194 mapping rules from Excel files or configuration
- **FR4:** The system MUST validate mapping rule structure and logic
- **FR5:** The system MUST handle Chinese text encoding in input files

### Rule Application & Transformation

- **FR6:** The system MUST apply all 194 mapping rules automatically to journal entries (no manual lookup required)
- **FR7:** The system MUST handle conditional logic in mapping rules (if-then-else conditions)
- **FR8:** The system MUST support one-to-many mappings (one journal entry → multiple ledger entries)
- **FR9:** The system MUST transform journal entries → ledger structure with hierarchical organization (4 levels, 25 accounts)
- **FR10:** The system MUST generate quarterly aggregations from ledger entries
- **FR11:** The system MUST preserve Excel formatting and structure in output files

### Validation & Error Detection

- **FR12:** The system MUST validate input data before processing (structure, completeness, data types)
- **FR13:** The system MUST validate transformation logic during processing (rule application, mapping correctness)
- **FR14:** The system MUST validate output data after processing (completeness, consistency, accuracy)
- **FR15:** The system MUST detect and flag all errors for human review
- **FR16:** The system MUST provide detailed error messages explaining what went wrong and why
- **FR17:** The system MUST support auto-fix suggestions with review flags (expert approves all fixes)

### Transparency & Audit Trail

- **FR18:** The system MUST track all transformations in a complete audit trail
- **FR19:** The system MUST generate Excel error reports showing all changes and issues
- **FR20:** The system MUST make all transformations visible and reviewable
- **FR21:** The system MUST show validation results and confidence indicators
- **FR22:** The system MUST preserve original data alongside processed data for comparison

### Output & Reporting

- **FR23:** The system MUST generate ledger output in Excel format with preserved formatting
- **FR24:** The system MUST generate quarterly aggregation reports
- **FR25:** The system MUST generate comprehensive error reports in Excel format
- **FR26:** The system MUST support export of audit trail data

### Rule Management

- **FR27:** The system MUST allow rules to be edited in Excel files (no code changes required)
- **FR28:** The system MUST validate rule syntax and logic before application
- **FR29:** The system MUST support rule versioning (track rule changes over time)

### User Experience

- **FR30:** The system MUST provide clear, actionable error messages
- **FR31:** The system MUST use Excel-native workflow (familiar interface, no new tools to learn)
- **FR32:** The system MUST provide simple process flow: input → process → review → output
- **FR33:** The system MUST be operable by non-expert users after brief training (< 2 hours)

---

## Non-Functional Requirements

### Performance

- **NFR1 — Processing Speed:**  
  - Target: Process 691 entries in < 5 minutes on standard hardware
  - Target: Complete full quarterly workflow (input → output) in < 1 hour total time (including review)

### Accuracy

- **NFR2 — Transformation Accuracy:**  
  - Target: 100% correct transformations for all journal entries
  - Target: 100% of errors detected and flagged for review
  - Requirement: Zero tolerance for undetected errors

### Reliability

- **NFR3 — Error Handling:**  
  - The system MUST fail gracefully and report errors with actionable messages
  - The system MUST not corrupt or lose input data
  - The system MUST preserve original data even when errors occur

### Maintainability

- **NFR4 — Rule Management:**  
  - Rules MUST be editable in Excel (no code changes required)
  - Rules MUST be versioned and change-tracked
  - System MUST validate rules before application

### Usability

- **NFR5 — Learning Curve:**  
  - New operators MUST be able to learn and use the system in < 2 hours
  - System MUST use Excel-native workflow (familiar interface)
  - Error messages MUST be clear and actionable

### Observability

- **NFR6 — Transparency:**  
  - All transformations MUST be visible and reviewable
  - Complete audit trail MUST be maintained
  - Error reports MUST be comprehensive and clear

---

## Dependencies & Assumptions

**Dependencies**
- Python 3.8+ runtime environment
- pandas library for data processing
- openpyxl library for Excel I/O
- Pydantic library for data validation
- rule-engine library for rule evaluation
- Standard Python libraries (logging, pathlib, typing)

**Assumptions**
- Users have access to Python environment and can install packages
- Input Excel files follow expected structure (documented format)
- Users are comfortable with Excel (familiar interface)
- Expert will review and approve all automated transformations
- Rules are maintained in Excel files (no code changes for rule updates)

---

## Risks & Open Questions

**Risks**
- R1: Complex Excel structure may not be fully preserved in output
- R2: 194 rules may have edge cases not handled by rule engine
- R3: Chinese text encoding issues may cause processing errors
- R4: Performance may be slower than expected with 691 entries
- R5: Expert may not trust automated system initially (adoption risk)

**Open Questions (for future clarification with stakeholders)**
- OQ1: What is the exact structure of input journal entry Excel files?
- OQ2: What is the exact format of the 194 mapping rules?
- OQ3: Are there specific Excel formatting requirements for output?
- OQ4: What level of detail is needed in error reports?
- OQ5: Are there regulatory compliance requirements beyond audit trail?

---

## Success Metrics (Initial Hypotheses)

- **M1:** Time reduction: 80-90% reduction in quarterly processing (5-10 hours → < 1 hour)
- **M2:** Accuracy: 100% correct transformations for all 691+ entries
- **M3:** Learning curve: New operators can use system in < 2 hours
- **M4:** Adoption: Expert uses system for all quarterly processing within 3 months
- **M5:** Error detection: 100% of errors caught and flagged

---

## Implementation Planning

### Epic Breakdown Required

Requirements must be decomposed into epics and bite-sized stories (200k context limit).

**Next Step:** Run `workflow create-epics-and-stories` to create the implementation breakdown.

---

## References

- Product Brief: `docs/product-brief-veritas-accounting-2025-12-07.md`
- Technical Research: `docs/research-technical-2025-12-07.md`
- Brainstorming Session: `docs/analysis/brainstorming-session-2025-12-07.md`
- Example Data: `账目分类明细.xlsx`

---

## Next Steps

1. **Epic & Story Breakdown** - Run: `workflow create-epics-and-stories`
2. **UX Design** (if UI) - Run: `workflow ux-design` (Not applicable - Excel-native, no custom UI)
3. **Architecture** - Run: `workflow create-architecture`

---

_This PRD captures the essence of veritas-accounting - Excel-native accounting automation with complete transparency and trust, reducing quarterly processing from 5-10 hours to < 1 hour while ensuring 100% accuracy and operational continuity._

_Created through collaborative discovery between dan and AI facilitator._
