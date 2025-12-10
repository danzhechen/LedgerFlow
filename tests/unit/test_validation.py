"""Unit tests for validation module."""

from datetime import datetime
from decimal import Decimal

import pandas as pd
import pytest

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.validation.input_validator import (
    JournalEntryValidator,
    ValidationError,
)


class TestJournalEntryValidator:
    """Test cases for JournalEntryValidator."""

    def test_valid_entries(self) -> None:
        """Test validation of valid journal entries."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001", "JE-002"],
                "year": [2024, 2024],
                "description": ["Test 1", "Test 2"],
                "old_type": ["OL", "OL"],
                "amount": [1000.50, 2000.00],
                "date": ["2024-01-15", "2024-01-16"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 2
        assert len(errors) == 0
        assert all(isinstance(e, JournalEntry) for e in valid_entries)

    def test_missing_required_column(self) -> None:
        """Test validation error when required column is missing."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["Test"],
                # Missing: old_type, amount, date
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any(e.error_type == "missing_column" for e in errors)
        assert any("old_type" in str(e) or "amount" in str(e) or "date" in str(e) for e in errors)

    def test_invalid_year_type(self) -> None:
        """Test validation error for invalid year type."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": ["not a number"],  # Invalid type
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any("year" in str(e).lower() for e in errors)

    def test_invalid_year_range(self) -> None:
        """Test validation error for year out of range."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [1999],  # Too low
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any("year" in str(e).lower() for e in errors)

    def test_invalid_amount_format(self) -> None:
        """Test validation error for invalid amount format."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": ["not a number"],  # Invalid format
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any("amount" in str(e).lower() for e in errors)

    def test_invalid_date_format(self) -> None:
        """Test validation error for invalid date format."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["invalid-date"],  # Invalid format
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any("date" in str(e).lower() for e in errors)

    def test_null_required_field(self) -> None:
        """Test validation error for null required field."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": [None],  # Null value
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0
        assert any("description" in str(e).lower() for e in errors)

    def test_duplicate_entries(self) -> None:
        """Test validation error for duplicate entries."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001", "JE-002"],
                "year": [2024, 2024],
                "description": ["Test", "Test"],  # Same description
                "old_type": ["OL", "OL"],
                "amount": [1000, 1000],  # Same amount
                "date": ["2024-01-15", "2024-01-15"],  # Same date
            }
        )

        valid_entries, errors = validator.validate(df)

        # Entries are parsed but marked as duplicates
        assert len(valid_entries) == 2
        assert len(errors) > 0
        assert any(e.error_type == "duplicate_entry" for e in errors)

    def test_chinese_text_support(self) -> None:
        """Test that Chinese text is supported in validation."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["测试条目"],  # Chinese text
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 1
        assert len(errors) == 0
        assert valid_entries[0].description == "测试条目"

    def test_multiple_errors_per_row(self) -> None:
        """Test that multiple errors are collected for a single row."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [1999],  # Invalid year
                "description": [None],  # Null description
                "old_type": ["OL"],
                "amount": ["invalid"],  # Invalid amount
                "date": ["invalid-date"],  # Invalid date
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) >= 3  # Should have multiple errors

    def test_optional_fields(self) -> None:
        """Test that optional fields (quarter, notes) work correctly."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
                "quarter": [1],  # Optional field
                "notes": ["Some notes"],  # Optional field
            }
        )

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 1
        assert len(errors) == 0
        assert valid_entries[0].quarter == 1
        assert valid_entries[0].notes == "Some notes"

    def test_custom_entry_id_column(self) -> None:
        """Test validation with custom entry_id column name."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "id": ["JE-001"],  # Custom column name
                "year": [2024],
                "description": ["Test"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )

        valid_entries, errors = validator.validate(df, entry_id_column="id")

        assert len(valid_entries) == 1
        assert len(errors) == 0

    def test_validate_required_fields_populated(self) -> None:
        """Test validate_required_fields_populated method."""
        validator = JournalEntryValidator()
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001", "JE-002"],
                "year": [2024, None],  # Null value
                "description": ["Test", "Test"],
                "old_type": ["OL", None],  # Null value
                "amount": [1000, 2000],
                "date": ["2024-01-15", "2024-01-16"],
            }
        )

        errors = validator.validate_required_fields_populated(df)

        assert len(errors) > 0
        assert any("year" in str(e).lower() for e in errors)
        assert any("old_type" in str(e).lower() for e in errors)

    def test_empty_dataframe(self) -> None:
        """Test validation of empty DataFrame."""
        validator = JournalEntryValidator()
        df = pd.DataFrame()

        valid_entries, errors = validator.validate(df)

        assert len(valid_entries) == 0
        assert len(errors) > 0  # Should have missing column errors

    def test_validation_error_str_representation(self) -> None:
        """Test ValidationError string representation."""
        error = ValidationError(
            row_number=5,
            field_name="amount",
            error_type="invalid_type",
            error_message="Expected number, got string",
            actual_value="not a number",
            entry_id="JE-001",
        )

        error_str = str(error)
        assert "Row 5" in error_str
        assert "amount" in error_str
        assert "JE-001" in error_str
        assert "not a number" in error_str
