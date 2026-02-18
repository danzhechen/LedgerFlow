"""LedgerEntry Pydantic model for veritas-accounting."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class LedgerEntry(BaseModel):
    """
    Ledger entry data model.

    Represents a single ledger entry in the hierarchical account structure.
    Generated from journal entries through mapping rules.
    """

    entry_id: str = Field(
        ...,
        description="Unique identifier for the ledger entry",
        min_length=1,
    )
    account_code: str = Field(
        ...,
        description="Account code in the hierarchy (e.g., 'A1', 'B2-3')",
        min_length=1,
    )
    account_path: str = Field(
        ...,
        description="Full hierarchy path (e.g., 'Level1/Level2/Level3/Level4')",
        min_length=1,
    )
    amount: Decimal = Field(
        ...,
        description="Amount of the ledger entry (financial amount)",
    )
    date: datetime = Field(
        ...,
        description="Date of the ledger entry",
    )
    description: str = Field(
        ...,
        description="Description of the ledger entry (supports Chinese text)",
        min_length=1,
    )
    source_entry_id: str = Field(
        ...,
        description="Link back to the source JournalEntry entry_id",
        min_length=1,
    )
    rule_applied: str = Field(
        ...,
        description="Rule ID that generated this ledger entry",
        min_length=1,
    )
    quarter: int = Field(
        ...,
        description="Quarter (1-4) for quarterly aggregation",
        ge=1,
        le=4,
    )
    year: int = Field(
        ...,
        description="Year of the ledger entry (must match date.year)",
        ge=2000,
        le=2100,
    )
    ledger_type: str | None = Field(
        None,
        description="Ledger type: 'CR' (Credit) or 'DR' (Debit). None if not specified.",
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
        extra = "ignore"
        use_enum_values = True







