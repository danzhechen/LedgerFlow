"""Custom exceptions for veritas-accounting."""


class VeritasAccountingError(Exception):
    """Base exception for all veritas-accounting errors."""

    pass


class ValidationError(VeritasAccountingError):
    """Raised when validation fails."""

    pass


class RuleError(VeritasAccountingError):
    """Raised when rule evaluation or application fails."""

    pass


class TransformationError(VeritasAccountingError):
    """Raised when transformation fails."""

    pass


class ExcelIOError(VeritasAccountingError):
    """Raised when Excel I/O operations fail."""

    pass








