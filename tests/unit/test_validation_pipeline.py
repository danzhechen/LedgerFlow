"""Unit tests for InputValidationPipeline class."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.validation.pipeline import (
    InputValidationPipeline,
    ValidationResult,
    ValidationWarning,
)
from veritas_accounting.validation.input_validator import ValidationError


class TestInputValidationPipeline:
    """Test suite for InputValidationPipeline class."""

    def test_validate_inputs_valid_data(self):
        """Test validation of valid journal entries and rules."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test Entry 1",
                old_type="OL",
                amount=Decimal("1000.50"),
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.valid_journal_entries) == 1
        assert len(result.valid_mapping_rules) == 1

    def test_validate_inputs_business_rule_warnings(self):
        """Test that business rule violations generate warnings."""
        pipeline = InputValidationPipeline()

        # Use valid Pydantic values but ones that will trigger warnings
        from datetime import datetime, timedelta

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,  # At lower bound (valid but might trigger warning)
                description="Test Entry",
                old_type="OL",
                amount=Decimal("0"),  # Zero amount
                date=datetime.now() + timedelta(days=1),  # Future date
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is True  # Warnings don't make it invalid
        assert len(result.warnings) >= 1
        # Zero amount and future date should trigger warnings
        assert any(w.warning_type == "zero_amount" for w in result.warnings)
        assert any(w.warning_type == "future_date" for w in result.warnings)

    def test_validate_inputs_completeness_errors(self):
        """Test that empty required fields generate errors."""
        # Note: This test is limited because Pydantic prevents creating invalid entries
        # But we can test that completeness validation runs
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description=" ",  # Empty after strip
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        # Completeness validation should catch empty description
        assert len(result.errors) >= 1
        assert any(e.error_type == "missing_field" for e in result.errors)

    def test_validate_inputs_consistency_warnings(self):
        """Test that consistency issues generate warnings."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Entry 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                quarter=1,
            ),
            JournalEntry(
                entry_id="JE-002",
                year=2025,  # Different year
                description="Entry 2",
                old_type="OL",
                amount=Decimal("2000"),
                date=datetime(2025, 4, 20),
                quarter=2,  # Different quarter
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is True
        assert any(w.warning_type == "mixed_years" for w in result.warnings)
        assert any(w.warning_type == "mixed_quarters" for w in result.warnings)

    def test_validate_inputs_duplicate_entry_ids(self):
        """Test that duplicate entry IDs generate errors."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Entry 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
            JournalEntry(
                entry_id="JE-001",  # Duplicate ID
                year=2024,
                description="Entry 2",
                old_type="CR",
                amount=Decimal("2000"),
                date=datetime(2024, 2, 20),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is False
        assert any(e.error_type == "duplicate_entry" for e in result.errors)

    def test_validate_inputs_cross_reference_errors(self):
        """Test that unmatched entry types generate errors."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Entry 1",
                old_type="UNKNOWN_TYPE",  # Doesn't match any rule
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is False
        assert any(e.error_type == "unmatched_type" for e in result.errors)
        assert any("UNKNOWN_TYPE" in str(e) for e in result.errors)

    def test_validate_inputs_rule_validation_integrated(self):
        """Test that rule validation errors are included."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Entry 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == ",  # Invalid syntax
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is False
        assert any(e.error_type == "syntax_error" for e in result.errors)
        assert len(result.valid_mapping_rules) == 0

    def test_validate_inputs_large_amount_warning(self):
        """Test that very large amounts generate warnings."""
        pipeline = InputValidationPipeline()

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Large Entry",
                old_type="OL",
                amount=Decimal("2000000000"),  # 2 billion
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is True
        assert any(w.warning_type == "large_amount" for w in result.warnings)

    def test_validate_inputs_with_account_hierarchy(self):
        """Test validation with account hierarchy for cross-reference validation."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        pipeline = InputValidationPipeline(account_hierarchy=hierarchy)

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Entry 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
        ]

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",  # Valid account code
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'CR'",
                old_type="CR",
                account_code="INVALID",  # Invalid account code
                priority=2,
            ),
        ]

        result = pipeline.validate_inputs(entries, rules)

        assert result.is_valid is False
        assert any(e.error_type == "invalid_account_code" for e in result.errors)

    def test_validation_result_properties(self):
        """Test ValidationResult helper properties."""
        from veritas_accounting.validation.input_validator import ValidationError

        result = ValidationResult(
            is_valid=False,
            errors=[
                ValidationError(
                    row_number=1,
                    field_name="amount",
                    error_type="validation_error",
                    error_message="Invalid amount",
                    actual_value=100,
                    entry_id="JE-001",
                )
            ],
            warnings=[
                ValidationWarning(
                    row_number=2,
                    field_name="year",
                    warning_type="unusual_year",
                    warning_message="Unusual year",
                    actual_value=1999,
                    entry_id="JE-002",
                )
            ],
            valid_journal_entries=[],
            valid_mapping_rules=[],
        )

        assert result.error_count == 1
        assert result.warning_count == 1
        assert result.entries_processed == 1
        assert result.rules_processed == 0






