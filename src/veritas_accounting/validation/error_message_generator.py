"""Error message generation for veritas-accounting."""

from typing import Optional

from veritas_accounting.validation.error_detector import DetectedError, ERROR_TYPE_DATA, ERROR_TYPE_RULE, ERROR_TYPE_TRANSFORMATION, ERROR_TYPE_OUTPUT


class ErrorMessageGenerator:
    """
    Generates detailed, user-friendly error messages.

    Creates comprehensive error messages that explain what went wrong,
    why it's an error, and how to fix it.
    """

    def __init__(self, language: str = "en"):
        """
        Initialize ErrorMessageGenerator.

        Args:
            language: Language for error messages ('en' for English, 'zh' for Chinese)
        """
        self.language = language

    def generate_message(self, error: DetectedError) -> str:
        """
        Generate a detailed error message for a detected error.

        Args:
            error: DetectedError object

        Returns:
            Detailed error message string
        """
        if self.language == "zh":
            return self._generate_message_zh(error)
        else:
            return self._generate_message_en(error)

    def _generate_message_en(self, error: DetectedError) -> str:
        """Generate English error message."""
        parts = []

        # Title: Short summary
        title = self._generate_title_en(error)
        parts.append(f"**{title}**")

        # Description: What went wrong
        description = self._generate_description_en(error)
        parts.append(f"\n{description}")

        # Details: Specific values
        details = self._generate_details_en(error)
        if details:
            parts.append(f"\n**Details:** {details}")

        # Location: Where the error occurred
        location = self._generate_location_en(error)
        if location:
            parts.append(f"\n**Location:** {location}")

        # Fix: How to fix
        fix = self._generate_fix_guidance_en(error)
        if fix:
            parts.append(f"\n**How to fix:** {fix}")

        return "\n".join(parts)

    def _generate_message_zh(self, error: DetectedError) -> str:
        """Generate Chinese error message."""
        parts = []

        # Title: Short summary
        title = self._generate_title_zh(error)
        parts.append(f"**{title}**")

        # Description: What went wrong
        description = self._generate_description_zh(error)
        parts.append(f"\n{description}")

        # Details: Specific values
        details = self._generate_details_zh(error)
        if details:
            parts.append(f"\n**详细信息:** {details}")

        # Location: Where the error occurred
        location = self._generate_location_zh(error)
        if location:
            parts.append(f"\n**位置:** {location}")

        # Fix: How to fix
        fix = self._generate_fix_guidance_zh(error)
        if fix:
            parts.append(f"\n**如何修复:** {fix}")

        return "\n".join(parts)

    def _generate_title_en(self, error: DetectedError) -> str:
        """Generate error title in English."""
        error_type = error.error_type
        field_name = error.field_name

        if error_type == ERROR_TYPE_DATA:
            return f"Data Error: Invalid {field_name}"
        elif error_type == ERROR_TYPE_RULE:
            return f"Rule Error: {field_name.replace('_', ' ').title()}"
        elif error_type == ERROR_TYPE_TRANSFORMATION:
            return f"Transformation Error: {field_name.replace('_', ' ').title()}"
        elif error_type == ERROR_TYPE_OUTPUT:
            return f"Output Error: {field_name.replace('_', ' ').title()}"
        else:
            return f"Validation Error: {field_name}"

    def _generate_title_zh(self, error: DetectedError) -> str:
        """Generate error title in Chinese."""
        error_type = error.error_type

        if error_type == ERROR_TYPE_DATA:
            return f"数据错误：无效的{error.field_name}"
        elif error_type == ERROR_TYPE_RULE:
            return f"规则错误：{error.field_name}"
        elif error_type == ERROR_TYPE_TRANSFORMATION:
            return f"转换错误：{error.field_name}"
        elif error_type == ERROR_TYPE_OUTPUT:
            return f"输出错误：{error.field_name}"
        else:
            return f"验证错误：{error.field_name}"

    def _generate_description_en(self, error: DetectedError) -> str:
        """Generate error description in English."""
        # Use the error message, but make it more user-friendly
        msg = error.error_message

        # Enhance common error messages
        if "missing" in msg.lower():
            return (
                f"The required field '{error.field_name}' is missing or empty. "
                f"This field is required for processing and cannot be omitted."
            )
        elif "invalid" in msg.lower():
            return (
                f"The value for '{error.field_name}' is invalid: {error.actual_value}. "
                f"{msg}"
            )
        elif "syntax" in msg.lower():
            return (
                f"The rule condition has invalid syntax: {error.actual_value}. "
                f"{msg}"
            )
        elif "not found" in msg.lower() or "does not exist" in msg.lower():
            return (
                f"The value '{error.actual_value}' referenced in '{error.field_name}' "
                f"does not exist in the system. {msg}"
            )
        else:
            return msg

    def _generate_description_zh(self, error: DetectedError) -> str:
        """Generate error description in Chinese."""
        msg = error.error_message

        if "missing" in msg.lower():
            return (
                f"必填字段 '{error.field_name}' 缺失或为空。"
                f"该字段为处理所必需，不能省略。"
            )
        elif "invalid" in msg.lower():
            return f"字段 '{error.field_name}' 的值无效：{error.actual_value}。{msg}"
        elif "syntax" in msg.lower():
            return f"规则条件语法无效：{error.actual_value}。{msg}"
        elif "not found" in msg.lower() or "does not exist" in msg.lower():
            return (
                f"字段 '{error.field_name}' 中引用的值 '{error.actual_value}' "
                f"在系统中不存在。{msg}"
            )
        else:
            return msg

    def _generate_details_en(self, error: DetectedError) -> Optional[str]:
        """Generate error details in English."""
        details_parts = []

        if error.actual_value is not None:
            details_parts.append(f"Actual value: {error.actual_value}")

        if error.expected_value is not None:
            details_parts.append(f"Expected: {error.expected_value}")

        if error.rule_id:
            details_parts.append(f"Rule ID: {error.rule_id}")

        return ", ".join(details_parts) if details_parts else None

    def _generate_details_zh(self, error: DetectedError) -> Optional[str]:
        """Generate error details in Chinese."""
        details_parts = []

        if error.actual_value is not None:
            details_parts.append(f"实际值：{error.actual_value}")

        if error.expected_value is not None:
            details_parts.append(f"期望值：{error.expected_value}")

        if error.rule_id:
            details_parts.append(f"规则ID：{error.rule_id}")

        return "，".join(details_parts) if details_parts else None

    def _generate_location_en(self, error: DetectedError) -> Optional[str]:
        """Generate location information in English."""
        location_parts = []

        if error.row_number > 0:
            location_parts.append(f"Row {error.row_number}")

        if error.entry_id:
            location_parts.append(f"Journal Entry: {error.entry_id}")

        if error.rule_id:
            location_parts.append(f"Mapping Rule: {error.rule_id}")

        return ", ".join(location_parts) if location_parts else None

    def _generate_location_zh(self, error: DetectedError) -> Optional[str]:
        """Generate location information in Chinese."""
        location_parts = []

        if error.row_number > 0:
            location_parts.append(f"第 {error.row_number} 行")

        if error.entry_id:
            location_parts.append(f"日记账条目：{error.entry_id}")

        if error.rule_id:
            location_parts.append(f"映射规则：{error.rule_id}")

        return "，".join(location_parts) if location_parts else None

    def _generate_fix_guidance_en(self, error: DetectedError) -> Optional[str]:
        """Generate fix guidance in English."""
        error_type = error.error_type.lower()
        field_name = error.field_name.lower()
        error_msg_lower = error.error_message.lower()

        # Missing field
        if "missing" in error_msg_lower:
            return (
                f"Add a value for the '{error.field_name}' field. "
                f"This field is required and cannot be empty."
            )

        # Field-specific guidance based on field name
        if "amount" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower or "format" in error_msg_lower:
                return (
                    f"Enter a valid number for '{error.field_name}'. "
                    f"Example: 1000.50 (decimal numbers are allowed)."
                )

        if "date" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower or "format" in error_msg_lower:
                return (
                    f"Enter a valid date for '{error.field_name}'. "
                    f"Format: YYYY-MM-DD (e.g., 2024-01-15)."
                )

        if "year" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower:
                return (
                    f"Enter a valid year for '{error.field_name}'. "
                    f"Must be between 2000 and 2100."
                )

        # Invalid account code
        if "account_code" in field_name or "account" in error_type:
            return (
                f"Update '{error.field_name}' to use a valid account code. "
                f"Check the account hierarchy for available codes."
            )

        # Syntax error
        if "syntax" in error_type:
            return (
                f"Fix the rule condition syntax. Check that all operators (==, !=, >, <) "
                f"are used correctly and all string values are in quotes."
            )

        # Rule conflict
        if "conflict" in error_type:
            return (
                f"Resolve the rule conflict by either: "
                f"(1) Changing one rule's condition to be more specific, "
                f"(2) Adjusting rule priorities, or "
                f"(3) Ensuring conflicting rules have different account codes only if intended."
            )

        # Default guidance
        return f"Review the value for '{error.field_name}' and ensure it meets the requirements."

    def _generate_fix_guidance_zh(self, error: DetectedError) -> Optional[str]:
        """Generate fix guidance in Chinese."""
        error_type = error.error_type.lower()
        field_name = error.field_name.lower()
        error_msg_lower = error.error_message.lower()

        if "missing" in error_msg_lower:
            return f"为字段 '{error.field_name}' 添加值。该字段为必填项，不能为空。"

        # Field-specific guidance
        if "amount" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower or "format" in error_msg_lower:
                return f"为 '{error.field_name}' 输入有效数字。示例：1000.50（允许小数）。"

        if "date" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower or "format" in error_msg_lower:
                return f"为 '{error.field_name}' 输入有效日期。格式：YYYY-MM-DD（例如：2024-01-15）。"

        if "year" in field_name:
            if "type" in error_msg_lower or "invalid" in error_msg_lower:
                return f"为 '{error.field_name}' 输入有效年份。必须在 2000 到 2100 之间。"

        if "account_code" in field_name or "account" in error_type:
            return f"更新 '{error.field_name}' 以使用有效的账户代码。请查看账户层次结构以获取可用代码。"

        if "syntax" in error_type:
            return (
                f"修复规则条件语法。检查所有运算符（==、!=、>、<）是否正确使用，"
                f"所有字符串值是否在引号内。"
            )

        if "conflict" in error_type:
            return (
                f"通过以下方式之一解决规则冲突："
                f"(1) 更改一个规则的条件使其更具体，"
                f"(2) 调整规则优先级，或 "
                f"(3) 确保冲突规则仅在需要时具有不同的账户代码。"
            )

        return f"检查字段 '{error.field_name}' 的值，确保其符合要求。"
