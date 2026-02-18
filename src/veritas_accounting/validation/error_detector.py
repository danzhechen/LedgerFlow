"""Error detection and flagging for veritas-accounting."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from veritas_accounting.validation.input_validator import ValidationError
from veritas_accounting.validation.pipeline import ValidationWarning


# Error types
ERROR_TYPE_DATA = "data_error"
ERROR_TYPE_RULE = "rule_error"
ERROR_TYPE_TRANSFORMATION = "transformation_error"
ERROR_TYPE_OUTPUT = "output_error"

# Severity levels
SEVERITY_CRITICAL = "critical"
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"


@dataclass
class DetectedError:
    """
    Enhanced error with categorization and context.

    Extends ValidationError with additional metadata for error detection and flagging.
    """

    row_number: int
    field_name: str
    error_type: str  # Type: data_error, rule_error, transformation_error, output_error
    error_message: str
    actual_value: any
    entry_id: str | None = None
    rule_id: str | None = None
    severity: str = SEVERITY_ERROR  # critical, error, warning, info
    expected_value: any = None
    requires_review: bool = True  # All errors require review by default

    def __str__(self) -> str:
        """Return human-readable error message."""
        entry_info = f" (entry_id: {self.entry_id})" if self.entry_id else ""
        rule_info = f" (rule_id: {self.rule_id})" if self.rule_id else ""
        severity_info = f" [{self.severity.upper()}]" if self.severity != SEVERITY_ERROR else ""
        return (
            f"Row {self.row_number}{entry_info}{rule_info}{severity_info}, "
            f"Field '{self.field_name}': {self.error_message} "
            f"(got: {self.actual_value})"
        )


@dataclass
class ErrorGroup:
    """Group of related errors."""

    group_key: str  # Key used for grouping (entry_id, rule_id, or error_type)
    errors: list[DetectedError]
    count: int

    def __post_init__(self):
        """Ensure count matches errors list length."""
        self.count = len(self.errors)


class ErrorDetector:
    """
    Detects and flags all errors from validation stages.

    Aggregates errors from input, transformation, and output validation,
    categorizes them, assigns severity levels, and groups related errors.
    """

    def __init__(self):
        """Initialize ErrorDetector."""
        self.all_errors: list[DetectedError] = []
        self.all_warnings: list[ValidationWarning] = []

    def add_validation_result(
        self,
        validation_errors: list[ValidationError],
        validation_warnings: Optional[list[ValidationWarning]] = None,
        error_category: str = ERROR_TYPE_DATA,
        default_severity: str = SEVERITY_ERROR,
    ) -> None:
        """
        Add errors and warnings from a validation stage.

        Args:
            validation_errors: List of ValidationError objects
            validation_warnings: Optional list of ValidationWarning objects
            error_category: Category for these errors (data_error, rule_error, etc.)
            default_severity: Default severity level for these errors
        """
        # Convert ValidationError to DetectedError with categorization
        for error in validation_errors:
            detected_error = self._convert_to_detected_error(
                error, error_category, default_severity
            )
            self.all_errors.append(detected_error)

        # Add warnings
        if validation_warnings:
            self.all_warnings.extend(validation_warnings)

    def _convert_to_detected_error(
        self,
        error: ValidationError,
        error_category: str,
        default_severity: str,
    ) -> DetectedError:
        """
        Convert ValidationError to DetectedError with categorization.

        Args:
            error: ValidationError to convert
            error_category: Category for this error
            default_severity: Default severity level

        Returns:
            DetectedError with enhanced metadata
        """
        # Determine severity based on error type
        severity = self._determine_severity(error, default_severity)

        # Extract rule_id if present in entry_id (rules have R- prefix)
        rule_id = error.entry_id if error.entry_id and error.entry_id.startswith("R-") else None
        entry_id = error.entry_id if error.entry_id and not error.entry_id.startswith("R-") else None

        return DetectedError(
            row_number=error.row_number,
            field_name=error.field_name,
            error_type=error_category,
            error_message=error.error_message,
            actual_value=error.actual_value,
            entry_id=entry_id,
            rule_id=rule_id,
            severity=severity,
            expected_value=None,  # Can be set by specific validators
            requires_review=True,  # All errors require review
        )

    def _determine_severity(self, error: ValidationError, default_severity: str) -> str:
        """
        Determine severity level based on error characteristics.

        Args:
            error: ValidationError to analyze
            default_severity: Default severity if not determined

        Returns:
            Severity level string
        """
        error_type = error.error_type.lower()

        # Critical errors: data corruption, transformation failure
        if any(
            keyword in error_type
            for keyword in ["corruption", "transformation_failure", "data_loss"]
        ):
            return SEVERITY_CRITICAL

        # Errors: invalid data, rule failure
        if any(
            keyword in error_type
            for keyword in [
                "validation_error",
                "missing_field",
                "invalid_type",
                "syntax_error",
                "rule_conflict",
            ]
        ):
            return SEVERITY_ERROR

        # Warnings: potential issues
        if any(
            keyword in error_type
            for keyword in ["unusual", "potential", "should_review", "warning"]
        ):
            return SEVERITY_WARNING

        # Default to provided severity
        return default_severity

    def get_all_errors(self) -> list[DetectedError]:
        """
        Get all detected errors.

        Returns:
            List of all DetectedError objects
        """
        return self.all_errors.copy()

    def get_all_warnings(self) -> list[ValidationWarning]:
        """
        Get all detected warnings.

        Returns:
            List of all ValidationWarning objects
        """
        return self.all_warnings.copy()

    def get_errors_by_type(self, error_type: str) -> list[DetectedError]:
        """
        Get errors filtered by type.

        Args:
            error_type: Error type to filter by (data_error, rule_error, etc.)

        Returns:
            List of DetectedError objects of specified type
        """
        return [e for e in self.all_errors if e.error_type == error_type]

    def get_errors_by_severity(self, severity: str) -> list[DetectedError]:
        """
        Get errors filtered by severity.

        Args:
            severity: Severity level to filter by (critical, error, warning, info)

        Returns:
            List of DetectedError objects with specified severity
        """
        return [e for e in self.all_errors if e.severity == severity]

    def get_errors_by_entry(self, entry_id: str) -> list[DetectedError]:
        """
        Get all errors for a specific journal entry.

        Args:
            entry_id: Journal entry ID

        Returns:
            List of DetectedError objects for this entry
        """
        return [e for e in self.all_errors if e.entry_id == entry_id]

    def get_errors_by_rule(self, rule_id: str) -> list[DetectedError]:
        """
        Get all errors for a specific mapping rule.

        Args:
            rule_id: Mapping rule ID

        Returns:
            List of DetectedError objects for this rule
        """
        return [e for e in self.all_errors if e.rule_id == rule_id]

    def group_errors_by_entry(self) -> dict[str, ErrorGroup]:
        """
        Group errors by journal entry ID.

        Returns:
            Dictionary mapping entry_id to ErrorGroup
        """
        groups: dict[str, list[DetectedError]] = defaultdict(list)

        for error in self.all_errors:
            if error.entry_id:
                groups[error.entry_id].append(error)

        return {
            entry_id: ErrorGroup(
                group_key=entry_id, errors=errors, count=len(errors)
            )
            for entry_id, errors in groups.items()
        }

    def group_errors_by_rule(self) -> dict[str, ErrorGroup]:
        """
        Group errors by mapping rule ID.

        Returns:
            Dictionary mapping rule_id to ErrorGroup
        """
        groups: dict[str, list[DetectedError]] = defaultdict(list)

        for error in self.all_errors:
            if error.rule_id:
                groups[error.rule_id].append(error)

        return {
            rule_id: ErrorGroup(group_key=rule_id, errors=errors, count=len(errors))
            for rule_id, errors in groups.items()
        }

    def group_errors_by_type(self) -> dict[str, ErrorGroup]:
        """
        Group errors by error type.

        Returns:
            Dictionary mapping error_type to ErrorGroup
        """
        groups: dict[str, list[DetectedError]] = defaultdict(list)

        for error in self.all_errors:
            groups[error.error_type].append(error)

        return {
            error_type: ErrorGroup(
                group_key=error_type, errors=errors, count=len(errors)
            )
            for error_type, errors in groups.items()
        }

    def group_errors_by_severity(self) -> dict[str, ErrorGroup]:
        """
        Group errors by severity level.

        Returns:
            Dictionary mapping severity to ErrorGroup
        """
        groups: dict[str, list[DetectedError]] = defaultdict(list)

        for error in self.all_errors:
            groups[error.severity].append(error)

        return {
            severity: ErrorGroup(
                group_key=severity, errors=errors, count=len(errors)
            )
            for severity, errors in groups.items()
        }

    def get_summary(self) -> dict[str, any]:
        """
        Get summary statistics of all errors and warnings.

        Returns:
            Dictionary with summary statistics
        """
        return {
            "total_errors": len(self.all_errors),
            "total_warnings": len(self.all_warnings),
            "errors_by_type": {
                error_type: len(self.get_errors_by_type(error_type))
                for error_type in [
                    ERROR_TYPE_DATA,
                    ERROR_TYPE_RULE,
                    ERROR_TYPE_TRANSFORMATION,
                    ERROR_TYPE_OUTPUT,
                ]
            },
            "errors_by_severity": {
                severity: len(self.get_errors_by_severity(severity))
                for severity in [
                    SEVERITY_CRITICAL,
                    SEVERITY_ERROR,
                    SEVERITY_WARNING,
                    SEVERITY_INFO,
                ]
            },
            "requires_review": len([e for e in self.all_errors if e.requires_review]),
            "unique_entries_with_errors": len(
                {e.entry_id for e in self.all_errors if e.entry_id}
            ),
            "unique_rules_with_errors": len(
                {e.rule_id for e in self.all_errors if e.rule_id}
            ),
        }

    def has_critical_errors(self) -> bool:
        """
        Check if there are any critical errors.

        Returns:
            True if any critical errors exist, False otherwise
        """
        return len(self.get_errors_by_severity(SEVERITY_CRITICAL)) > 0

    def has_errors(self) -> bool:
        """
        Check if there are any errors (excluding warnings).

        Returns:
            True if any errors exist (critical or error severity), False otherwise
        """
        return (
            len(self.get_errors_by_severity(SEVERITY_CRITICAL)) > 0
            or len(self.get_errors_by_severity(SEVERITY_ERROR)) > 0
        )








