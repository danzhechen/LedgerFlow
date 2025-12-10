"""Account hierarchy Pydantic model for veritas-accounting."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Account(BaseModel):
    """
    Account data model for hierarchical account structure.

    Represents a single account in the 4-level hierarchy (25 accounts total).
    """

    code: str = Field(
        ...,
        description="Account code (e.g., 'A1', 'B2-3')",
        min_length=1,
    )
    name: str = Field(
        ...,
        description="Account name (supports Chinese text)",
        min_length=1,
    )
    level: int = Field(
        ...,
        description="Hierarchy level (1-4)",
        ge=1,
        le=4,
    )
    parent_code: Optional[str] = Field(
        None,
        description="Parent account code (None for level 1 accounts)",
    )
    full_path: str = Field(
        ...,
        description="Full hierarchy path (e.g., 'Level1/Level2/Level3/Level4')",
        min_length=1,
    )

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        """
        Validate account code is not empty.

        Args:
            v: Account code

        Returns:
            Account code

        Raises:
            ValueError: If code is empty
        """
        if not v or not v.strip():
            raise ValueError("Account code cannot be empty")
        return v.strip()

    @field_validator("parent_code")
    @classmethod
    def validate_parent_code(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate parent code based on level.

        Args:
            v: Parent code or None
            info: Validation info containing other field values

        Returns:
            Parent code or None

        Raises:
            ValueError: If level 1 has parent or level > 1 has no parent
        """
        level = info.data.get("level") if hasattr(info, "data") else None
        if level is None:
            # Can't validate without level, skip
            return v

        if level == 1 and v is not None:
            raise ValueError("Level 1 accounts cannot have a parent code")
        if level > 1 and v is None:
            raise ValueError(f"Level {level} accounts must have a parent code")

        return v.strip() if v else None

    class Config:
        """Pydantic configuration."""

        extra = "ignore"
        use_enum_values = True


class AccountHierarchy:
    """
    Account hierarchy manager.

    Manages the hierarchical account structure (4 levels, 25 accounts).
    Provides methods to query and navigate the hierarchy.
    """

    def __init__(self, accounts: list[Account]) -> None:
        """
        Initialize account hierarchy.

        Args:
            accounts: List of Account objects

        Raises:
            ValueError: If accounts are invalid (duplicates, invalid hierarchy)
        """
        self._accounts: dict[str, Account] = {}
        self._by_level: dict[int, list[Account]] = {1: [], 2: [], 3: [], 4: []}

        # Validate and index accounts
        seen_codes: set[str] = set()
        for account in accounts:
            if account.code in seen_codes:
                raise ValueError(f"Duplicate account code: {account.code}")
            seen_codes.add(account.code)

            self._accounts[account.code] = account
            if account.level in self._by_level:
                self._by_level[account.level].append(account)

        # Validate hierarchy relationships
        self._validate_hierarchy()

    def _validate_hierarchy(self) -> None:
        """Validate parent-child relationships in the hierarchy."""
        for account in self._accounts.values():
            if account.level > 1 and account.parent_code:
                if account.parent_code not in self._accounts:
                    raise ValueError(
                        f"Account {account.code} references non-existent parent: {account.parent_code}"
                    )
                parent = self._accounts[account.parent_code]
                if parent.level != account.level - 1:
                    raise ValueError(
                        f"Account {account.code} (level {account.level}) has invalid parent level: {parent.level}"
                    )

    def get_account(self, code: str) -> Account | None:
        """
        Get account by code.

        Args:
            code: Account code

        Returns:
            Account object or None if not found
        """
        return self._accounts.get(code)

    def get_children(self, parent_code: str) -> list[Account]:
        """
        Get all child accounts of a parent.

        Args:
            parent_code: Parent account code

        Returns:
            List of child Account objects
        """
        return [
            account
            for account in self._accounts.values()
            if account.parent_code == parent_code
        ]

    def get_full_path(self, code: str) -> str:
        """
        Get full hierarchy path for an account.

        Args:
            code: Account code

        Returns:
            Full path string (e.g., 'Level1/Level2/Level3/Level4')

        Raises:
            ValueError: If account not found
        """
        account = self.get_account(code)
        if account is None:
            raise ValueError(f"Account not found: {code}")
        return account.full_path

    def get_by_level(self, level: int) -> list[Account]:
        """
        Get all accounts at a specific level.

        Args:
            level: Hierarchy level (1-4)

        Returns:
            List of Account objects at that level
        """
        return self._by_level.get(level, [])

    def get_all_accounts(self) -> list[Account]:
        """
        Get all accounts in the hierarchy.

        Returns:
            List of all Account objects
        """
        return list(self._accounts.values())

    @classmethod
    def from_excel(
        cls, file_path: str | Path, sheet_name: str | None = None
    ) -> "AccountHierarchy":
        """
        Create AccountHierarchy from an Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Worksheet name (optional)

        Returns:
            AccountHierarchy object
        """
        from veritas_accounting.models.account_loader import AccountHierarchyLoader

        loader = AccountHierarchyLoader()
        return loader.load_from_excel(file_path, sheet_name)

    @classmethod
    def from_yaml(cls, file_path: str | Path) -> "AccountHierarchy":
        """
        Create AccountHierarchy from a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            AccountHierarchy object
        """
        from veritas_accounting.models.account_loader import AccountHierarchyLoader

        loader = AccountHierarchyLoader()
        return loader.load_from_yaml(file_path)

    @classmethod
    def from_json(cls, file_path: str | Path) -> "AccountHierarchy":
        """
        Create AccountHierarchy from a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            AccountHierarchy object
        """
        from veritas_accounting.models.account_loader import AccountHierarchyLoader

        loader = AccountHierarchyLoader()
        return loader.load_from_json(file_path)
