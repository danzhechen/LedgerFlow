# Product Brief: Veritas Accounting Automation System

**Project:** veritas-accounting  
**Date:** 2025-12-07  
**Author:** dan  
**Status:** Draft

---

## Executive Summary

**Product Vision:** An automated accounting system that transforms Veritas's quarterly accounting process from a 5-10 hour manual task (dependent on a single expert) into a streamlined, accessible workflow that anyone can operate and maintain.

**Core Value Proposition:** Eliminate knowledge silos, reduce processing time by 80-90%, and ensure continuity of critical accounting operations through automation and clear documentation.

---

## The Problem Worth Solving

### Current State Pain Points

**Time Investment:**
- **5-10 hours per quarter** of manual accounting work
- **20-40 hours annually** spent on repetitive data processing
- Significant opportunity cost - time that could be spent on strategic work

**Knowledge Dependency:**
- **Single point of failure:** Only one person knows the entire process
- **Bus factor risk:** If that person is unavailable, accounting stops
- **Knowledge silo:** Critical institutional knowledge locked in one person's head
- **Onboarding challenge:** New team members face steep learning curve

**Process Complexity:**
- **194 mapping rules** require manual input and lookup for each entry
- **No easy way to map journal → ledger:** Manual translation is the primary time sink
- **691+ journal entries** processed manually each quarter
- **Complex mapping logic:** Too complicated to learn quickly
- **Error-prone:** Manual translation from journal to ledger increases error risk
- **Inconsistent:** Process may vary slightly each time

**Operational Risks:**
- **Human error:** Manual processing increases error risk
- **Delays:** 5-10 hours blocks availability for other work (especially critical for PhD student)
- **Expert availability:** Only expert is doing PhD and has very limited time
- **Scalability:** Process doesn't scale with organization growth
- **Compliance:** Manual process harder to audit and verify

### Urgency Drivers

**Immediate Pressures:**
- **Expert time constraints:** The only person who knows the process is doing PhD and has very limited time
- **Time investment unsustainable:** 5-10 hours per quarter is too much given other commitments
- **Knowledge transfer urgency:** Need to preserve and transfer knowledge before expert becomes unavailable
- **Process bottleneck:** Accounting work blocks other important work

### The Cost of the Problem

**Quantifiable Costs:**
- **Time:** 20-40 hours annually (5-10 hours × 4 quarters)
- **Opportunity Cost:** Strategic work delayed or missed
- **Risk Cost:** Potential errors in financial reporting

**Qualitative Costs:**
- **Organizational Risk:** Dependency on single person
- **Team Stress:** Pressure on the person who knows the process
- **Growth Limitation:** Process doesn't scale with organization
- **Knowledge Loss Risk:** If expert leaves, process knowledge may be lost

---

## Target Users

### Primary User: Current Accounting Operator
**Profile:**
- The person who currently does the 5-10 hour quarterly work
- Has deep knowledge of the 194 mapping rules
- Understands the journal → ledger → quarterly workflow
- Wants to save time and reduce manual work

**Needs:**
- Reduce quarterly processing time from 5-10 hours to < 1 hour
- Maintain accuracy and correctness
- Easy to use (Excel-native, familiar workflow)
- Confidence that automation is correct

**Pain Points:**
- **Time-consuming manual work:** 5-10 hours per quarter is unsustainable
- **Rule input overhead:** Inputting every rule manually takes significant time
- **No easy mapping method:** Manual journal → ledger mapping is the primary bottleneck
- **Complexity barrier:** Mapping rules are too complicated to teach quickly
- **Time pressure:** PhD commitments leave very limited time for accounting work
- **Pressure of being the only expert:** Stress of being the single point of knowledge
- **Risk of errors:** Manual processing increases error risk
- **Difficulty explaining process:** Hard to transfer knowledge due to complexity

### Secondary User: Future Inheritors
**Profile:**
- Team members who will take over accounting responsibilities
- May not have deep knowledge of mapping rules initially
- Need to understand and operate the system
- Want to maintain continuity

**Needs:**
- Easy to learn and operate
- Clear documentation and error handling
- Confidence that system is correct
- Ability to understand what the system is doing

**Pain Points:**
- **Steep learning curve:** Mapping rules are too complicated to learn quickly
- **No easy mapping method:** Manual journal → ledger translation is time-consuming and error-prone
- **Rule complexity:** 194 mapping rules with conditional logic are hard to understand
- **Fear of making mistakes:** Complex process increases anxiety about errors
- **Uncertainty about mapping rules:** Not clear which rule applies when
- **Need for extensive training:** Current process requires deep knowledge transfer

### Tertiary User: Organization Leadership
**Profile:**
- Decision makers who need reliable financial reporting
- Concerned about operational continuity
- Want to reduce organizational risk

**Needs:**
- Reliable, accurate quarterly reports
- Reduced dependency on single person
- Audit trail and compliance
- Scalable process

---

## Product Vision

### Core Goals

**1. Accurate** ⭐ **PRIMARY GOAL**
- 100% accuracy in all transformations
- Comprehensive validation at every step
- Error detection and reporting
- Audit trail for verification

**2. Trust System** ⭐ **CRITICAL FOR ADOPTION**
- Complete transparency: Show exactly what the system did
- Reviewable: Expert can review and approve all transformations
- Confidence-building: Clear error reporting, validation results
- Audit trail: Track every decision and transformation
- Human oversight: Auto-fixes flagged for review, expert has final say

**3. Easy to Understand** ⭐ **ENABLES KNOWLEDGE TRANSFER**
- Excel-native: Familiar interface, no new tools
- Clear error messages: Understand what went wrong and why
- Self-documenting: Rules and mappings are explicit
- Simple workflow: Input → Process → Review → Output
- Accessible: New operators can learn quickly

### What We're Building

An **Excel-native accounting automation system** that:

1. **Automates the Complete Workflow:**
   - Processes 691+ journal entries automatically
   - Applies 194 mapping rules with conditional logic (no manual lookup)
   - Transforms journal → ledger with hierarchical structure automatically
   - Generates quarterly aggregations and reports

2. **Ensures Accuracy (Goal 1):**
   - Multi-layer validation at every step
   - Comprehensive error detection and reporting
   - Hybrid auto-fix with human review flags
   - Audit trail for all transformations
   - 100% correctness verification

3. **Builds Trust (Goal 2):**
   - Complete transparency: Show all transformations
   - Reviewable outputs: Excel error report with all changes
   - Confidence indicators: Validation results, confidence scores
   - Human oversight: Expert reviews and approves
   - Audit trail: Track every decision

4. **Easy to Understand (Goal 3):**
   - Excel-native workflow (familiar interface)
   - Excel-based rule management (edit 194 rules in Excel)
   - Clear error messages and guidance
   - Self-documenting system (rules, mappings, validations explicit)
   - Simple process: Anyone can operate after brief training

### Success Criteria

**Time Savings (Critical for PhD Student):**
- ✅ Reduce quarterly processing from **5-10 hours → < 1 hour**
- ✅ **80-90% time reduction** (4-9 hours saved per quarter)
- ✅ **16-36 hours saved annually**
- ✅ **Eliminate rule input overhead:** Rules loaded once, applied automatically
- ✅ **Automate journal → ledger mapping:** No more manual translation bottleneck

**Knowledge Accessibility:**
- ✅ System can be operated by anyone (not just the expert)
- ✅ **Simplify mapping complexity:** System handles complex rule logic automatically
- ✅ Clear documentation and error handling
- ✅ Rules and mappings are explicit (in Excel/config, not in someone's head)
- ✅ New team members can learn in < 2 hours (vs. weeks of training currently)

**Correctness:**
- ✅ 100% accuracy in transformations
- ✅ All 691 entries processed correctly
- ✅ All 194 mapping rules applied automatically (no manual lookup)
- ✅ Comprehensive validation and error detection
- ✅ Clear error reporting for review

**Operational Continuity:**
- ✅ No single point of failure
- ✅ Process can continue even when expert unavailable (PhD commitments)
- ✅ Clear handoff process for new operators
- ✅ System is maintainable and updatable
- ✅ **Expert can focus on PhD:** System handles routine work automatically

---

## Unique Value Proposition

**For the Current Operator (PhD Student):**
"Get your 5-10 hours back every quarter. The system handles the tedious rule lookups and mappings automatically. You review the results, approve what's correct, and fix what needs attention. Your expertise is preserved in the system, and you can focus on your PhD work."

**For Future Inheritors:**
"Learn the accounting process in hours, not weeks. The system shows you exactly what it's doing, explains any errors clearly, and guides you through the review process. You can operate confidently even without deep knowledge of the 194 mapping rules."

**For the Organization:**
"Eliminate the bus factor risk. Your critical accounting process is now accurate, transparent, and accessible. Anyone can operate it with confidence, and the system ensures correctness through comprehensive validation and human oversight."

---

## Market Positioning

**Category:** Internal Tool / Business Process Automation

**Positioning Statement:**
"Veritas Accounting Automation is an Excel-native system that transforms our quarterly accounting from a 5-10 hour manual process (dependent on a single expert) into a streamlined, accessible workflow that anyone can operate, saving 16-36 hours annually while ensuring accuracy and continuity."

**Differentiators:**
- Excel-native (no new tools to learn)
- Designed for correctness (accounting accuracy critical)
- Knowledge preservation (rules and logic explicit)
- Accessible to non-experts (clear error handling and guidance)

---

## Success Metrics

### Goal 1: Accurate
- **Processing Accuracy:** 100% correct transformations
- **Error Detection:** 100% of errors caught and flagged
- **Validation Coverage:** All entries validated at every step
- **Audit Trail:** Complete record of all transformations

### Goal 2: Trust System
- **Transparency:** All transformations visible and reviewable
- **Expert Confidence:** Expert trusts system enough to use it regularly
- **Review Process:** Expert can review and approve all changes
- **Error Reporting:** Comprehensive error report with clear explanations
- **Adoption:** System used for all quarterly processing within 3 months

### Goal 3: Easy to Understand
- **Learning Time:** New operators can learn in < 2 hours (vs. weeks currently)
- **User Confidence:** Operators feel confident using the system
- **Knowledge Transfer:** New team members can operate system successfully
- **Documentation:** Clear, accessible documentation
- **Error Clarity:** Error messages are clear and actionable

### Overall Success Metrics
- **Time Reduction:** 80-90% reduction (5-10 hours → < 1 hour per quarter)
- **Stress Reduction:** Current operator (PhD student) feels less pressure
- **Organizational Resilience:** Process continues even if expert unavailable
- **Knowledge Preservation:** Rules and logic are explicit and documented

---

## MVP Scope

### Core Features (Must Have)

**Accuracy Features:**
- Automated journal → ledger transformation (eliminates manual mapping bottleneck)
- 194 mapping rules applied automatically (no manual rule input)
- Multi-layer validation (input, transformation, output)
- Comprehensive error detection and reporting

**Trust System Features:**
- Complete audit trail (track all transformations)
- Excel error report (reviewable, shows all changes)
- Auto-fix with review flags (expert approves all fixes)
- Validation results visible (confidence indicators)

**Easy to Understand Features:**
- Excel-native interface (familiar workflow)
- Excel-based rule management (edit rules in Excel)
- Clear error messages (understand what went wrong)
- Simple process flow (input → process → review → output)

### Out of Scope for MVP

- Bank statement → journal automation (deferred to future)
- Pattern learning from corrections (deferred to post-MVP)
- Parallel processing optimization (sequential first, optimize later)
- Web interface (Excel-native only for MVP)

### MVP Success Criteria

- ✅ Processes 691 entries correctly
- ✅ Applies all 194 mapping rules automatically
- ✅ Reduces processing time from 5-10 hours to < 1 hour
- ✅ Expert can review and approve all transformations
- ✅ New operator can learn and use system in < 2 hours
- ✅ System is trusted for quarterly processing

---

## Next Steps

This product brief will inform the **Product Requirements Document (PRD)**, which will detail:
- Functional requirements (features and capabilities)
- Technical requirements (architecture and implementation)
- User stories and acceptance criteria aligned with the three goals (Accurate, Trust System, Easy to Understand)
- Implementation roadmap

**Ready to proceed to PRD creation?** The PRD will break down this vision into actionable requirements and user stories.

---

## References

- Brainstorming Session: `docs/analysis/brainstorming-session-2025-12-07.md`
- Technical Research: `docs/research-technical-2025-12-07.md`
- Example Data: `账目分类明细.xlsx`
