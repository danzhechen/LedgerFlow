"""Unit tests for ErrorDetector class."""

import pytest

from veritas_accounting.validation.error_detector import (
    ERROR_TYPE_DATA,
    ERROR_TYPE_RULE,
    ERROR_TYPE_TRANSFORMATION,
    DetectedError,
    ErrorDetector,
    ErrorGroup,
    SEVERITY_CRITICAL,
    SEVERITY_ERROR,
    SEVERITY_WARNING,
)
from veritas_accounting.validation.input_validator import ValidationError
from veritas_accounting.validation.pipeline import ValidationWarning


class TestErrorDetector:
    """Test suite for ErrorDetector class."""

    def test_add_validation_result_with_errors(self):
        """Test adding validation errors from a validation stage."""
        detector = ErrorDetector()

        errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
        ]

        detector.add_validation_result(
            validation_errors=errors,
            error_category=ERROR_TYPE_DATA,
        )

        all_errors = detector.get_all_errors()
        assert len(all_errors) == 1
        assert all_errors[0].error_type == ERROR_TYPE_DATA
        assert all_errors[0].entry_id == "JE-001"

    def test_add_validation_result_with_warnings(self):
        """Test adding validation warnings."""
        detector = ErrorDetector()

        warnings = [
            ValidationWarning(
                row_number=2,
                field_name="year",
                warning_type="unusual_year",
                warning_message="Unusual year",
                actual_value=1999,
                entry_id="JE-002",
            ),
        ]

        detector.add_validation_result(
            validation_errors=[],
            validation_warnings=warnings,
            error_category=ERROR_TYPE_DATA,
        )

        all_warnings = detector.get_all_warnings()
        assert len(all_warnings) == 1

    def test_categorize_errors_by_type(self):
        """Test error categorization by type."""
        detector = ErrorDetector()

        data_errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
        ]

        rule_errors = [
            ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message="Invalid syntax",
                actual_value="old_type == ",
                entry_id="R-001",
            ),
        ]

        detector.add_validation_result(data_errors, error_category=ERROR_TYPE_DATA)
        detector.add_validation_result(rule_errors, error_category=ERROR_TYPE_RULE)

        data_error_list = detector.get_errors_by_type(ERROR_TYPE_DATA)
        rule_error_list = detector.get_errors_by_type(ERROR_TYPE_RULE)

        assert len(data_error_list) == 1
        assert len(rule_error_list) == 1
        assert data_error_list[0].error_type == ERROR_TYPE_DATA
        assert rule_error_list[0].error_type == ERROR_TYPE_RULE

    def test_severity_assignment(self):
        """Test that severity levels are assigned correctly."""
        detector = ErrorDetector()

        critical_error = ValidationError(
            row_number=1,
            field_name="data",
            error_type="data_corruption",
            error_message="Data corruption detected",
            actual_value=None,
            entry_id="JE-001",
        )

        normal_error = ValidationError(
            row_number=2,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount",
            actual_value=100,
            entry_id="JE-002",
        )

        detector.add_validation_result(
            [critical_error], error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )
        detector.add_validation_result(
            [normal_error], error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )

        critical_errors = detector.get_errors_by_severity(SEVERITY_CRITICAL)
        normal_errors = detector.get_errors_by_severity(SEVERITY_ERROR)

        assert len(critical_errors) == 1
        assert len(normal_errors) == 1
        assert critical_errors[0].severity == SEVERITY_CRITICAL

    def test_get_errors_by_entry(self):
        """Test filtering errors by entry ID."""
        detector = ErrorDetector()

        errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
            ValidationError(
                row_number=2,
                field_name="year",
                error_type="validation_error",
                error_message="Invalid year",
                actual_value=1999,
                entry_id="JE-001",
            ),
            ValidationError(
                row_number=3,
                field_name="description",
                error_type="validation_error",
                error_message="Missing description",
                actual_value=None,
                entry_id="JE-002",
            ),
        ]

        detector.add_validation_result(errors, error_category=ERROR_TYPE_DATA)

        je001_errors = detector.get_errors_by_entry("JE-001")
        je002_errors = detector.get_errors_by_entry("JE-002")

        assert len(je001_errors) == 2
        assert len(je002_errors) == 1

    def test_get_errors_by_rule(self):
        """Test filtering errors by rule ID."""
        detector = ErrorDetector()

        errors = [
            ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message="Invalid syntax",
                actual_value="old_type == ",
                entry_id="R-001",
            ),
            ValidationError(
                row_number=0,
                field_name="account_code",
                error_type="invalid_account_code",
                error_message="Invalid account code",
                actual_value="INVALID",
                entry_id="R-001",
            ),
            ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message="Invalid syntax",
                actual_value="old_type == ",
                entry_id="R-002",
            ),
        ]

        detector.add_validation_result(errors, error_category=ERROR_TYPE_RULE)

        r001_errors = detector.get_errors_by_rule("R-001")
        r002_errors = detector.get_errors_by_rule("R-002")

        assert len(r001_errors) == 2
        assert len(r002_errors) == 1

    def test_group_errors_by_entry(self):
        """Test grouping errors by entry ID."""
        detector = ErrorDetector()

        errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
            ValidationError(
                row_number=2,
                field_name="year",
                error_type="validation_error",
                error_message="Invalid year",
                actual_value=1999,
                entry_id="JE-001",
            ),
            ValidationError(
                row_number=3,
                field_name="description",
                error_type="validation_error",
                error_message="Missing description",
                actual_value=None,
                entry_id="JE-002",
            ),
        ]

        detector.add_validation_result(errors, error_category=ERROR_TYPE_DATA)

        groups = detector.group_errors_by_entry()

        assert "JE-001" in groups
        assert "JE-002" in groups
        assert groups["JE-001"].count == 2
        assert groups["JE-002"].count == 1
        assert isinstance(groups["JE-001"], ErrorGroup)

    def test_group_errors_by_type(self):
        """Test grouping errors by error type."""
        detector = ErrorDetector()

        data_errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
        ]

        rule_errors = [
            ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message="Invalid syntax",
                actual_value="old_type == ",
                entry_id="R-001",
            ),
        ]

        detector.add_validation_result(data_errors, error_category=ERROR_TYPE_DATA)
        detector.add_validation_result(rule_errors, error_category=ERROR_TYPE_RULE)

        groups = detector.group_errors_by_type()

        assert ERROR_TYPE_DATA in groups
        assert ERROR_TYPE_RULE in groups
        assert groups[ERROR_TYPE_DATA].count == 1
        assert groups[ERROR_TYPE_RULE].count == 1

    def test_group_errors_by_severity(self):
        """Test grouping errors by severity level."""
        detector = ErrorDetector()

        critical_error = ValidationError(
            row_number=1,
            field_name="data",
            error_type="data_corruption",
            error_message="Data corruption",
            actual_value=None,
            entry_id="JE-001",
        )

        normal_error = ValidationError(
            row_number=2,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount",
            actual_value=100,
            entry_id="JE-002",
        )

        detector.add_validation_result(
            [critical_error], error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )
        detector.add_validation_result(
            [normal_error], error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )

        groups = detector.group_errors_by_severity()

        assert SEVERITY_CRITICAL in groups
        assert SEVERITY_ERROR in groups
        assert groups[SEVERITY_CRITICAL].count == 1
        assert groups[SEVERITY_ERROR].count == 1

    def test_get_summary(self):
        """Test getting summary statistics."""
        detector = ErrorDetector()

        data_errors = [
            ValidationError(
                row_number=1,
                field_name="amount",
                error_type="validation_error",
                error_message="Invalid amount",
                actual_value=100,
                entry_id="JE-001",
            ),
        ]

        rule_errors = [
            ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message="Invalid syntax",
                actual_value="old_type == ",
                entry_id="R-001",
            ),
        ]

        warnings = [
            ValidationWarning(
                row_number=2,
                field_name="year",
                warning_type="unusual_year",
                warning_message="Unusual year",
                actual_value=1999,
                entry_id="JE-002",
            ),
        ]

        detector.add_validation_result(data_errors, error_category=ERROR_TYPE_DATA)
        detector.add_validation_result(rule_errors, error_category=ERROR_TYPE_RULE)
        detector.add_validation_result(
            [], validation_warnings=warnings, error_category=ERROR_TYPE_DATA
        )

        summary = detector.get_summary()

        assert summary["total_errors"] == 2
        assert summary["total_warnings"] == 1
        assert summary["errors_by_type"][ERROR_TYPE_DATA] == 1
        assert summary["errors_by_type"][ERROR_TYPE_RULE] == 1
        assert summary["requires_review"] == 2
        assert summary["unique_entries_with_errors"] == 1
        assert summary["unique_rules_with_errors"] == 1

    def test_has_critical_errors(self):
        """Test checking for critical errors."""
        detector = ErrorDetector()

        normal_error = ValidationError(
            row_number=1,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount",
            actual_value=100,
            entry_id="JE-001",
        )

        detector.add_validation_result([normal_error], error_category=ERROR_TYPE_DATA)
        assert not detector.has_critical_errors()

        critical_error = ValidationError(
            row_number=2,
            field_name="data",
            error_type="data_corruption",
            error_message="Data corruption",
            actual_value=None,
            entry_id="JE-002",
        )

        detector.add_validation_result(
            [critical_error], error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )
        assert detector.has_critical_errors()

    def test_has_errors(self):
        """Test checking for any errors."""
        detector = ErrorDetector()

        assert not detector.has_errors()

        error = ValidationError(
            row_number=1,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount",
            actual_value=100,
            entry_id="JE-001",
        )

        detector.add_validation_result([error], error_category=ERROR_TYPE_DATA)
        assert detector.has_errors()

    def test_error_requires_review_flag(self):
        """Test that all errors are flagged for review."""
        detector = ErrorDetector()

        error = ValidationError(
            row_number=1,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount",
            actual_value=100,
            entry_id="JE-001",
        )

        detector.add_validation_result([error], error_category=ERROR_TYPE_DATA)

        all_errors = detector.get_all_errors()
        assert len(all_errors) == 1
        assert all_errors[0].requires_review is True

    def test_error_context_preservation(self):
        """Test that error context (entry_id, rule_id, field_name, etc.) is preserved."""
        detector = ErrorDetector()

        error = ValidationError(
            row_number=5,
            field_name="amount",
            error_type="validation_error",
            error_message="Invalid amount format",
            actual_value="not-a-number",
            entry_id="JE-001",
        )

        detector.add_validation_result([error], error_category=ERROR_TYPE_DATA)

        all_errors = detector.get_all_errors()
        assert len(all_errors) == 1
        detected_error = all_errors[0]

        assert detected_error.row_number == 5
        assert detected_error.field_name == "amount"
        assert detected_error.entry_id == "JE-001"
        assert detected_error.actual_value == "not-a-number"
        assert detected_error.error_message == "Invalid amount format"

    def test_rule_id_extraction(self):
        """Test that rule IDs are correctly extracted from entry_id."""
        detector = ErrorDetector()

        rule_error = ValidationError(
            row_number=0,
            field_name="condition",
            error_type="syntax_error",
            error_message="Invalid syntax",
            actual_value="old_type == ",
            entry_id="R-001",
        )

        detector.add_validation_result([rule_error], error_category=ERROR_TYPE_RULE)

        all_errors = detector.get_all_errors()
        assert len(all_errors) == 1
        assert all_errors[0].rule_id == "R-001"
        assert all_errors[0].entry_id is None  # Should not be set for rules
