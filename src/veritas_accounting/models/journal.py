"""JournalEntry Pydantic model for veritas-accounting."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class JournalEntry(BaseModel):
    """
    Journal entry data model.

    Represents a single journal entry from the input Excel file.
    """

    entry_id: str = Field(
        ...,
        description="Unique identifier for the journal entry",
        min_length=1,
    )
    year: int = Field(
        ...,
        description="Year of the journal entry",
        ge=2000,
        le=2100,
    )
    description: str = Field(
        ...,
        description="Description of the journal entry (supports Chinese text)",
        min_length=1,
    )
    old_type: str = Field(
        ...,
        description="Original account type/category from journal entry",
        min_length=1,
    )
    amount: Decimal = Field(
        ...,
        description="Amount of the journal entry (financial amount)",
    )
    date: datetime = Field(
        ...,
        description="Date of the journal entry",
    )
    # Optional fields
    quarter: Optional[int] = Field(
        None,
        description="Quarter (1-4) if specified",
        ge=1,
        le=4,
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes or comments",
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal | float | str) -> Decimal:
        """
        Validate amount is a valid Decimal.

        Args:
            v: Amount value

        Returns:
            Decimal amount

        Raises:
            ValueError: If amount cannot be converted to Decimal
        """
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount format: {v}. Must be a number.") from e

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v: str | datetime) -> datetime:
        """
        Parse date from string or datetime object.

        Args:
            v: Date value (string or datetime)

        Returns:
            datetime object

        Raises:
            ValueError: If date cannot be parsed
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue
            raise ValueError(
                f"Invalid date format: {v}. Expected formats: YYYY-MM-DD, YYYY/MM/DD, etc."
            )
        raise ValueError(f"Invalid date type: {type(v)}. Expected string or datetime.")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }
        # Allow extra fields for flexibility during development
        extra = "ignore"
        # Use enum values instead of names
        use_enum_values = True
