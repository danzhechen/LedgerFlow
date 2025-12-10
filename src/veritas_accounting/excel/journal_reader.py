"""Journal entry Excel reader for veritas-accounting."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from veritas_accounting.excel.reader import ExcelReader
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.utils.exceptions import ExcelIOError, ValidationError


class JournalEntryReader:
    """
    Reads journal entries from Excel files and parses them into JournalEntry models.

    Handles column mapping, date parsing, empty rows, and validation errors.
    """

    # Default column mappings (can be customized)
    DEFAULT_COLUMN_MAPPING = {
        "year": ["year", "Year", "YEAR", "年份"],
        "description": ["description", "Description", "DESCRIPTION", "描述", "说明"],
        "old_type": ["old_type", "Old Type", "OLD_TYPE", "type", "Type", "TYPE", "类型"],
        "amount": ["amount", "Amount", "AMOUNT", "金额"],
        "date": ["date", "Date", "DATE", "日期"],
        "entry_id": ["entry_id", "Entry ID", "ENTRY_ID", "id", "ID", "编号"],
        "quarter": ["quarter", "Quarter", "QUARTER", "季度"],
        "notes": ["notes", "Notes", "NOTES", "备注"],
    }

    def __init__(
        self,
        column_mapping: Optional[dict[str, list[str]]] = None,
        sheet_name: Optional[str] = None,
    ):
        """
        Initialize the journal entry reader.

        Args:
            column_mapping: Custom column mapping dictionary. If None, uses default mapping.
            sheet_name: Name of the worksheet to read. If None, reads the first sheet.
        """
        self.excel_reader = ExcelReader()
        self.column_mapping = column_mapping or self.DEFAULT_COLUMN_MAPPING
        self.sheet_name = sheet_name

    def _find_column(
        self, df: pd.DataFrame, field_name: str, possible_names: list[str]
    ) -> Optional[str]:
        """
        Find the actual column name in DataFrame that matches one of the possible names.

        Args:
            df: DataFrame to search
            field_name: Name of the field we're looking for
            possible_names: List of possible column names to match

        Returns:
            Actual column name if found, None otherwise
        """
        # Normalize column names (strip whitespace, case-insensitive)
        df_columns_lower = {col.strip().lower(): col for col in df.columns}
        possible_names_lower = [name.strip().lower() for name in possible_names]

        for possible_name in possible_names_lower:
            if possible_name in df_columns_lower:
                return df_columns_lower[possible_name]

        return None

    def _map_columns(self, df: pd.DataFrame) -> dict[str, Optional[str]]:
        """
        Map DataFrame columns to JournalEntry model fields.

        Args:
            df: DataFrame with journal entry data

        Returns:
            Dictionary mapping field names to column names (or None if not found)

        Raises:
            ValidationError: If required columns are missing
        """
        mapping = {}
        missing_required = []

        # Required fields
        required_fields = ["entry_id", "year", "description", "old_type", "amount", "date"]
        optional_fields = ["quarter", "notes"]

        # Map required fields
        for field in required_fields:
            possible_names = self.column_mapping.get(field, [field])
            column_name = self._find_column(df, field, possible_names)
            if column_name is None:
                missing_required.append(field)
            mapping[field] = column_name

        # Check for missing required columns
        if missing_required:
            available_columns = ", ".join(df.columns.tolist())
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_required)}. "
                f"Available columns: {available_columns}"
            )

        # Map optional fields
        for field in optional_fields:
            possible_names = self.column_mapping.get(field, [field])
            column_name = self._find_column(df, field, possible_names)
            mapping[field] = column_name

        return mapping

    def _parse_date(self, value) -> Optional[datetime]:
        """
        Parse date value using pandas to_datetime with multiple format attempts.

        Args:
            value: Date value (string, datetime, or pandas Timestamp)

        Returns:
            datetime object or None if parsing fails
        """
        if pd.isna(value):
            return None

        # If already a datetime, return it
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        if isinstance(value, datetime):
            return value

        # Try pandas to_datetime (handles many formats automatically)
        try:
            dt = pd.to_datetime(value, errors="raise")
            return dt.to_pydatetime()
        except (ValueError, TypeError):
            return None

    def _parse_row(
        self, row: pd.Series, column_mapping: dict[str, Optional[str]], row_index: int
    ) -> tuple[Optional[JournalEntry], Optional[ValidationError]]:
        """
        Parse a single row into a JournalEntry model.

        Args:
            row: pandas Series representing a row
            column_mapping: Dictionary mapping field names to column names
            row_index: Row index (0-based, for error reporting)

        Returns:
            Tuple of (JournalEntry or None, ValidationError or None)
        """
        try:
            # Extract values using column mapping
            data = {}
            for field, column_name in column_mapping.items():
                if column_name is None:
                    # Optional field not found, skip
                    continue

                value = row.get(column_name)

                # Handle NaN/None values
                if pd.isna(value):
                    if field in ["entry_id", "year", "description", "old_type", "amount", "date"]:
                        # Required field is missing
                        return None, ValidationError(
                            f"Row {row_index + 1}: Missing required field '{field}' "
                            f"(column: {column_name})"
                        )
                    # Optional field, set to None
                    data[field] = None
                    continue

                # Process value based on field type
                if field == "date":
                    parsed_date = self._parse_date(value)
                    if parsed_date is None:
                        return None, ValidationError(
                            f"Row {row_index + 1}: Invalid date format in column '{column_name}': {value}"
                        )
                    data[field] = parsed_date
                elif field == "year":
                    try:
                        data[field] = int(float(value))  # Handle float years like 2024.0
                    except (ValueError, TypeError):
                        return None, ValidationError(
                            f"Row {row_index + 1}: Invalid year in column '{column_name}': {value}"
                        )
                elif field == "amount":
                    try:
                        data[field] = float(value)
                    except (ValueError, TypeError):
                        return None, ValidationError(
                            f"Row {row_index + 1}: Invalid amount in column '{column_name}': {value}"
                        )
                elif field == "quarter":
                    try:
                        data[field] = int(float(value)) if value is not None else None
                    except (ValueError, TypeError):
                        return None, ValidationError(
                            f"Row {row_index + 1}: Invalid quarter in column '{column_name}': {value}"
                        )
                else:
                    # String fields (description, old_type, entry_id, notes)
                    data[field] = str(value).strip()

            # Create JournalEntry model (Pydantic will validate)
            entry = JournalEntry(**data)
            return entry, None

        except PydanticValidationError as e:
            # Pydantic validation errors
            error_messages = []
            for error in e.errors():
                field = error.get("loc", ("unknown",))[0]
                msg = error.get("msg", "Validation error")
                error_messages.append(f"{field}: {msg}")
            return None, ValidationError(
                f"Row {row_index + 1}: Validation error - {'; '.join(error_messages)}"
            )
        except Exception as e:
            return None, ValidationError(f"Row {row_index + 1}: Unexpected error: {str(e)}")

    def read_journal_entries(
        self, file_path: str | Path
    ) -> tuple[list[JournalEntry], list[ValidationError]]:
        """
        Read journal entries from an Excel file.

        Args:
            file_path: Path to the Excel file containing journal entries

        Returns:
            Tuple of (list of JournalEntry objects, list of ValidationError objects)

        Raises:
            ExcelIOError: If file cannot be read
            ValidationError: If required columns are missing
        """
        file_path = Path(file_path)

        # Read Excel file using ExcelReader
        try:
            if self.sheet_name:
                df = self.excel_reader.read_sheet(file_path, self.sheet_name)
            else:
                df = self.excel_reader.read_file(file_path)
        except ExcelIOError:
            raise
        except Exception as e:
            raise ExcelIOError(f"Error reading Excel file: {file_path}. {str(e)}")

        # Check if DataFrame is completely empty (no columns at all)
        if len(df.columns) == 0:
            # Completely empty file (no columns) - return empty results
            return [], []

        # Map columns to fields (check even if DataFrame has no rows)
        try:
            column_mapping = self._map_columns(df)
        except ValidationError:
            raise

        # Check if DataFrame has no data rows (but has valid columns)
        if df.empty:
            return [], []

        # Parse rows into JournalEntry models
        entries = []
        errors = []

        for idx, row in df.iterrows():
            # Skip completely empty rows
            if row.isna().all():
                continue

            entry, error = self._parse_row(row, column_mapping, idx)
            if entry is not None:
                entries.append(entry)
            if error is not None:
                errors.append(error)

        return entries, errors
