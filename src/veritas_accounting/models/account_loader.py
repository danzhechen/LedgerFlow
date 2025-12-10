"""Account hierarchy loading utilities for veritas-accounting."""

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from veritas_accounting.excel.reader import ExcelReader
from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.utils.exceptions import ExcelIOError, ValidationError


class AccountHierarchyLoader:
    """Loads account hierarchy from Excel files or configuration files."""

    def __init__(self) -> None:
        """Initialize AccountHierarchyLoader."""
        self.excel_reader = ExcelReader()

    def load_from_excel(
        self, file_path: str | Path, sheet_name: str | None = None
    ) -> AccountHierarchy:
        """
        Load account hierarchy from an Excel file.

        Args:
            file_path: Path to Excel file containing account hierarchy
            sheet_name: Name of worksheet containing accounts. If None, uses first sheet.

        Returns:
            AccountHierarchy object

        Raises:
            ExcelIOError: If file cannot be read
            ValidationError: If account data is invalid
        """
        file_path = Path(file_path)

        try:
            if sheet_name:
                df = self.excel_reader.read_sheet(file_path, sheet_name)
            else:
                df = self.excel_reader.read_file(file_path)
        except ExcelIOError:
            raise
        except Exception as e:
            raise ExcelIOError(
                f"Failed to read account hierarchy file: {file_path}. Error: {e}"
            ) from e

        # Parse DataFrame into Account objects
        accounts = self._parse_dataframe(df)
        return AccountHierarchy(accounts)

    def load_from_yaml(self, file_path: str | Path) -> AccountHierarchy:
        """
        Load account hierarchy from a YAML file.

        Args:
            file_path: Path to YAML file containing account hierarchy

        Returns:
            AccountHierarchy object

        Raises:
            ValidationError: If file cannot be read or data is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"Account hierarchy file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise ValidationError(
                f"Failed to read YAML file: {file_path}. Error: {e}"
            ) from e

        accounts = self._parse_yaml_data(data)
        return AccountHierarchy(accounts)

    def load_from_json(self, file_path: str | Path) -> AccountHierarchy:
        """
        Load account hierarchy from a JSON file.

        Args:
            file_path: Path to JSON file containing account hierarchy

        Returns:
            AccountHierarchy object

        Raises:
            ValidationError: If file cannot be read or data is invalid
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"Account hierarchy file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ValidationError(
                f"Failed to read JSON file: {file_path}. Error: {e}"
            ) from e

        accounts = self._parse_json_data(data)
        return AccountHierarchy(accounts)

    def _parse_dataframe(self, df: pd.DataFrame) -> list[Account]:
        """
        Parse DataFrame into Account objects.

        Args:
            df: DataFrame containing account data

        Returns:
            List of Account objects

        Raises:
            ValidationError: If required columns are missing or data is invalid
        """
        required_columns = {"code", "name", "level", "full_path"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValidationError(
                f"Missing required columns in account hierarchy: {', '.join(missing_columns)}"
            )

        accounts: list[Account] = []
        errors: list[str] = []

        for idx, row in df.iterrows():
            try:
                # Convert row to dict, handling NaN values
                row_dict: dict[str, Any] = {}
                for col in df.columns:
                    value = row.get(col)
                    if pd.isna(value):
                        row_dict[col] = None
                    else:
                        row_dict[col] = value

                # Create Account object
                account = Account(**row_dict)
                accounts.append(account)

            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")

        if errors:
            raise ValidationError(
                f"Errors parsing account hierarchy:\n" + "\n".join(errors)
            )

        return accounts

    def _parse_yaml_data(self, data: dict[str, Any] | list[dict[str, Any]]) -> list[Account]:
        """
        Parse YAML data into Account objects.

        Args:
            data: YAML data (dict or list of dicts)

        Returns:
            List of Account objects
        """
        if isinstance(data, dict):
            # If it's a dict, look for 'accounts' key
            if "accounts" in data:
                accounts_data = data["accounts"]
            else:
                # Assume the dict itself contains account data
                accounts_data = [data]
        else:
            accounts_data = data

        accounts: list[Account] = []
        for account_data in accounts_data:
            account = Account(**account_data)
            accounts.append(account)

        return accounts

    def _parse_json_data(self, data: dict[str, Any] | list[dict[str, Any]]) -> list[Account]:
        """
        Parse JSON data into Account objects.

        Args:
            data: JSON data (dict or list of dicts)

        Returns:
            List of Account objects
        """
        # Same logic as YAML parsing
        return self._parse_yaml_data(data)


def load_account_hierarchy(
    file_path: str | Path, file_type: str | None = None
) -> AccountHierarchy:
    """
    Convenience function to load account hierarchy from a file.

    Automatically detects file type based on extension if not specified.

    Args:
        file_path: Path to account hierarchy file
        file_type: File type ('excel', 'yaml', 'json'). If None, auto-detects from extension.

    Returns:
        AccountHierarchy object
    """
    file_path = Path(file_path)
    loader = AccountHierarchyLoader()

    # Auto-detect file type if not specified
    if file_type is None:
        ext = file_path.suffix.lower()
        if ext in [".xlsx", ".xls"]:
            file_type = "excel"
        elif ext in [".yaml", ".yml"]:
            file_type = "yaml"
        elif ext == ".json":
            file_type = "json"
        else:
            raise ValidationError(
                f"Unknown file type: {ext}. Supported: .xlsx, .yaml, .json"
            )

    if file_type == "excel":
        return loader.load_from_excel(file_path)
    elif file_type == "yaml":
        return loader.load_from_yaml(file_path)
    elif file_type == "json":
        return loader.load_from_json(file_path)
    else:
        raise ValidationError(f"Unknown file type: {file_type}")
