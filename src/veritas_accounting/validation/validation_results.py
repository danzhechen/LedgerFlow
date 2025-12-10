"""Validation results and confidence indicators for veritas-accounting."""

from dataclasses import dataclass
from typing import Optional

from veritas_accounting.validation.error_detector import DetectedError, ErrorDetector
from veritas_accounting.validation.pipeline import ValidationWarning


# Confidence levels
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"


@dataclass
class ConfidenceScore:
    """Confidence score for a transformation or validation result."""

    score: float  # 0.0 to 1.0
    level: str  # high, medium, low
    factors: list[str]  # Reasons for the confidence level

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceScore":
        """
        Create ConfidenceScore from numeric score (0.0 to 1.0).

        Args:
            score: Confidence score between 0.0 and 1.0

        Returns:
            ConfidenceScore object
        """
        if score >= 0.8:
            level = CONFIDENCE_HIGH
        elif score >= 0.5:
            level = CONFIDENCE_MEDIUM
        else:
            level = CONFIDENCE_LOW

        return cls(score=score, level=level, factors=[])


@dataclass
class ValidationSummary:
    """Comprehensive validation summary with confidence indicators."""

    overall_status: str  # "pass", "fail", "warning"
    entries_processed: int
    entries_valid: int
    errors_found: int
    warnings_found: int
    overall_confidence: ConfidenceScore
    coverage: dict[str, bool]  # What was validated (input, transformation, output)
    status_indicator: str  # "green", "yellow", "red" for visual scanning

    @property
    def error_rate(self) -> float:
        """Calculate error rate (errors / entries processed)."""
        if self.entries_processed == 0:
            return 0.0
        return self.errors_found / self.entries_processed


class ValidationResultsViewer:
    """
    Provides validation results and confidence indicators.

    Displays validation status, statistics, confidence scores, and coverage
    to help users understand how confident they can be in automated results.
    """

    def __init__(self):
        """Initialize ValidationResultsViewer."""
        pass

    def generate_summary(
        self,
        error_detector: ErrorDetector,
        entries_processed: int,
        entries_valid: Optional[int] = None,
        validation_coverage: Optional[dict[str, bool]] = None,
    ) -> ValidationSummary:
        """
        Generate comprehensive validation summary.

        Args:
            error_detector: ErrorDetector with all errors and warnings
            entries_processed: Total number of entries processed
            entries_valid: Number of valid entries (if known)
            validation_coverage: Dictionary indicating what was validated

        Returns:
            ValidationSummary with all statistics and confidence indicators
        """
        errors_found = len(error_detector.get_all_errors())
        warnings_found = len(error_detector.get_all_warnings())

        # Determine overall status
        if error_detector.has_critical_errors():
            overall_status = "fail"
            status_indicator = "red"
        elif errors_found > 0:
            overall_status = "fail"
            status_indicator = "red"
        elif warnings_found > 0:
            overall_status = "warning"
            status_indicator = "yellow"
        else:
            overall_status = "pass"
            status_indicator = "green"

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            error_detector, entries_processed, entries_valid
        )

        # Default coverage
        if validation_coverage is None:
            validation_coverage = {
                "input": True,
                "transformation": False,  # Will be True when Story 4.2 is done
                "output": False,  # Will be True when Story 4.3 is done
            }

        return ValidationSummary(
            overall_status=overall_status,
            entries_processed=entries_processed,
            entries_valid=entries_valid or (entries_processed - errors_found),
            errors_found=errors_found,
            warnings_found=warnings_found,
            overall_confidence=overall_confidence,
            coverage=validation_coverage,
            status_indicator=status_indicator,
        )

    def _calculate_overall_confidence(
        self,
        error_detector: ErrorDetector,
        entries_processed: int,
        entries_valid: Optional[int],
    ) -> ConfidenceScore:
        """
        Calculate overall confidence score based on validation results.

        Args:
            error_detector: ErrorDetector with all errors
            entries_processed: Total entries processed
            entries_valid: Number of valid entries

        Returns:
            ConfidenceScore object
        """
        factors: list[str] = []

        if entries_processed == 0:
            return ConfidenceScore(score=0.0, level=CONFIDENCE_LOW, factors=["No entries processed"])

        # Base confidence: ratio of valid entries
        if entries_valid is not None:
            base_score = entries_valid / entries_processed
        else:
            # Estimate based on errors
            errors_found = len(error_detector.get_all_errors())
            base_score = max(0.0, 1.0 - (errors_found / entries_processed))

        # Adjust for error severity
        critical_errors = len(error_detector.get_errors_by_severity("critical"))
        if critical_errors > 0:
            base_score *= 0.5  # Significantly reduce confidence
            factors.append(f"{critical_errors} critical errors found")

        # Adjust for warnings (less impact than errors)
        warnings = len(error_detector.get_all_warnings())
        if warnings > 0:
            warning_penalty = min(0.2, warnings / entries_processed * 0.5)
            base_score *= (1.0 - warning_penalty)
            factors.append(f"{warnings} warnings found")

        # Normalize to 0.0-1.0 range
        confidence_score = max(0.0, min(1.0, base_score))

        return ConfidenceScore.from_score(confidence_score)

    def format_summary_display(self, summary: ValidationSummary) -> str:
        """
        Format validation summary for human-readable display.

        Args:
            summary: ValidationSummary to format

        Returns:
            Formatted string representation
        """
        lines = []

        # Status header
        status_emoji = {"green": "✅", "yellow": "⚠️", "red": "❌"}.get(
            summary.status_indicator, "❓"
        )
        lines.append(
            f"{status_emoji} **Validation Status: {summary.overall_status.upper()}**"
        )

        # Statistics
        lines.append("\n**Summary Statistics:**")
        lines.append(f"  • Entries processed: {summary.entries_processed}")
        lines.append(f"  • Valid entries: {summary.entries_valid}")
        lines.append(f"  • Errors found: {summary.errors_found}")
        lines.append(f"  • Warnings found: {summary.warnings_found}")
        if summary.entries_processed > 0:
            error_rate_pct = (summary.error_rate * 100)
            lines.append(f"  • Error rate: {error_rate_pct:.1f}%")

        # Confidence indicator
        confidence_emoji = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴",
        }.get(summary.overall_confidence.level.lower(), "⚪")
        lines.append(f"\n{confidence_emoji} **Overall Confidence: {summary.overall_confidence.level.upper()}** ({summary.overall_confidence.score:.1%})")
        if summary.overall_confidence.factors:
            lines.append("  Factors:")
            for factor in summary.overall_confidence.factors:
                lines.append(f"    • {factor}")

        # Coverage
        lines.append("\n**Validation Coverage:**")
        for stage, covered in summary.coverage.items():
            status = "✅ Covered" if covered else "⏭️ Not validated"
            lines.append(f"  • {stage.title()}: {status}")

        return "\n".join(lines)
