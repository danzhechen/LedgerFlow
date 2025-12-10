"""Validation modules for veritas-accounting."""

from veritas_accounting.validation.auto_fix import (
    AutoFixSuggestion,
    AutoFixSuggester,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
)
from veritas_accounting.validation.error_detector import (
    DetectedError,
    ErrorDetector,
    ErrorGroup,
    ERROR_TYPE_DATA,
    ERROR_TYPE_OUTPUT,
    ERROR_TYPE_RULE,
    ERROR_TYPE_TRANSFORMATION,
    SEVERITY_CRITICAL,
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
)
from veritas_accounting.validation.error_message_generator import ErrorMessageGenerator
from veritas_accounting.validation.input_validator import (
    JournalEntryValidator,
    ValidationError,
)
from veritas_accounting.validation.output_validator import OutputValidator
from veritas_accounting.validation.pipeline import (
    InputValidationPipeline,
    ValidationResult,
    ValidationWarning,
)
from veritas_accounting.validation.rule_validator import MappingRuleValidator
from veritas_accounting.validation.transformation_validator import (
    TransformationValidator,
)
from veritas_accounting.validation.validation_results import (
    ConfidenceScore,
    ValidationResultsViewer,
    ValidationSummary,
)

__all__ = [
    "JournalEntryValidator",
    "MappingRuleValidator",
    "ValidationError",
    "InputValidationPipeline",
    "ValidationResult",
    "ValidationWarning",
    "TransformationValidator",
    "OutputValidator",
    "ErrorDetector",
    "DetectedError",
    "ErrorGroup",
    "ErrorMessageGenerator",
    "AutoFixSuggester",
    "AutoFixSuggestion",
    "ValidationResultsViewer",
    "ValidationSummary",
    "ConfidenceScore",
    "ERROR_TYPE_DATA",
    "ERROR_TYPE_RULE",
    "ERROR_TYPE_TRANSFORMATION",
    "ERROR_TYPE_OUTPUT",
    "SEVERITY_CRITICAL",
    "SEVERITY_ERROR",
    "SEVERITY_WARNING",
    "SEVERITY_INFO",
    "CONFIDENCE_HIGH",
    "CONFIDENCE_MEDIUM",
    "CONFIDENCE_LOW",
]
