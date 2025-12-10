"""Auto-fix suggestions for validation errors."""

from dataclasses import dataclass
from typing import Optional

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.validation.error_detector import DetectedError


# Confidence levels
CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"


@dataclass
class AutoFixSuggestion:
    """Auto-fix suggestion for an error."""

    error: DetectedError
    suggested_value: any
    confidence: str  # high, medium, low
    fix_reason: str
    before_value: any
    after_value: any
    requires_approval: bool = True  # All fixes require approval

    def __str__(self) -> str:
        """Return human-readable fix suggestion."""
        return (
            f"Error: {self.error.error_message}\n"
            f"Suggested fix: Change '{self.before_value}' to '{self.after_value}'\n"
            f"Confidence: {self.confidence.upper()}\n"
            f"Reason: {self.fix_reason}"
        )


class AutoFixSuggester:
    """
    Suggests automatic fixes for common validation errors.

    Identifies fixable errors and suggests corrections with confidence scores.
    All suggestions require expert review and approval before application.
    """

    def __init__(
        self,
        account_hierarchy: Optional[AccountHierarchy] = None,
        known_types: Optional[list[str]] = None,
    ):
        """
        Initialize AutoFixSuggester.

        Args:
            account_hierarchy: Optional AccountHierarchy for account code suggestions
            known_types: Optional list of known journal entry types (e.g., ['OL', 'CR', 'DR'])
        """
        self.account_hierarchy = account_hierarchy
        self.known_types = known_types or []

    def suggest_fixes(
        self, errors: list[DetectedError]
    ) -> list[AutoFixSuggestion]:
        """
        Suggest auto-fixes for a list of errors.

        Args:
            errors: List of DetectedError objects

        Returns:
            List of AutoFixSuggestion objects (only high/medium confidence suggestions)
        """
        suggestions: list[AutoFixSuggestion] = []

        for error in errors:
            suggestion = self._suggest_fix_for_error(error)
            if suggestion and suggestion.confidence in [CONFIDENCE_HIGH, CONFIDENCE_MEDIUM]:
                suggestions.append(suggestion)

        return suggestions

    def _suggest_fix_for_error(
        self, error: DetectedError
    ) -> Optional[AutoFixSuggestion]:
        """
        Suggest a fix for a single error.

        Args:
            error: DetectedError to analyze

        Returns:
            AutoFixSuggestion if a fix can be suggested, None otherwise
        """
        field_name = error.field_name.lower()
        error_msg_lower = error.error_message.lower()
        actual_value = error.actual_value

        # Typo correction for old_type (common pattern: "0L" vs "OL")
        if "old_type" in field_name or "type" in field_name:
            if actual_value and isinstance(actual_value, str):
                suggestion = self._suggest_type_typo_fix(error, actual_value)
                if suggestion:
                    return suggestion

        # Case mismatch (e.g., "ol" vs "OL")
        if actual_value and isinstance(actual_value, str):
            suggestion = self._suggest_case_fix(error, actual_value)
            if suggestion:
                return suggestion

        # Account code typo (if hierarchy available)
        if "account_code" in field_name and self.account_hierarchy:
            if actual_value and isinstance(actual_value, str):
                suggestion = self._suggest_account_code_fix(error, actual_value)
                if suggestion:
                    return suggestion

        return None

    def _suggest_type_typo_fix(
        self, error: DetectedError, actual_value: str
    ) -> Optional[AutoFixSuggestion]:
        """
        Suggest fix for type field typos.

        Args:
            error: DetectedError
            actual_value: Actual value string

        Returns:
            AutoFixSuggestion if typo found, None otherwise
        """
        if not self.known_types:
            return None

        actual_upper = actual_value.upper()

        # Check for common typos (character substitutions)
        for known_type in self.known_types:
            known_upper = known_type.upper()

            # Exact match (case difference)
            if actual_upper == known_upper and actual_value != known_type:
                return AutoFixSuggestion(
                    error=error,
                    suggested_value=known_type,
                    confidence=CONFIDENCE_HIGH,
                    fix_reason=f"Case mismatch: '{actual_value}' should be '{known_type}'",
                    before_value=actual_value,
                    after_value=known_type,
                )

            # Single character typo (e.g., "0L" vs "OL", "1L" vs "OL")
            if len(actual_value) == len(known_type):
                diff_count = sum(c1 != c2 for c1, c2 in zip(actual_upper, known_upper))
                if diff_count == 1:
                    # Check if it's a common typo pattern
                    if self._is_likely_typo(actual_upper, known_upper):
                        return AutoFixSuggestion(
                            error=error,
                            suggested_value=known_type,
                            confidence=CONFIDENCE_HIGH,
                            fix_reason=f"Likely typo: '{actual_value}' should be '{known_type}'",
                            before_value=actual_value,
                            after_value=known_type,
                        )

        return None

    def _is_likely_typo(self, actual: str, expected: str) -> bool:
        """
        Check if actual value is a likely typo of expected value.

        Common typo patterns: O/0, I/1, S/5, etc.

        Args:
            actual: Actual value
            expected: Expected value

        Returns:
            True if likely typo, False otherwise
        """
        # Common typo character pairs
        typo_pairs = [
            ("0", "O"),
            ("O", "0"),
            ("1", "I"),
            ("I", "1"),
            ("5", "S"),
            ("S", "5"),
            ("Z", "2"),
            ("2", "Z"),
        ]

        for i, (a_char, e_char) in enumerate(zip(actual, expected)):
            if a_char != e_char:
                if (a_char, e_char) in typo_pairs:
                    # Check if rest of string matches
                    if actual[:i] + actual[i + 1 :] == expected[:i] + expected[i + 1 :]:
                        return True

        return False

    def _suggest_case_fix(
        self, error: DetectedError, actual_value: str
    ) -> Optional[AutoFixSuggestion]:
        """
        Suggest fix for case mismatches.

        Args:
            error: DetectedError
            actual_value: Actual value string

        Returns:
            AutoFixSuggestion if case mismatch found, None otherwise
        """
        if not self.known_types:
            return None

        actual_lower = actual_value.lower()
        actual_upper = actual_value.upper()

        # Check if lowercase or uppercase version matches a known type
        for known_type in self.known_types:
            known_lower = known_type.lower()
            known_upper = known_type.upper()

            # Lowercase matches but value is mixed case
            if actual_lower == known_lower and actual_value != known_type:
                # Only suggest if it's a case-only difference
                if actual_upper == known_upper:
                    return AutoFixSuggestion(
                        error=error,
                        suggested_value=known_type,
                        confidence=CONFIDENCE_MEDIUM,
                        fix_reason=f"Case mismatch: standardize to '{known_type}'",
                        before_value=actual_value,
                        after_value=known_type,
                    )

        return None

    def _suggest_account_code_fix(
        self, error: DetectedError, actual_value: str
    ) -> Optional[AutoFixSuggestion]:
        """
        Suggest fix for account code typos.

        Args:
            error: DetectedError
            actual_value: Actual account code value

        Returns:
            AutoFixSuggestion if close match found, None otherwise
        """
        if not self.account_hierarchy:
            return None

        all_accounts = self.account_hierarchy.get_all_accounts()
        valid_codes = [acc.code for acc in all_accounts]

        # Exact case-insensitive match
        actual_upper = actual_value.upper()
        for code in valid_codes:
            if code.upper() == actual_upper and code != actual_value:
                return AutoFixSuggestion(
                    error=error,
                    suggested_value=code,
                    confidence=CONFIDENCE_HIGH,
                    fix_reason=f"Case mismatch: '{actual_value}' should be '{code}'",
                    before_value=actual_value,
                    after_value=code,
                )

        # Find close matches (Levenshtein distance)
        close_matches = self._find_close_matches(actual_value, valid_codes, max_distance=1)

        if len(close_matches) == 1:
            # Single close match - medium confidence
            suggested_code = close_matches[0]
            return AutoFixSuggestion(
                error=error,
                suggested_value=suggested_code,
                confidence=CONFIDENCE_MEDIUM,
                fix_reason=(
                    f"Close match found: '{actual_value}' is similar to "
                    f"'{suggested_code}' (typo likely)"
                ),
                before_value=actual_value,
                after_value=suggested_code,
            )
        elif len(close_matches) > 1:
            # Multiple close matches - low confidence, don't suggest
            return None

        return None

    def _find_close_matches(
        self, value: str, candidates: list[str], max_distance: int = 1
    ) -> list[str]:
        """
        Find close matches using simple edit distance.

        Args:
            value: Value to match
            candidates: List of candidate strings
            max_distance: Maximum edit distance for a match

        Returns:
            List of close matching strings
        """
        matches = []

        for candidate in candidates:
            distance = self._simple_edit_distance(value.lower(), candidate.lower())
            if distance <= max_distance:
                matches.append(candidate)

        return matches

    def _simple_edit_distance(self, s1: str, s2: str) -> int:
        """
        Calculate simple edit distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance (number of character differences)
        """
        if len(s1) != len(s2):
            # Only handle same-length strings for now
            return max(len(s1), len(s2))

        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
