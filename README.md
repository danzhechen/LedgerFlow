# LedgerFlow

**Excel-native accounting automation with complete transparency and trust.**

Transform your quarterly accounting process from a 5-10 hour manual task into a streamlined, automated workflow. **LedgerFlow** processes hundreds of journal entries through complex mapping rules, generating hierarchical ledger structures—all while maintaining complete transparency and validation.

## Overview

**LedgerFlow** is Excel-native accounting automation that actually makes sense. No new tools to learn, no black boxes to worry about—just your familiar Excel files, automated through intelligent rule mapping, with complete audit trails. Turn hours of manual journal-to-ledger translation into a single command, while maintaining 100% accuracy and full visibility into every step.

**Key Features:**
- ✅ Excel-native workflow (familiar interface, no new tools to learn)
- ✅ Automated rule application (194 mapping rules applied automatically)
- ✅ Complete transparency (audit trail, error reports, transformation visibility)
- ✅ 100% accuracy (comprehensive validation at every stage)
- ✅ Human oversight (expert review and approval of all changes)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/danzhechen/LedgerFlow.git
cd LedgerFlow
```

2. Create a virtual environment:
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Install development dependencies (optional):
```bash
pip install -e ".[dev]"
```

### Basic Usage

```bash
ledgerflow process --input journal.xlsx --rules rules.xlsx --output ./output
```

> **Note:** The CLI command is still `veritas-accounting` until package renaming is complete. This will be updated in a future release.

## Project Structure

```
LedgerFlow/
├── src/veritas_accounting/    # Main package (internal name)
│   ├── cli/                   # CLI interface
│   ├── config/                # Configuration management
│   ├── models/                # Data models (Pydantic)
│   ├── excel/                 # Excel I/O operations
│   ├── validation/            # Validation pipeline
│   ├── rules/                 # Rule engine
│   ├── transformation/        # Journal → Ledger transformation
│   ├── audit/                 # Audit trail tracking
│   ├── reporting/             # Report generation
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── docs/                      # Documentation
└── examples/                  # Example files
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff check .
mypy src/
```

## Documentation

### User Guides
- [Getting Started](./docs/getting-started.md) - Installation and first run guide
- [User Manual](./docs/user-manual.md) - Complete feature reference
- [Configuration Guide](./docs/configuration.md) - Configuration options and setup
- [Error Handling Guide](./docs/error-handling.md) - Understanding and fixing errors
- [Troubleshooting Guide](./docs/troubleshooting.md) - Common issues and solutions
- [Rule Management Guide](./docs/rule-management.md) - Editing and managing mapping rules

### Technical Documentation
- [Architecture](./docs/architecture.md) - System architecture and design decisions
- [PRD](./docs/PRD.md) - Product requirements document
- [Epics](./docs/epics.md) - Epic and story breakdown

### Examples
- [Example Files](./examples/) - Sample Excel files showing correct formats

## License

MIT License

## Status

✅ **Epic 1-7 Complete** - Foundation, Input Processing, Rule Engine, Validation, Audit Trail, Output Generation, and User Interface implemented

**Completed Epics:**
- ✅ Epic 1: Foundation & Project Setup
- ✅ Epic 2: Input Processing & Validation
- ✅ Epic 3: Rule Engine & Transformation Core
- ✅ Epic 4: Validation & Error Detection
- ✅ Epic 5: Transparency & Audit Trail
- ✅ Epic 6: Output Generation & Reporting
- ✅ Epic 7: User Interface & Experience
- ✅ Epic 8: Documentation & Examples

**Ready for Production Use**
