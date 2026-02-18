"""Unit tests for TransformationValidator class."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.applicator import RuleApplicationResult
from veritas_accounting.validation.transformation_validator import (
    TransformationValidator,
)
from veritas_accounting.validation.input_validator import ValidationError


class TestTransformationValidator:
    """Test suite for TransformationValidator class."""

    def test_validate_rule_match_with_matching_rule(self):
        """Test validation when rule matches."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
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
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        # Should have no errors for valid transformation
        assert len(errors) == 0

    def test_validate_rule_match_no_match_flag(self):
        """Test validation when no rules match (expected case)."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="UNKNOWN",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = RuleApplicationResult(
            ledger_entries=[],
            applied_rules=[],
            no_match=True,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [])

        # No-match is expected, not an error
        assert len(errors) == 0

    def test_validate_rule_match_unexpected_state(self):
        """Test validation catches unexpected state (no-match but has entries)."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
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
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[],
            no_match=True,  # Unexpected: no_match but has entries
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [])

        assert len(errors) >= 1
        assert any(e.error_type == "unexpected_state" for e in errors)

    def test_validate_rule_correctness_mismatch(self):
        """Test validation catches rule that doesn't actually match."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="CR",  # Different from rule condition
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",  # Condition doesn't match entry
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        # Simulate incorrect application: rule applied but doesn't match
        ledger_entry = LedgerEntry(
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
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        assert len(errors) >= 1
        assert any(e.error_type == "rule_mismatch" for e in errors)

    def test_validate_account_codes_invalid(self):
        """Test validation catches invalid account codes."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = TransformationValidator(account_hierarchy=hierarchy)

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
            entry_id="LE-001",
            account_code="INVALID",  # Invalid account code
            account_path="INVALID",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        assert len(errors) >= 1
        assert any(e.error_type == "invalid_account_code" for e in errors)

    def test_validate_account_codes_valid(self):
        """Test validation passes for valid account codes."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = TransformationValidator(account_hierarchy=hierarchy)

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",  # Valid account code
            account_path="A1",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        # Should not have account code errors
        assert not any(e.error_type == "invalid_account_code" for e in errors)

    def test_validate_amount_preservation_match(self):
        """Test amount preservation validation passes when amounts match."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",
            account_path="A1",
            amount=Decimal("1000"),  # Matches journal entry amount
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        # Should not have amount mismatch errors
        assert not any(e.error_type == "amount_mismatch" for e in errors)

    def test_validate_amount_preservation_mismatch(self):
        """Test amount preservation validation catches mismatches."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entry = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",
            account_path="A1",
            amount=Decimal("500"),  # Doesn't match journal entry amount
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        assert len(errors) >= 1
        assert any(e.error_type == "amount_mismatch" for e in errors)

    def test_validate_amount_preservation_one_to_many(self):
        """Test amount preservation for one-to-many mappings."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        # One-to-many: split 1000 into 600 + 400
        ledger_entry1 = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",
            account_path="A1",
            amount=Decimal("600"),
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        ledger_entry2 = LedgerEntry(
            entry_id="LE-002",
            account_code="B2",
            account_path="A1/B2",
            amount=Decimal("400"),
            date=datetime(2024, 1, 15),
            year=2024,
            quarter=1,
            description="Test",
            source_entry_id="JE-001",
            rule_applied="R-001",
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
            generates_multiple=True,
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry1, ledger_entry2],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        # Amounts sum correctly: 600 + 400 = 1000
        assert not any(e.error_type == "amount_mismatch" for e in errors)

    def test_validate_completeness_one_to_many_incomplete(self):
        """Test completeness validation catches incomplete one-to-many mappings."""
        validator = TransformationValidator()

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
            generates_multiple=True,  # One-to-many rule
        )

        # Only one ledger entry created, but rule expects multiple
        ledger_entry = LedgerEntry(
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
        )

        result = RuleApplicationResult(
            ledger_entries=[ledger_entry],
            applied_rules=[rule],
            no_match=False,
            entry_id="JE-001",
        )

        errors = validator.validate_transformation(entry, result, [rule])

        assert len(errors) >= 1
        assert any(e.error_type == "incomplete_one_to_many" for e in errors)

    def test_validate_batch(self):
        """Test batch validation."""
        validator = TransformationValidator()

        entries = [
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

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )

        results = [
            RuleApplicationResult(
                ledger_entries=[
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
                    )
                ],
                applied_rules=[rule],
                no_match=False,
                entry_id="JE-001",
            ),
            RuleApplicationResult(
                ledger_entries=[],
                applied_rules=[],
                no_match=True,
                entry_id="JE-002",
            ),
        ]

        errors = validator.validate_batch(entries, results, [rule])

        # Batch validation should work
        assert isinstance(errors, list)

    def test_validate_batch_count_mismatch(self):
        """Test batch validation catches count mismatch."""
        validator = TransformationValidator()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        results = [
            RuleApplicationResult(
                ledger_entries=[],
                applied_rules=[],
                no_match=True,
                entry_id="JE-001",
            ),
            RuleApplicationResult(  # Extra result
                ledger_entries=[],
                applied_rules=[],
                no_match=True,
                entry_id="JE-002",
            ),
        ]

        errors = validator.validate_batch(entries, results, [])

        assert len(errors) >= 1
        assert any(e.error_type == "batch_mismatch" for e in errors)








