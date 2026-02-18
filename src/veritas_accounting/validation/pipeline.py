"""Input validation pipeline for veritas-accounting."""

from dataclasses import dataclass
from typing import Optional

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.validation.input_validator import (
    JournalEntryValidator,
    ValidationError,
)
from veritas_accounting.validation.rule_validator import MappingRuleValidator


# Severity levels for validation results
SEVERITY_CRITICAL = "critical"
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"


@dataclass
class ValidationWarning:
    """Validation warning (non-blocking issue)."""

    row_number: int
    field_name: str
    warning_type: str
    warning_message: str
    actual_value: any
    entry_id: str | None = None

    def __str__(self) -> str:
        """Return human-readable warning message."""
        entry_info = f" (entry_id: {self.entry_id})" if self.entry_id else ""
        return (
            f"Row {self.row_number}{entry_info}, Field '{self.field_name}': "
            f"{self.warning_message} (got: {self.actual_value})"
        )


@dataclass
class ValidationResult:
    """Comprehensive validation result from input validation pipeline."""

    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    valid_journal_entries: list[JournalEntry]
    valid_mapping_rules: list[MappingRule]

    @property
    def error_count(self) -> int:
        """Return total number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Return total number of warnings."""
        return len(self.warnings)

    @property
    def entries_processed(self) -> int:
        """Return number of journal entries processed."""
        return len(self.valid_journal_entries) + len(
            [e for e in self.errors if e.entry_id and e.entry_id.startswith("JE-")]
        )

    @property
    def rules_processed(self) -> int:
        """Return number of mapping rules processed."""
        return len(self.valid_mapping_rules) + len(
            [e for e in self.errors if e.entry_id and e.entry_id.startswith("R-")]
        )


class InputValidationPipeline:
    """
    Comprehensive input data validation pipeline.

    Orchestrates multiple validation stages:
    1. Structure validation (Pydantic models)
    2. Business rule validation (custom validators)
    3. Completeness validation (null checks)
    4. Consistency validation (cross-field checks)
    5. Reference validation (foreign key checks)
    """

    def __init__(self, account_hierarchy: Optional[AccountHierarchy] = None):
        """
        Initialize InputValidationPipeline.

        Args:
            account_hierarchy: Optional AccountHierarchy for account code validation.
                              If None, account code validation is skipped.
        """
        self.journal_validator = JournalEntryValidator()
        self.rule_validator = MappingRuleValidator(account_hierarchy=account_hierarchy)
        self.account_hierarchy = account_hierarchy

    def validate_inputs(
        self,
        journal_entries: list[JournalEntry],
        mapping_rules: list[MappingRule],
    ) -> ValidationResult:
        """
        Validate journal entries and mapping rules comprehensively.

        Args:
            journal_entries: List of JournalEntry objects to validate
            mapping_rules: List of MappingRule objects to validate

        Returns:
            ValidationResult with validation status, errors, warnings, and valid data
        """
        all_errors: list[ValidationError] = []
        all_warnings: list[ValidationWarning] = []
        valid_entries: list[JournalEntry] = []
        valid_rules: list[MappingRule] = []

        # Stage 1: Structure validation (Pydantic models)
        # This is already done when creating JournalEntry and MappingRule objects
        # We'll validate rules structure here
        valid_rules, rule_errors = self.rule_validator.validate_rules(mapping_rules)
        all_errors.extend(rule_errors)

        # All journal entries passed structure validation (they're already JournalEntry objects)
        valid_entries = journal_entries.copy()

        # Stage 2: Business rule validation
        business_errors, business_warnings = self._validate_business_rules(
            valid_entries
        )
        all_errors.extend(business_errors)
        all_warnings.extend(business_warnings)

        # Stage 3: Completeness validation
        completeness_errors = self._validate_completeness(valid_entries)
        all_errors.extend(completeness_errors)

        # Stage 4: Consistency validation
        consistency_errors, consistency_warnings = self._validate_consistency(
            valid_entries
        )
        all_errors.extend(consistency_errors)
        all_warnings.extend(consistency_warnings)

        # Stage 5: Cross-reference validation
        reference_errors = self._validate_cross_references(valid_entries, valid_rules)
        all_errors.extend(reference_errors)

        # Determine overall validation status
        # Valid if no errors (warnings are OK)
        is_valid = len(all_errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            valid_journal_entries=valid_entries,
            valid_mapping_rules=valid_rules,
        )

    def _validate_business_rules(
        self, entries: list[JournalEntry]
    ) -> tuple[list[ValidationError], list[ValidationWarning]]:
        """
        Validate business rules (year ranges, amount ranges, date validity).

        Args:
            entries: List of JournalEntry objects

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        for entry in entries:
            # Year range validation (should be in reasonable range)
            # Note: Pydantic already enforces year >= 2000 and <= 2100
            # This check is for additional warnings if needed (e.g., very old/future years)
            # For now, we skip since Pydantic handles it

            # Amount range validation
            if entry.amount == 0:
                warnings.append(
                    ValidationWarning(
                        row_number=0,
                        field_name="amount",
                        warning_type="zero_amount",
                        warning_message="Amount is zero. Please verify this is intentional.",
                        actual_value=entry.amount,
                        entry_id=entry.entry_id,
                    )
                )
            elif abs(float(entry.amount)) > 1_000_000_000:  # 1 billion
                warnings.append(
                    ValidationWarning(
                        row_number=0,
                        field_name="amount",
                        warning_type="large_amount",
                        warning_message=(
                            f"Amount {entry.amount} is very large (> 1 billion). "
                            "Please verify this is correct."
                        ),
                        actual_value=entry.amount,
                        entry_id=entry.entry_id,
                    )
                )

            # Date validity (already validated by Pydantic, but check for future dates)
            from datetime import datetime

            if entry.date > datetime.now():
                warnings.append(
                    ValidationWarning(
                        row_number=0,
                        field_name="date",
                        warning_type="future_date",
                        warning_message=(
                            f"Date {entry.date.date()} is in the future. "
                            "Please verify this is correct."
                        ),
                        actual_value=entry.date,
                        entry_id=entry.entry_id,
                    )
                )

        return errors, warnings

    def _validate_completeness(
        self, entries: list[JournalEntry]
    ) -> list[ValidationError]:
        """
        Validate completeness (no nulls in required fields).

        Args:
            entries: List of JournalEntry objects

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Pydantic already ensures required fields are not None
        # But we can check for empty strings or other edge cases
        for entry in entries:
            # Check for empty strings in required text fields
            if not entry.description or not entry.description.strip():
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="description",
                        error_type="missing_field",
                        error_message="Description cannot be empty",
                        actual_value=entry.description,
                        entry_id=entry.entry_id,
                    )
                )

            if not entry.old_type or not entry.old_type.strip():
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="old_type",
                        error_type="missing_field",
                        error_message="Old type cannot be empty",
                        actual_value=entry.old_type,
                        entry_id=entry.entry_id,
                    )
                )

        return errors

    def _validate_consistency(
        self, entries: list[JournalEntry]
    ) -> tuple[list[ValidationError], list[ValidationWarning]]:
        """
        Validate consistency (dates in same quarter, amounts are reasonable).

        Args:
            entries: List of JournalEntry objects

        Returns:
            Tuple of (errors, warnings)
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        if not entries:
            return errors, warnings

        # Check that all entries are in the same year (warning if not)
        years = {entry.year for entry in entries}
        if len(years) > 1:
            warnings.append(
                ValidationWarning(
                    row_number=0,
                    field_name="year",
                    warning_type="mixed_years",
                    warning_message=(
                        f"Entries span multiple years: {sorted(years)}. "
                        "Please verify this is intentional."
                    ),
                    actual_value=list(years),
                    entry_id=None,
                )
            )

        # Check for duplicate entry IDs (if any)
        entry_ids = {}
        for entry in entries:
            if entry.entry_id in entry_ids:
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="entry_id",
                        error_type="duplicate_entry",
                        error_message=(
                            f"Duplicate entry ID '{entry.entry_id}'. "
                            "Each entry must have a unique ID."
                        ),
                        actual_value=entry.entry_id,
                        entry_id=entry.entry_id,
                    )
                )
            entry_ids[entry.entry_id] = entry

        # Check quarter consistency if quarter is specified
        entries_with_quarter = [e for e in entries if e.quarter is not None]
        if entries_with_quarter:
            quarters = {e.quarter for e in entries_with_quarter}
            if len(quarters) > 1:
                warnings.append(
                    ValidationWarning(
                        row_number=0,
                        field_name="quarter",
                        warning_type="mixed_quarters",
                        warning_message=(
                            f"Entries span multiple quarters: {sorted(quarters)}. "
                            "Please verify this is intentional."
                        ),
                        actual_value=list(quarters),
                        entry_id=None,
                    )
                )

        return errors, warnings

    def _validate_cross_references(
        self, entries: list[JournalEntry], rules: list[MappingRule]
    ) -> list[ValidationError]:
        """
        Validate cross-references (account codes in rules exist in hierarchy).

        Args:
            entries: List of JournalEntry objects
            rules: List of MappingRule objects

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Account code validation is already done in MappingRuleValidator
        # if account_hierarchy is provided
        # This stage is mainly for additional cross-references if needed

        # Check if old_type values in entries match any rules
        if rules:
            rule_old_types = {
                rule.old_type for rule in rules if rule.old_type is not None
            }
            entry_old_types = {entry.old_type for entry in entries}

            # Warn about entry types that don't match any rule
            unmatched_types = entry_old_types - rule_old_types
            if unmatched_types:
                for entry in entries:
                    if entry.old_type in unmatched_types:
                        errors.append(
                            ValidationError(
                                row_number=0,
                                field_name="old_type",
                                error_type="unmatched_type",
                                error_message=(
                                    f"Old type '{entry.old_type}' in entry does not match "
                                    "any mapping rule. Entry may not be processed correctly."
                                ),
                                actual_value=entry.old_type,
                                entry_id=entry.entry_id,
                            )
                        )

        return errors








