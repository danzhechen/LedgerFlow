"""Unit tests for ValidationResultsViewer and confidence indicators."""

from veritas_accounting.validation.error_detector import ErrorDetector, ERROR_TYPE_DATA, SEVERITY_CRITICAL, SEVERITY_ERROR
from veritas_accounting.validation.input_validator import ValidationError
from veritas_accounting.validation.validation_results import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    ConfidenceScore,
    ValidationResultsViewer,
)


class TestValidationResultsViewer:
    """Test suite for ValidationResultsViewer class."""

    def test_generate_summary_no_errors(self):
        """Test summary generation with no errors."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=100)

        assert summary.overall_status == "pass"
        assert summary.status_indicator == "green"
        assert summary.entries_processed == 100
        assert summary.errors_found == 0
        assert summary.overall_confidence.level in [CONFIDENCE_HIGH, CONFIDENCE_MEDIUM]

    def test_generate_summary_with_errors(self):
        """Test summary generation with errors."""
        viewer = ValidationResultsViewer()
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

        detector.add_validation_result(errors, error_category=ERROR_TYPE_DATA)

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=99)

        assert summary.overall_status == "fail"
        assert summary.status_indicator == "red"
        assert summary.errors_found == 1

    def test_generate_summary_with_warnings(self):
        """Test summary generation with warnings only."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        from veritas_accounting.validation.pipeline import ValidationWarning

        warnings = [
            ValidationWarning(
                row_number=1,
                field_name="year",
                warning_type="unusual_year",
                warning_message="Unusual year",
                actual_value=2000,
                entry_id="JE-001",
            ),
        ]

        detector.add_validation_result([], validation_warnings=warnings, error_category=ERROR_TYPE_DATA)

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=100)

        assert summary.overall_status == "warning"
        assert summary.status_indicator == "yellow"
        assert summary.warnings_found == 1

    def test_generate_summary_with_critical_errors(self):
        """Test summary generation with critical errors."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        errors = [
            ValidationError(
                row_number=1,
                field_name="data",
                error_type="data_corruption",
                error_message="Data corruption detected",
                actual_value=None,
                entry_id="JE-001",
            ),
        ]

        detector.add_validation_result(
            errors, error_category=ERROR_TYPE_DATA, default_severity=SEVERITY_ERROR
        )

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=99)

        assert summary.overall_status == "fail"
        assert summary.status_indicator == "red"
        assert detector.has_critical_errors()

    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        # No errors - high confidence
        summary1 = viewer.generate_summary(detector, entries_processed=100, entries_valid=100)
        assert summary1.overall_confidence.level == CONFIDENCE_HIGH
        assert summary1.overall_confidence.score >= 0.8

        # Some errors - medium/low confidence
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
        detector.add_validation_result(errors, error_category=ERROR_TYPE_DATA)

        summary2 = viewer.generate_summary(detector, entries_processed=100, entries_valid=99)
        assert summary2.overall_confidence.score < summary1.overall_confidence.score

    def test_confidence_score_from_score(self):
        """Test ConfidenceScore.from_score factory method."""
        score_high = ConfidenceScore.from_score(0.9)
        assert score_high.level == CONFIDENCE_HIGH

        score_medium = ConfidenceScore.from_score(0.6)
        assert score_medium.level == CONFIDENCE_MEDIUM

        score_low = ConfidenceScore.from_score(0.3)
        assert score_low.level == CONFIDENCE_LOW

    def test_format_summary_display(self):
        """Test formatting summary for display."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=100)

        formatted = viewer.format_summary_display(summary)

        assert "Validation Status" in formatted
        assert "Summary Statistics" in formatted
        assert "Entries processed: 100" in formatted
        assert "Overall Confidence" in formatted
        assert "Validation Coverage" in formatted

    def test_validation_coverage(self):
        """Test validation coverage tracking."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        coverage = {
            "input": True,
            "transformation": False,
            "output": False,
        }

        summary = viewer.generate_summary(
            detector, entries_processed=100, validation_coverage=coverage
        )

        assert summary.coverage == coverage
        assert summary.coverage["input"] is True
        assert summary.coverage["transformation"] is False

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        viewer = ValidationResultsViewer()
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

        detector.add_validation_result(errors, error_category=ERROR_TYPE_DATA)

        summary = viewer.generate_summary(detector, entries_processed=100, entries_valid=99)

        assert summary.error_rate == 0.01  # 1 error / 100 entries
        assert summary.errors_found == 1

    def test_summary_with_no_entries(self):
        """Test summary generation with zero entries."""
        viewer = ValidationResultsViewer()
        detector = ErrorDetector()

        summary = viewer.generate_summary(detector, entries_processed=0, entries_valid=0)

        assert summary.entries_processed == 0
        assert summary.overall_confidence.level == CONFIDENCE_LOW
