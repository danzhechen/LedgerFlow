"""Mapping rules Excel reader for veritas-accounting."""

from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pydantic import ValidationError as PydanticValidationError

from veritas_accounting.excel.reader import ExcelReader
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.utils.exceptions import ExcelIOError


class MappingRuleReader:
    """
    Reads mapping rules from Excel files.

    Parses Excel files containing mapping rules and converts them to MappingRule models.
    """

    # Expected columns for mapping rules (flexible - some may be optional)
    EXPECTED_COLUMNS = {
        "rule_id",
        "condition",
        "account_code",
        "priority",
    }
    OPTIONAL_COLUMNS = {
        "old_type",
        "new_type",
        "description",
        "generates_multiple",
    }

    def __init__(self) -> None:
        """Initialize MappingRuleReader."""
        self.excel_reader = ExcelReader()

    def read_rules(
        self,
        file_path: str | Path,
        sheet_name: Optional[str] = None,
    ) -> tuple[list[MappingRule], list["ValidationError"]]:
        """
        Read mapping rules from an Excel file.

        Args:
            file_path: Path to the Excel file containing mapping rules
            sheet_name: Name of the worksheet containing rules. If None, uses first sheet.

        Returns:
            Tuple of (rules, errors) where:
            - rules: List of validated MappingRule objects
            - errors: List of ValidationError objects for invalid rules
            
        Note: ValidationError is imported locally to avoid circular imports.

        Raises:
            ExcelIOError: If file cannot be read
        """
        # Import here to avoid circular import
        from veritas_accounting.validation.input_validator import ValidationError
        
        file_path = Path(file_path)

        # Read Excel file
        try:
            if sheet_name:
                df = self.excel_reader.read_sheet(file_path, sheet_name)
            else:
                df = self.excel_reader.read_file(file_path)
        except ExcelIOError:
            raise
        except Exception as e:
            raise ExcelIOError(
                f"Failed to read mapping rules file: {file_path}. Error: {e}"
            ) from e

        # Validate and parse rules
        return self._parse_rules(df)

    def _parse_rules(
        self, df: pd.DataFrame
    ) -> tuple[list[MappingRule], list["ValidationError"]]:
        """
        Parse DataFrame into MappingRule objects.

        Args:
            df: DataFrame containing mapping rule data

        Returns:
            Tuple of (rules, errors)
        """
        # Import here to avoid circular import
        from veritas_accounting.validation.input_validator import ValidationError
        
        rules: list[MappingRule] = []
        errors: list[ValidationError] = []

        # Check for required columns
        missing_required = self.EXPECTED_COLUMNS - set(df.columns)
        if missing_required:
            for col in missing_required:
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name=col,
                        error_type="missing_column",
                        error_message=f"Required column '{col}' is missing",
                        actual_value=None,
                    )
                )
            # Can't proceed without required columns
            return rules, errors

        # Parse each row
        for idx, row in df.iterrows():
            row_number = idx + 2  # +2 for 0-indexed + header row
            row_errors: list[ValidationError] = []

            try:
                # Convert row to dict, handling NaN values
                row_dict = self._row_to_dict(row)

                # Extract rule_id for error reporting
                rule_id = str(row_dict.get("rule_id", f"ROW-{row_number}"))

                # Handle generates_multiple (may be boolean string or boolean)
                if "generates_multiple" in row_dict:
                    generates_multiple = row_dict["generates_multiple"]
                    if isinstance(generates_multiple, str):
                        generates_multiple = generates_multiple.lower() in (
                            "true",
                            "yes",
                            "1",
                            "y",
                        )
                    row_dict["generates_multiple"] = bool(generates_multiple)

                # Create MappingRule (Pydantic validates types and values)
                rule = MappingRule(**row_dict)
                rules.append(rule)

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
                            entry_id=rule_id if "rule_id" in locals() else None,
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
                    )
                )

            errors.extend(row_errors)

        return rules, errors

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
                # Only set None for optional columns, skip required columns (will fail validation)
                if col in self.OPTIONAL_COLUMNS:
                    row_dict[col] = None
            else:
                row_dict[col] = value
        return row_dict

    def read_rules_from_dataframe(
        self, df: pd.DataFrame
    ) -> tuple[list[MappingRule], list["ValidationError"]]:
        """
        Read mapping rules directly from a DataFrame.

        Useful when rules are already loaded into a DataFrame.

        Args:
            df: DataFrame containing mapping rule data

        Returns:
            Tuple of (rules, errors)
        """
        return self._parse_rules(df)
