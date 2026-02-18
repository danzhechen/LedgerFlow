"""Input data validation for veritas-accounting."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from veritas_accounting.models.journal import JournalEntry


@dataclass
class ValidationError:
    """
    Structured validation error information.

    Represents a single validation error with context for easy fixing.
    """

    row_number: int
    field_name: str
    error_type: str
    error_message: str
    actual_value: Any
    entry_id: str | None = None

    def __str__(self) -> str:
        """Return human-readable error message."""
        entry_info = f" (entry_id: {self.entry_id})" if self.entry_id else ""
        return (
            f"Row {self.row_number}{entry_info}, Field '{self.field_name}': "
            f"{self.error_message} (got: {self.actual_value})"
        )


class JournalEntryValidator:
    """
    Validates journal entries from Excel data.

    Performs structure, type, value, and uniqueness validation.
    """

    # Required columns for journal entries
    REQUIRED_COLUMNS = {"year", "description", "old_type", "amount", "date"}

    def __init__(self) -> None:
        """Initialize JournalEntryValidator."""
        pass

    def validate(
        self, df: pd.DataFrame, entry_id_column: str = "entry_id"
    ) -> tuple[list[JournalEntry], list[ValidationError]]:
        """
        Validate journal entries from a DataFrame.

        Args:
            df: DataFrame containing journal entry data
            entry_id_column: Name of the column containing entry IDs (default: "entry_id")

        Returns:
            Tuple of (valid_entries, errors) where:
            - valid_entries: List of validated JournalEntry objects
            - errors: List of ValidationError objects
        """
        errors: list[ValidationError] = []
        valid_entries: list[JournalEntry] = []

        # Check structure: required columns present
        structure_errors = self._validate_structure(df)
        errors.extend(structure_errors)

        # If structure is invalid, we can't proceed with type/value validation
        if structure_errors:
            return valid_entries, errors

        # Validate each row
        for idx, row in df.iterrows():
            row_number = idx + 2  # +2 because: 0-indexed + 1 for header row
            row_errors: list[ValidationError] = []

            # Get entry_id if present
            entry_id = str(row.get(entry_id_column, f"ROW-{row_number}"))

            # Try to create JournalEntry (this validates types and values via Pydantic)
            try:
                # Convert row to dict, handling NaN values
                row_dict = self._row_to_dict(row)

                # Map custom entry_id column to model field name
                if entry_id_column != "entry_id" and entry_id_column in row_dict:
                    row_dict["entry_id"] = row_dict.pop(entry_id_column)

                # Always derive year from date when date is present so year and date stay in sync
                if "date" in row_dict and row_dict["date"] is not None:
                    row_dict["year"] = row_dict["date"].year
                elif row_dict.get("year") is None:
                    from datetime import datetime
                    row_dict["year"] = datetime.now().year

                # Create JournalEntry (Pydantic validates types and values)
                entry = JournalEntry(**row_dict)
                valid_entries.append(entry)

            except PydanticValidationError as e:
                # Extract validation errors from Pydantic
                for error in e.errors():
                    field_name = ".".join(str(loc) for loc in error.get("loc", []))
                    if not field_name:
                        field_name = "unknown"

                    error_type = error.get("type", "validation_error")
                    error_msg = error.get("msg", "Validation failed")
                    actual_value = row.get(field_name, "N/A")

                    row_errors.append(
                        ValidationError(
                            row_number=row_number,
                            field_name=field_name,
                            error_type=error_type,
                            error_message=error_msg,
                            actual_value=actual_value,
                            entry_id=entry_id,
                        )
                    )

            except Exception as e:
                # Catch any other unexpected errors
                row_errors.append(
                    ValidationError(
                        row_number=row_number,
                        field_name="general",
                        error_type="unexpected_error",
                        error_message=f"Unexpected error: {str(e)}",
                        actual_value=str(row.to_dict()),
                        entry_id=entry_id,
                    )
                )

            errors.extend(row_errors)

        # Check for duplicates (after successful parsing)
        if valid_entries:
            duplicate_errors = self._validate_uniqueness(valid_entries)
            errors.extend(duplicate_errors)

        return valid_entries, errors

    def _validate_structure(self, df: pd.DataFrame) -> list[ValidationError]:
        """
        Validate that required columns are present.

        Args:
            df: DataFrame to validate

        Returns:
            List of ValidationError objects for missing columns
        """
        errors: list[ValidationError] = []
        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)

        for missing_col in missing_columns:
            errors.append(
                ValidationError(
                    row_number=0,  # Structure error, not row-specific
                    field_name=missing_col,
                    error_type="missing_column",
                    error_message=f"Required column '{missing_col}' is missing",
                    actual_value=None,
                )
            )

        return errors

    def _row_to_dict(self, row: pd.Series) -> dict[str, Any]:
        """
        Convert pandas Series row to dictionary, handling NaN values.

        Args:
            row: pandas Series row

        Returns:
            Dictionary with None for NaN values
        """
        row_dict: dict[str, Any] = {}
        for col, value in row.items():
            # Convert NaN/NaT to None
            if pd.isna(value):
                row_dict[col] = None
            else:
                row_dict[col] = value
        return row_dict

    def _validate_uniqueness(
        self, entries: list[JournalEntry]
    ) -> list[ValidationError]:
        """
        Validate that there are no duplicate entries.

        Uses composite key: (year, description, date, amount) to identify duplicates.

        Args:
            entries: List of validated JournalEntry objects

        Returns:
            List of ValidationError objects for duplicate entries
        """
        errors: list[ValidationError] = []
        seen: dict[tuple[int, str, datetime, Decimal], list[JournalEntry]] = {}

        # Group entries by composite key
        for entry in entries:
            key = (entry.year, entry.description, entry.date, entry.amount)
            if key not in seen:
                seen[key] = []
            seen[key].append(entry)

        # Find duplicates
        for key, duplicate_entries in seen.items():
            if len(duplicate_entries) > 1:
                # All entries with this key are duplicates
                for entry in duplicate_entries:
                    errors.append(
                        ValidationError(
                            row_number=0,  # Row number not available after parsing
                            field_name="composite_key",
                            error_type="duplicate_entry",
                            error_message=(
                                f"Duplicate entry found. "
                                f"Same (year, description, date, amount) as other entries: "
                                f"{[e.entry_id for e in duplicate_entries if e.entry_id != entry.entry_id]}"
                            ),
                            actual_value=f"year={entry.year}, description={entry.description}, "
                            f"date={entry.date}, amount={entry.amount}",
                            entry_id=entry.entry_id,
                        )
                    )

        return errors

    def validate_required_fields_populated(
        self, df: pd.DataFrame
    ) -> list[ValidationError]:
        """
        Validate that required fields are not null/empty.

        Args:
            df: DataFrame to validate

        Returns:
            List of ValidationError objects for null required fields
        """
        errors: list[ValidationError] = []

        # Check each required column for null values
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                continue  # Already reported as missing column

            null_rows = df[df[col].isna()]
            for idx in null_rows.index:
                row_number = idx + 2  # +2 for 0-indexed + header
                errors.append(
                    ValidationError(
                        row_number=row_number,
                        field_name=col,
                        error_type="null_value",
                        error_message=f"Required field '{col}' is null or empty",
                        actual_value=None,
                    )
                )

        return errors






