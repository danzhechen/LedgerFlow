"""Unit tests for rule engine (RuleEvaluator)."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.engine import RuleEvaluator
from veritas_accounting.utils.exceptions import RuleError


class TestRuleEvaluator:
    """Test cases for RuleEvaluator."""

    def test_simple_condition_match(self) -> None:
        """Test evaluating a simple condition that matches."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is True
        assert error is None

    def test_simple_condition_no_match(self) -> None:
        """Test evaluating a simple condition that doesn't match."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OTHER",  # Different type
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is False
        assert error is None

    def test_complex_condition_and(self) -> None:
        """Test evaluating a complex condition with AND."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-002",
            condition="old_type == 'OL' and year == 2024",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is True
        assert error is None

    def test_complex_condition_or(self) -> None:
        """Test evaluating a complex condition with OR."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-003",
            condition="old_type == 'OL' or old_type == 'OTHER'",
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OTHER",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is True
        assert error is None

    def test_comparison_operators(self) -> None:
        """Test comparison operators (>, <, >=, <=)."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-004",
            condition="amount > 1000",
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("2000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is True
        assert error is None

    def test_invalid_rule_syntax(self) -> None:
        """Test handling of invalid rule syntax."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-005",
            condition="invalid syntax !!!",  # Invalid syntax
            account_code="A1",
            priority=1,
        )
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        matches, error = evaluator.evaluate(rule, entry)

        assert matches is False
        assert error is not None
        assert "Error evaluating rule" in error

    def test_rule_compilation_caching(self) -> None:
        """Test that rules are compiled and cached."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-006",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )

        # First evaluation should compile
        entry1 = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )
        matches1, _ = evaluator.evaluate(rule, entry1)

        # Second evaluation should use cached compiled rule
        entry2 = JournalEntry(
            entry_id="JE-002",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("2000"),
            date=datetime(2024, 1, 15),
        )
        matches2, _ = evaluator.evaluate(rule, entry2)

        assert matches1 is True
        assert matches2 is True

    def test_compile_rules_validation(self) -> None:
        """Test compile_rules method for early validation."""
        evaluator = RuleEvaluator()
        valid_rule = MappingRule(
            rule_id="R-007",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        invalid_rule = MappingRule(
            rule_id="R-008",
            condition="invalid !!!",  # Invalid syntax
            account_code="A1",
            priority=1,
        )

        errors = evaluator.compile_rules([valid_rule, invalid_rule])

        assert "R-007" not in errors  # Valid rule has no error
        assert "R-008" in errors  # Invalid rule has error

    def test_clear_cache(self) -> None:
        """Test clearing the compiled rules cache."""
        evaluator = RuleEvaluator()
        rule = MappingRule(
            rule_id="R-009",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )

        # Compile a rule
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )
        evaluator.evaluate(rule, entry)

        # Clear cache
        evaluator.clear_cache()

        # Cache should be empty (can't directly test, but verify it still works)
        matches, _ = evaluator.evaluate(rule, entry)
        assert matches is True








