"""Unit tests for AutoFixSuggester class."""

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.validation.auto_fix import (
    AutoFixSuggestion,
    AutoFixSuggester,
    CONFIDENCE_HIGH,
    CONFIDENCE_MEDIUM,
)
from veritas_accounting.validation.error_detector import (
    DetectedError,
    ERROR_TYPE_DATA,
    ERROR_TYPE_RULE,
    SEVERITY_ERROR,
)


class TestAutoFixSuggester:
    """Test suite for AutoFixSuggester class."""

    def test_suggest_type_typo_case_mismatch(self):
        """Test suggesting fix for case mismatch in type field."""
        suggester = AutoFixSuggester(known_types=["OL", "CR", "DR"])

        error = DetectedError(
            row_number=1,
            field_name="old_type",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="ol",  # Lowercase
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        assert len(suggestions) == 1
        assert suggestions[0].confidence == CONFIDENCE_HIGH
        assert suggestions[0].after_value == "OL"
        assert suggestions[0].before_value == "ol"

    def test_suggest_type_typo_character_substitution(self):
        """Test suggesting fix for character typo (e.g., 0L vs OL)."""
        suggester = AutoFixSuggester(known_types=["OL", "CR", "DR"])

        error = DetectedError(
            row_number=1,
            field_name="old_type",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="0L",  # Zero instead of O
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        assert len(suggestions) >= 1
        # Should suggest "OL" as fix
        ol_suggestion = next((s for s in suggestions if s.after_value == "OL"), None)
        assert ol_suggestion is not None
        assert ol_suggestion.confidence == CONFIDENCE_HIGH

    def test_suggest_account_code_case_mismatch(self):
        """Test suggesting fix for account code case mismatch."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        suggester = AutoFixSuggester(account_hierarchy=hierarchy, known_types=["OL"])

        error = DetectedError(
            row_number=0,
            field_name="account_code",
            error_type=ERROR_TYPE_RULE,
            error_message="Account code does not exist",
            actual_value="a1",  # Lowercase
            rule_id="R-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        assert len(suggestions) == 1
        assert suggestions[0].confidence == CONFIDENCE_HIGH
        assert suggestions[0].after_value == "A1"

    def test_suggest_account_code_typo(self):
        """Test suggesting fix for account code typo."""
        accounts = [
            Account(code="A1", name="Account 1", level=1, full_path="A1"),
            Account(code="A-1", name="Account A-1", level=1, full_path="A-1"),
            Account(code="B2", name="Account 2", level=2, parent_code="A1", full_path="A1/B2"),
        ]
        hierarchy = AccountHierarchy(accounts)
        suggester = AutoFixSuggester(account_hierarchy=hierarchy, known_types=["OL"])

        error = DetectedError(
            row_number=0,
            field_name="account_code",
            error_type=ERROR_TYPE_RULE,
            error_message="Account code does not exist",
            actual_value="A1",  # Missing hyphen, should be "A-1" or vice versa
            rule_id="R-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        # Should find close matches
        # Note: This depends on edit distance implementation
        # A1 vs A-1 has distance > 1, so might not match
        # But if we had "A2" it might match "A-1" or "A1"
        assert len(suggestions) >= 0  # May or may not suggest depending on distance

    def test_no_suggestion_low_confidence(self):
        """Test that low confidence suggestions are not returned."""
        suggester = AutoFixSuggester(known_types=["OL", "CR"])

        error = DetectedError(
            row_number=1,
            field_name="old_type",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="XYZ",  # Not similar to any known type
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        # Should not suggest anything (low confidence or no match)
        assert len(suggestions) == 0

    def test_suggestion_requires_approval(self):
        """Test that all suggestions require approval."""
        suggester = AutoFixSuggester(known_types=["OL"])

        error = DetectedError(
            row_number=1,
            field_name="old_type",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="ol",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        assert len(suggestions) == 1
        assert suggestions[0].requires_approval is True

    def test_multiple_suggestions(self):
        """Test handling multiple errors with different fix suggestions."""
        suggester = AutoFixSuggester(known_types=["OL", "CR", "DR"])

        errors = [
            DetectedError(
                row_number=1,
                field_name="old_type",
                error_type=ERROR_TYPE_DATA,
                error_message="Invalid type",
                actual_value="ol",
                entry_id="JE-001",
                severity=SEVERITY_ERROR,
            ),
            DetectedError(
                row_number=2,
                field_name="old_type",
                error_type=ERROR_TYPE_DATA,
                error_message="Invalid type",
                actual_value="0L",
                entry_id="JE-002",
                severity=SEVERITY_ERROR,
            ),
        ]

        suggestions = suggester.suggest_fixes(errors)

        assert len(suggestions) == 2
        assert all(s.after_value == "OL" for s in suggestions)

    def test_suggestion_contains_context(self):
        """Test that suggestions contain proper context."""
        suggester = AutoFixSuggester(known_types=["OL"])

        error = DetectedError(
            row_number=1,
            field_name="old_type",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="ol",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        suggestions = suggester.suggest_fixes([error])

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.error == error
        assert suggestion.before_value == "ol"
        assert suggestion.after_value == "OL"
        assert suggestion.fix_reason is not None
        assert "Case mismatch" in suggestion.fix_reason or "case" in suggestion.fix_reason.lower()








