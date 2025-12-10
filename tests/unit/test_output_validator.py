"""Unit tests for OutputValidator class."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.transformation.aggregator import QuarterlyAggregation
from veritas_accounting.validation.output_validator import OutputValidator
from veritas_accounting.validation.input_validator import ValidationError


class TestOutputValidator:
    """Test suite for OutputValidator class."""

    def test_validate_completeness_all_processed(self):
        """Test completeness validation passes when all entries are processed."""
        validator = OutputValidator()

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
            JournalEntry(
                entry_id="JE-002",
                year=2024,
                description="Test 2",
                old_type="CR",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 20),
            ),
        ]

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test 1",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
            LedgerEntry(
                entry_id="LE-002",
                account_code="B2",
                account_path="A1/B2",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 20),
                year=2024,
                quarter=1,
                description="Test 2",
                source_entry_id="JE-002",
                rule_applied="R-002",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        # Should not have completeness errors
        assert not any(e.error_type == "missing_entry" for e in errors)
        assert not any(e.error_type == "orphaned_entry" for e in errors)

    def test_validate_completeness_missing_entry(self):
        """Test completeness validation catches missing entries."""
        validator = OutputValidator()

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
            JournalEntry(
                entry_id="JE-002",
                year=2024,
                description="Test 2",
                old_type="CR",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 20),
            ),
        ]

        # Only one entry processed
        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test 1",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        assert len([e for e in errors if e.error_type == "missing_entry"]) >= 1

    def test_validate_completeness_orphaned_entry(self):
        """Test completeness validation catches orphaned ledger entries."""
        validator = OutputValidator()

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        # Ledger entry references non-existent source
        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test 1",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
            LedgerEntry(
                entry_id="LE-002",
                account_code="B2",
                account_path="A1/B2",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 20),
                year=2024,
                quarter=1,
                description="Test 2",
                source_entry_id="JE-999",  # Non-existent source
                rule_applied="R-002",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        assert len([e for e in errors if e.error_type == "orphaned_entry"]) >= 1

    def test_validate_accuracy_amount_match(self):
        """Test accuracy validation passes when amounts match."""
        validator = OutputValidator()

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        # Should not have accuracy errors
        assert not any(e.error_type == "amount_mismatch" for e in errors)
        assert not any(e.error_type == "date_mismatch" for e in errors)

    def test_validate_accuracy_amount_mismatch(self):
        """Test accuracy validation catches amount mismatches."""
        validator = OutputValidator()

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("500"),  # Doesn't match
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        assert len([e for e in errors if e.error_type == "amount_mismatch"]) >= 1

    def test_validate_account_structure_valid(self):
        """Test account structure validation passes for valid codes."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = OutputValidator(account_hierarchy=hierarchy)

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        assert not any(e.error_type == "invalid_account_code" for e in errors)

    def test_validate_account_structure_invalid(self):
        """Test account structure validation catches invalid codes."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = OutputValidator(account_hierarchy=hierarchy)

        journal_entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="INVALID",  # Invalid code
                account_path="INVALID",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                year=2024,
                quarter=1,
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries)

        assert len([e for e in errors if e.error_type == "invalid_account_code"]) >= 1

    def test_validate_quarterly_totals_duplicate(self):
        """Test quarterly totals validation catches duplicates."""
        validator = OutputValidator()

        journal_entries = []
        ledger_entries = []

        # Duplicate aggregations for same account/quarter/year
        aggregations = [
            QuarterlyAggregation(
                account_code="A1",
                account_path="A1",
                quarter=1,
                year=2024,
                total_amount=Decimal("1000"),
                entry_count=5,
                level=1,
            ),
            QuarterlyAggregation(
                account_code="A1",  # Duplicate
                account_path="A1",
                quarter=1,
                year=2024,
                total_amount=Decimal("500"),
                entry_count=3,
                level=1,
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries, aggregations)

        assert len([e for e in errors if e.error_type == "duplicate_aggregation"]) >= 1

    def test_validate_consistency_hierarchy_mismatch(self):
        """Test consistency validation catches hierarchy mismatches."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
            Account(code="B3", name="Account 3", level=2, parent_code="A1", full_path="A1/B3"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = OutputValidator(account_hierarchy=hierarchy)

        journal_entries = []
        ledger_entries = []

        # Level 2 totals don't sum to Level 1 total
        aggregations = [
            QuarterlyAggregation(
                account_code="A1",
                account_path="A1",
                quarter=1,
                year=2024,
                total_amount=Decimal("1000"),  # Level 1 total
                entry_count=0,
                level=1,
            ),
            QuarterlyAggregation(
                account_code="B2",
                account_path="A1/B2",
                quarter=1,
                year=2024,
                total_amount=Decimal("400"),
                entry_count=2,
                level=2,
            ),
            QuarterlyAggregation(
                account_code="B3",
                account_path="A1/B3",
                quarter=1,
                year=2024,
                total_amount=Decimal("700"),  # 400 + 700 = 1100, not 1000
                entry_count=3,
                level=2,
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries, aggregations)

        assert len([e for e in errors if e.error_type == "hierarchy_mismatch"]) >= 1

    def test_validate_consistency_valid_hierarchy(self):
        """Test consistency validation passes for valid hierarchy."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
            Account(code="B3", name="Account 3", level=2, parent_code="A1", full_path="A1/B3"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = OutputValidator(account_hierarchy=hierarchy)

        journal_entries = []
        ledger_entries = []

        # Level 2 totals correctly sum to Level 1 total
        aggregations = [
            QuarterlyAggregation(
                account_code="A1",
                account_path="A1",
                quarter=1,
                year=2024,
                total_amount=Decimal("1100"),  # Level 1 total
                entry_count=0,
                level=1,
            ),
            QuarterlyAggregation(
                account_code="B2",
                account_path="A1/B2",
                quarter=1,
                year=2024,
                total_amount=Decimal("400"),
                entry_count=2,
                level=2,
            ),
            QuarterlyAggregation(
                account_code="B3",
                account_path="A1/B3",
                quarter=1,
                year=2024,
                total_amount=Decimal("700"),  # 400 + 700 = 1100 ✓
                entry_count=3,
                level=2,
            ),
        ]

        errors = validator.validate_output(journal_entries, ledger_entries, aggregations)

        assert not any(e.error_type == "hierarchy_mismatch" for e in errors)
