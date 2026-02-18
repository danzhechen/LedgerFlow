"""Unit tests for MappingRuleReader."""

from pathlib import Path

import pandas as pd
import pytest

from veritas_accounting.excel.rule_reader import MappingRuleReader
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.utils.exceptions import ExcelIOError
from veritas_accounting.validation.input_validator import ValidationError


class TestMappingRuleReader:
    """Test cases for MappingRuleReader."""

    def test_read_valid_rules_from_dataframe(self) -> None:
        """Test reading valid mapping rules from DataFrame."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001", "R-002"],
                "condition": [
                    "old_type == 'OL'",
                    "old_type == 'OL' and year == 2024",
                ],
                "old_type": ["OL", "OL"],
                "account_code": ["A1", "A2"],
                "priority": [1, 2],
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 2
        assert len(errors) == 0
        assert all(isinstance(r, MappingRule) for r in rules)
        assert rules[0].rule_id == "R-001"
        assert rules[1].rule_id == "R-002"

    def test_read_rules_with_optional_fields(self) -> None:
        """Test reading rules with optional fields."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "old_type": ["OL"],
                "new_type": ["NEW"],
                "account_code": ["A1"],
                "priority": [1],
                "description": ["Test rule description"],
                "generates_multiple": [False],
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].new_type == "NEW"
        assert rules[0].description == "Test rule description"
        assert rules[0].generates_multiple is False

    def test_missing_required_column(self) -> None:
        """Test error when required column is missing."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                # Missing: account_code, priority
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) > 0
        assert any(e.error_type == "missing_column" for e in errors)
        assert any("account_code" in str(e) or "priority" in str(e) for e in errors)

    def test_invalid_priority_type(self) -> None:
        """Test validation error for invalid priority type."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": ["not a number"],  # Invalid type
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) > 0
        assert any("priority" in str(e).lower() for e in errors)

    def test_invalid_priority_range(self) -> None:
        """Test validation error for priority out of range."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [0],  # Too low (must be >= 1)
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) > 0
        assert any("priority" in str(e).lower() for e in errors)

    def test_empty_condition(self) -> None:
        """Test validation error for empty condition."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": [""],  # Empty condition
                "account_code": ["A1"],
                "priority": [1],
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) > 0
        assert any("condition" in str(e).lower() for e in errors)

    def test_chinese_text_support(self) -> None:
        """Test that Chinese text is supported in rule descriptions."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "description": ["测试规则描述"],  # Chinese text
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].description == "测试规则描述"

    def test_generates_multiple_flag(self) -> None:
        """Test generates_multiple flag parsing."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "generates_multiple": [True],
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].generates_multiple is True

    def test_generates_multiple_string_parsing(self) -> None:
        """Test generates_multiple flag parsing from string."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "generates_multiple": ["true"],  # String "true"
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].generates_multiple is True

    def test_complex_condition_expression(self) -> None:
        """Test reading rules with complex condition expressions."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": [
                    "old_type == 'OL' and year == 2024 and amount > 1000"
                ],
                "account_code": ["A1"],
                "priority": [1],
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert "old_type == 'OL' and year == 2024 and amount > 1000" in rules[
            0
        ].condition

    def test_multiple_errors_per_row(self) -> None:
        """Test that multiple errors are collected for a single row."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": [""],  # Empty rule_id
                "condition": [""],  # Empty condition
                "account_code": ["A1"],
                "priority": [0],  # Invalid priority
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) >= 2  # Should have multiple errors

    def test_optional_fields_none(self) -> None:
        """Test that optional fields can be None."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "old_type": [None],  # Optional field as None
                "new_type": [None],  # Optional field as None
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].old_type is None
        assert rules[0].new_type is None

    def test_empty_dataframe(self) -> None:
        """Test reading from empty DataFrame."""
        reader = MappingRuleReader()
        df = pd.DataFrame()

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 0
        assert len(errors) > 0  # Should have missing column errors

    def test_rule_priority_ordering(self) -> None:
        """Test that rules maintain priority information."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001", "R-002", "R-003"],
                "condition": [
                    "old_type == 'OL'",
                    "old_type == 'OL'",
                    "old_type == 'OL'",
                ],
                "account_code": ["A1", "A2", "A3"],
                "priority": [3, 1, 2],  # Different priorities
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 3
        assert len(errors) == 0
        # Verify priorities are preserved
        priorities = [r.priority for r in rules]
        assert priorities == [3, 1, 2]

    def test_one_to_many_mapping_flag(self) -> None:
        """Test one-to-many mapping flag (generates_multiple)."""
        reader = MappingRuleReader()
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "generates_multiple": [True],  # One-to-many mapping
            }
        )

        rules, errors = reader.read_rules_from_dataframe(df)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].generates_multiple is True








