"""MappingRule Pydantic model for veritas-accounting."""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class MappingRule(BaseModel):
    """
    Mapping rule data model.

    Represents a single mapping rule that transforms journal entries to ledger entries.
    Rules contain conditions (rule-engine expressions) and target account codes.
    """

    rule_id: str = Field(
        ...,
        description="Unique identifier for the mapping rule",
        min_length=1,
    )
    condition: str = Field(
        ...,
        description="Rule-engine expression (e.g., 'old_type == \"OL\" and year == 2022')",
        min_length=1,
    )
    old_type: Optional[str] = Field(
        None,
        description="Source journal entry type to match (optional)",
    )
    new_type: Optional[str] = Field(
        None,
        description="Target ledger account type (optional)",
    )
    account_code: str = Field(
        ...,
        description="Target account code in the hierarchy",
        min_length=1,
    )
    priority: int = Field(
        ...,
        description="Rule priority/order (higher priority = applied first)",
        ge=1,
    )
    generates_multiple: bool = Field(
        False,
        description="Whether this rule generates multiple ledger entries (one-to-many)",
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description of the rule (supports Chinese text)",
    )

    @field_validator("condition")
    @classmethod
    def validate_condition_not_empty(cls, v: str) -> str:
        """
        Validate condition is not empty.

        Args:
            v: Condition string

        Returns:
            Condition string

        Raises:
            ValueError: If condition is empty
        """
        if not v or not v.strip():
            raise ValueError("Condition cannot be empty")
        return v.strip()

    @field_validator("old_type", "new_type")
    @classmethod
    def validate_type_not_empty_if_present(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate type fields are not empty strings if provided.

        Args:
            v: Type string or None

        Returns:
            Type string or None

        Raises:
            ValueError: If type is empty string
        """
        if v is not None and not v.strip():
            raise ValueError("Type cannot be an empty string. Use None instead.")
        return v.strip() if v else None

    class Config:
        """Pydantic configuration."""

        extra = "ignore"  # Ignore extra fields during validation
        use_enum_values = True
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting dynamic attributes like ledger_type."""
        # Allow setting attributes that aren't in the model
        # This is needed for ledger_type which is added dynamically
        object.__setattr__(self, name, value)








