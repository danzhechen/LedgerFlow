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

                # Extract ledger_type if present (for CR/DR tracking)
                # Remove it from row_dict BEFORE creating MappingRule to avoid Pydantic errors
                ledger_type = row_dict.pop("ledger_type", None) if "ledger_type" in row_dict else None
                
                # Also remove any other unexpected fields that might cause issues
                # Keep only fields that MappingRule expects
                expected_fields = {
                    "rule_id", "condition", "account_code", "priority",
                    "old_type", "new_type", "description", "generates_multiple"
                }
                # Explicitly filter to only expected fields
                rule_dict = {}
                for k, v in row_dict.items():
                    if k in expected_fields:
                        rule_dict[k] = v
                
                # Double-check: ledger_type should NOT be in rule_dict
                if "ledger_type" in rule_dict:
                    raise ValueError(f"ledger_type should not be in rule_dict! Keys: {list(rule_dict.keys())}")
                
                # Create MappingRule (Pydantic validates types and values)
                rule = MappingRule(**rule_dict)
                
                # Attach ledger_type as attribute (not part of Pydantic model)
                if ledger_type:
                    rule.ledger_type = ledger_type
                
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
                # Check if this is actually a Pydantic error that wasn't caught
                error_msg = str(e)
                if "no field" in error_msg.lower() and "ledger_type" in error_msg:
                    # This is a Pydantic error about ledger_type - it means the field is still in the dict
                    # This shouldn't happen if filtering worked, so log the actual dict keys
                    error_dict = rule_dict if 'rule_dict' in locals() else row_dict
                    error_msg = f"Pydantic error: {error_msg}. Dict keys were: {list(error_dict.keys())}"
                
                # Use rule_dict if available, otherwise use row dict (but filter out ledger_type)
                error_dict = rule_dict if 'rule_dict' in locals() else {k: v for k, v in row_dict.items() if k != 'ledger_type'}
                row_errors.append(
                    ValidationError(
                        row_number=row_number,
                        field_name="general",
                        error_type="unexpected_error",
                        error_message=error_msg,
                        actual_value=str(error_dict),
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

    def read_rules_from_journal_to_ledger(
        self, file_path: str | Path
    ) -> tuple[list[MappingRule], list["ValidationError"]]:
        """
        Read mapping rules from 账目分类明细.xlsx sheet "journal_to_ledger".

        OLD section: year, type, cr_ledger, dr_ledger.
        NEW section: type.1, cr_ledger.1, dr_ledger.1.
        When multiple rows exist for (year, type), use 摘要 (description): column Unnamed: 12
        is used as a keyword; rules with a keyword get higher priority and condition
        includes ` and "keyword" in description`.

        Returns:
            Tuple of (rules, errors). Rules are suitable for RuleApplicator (CR/DR pairs).
        """
        from veritas_accounting.validation.input_validator import ValidationError

        file_path = Path(file_path)
        errors: list["ValidationError"] = []
        rules: list[MappingRule] = []

        try:
            df = pd.read_excel(file_path, sheet_name="journal_to_ledger", header=1)
        except Exception as e:
            raise ExcelIOError(
                f"Failed to read journal_to_ledger from {file_path}. Error: {e}"
            ) from e

        required = {"year", "type", "type.1", "cr_ledger.1", "dr_ledger.1"}
        if not required.issubset(df.columns):
            missing = required - set(df.columns)
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name=",".join(missing),
                    error_type="missing_column",
                    error_message=f"journal_to_ledger missing columns: {missing}",
                    actual_value=None,
                )
            )
            return rules, errors

        desc_keyword_col = "Unnamed: 12" if "Unnamed: 12" in df.columns else None
        base_priority = 10
        keyword_priority = 20
        seen_default: set[tuple[int, str]] = set()

        for idx, row in df.iterrows():
            try:
                year_val = row.get("year")
                old_type = row.get("type")
                new_type = row.get("type.1")
                cr_ledger = row.get("cr_ledger.1")
                dr_ledger = row.get("dr_ledger.1")
                if pd.isna(year_val) or pd.isna(old_type) or pd.isna(cr_ledger) or pd.isna(dr_ledger):
                    continue
                if str(new_type).strip() == "/" or (pd.isna(new_type) and str(cr_ledger).strip() == "/"):
                    continue
                year_int = int(float(year_val))
                old_str = str(old_type).strip()
                cr_str = str(cr_ledger).strip()
                dr_str = str(dr_ledger).strip()
                if not cr_str or not dr_str:
                    continue

                keyword = None
                if desc_keyword_col and desc_keyword_col in row.index:
                    v = row.get(desc_keyword_col)
                    if v is not None and not pd.isna(v) and str(v).strip():
                        keyword = str(v).strip()

                if not keyword:
                    key = (year_int, old_str)
                    if key in seen_default:
                        continue
                    seen_default.add(key)

                condition = f'old_type == "{old_str}" and year == {year_int}'
                if keyword:
                    condition += f' and "{keyword}" in description'
                priority = keyword_priority if keyword else base_priority

                rule_id_base = f"JTL-{idx+2}"
                cr_rule = MappingRule(
                    rule_id=f"{rule_id_base}-CR",
                    condition=condition,
                    account_code=cr_str,
                    priority=priority,
                    old_type=old_str,
                    new_type=str(new_type).strip() if pd.notna(new_type) else None,
                    description=f"From journal_to_ledger: {old_str} -> CR {cr_str}",
                )
                cr_rule.ledger_type = "CR"
                dr_rule = MappingRule(
                    rule_id=f"{rule_id_base}-DR",
                    condition=condition,
                    account_code=dr_str,
                    priority=priority,
                    old_type=old_str,
                    new_type=str(new_type).strip() if pd.notna(new_type) else None,
                    description=f"From journal_to_ledger: {old_str} -> DR {dr_str}",
                )
                dr_rule.ledger_type = "DR"
                rules.append(cr_rule)
                rules.append(dr_rule)
            except Exception as e:
                errors.append(
                    ValidationError(
                        row_number=idx + 2,
                        field_name="journal_to_ledger",
                        error_type="parse_error",
                        error_message=str(e),
                        actual_value=str(row.to_dict()),
                    )
                )

        return rules, errors
