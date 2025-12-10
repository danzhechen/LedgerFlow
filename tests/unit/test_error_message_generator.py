"""Unit tests for ErrorMessageGenerator class."""

from veritas_accounting.validation.error_detector import (
    DetectedError,
    ERROR_TYPE_DATA,
    ERROR_TYPE_RULE,
    SEVERITY_ERROR,
)
from veritas_accounting.validation.error_message_generator import ErrorMessageGenerator


class TestErrorMessageGenerator:
    """Test suite for ErrorMessageGenerator class."""

    def test_generate_message_english_basic(self):
        """Test generating basic English error message."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=5,
            field_name="amount",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid amount format",
            actual_value="not-a-number",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "**Data Error: Invalid amount**" in message
        assert "amount" in message
        assert "JE-001" in message
        assert "Row 5" in message

    def test_generate_message_missing_field(self):
        """Test error message for missing field."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=3,
            field_name="description",
            error_type=ERROR_TYPE_DATA,
            error_message="Missing required field 'description'",
            actual_value=None,
            entry_id="JE-002",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "missing" in message.lower()
        assert "required" in message.lower()
        assert "How to fix" in message

    def test_generate_message_syntax_error(self):
        """Test error message for rule syntax error."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=0,
            field_name="condition",
            error_type=ERROR_TYPE_RULE,
            error_message="Invalid rule syntax: syntax error",
            actual_value="old_type == ",
            rule_id="R-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "Rule Error" in message
        assert "syntax" in message.lower()
        assert "R-001" in message
        assert "How to fix" in message

    def test_generate_message_chinese(self):
        """Test generating Chinese error message."""
        generator = ErrorMessageGenerator(language="zh")

        error = DetectedError(
            row_number=5,
            field_name="amount",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid amount format",
            actual_value="not-a-number",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "数据错误" in message
        assert "如何修复" in message
        assert "位置" in message

    def test_generate_message_with_expected_value(self):
        """Test error message includes expected value if provided."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=2,
            field_name="account_code",
            error_type=ERROR_TYPE_RULE,
            error_message="Account code does not exist",
            actual_value="INVALID",
            expected_value="A1, B2, C3",
            rule_id="R-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "Actual value" in message or "INVALID" in message
        assert "Expected" in message or "A1" in message

    def test_generate_message_location_info(self):
        """Test that location information is included."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=10,
            field_name="year",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid year",
            actual_value=1999,
            entry_id="JE-005",
            rule_id=None,
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "Row 10" in message
        assert "Journal Entry: JE-005" in message

    def test_generate_message_fix_guidance_amount(self):
        """Test fix guidance for amount field."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=1,
            field_name="amount",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid type",
            actual_value="text",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "valid number" in message.lower()
        assert "1000.50" in message or "decimal" in message.lower()

    def test_generate_message_fix_guidance_date(self):
        """Test fix guidance for date field."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=1,
            field_name="date",
            error_type=ERROR_TYPE_DATA,
            error_message="Invalid date format",
            actual_value="invalid-date",
            entry_id="JE-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "valid date" in message.lower()
        assert "YYYY-MM-DD" in message or "2024-01-15" in message

    def test_generate_message_fix_guidance_account_code(self):
        """Test fix guidance for account code errors."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=0,
            field_name="account_code",
            error_type=ERROR_TYPE_RULE,
            error_message="Account code does not exist",
            actual_value="INVALID",
            rule_id="R-001",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "valid account code" in message.lower()
        assert "account hierarchy" in message.lower()

    def test_generate_message_fix_guidance_rule_conflict(self):
        """Test fix guidance for rule conflicts."""
        generator = ErrorMessageGenerator(language="en")

        error = DetectedError(
            row_number=0,
            field_name="condition,account_code",
            error_type=ERROR_TYPE_RULE,
            error_message="Rule conflict detected",
            actual_value="old_type == 'OL'",
            rule_id="R-001, R-002",
            severity=SEVERITY_ERROR,
        )

        message = generator.generate_message(error)

        assert "conflict" in message.lower()
        assert "priority" in message.lower() or "condition" in message.lower()
