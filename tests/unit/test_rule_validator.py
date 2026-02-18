"""Unit tests for MappingRuleValidator class."""

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.validation.rule_validator import MappingRuleValidator
from veritas_accounting.validation.input_validator import ValidationError


class TestMappingRuleValidator:
    """Test suite for MappingRuleValidator class."""

    def test_validate_rules_valid_rules(self):
        """Test validation of valid rules."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL' and year == 2024",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'CR'",
                old_type="CR",
                account_code="B2",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0

    def test_validate_rules_syntax_error(self):
        """Test validation catches syntax errors."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",  # Valid
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == ",  # Invalid syntax
                old_type="CR",
                account_code="B2",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 1
        assert len(errors) == 1
        assert errors[0].error_type == "syntax_error"
        assert "R-002" in errors[0].entry_id

    def test_validate_rules_invalid_field_reference(self):
        """Test validation catches invalid field references."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="invalid_field == 'value'",  # Invalid field
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 0
        assert len(errors) == 1
        assert errors[0].error_type == "invalid_field_reference"
        assert "invalid_field" in errors[0].error_message

    def test_validate_rules_valid_field_references(self):
        """Test that valid JournalEntry fields are accepted."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL' and year == 2024 and amount > 1000",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="description.contains('test') and quarter == 1",
                old_type="OL",
                account_code="A1",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0

    def test_validate_rules_missing_old_type_and_new_type(self):
        """Test validation requires at least one of old_type or new_type."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="year == 2024",
                account_code="A1",
                priority=1,
                # Missing both old_type and new_type
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 0
        assert len(errors) == 1
        assert errors[0].error_type == "missing_field"
        assert "old_type" in errors[0].field_name or "new_type" in errors[0].field_name

    def test_validate_rules_with_old_type_only(self):
        """Test that old_type alone is sufficient."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 1
        assert len(errors) == 0

    def test_validate_rules_with_new_type_only(self):
        """Test that new_type alone is sufficient."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="year == 2024",
                new_type="NEW",
                account_code="A1",
                priority=1,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 1
        assert len(errors) == 0

    def test_validate_rules_account_code_validation(self):
        """Test account code validation with hierarchy."""
        # Create account hierarchy
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        validator = MappingRuleValidator(account_hierarchy=hierarchy)

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",  # Valid
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'CR'",
                old_type="CR",
                account_code="INVALID",  # Invalid
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        # Account code validation is NON-BLOCKING (per code comments)
        # Both rules should be valid, but there should be 1 error for the invalid account code
        assert len(valid_rules) == 2  # Both rules are valid (account code check doesn't block)
        # There should be 1 error for the invalid account code (warning/non-blocking)
        account_code_errors = [e for e in errors if e.error_type == "invalid_account_code"]
        assert len(account_code_errors) == 1
        assert "INVALID" in account_code_errors[0].error_message

    def test_validate_rules_account_code_validation_skipped(self):
        """Test that account code validation is skipped without hierarchy."""
        validator = MappingRuleValidator()  # No hierarchy

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="INVALID",  # Would be invalid with hierarchy
                priority=1,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        # Should pass validation (account code check skipped)
        assert len(valid_rules) == 1
        assert len(errors) == 0

    def test_validate_rules_conflict_detection(self):
        """Test conflict detection for same condition and priority."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'OL'",  # Same condition
                old_type="OL",
                account_code="B2",  # Different account code
                priority=1,  # Same priority
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        # Both rules are valid individually, but conflict detected
        assert len(valid_rules) == 2  # Both are valid
        assert len(errors) == 1
        assert errors[0].error_type == "rule_conflict"
        assert "R-001" in errors[0].entry_id
        assert "R-002" in errors[0].entry_id

    def test_validate_rules_no_conflict_different_priority(self):
        """Test that rules with same condition but different priority don't conflict."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'OL'",  # Same condition
                old_type="OL",
                account_code="B2",  # Different account code
                priority=2,  # Different priority (resolves conflict)
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0  # No conflict (different priorities)

    def test_validate_rules_no_conflict_same_account_code(self):
        """Test that rules with same condition and same account code don't conflict."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL'",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type == 'OL'",  # Same condition
                old_type="OL",
                account_code="A1",  # Same account code
                priority=1,  # Same priority
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0  # No conflict (same account code)

    def test_validate_rules_complex_condition(self):
        """Test validation of complex rule conditions."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL' and year == 2024 and amount > 1000",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="(old_type == 'CR' or old_type == 'DR') and year >= 2023",
                old_type="CR",
                account_code="B2",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0

    def test_validate_rules_keywords_ignored(self):
        """Test that rule-engine keywords are not flagged as invalid fields."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == 'OL' and year == 2024 or amount > 1000",
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="old_type != null and year >= 2023",
                old_type="OL",
                account_code="A1",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 2
        assert len(errors) == 0

    def test_validate_rules_multiple_errors_per_rule(self):
        """Test that multiple errors can be detected for a single rule."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="invalid_field == 'value'",  # Invalid field
                account_code="A1",
                priority=1,
                # Missing old_type and new_type
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 0
        # Should have at least syntax error (if condition parses) or field reference error
        # and missing field error
        assert len(errors) >= 1

    def test_validate_rules_error_categorization(self):
        """Test that errors are properly categorized."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == ",  # Syntax error
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
            MappingRule(
                rule_id="R-002",
                condition="invalid_field == 'value'",  # Invalid field reference
                old_type="OL",
                account_code="A1",
                priority=2,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(valid_rules) == 0
        assert len(errors) == 2

        error_types = {e.error_type for e in errors}
        assert "syntax_error" in error_types
        assert "invalid_field_reference" in error_types

    def test_validate_rules_rule_ids_in_errors(self):
        """Test that rule IDs are included in error messages."""
        validator = MappingRuleValidator()

        rules = [
            MappingRule(
                rule_id="R-001",
                condition="old_type == ",  # Syntax error
                old_type="OL",
                account_code="A1",
                priority=1,
            ),
        ]

        valid_rules, errors = validator.validate_rules(rules)

        assert len(errors) == 1
        assert errors[0].entry_id == "R-001"
        assert "R-001" in str(errors[0])








