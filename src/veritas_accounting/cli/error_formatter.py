"""CLI error message formatting for veritas-accounting."""

import click
from typing import Optional

from veritas_accounting.validation.error_detector import DetectedError
from veritas_accounting.validation.error_message_generator import ErrorMessageGenerator


class CLIErrorFormatter:
    """
    Formats error messages for CLI output with colors and actionable guidance.

    Enhances ErrorMessageGenerator output for terminal display with:
    - Color coding (red for errors, yellow for warnings)
    - Simplified format for console
    - Actionable guidance
    - Examples when helpful
    """

    def __init__(self, use_colors: bool = True) -> None:
        """
        Initialize CLIErrorFormatter.

        Args:
            use_colors: Whether to use colored output (default: True)
        """
        # Check if colors should be used
        try:
            ctx = click.get_current_context(silent=True)
            if ctx:
                self.use_colors = use_colors and not ctx.color
            else:
                self.use_colors = use_colors
        except RuntimeError:
            # No click context available
            self.use_colors = use_colors
        self.message_generator = ErrorMessageGenerator()

    def format_error(self, error: DetectedError, verbose: bool = False) -> str:
        """
        Format error for CLI display.

        Args:
            error: DetectedError object
            verbose: If True, show detailed message; if False, show simplified message

        Returns:
            Formatted error message string
        """
        if verbose:
            return self._format_detailed_error(error)
        else:
            return self._format_simple_error(error)

    def _format_simple_error(self, error: DetectedError) -> str:
        """Format simplified error message for console."""
        severity_color = self._get_severity_color(error.severity)
        error_type_icon = self._get_error_type_icon(error.error_type)

        # Build simple message
        parts = []

        # Icon and severity
        if self.use_colors:
            severity_text = click.style(
                error.severity.upper(), fg=severity_color, bold=True
            )
        else:
            severity_text = f"[{error.severity.upper()}]"

        parts.append(f"{error_type_icon} {severity_text}")

        # Location
        location_parts = []
        if error.entry_id:
            location_parts.append(f"Entry: {error.entry_id}")
        if error.rule_id:
            location_parts.append(f"Rule: {error.rule_id}")
        if error.row_number:
            location_parts.append(f"Row: {error.row_number}")

        if location_parts:
            parts.append(f"({', '.join(location_parts)})")

        # Error message
        parts.append(f": {error.error_message}")

        # Field and value
        if error.field_name:
            parts.append(f"\n   Field: {error.field_name}")
        if error.actual_value is not None:
            parts.append(f"   Value: {error.actual_value}")

        # Quick fix hint
        fix_hint = self._get_quick_fix_hint(error)
        if fix_hint:
            parts.append(f"\n   💡 {fix_hint}")

        return " ".join(parts)

    def _format_detailed_error(self, error: DetectedError) -> str:
        """Format detailed error message for verbose output."""
        # Use the full error message generator
        full_message = self.message_generator.generate_message(error)

        # Add color coding
        if self.use_colors:
            severity_color = self._get_severity_color(error.severity)
            # Color the title
            lines = full_message.split("\n")
            if lines:
                lines[0] = click.style(lines[0], fg=severity_color, bold=True)
            return "\n".join(lines)

        return full_message

    def format_error_list(
        self, errors: list[DetectedError], max_display: int = 10
    ) -> str:
        """
        Format a list of errors for CLI display.

        Args:
            errors: List of DetectedError objects
            max_display: Maximum number of errors to display (default: 10)

        Returns:
            Formatted error list string
        """
        if not errors:
            return ""

        parts = []
        parts.append(f"\nFound {len(errors)} error(s):\n")

        # Group by severity
        critical = [e for e in errors if e.severity == "critical"]
        error_level = [e for e in errors if e.severity == "error"]
        warnings = [e for e in errors if e.severity == "warning"]

        # Display critical errors first
        if critical:
            parts.append(click.style("Critical Errors:", fg="red", bold=True))
            for err in critical[:max_display]:
                parts.append(f"  {self.format_error(err, verbose=False)}")
            if len(critical) > max_display:
                parts.append(
                    f"  ... and {len(critical) - max_display} more critical errors"
                )

        # Then regular errors
        if error_level:
            parts.append(click.style("\nErrors:", fg="red", bold=True))
            for err in error_level[:max_display]:
                parts.append(f"  {self.format_error(err, verbose=False)}")
            if len(error_level) > max_display:
                parts.append(f"  ... and {len(error_level) - max_display} more errors")

        # Then warnings
        if warnings:
            parts.append(click.style("\nWarnings:", fg="yellow", bold=True))
            for err in warnings[:max_display]:
                parts.append(f"  {self.format_error(err, verbose=False)}")
            if len(warnings) > max_display:
                parts.append(
                    f"  ... and {len(warnings) - max_display} more warnings"
                )

        if len(errors) > max_display:
            parts.append(
                f"\n💡 Tip: Use --verbose flag to see all errors with full details"
            )

        return "\n".join(parts)

    def _get_severity_color(self, severity: str) -> str:
        """
        Get color for severity level.

        Args:
            severity: Severity level (critical, error, warning, info)

        Returns:
            Color name for click.style
        """
        colors = {
            "critical": "red",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
        }
        return colors.get(severity.lower(), "white")

    def _get_error_type_icon(self, error_type: str) -> str:
        """
        Get icon for error type.

        Args:
            error_type: Error type (data_error, rule_error, etc.)

        Returns:
            Icon emoji or symbol
        """
        icons = {
            "data_error": "📊",
            "rule_error": "📋",
            "transformation_error": "🔄",
            "output_error": "📤",
        }
        return icons.get(error_type, "❌")

    def _get_quick_fix_hint(self, error: DetectedError) -> Optional[str]:
        """
        Get quick fix hint for error.

        Args:
            error: DetectedError object

        Returns:
            Quick fix hint string or None
        """
        field_name = error.field_name.lower()
        error_msg_lower = error.error_message.lower()

        # Common fix hints
        if "missing" in error_msg_lower or "required" in error_msg_lower:
            return f"Add the missing '{error.field_name}' field to your input file"

        if "invalid" in error_msg_lower and "type" in error_msg_lower:
            return f"Check that '{error.field_name}' has the correct data type"

        if "not found" in error_msg_lower:
            return f"Verify that the referenced value exists in your data"

        if "duplicate" in error_msg_lower:
            return f"Remove duplicate entry or ensure unique identifiers"

        return None








