"""Mapping rule validation for veritas-accounting."""

import re
from typing import Optional

from rule_engine import Rule, RuleSyntaxError

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.validation.input_validator import ValidationError

# Valid JournalEntry field names that can be used in rule conditions
VALID_JOURNAL_ENTRY_FIELDS = {
    "entry_id",
    "year",
    "description",
    "old_type",
    "amount",
    "date",
    "quarter",
    "notes",
}


class MappingRuleValidator:
    """
    Validates mapping rules for structure, syntax, and logic.

    Performs comprehensive validation including:
    - Rule syntax validation (rule-engine expressions)
    - Field reference validation (condition fields match JournalEntry fields)
    - Account code validation (codes exist in hierarchy)
    - Conflict detection (same condition → different results)
    - Priority validation
    """

    def __init__(self, account_hierarchy: Optional[AccountHierarchy] = None):
        """
        Initialize MappingRuleValidator.

        Args:
            account_hierarchy: Optional AccountHierarchy for account code validation.
                              If None, account code validation is skipped.
        """
        self.account_hierarchy = account_hierarchy

    def validate_rules(
        self, rules: list[MappingRule]
    ) -> tuple[list[MappingRule], list[ValidationError]]:
        """
        Validate a list of mapping rules.

        Args:
            rules: List of MappingRule objects to validate

        Returns:
            Tuple of (valid_rules, errors) where:
            - valid_rules: List of validated MappingRule objects
            - errors: List of ValidationError objects categorized by type
        """
        valid_rules: list[MappingRule] = []
        errors: list[ValidationError] = []

        # Track rules by condition for conflict detection
        condition_map: dict[str, list[MappingRule]] = {}

        for rule in rules:
            rule_errors: list[ValidationError] = []

            # 1. Validate rule syntax
            syntax_error = self._validate_syntax(rule)
            if syntax_error:
                rule_errors.append(syntax_error)
                errors.extend(rule_errors)
                continue  # Skip further validation if syntax is invalid

            # 2. Validate field references in condition
            field_errors = self._validate_field_references(rule)
            rule_errors.extend(field_errors)

            # 3. Validate required fields
            required_errors = self._validate_required_fields(rule)
            rule_errors.extend(required_errors)

            # 4. Validate account code (if hierarchy provided)
            if self.account_hierarchy:
                account_error = self._validate_account_code(rule)
                if account_error:
                    rule_errors.append(account_error)

            # If no errors so far, add to valid rules and track for conflict detection
            if not rule_errors:
                valid_rules.append(rule)
                # Normalize condition for conflict detection (strip whitespace, lowercase)
                normalized_condition = rule.condition.strip().lower()
                if normalized_condition not in condition_map:
                    condition_map[normalized_condition] = []
                condition_map[normalized_condition].append(rule)
            else:
                errors.extend(rule_errors)

        # 5. Detect conflicts (same condition → different results)
        conflict_errors = self._detect_conflicts(condition_map)
        errors.extend(conflict_errors)

        # 6. Validate priorities (check for duplicates if needed)
        priority_errors = self._validate_priorities(valid_rules)
        errors.extend(priority_errors)

        return valid_rules, errors

    def _validate_syntax(self, rule: MappingRule) -> Optional[ValidationError]:
        """
        Validate rule condition syntax using rule-engine.

        Args:
            rule: MappingRule to validate

        Returns:
            ValidationError if syntax is invalid, None otherwise
        """
        try:
            # Try to parse the condition using rule-engine
            Rule(rule.condition)
            return None
        except RuleSyntaxError as e:
            return ValidationError(
                row_number=0,  # Row number not available at this level
                field_name="condition",
                error_type="syntax_error",
                error_message=f"Invalid rule syntax: {str(e)}",
                actual_value=rule.condition,
                entry_id=rule.rule_id,
            )
        except Exception as e:
            return ValidationError(
                row_number=0,
                field_name="condition",
                error_type="syntax_error",
                error_message=f"Error parsing rule condition: {str(e)}",
                actual_value=rule.condition,
                entry_id=rule.rule_id,
            )

    def _validate_field_references(
        self, rule: MappingRule
    ) -> list[ValidationError]:
        """
        Validate that condition fields reference valid JournalEntry fields.

        Args:
            rule: MappingRule to validate

        Returns:
            List of ValidationError objects for invalid field references
        """
        errors: list[ValidationError] = []

        # First, remove string literals from condition to avoid false positives
        # Replace quoted strings with placeholders
        string_pattern = r'(["\'][^"\']*["\'])'
        string_placeholders: dict[str, str] = {}
        condition_without_strings = rule.condition
        placeholder_idx = 0

        for match in re.finditer(string_pattern, rule.condition):
            placeholder = f"__STRING_{placeholder_idx}__"
            string_placeholders[placeholder] = match.group(0)
            condition_without_strings = condition_without_strings.replace(
                match.group(0), placeholder, 1
            )
            placeholder_idx += 1

        # Extract field names from condition using regex
        # Pattern matches identifiers (field names) in rule-engine expressions
        # Matches: word characters, dots, underscores (for field access like "entry.year")
        field_pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)\b"

        # Find all potential field references
        matches = re.findall(field_pattern, condition_without_strings)

        # Filter out operators, literals, and known rule-engine keywords
        rule_engine_keywords = {
            "and",
            "or",
            "not",
            "in",
            "is",
            "true",
            "false",
            "none",
            "null",
        }

        seen_fields = set()  # Track fields we've already reported

        for match in matches:
            # Skip if it's a placeholder (was a string literal)
            if match.startswith("__STRING_"):
                continue

            # Skip if it's a keyword or operator
            if match.lower() in rule_engine_keywords:
                continue

            # Skip if it's a number
            try:
                float(match)
                continue
            except ValueError:
                pass

            # Extract base field name (before any dot)
            base_field = match.split(".")[0]

            # Skip if we've already reported this field
            if base_field in seen_fields:
                continue

            # Check if field is valid JournalEntry field
            if base_field not in VALID_JOURNAL_ENTRY_FIELDS:
                seen_fields.add(base_field)
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="condition",
                        error_type="invalid_field_reference",
                        error_message=(
                            f"Field '{base_field}' in condition does not exist in JournalEntry. "
                            f"Valid fields: {', '.join(sorted(VALID_JOURNAL_ENTRY_FIELDS))}"
                        ),
                        actual_value=rule.condition,
                        entry_id=rule.rule_id,
                    )
                )

        return errors

    def _validate_required_fields(self, rule: MappingRule) -> list[ValidationError]:
        """
        Validate that required fields are present.

        According to the story, required fields are:
        - condition (already validated by Pydantic)
        - old_type OR new_type (at least one should be present)
        - account_code (already validated by Pydantic)

        Args:
            rule: MappingRule to validate

        Returns:
            List of ValidationError objects for missing required fields
        """
        errors: list[ValidationError] = []

        # Check that at least one of old_type or new_type is present
        if not rule.old_type and not rule.new_type:
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name="old_type,new_type",
                    error_type="missing_field",
                    error_message=(
                        "At least one of 'old_type' or 'new_type' must be specified"
                    ),
                    actual_value=None,
                    entry_id=rule.rule_id,
                )
            )

        return errors

    def _validate_account_code(
        self, rule: MappingRule
    ) -> Optional[ValidationError]:
        """
        Validate that account code exists in the account hierarchy.

        Args:
            rule: MappingRule to validate

        Returns:
            ValidationError if account code is invalid, None otherwise
        """
        if not self.account_hierarchy:
            return None

        account = self.account_hierarchy.get_account(rule.account_code)
        if account is None:
            # Get list of available account codes for error message
            all_accounts = self.account_hierarchy.get_all_accounts()
            available_codes = ", ".join(
                sorted([acc.code for acc in all_accounts[:10]])
            )  # Show first 10
            if len(all_accounts) > 10:
                available_codes += f", ... ({len(all_accounts)} total)"

            return ValidationError(
                row_number=0,
                field_name="account_code",
                error_type="invalid_account_code",
                error_message=(
                    f"Account code '{rule.account_code}' does not exist in account hierarchy. "
                    f"Available codes: {available_codes}"
                ),
                actual_value=rule.account_code,
                entry_id=rule.rule_id,
            )

        return None

    def _detect_conflicts(
        self, condition_map: dict[str, list[MappingRule]]
    ) -> list[ValidationError]:
        """
        Detect conflicting rules (same condition → different results).

        Args:
            condition_map: Dictionary mapping normalized conditions to lists of rules

        Returns:
            List of ValidationError objects for conflicts
        """
        errors: list[ValidationError] = []

        for normalized_condition, rules in condition_map.items():
            if len(rules) <= 1:
                continue  # No conflict if only one rule

            # Check if rules have different results (different account_code or different priority)
            # Rules with same condition but different priorities are OK (priority resolves conflict)
            # Rules with same condition, same priority, but different account_code are conflicts

            # Group by priority
            by_priority: dict[int, list[MappingRule]] = {}
            for rule in rules:
                if rule.priority not in by_priority:
                    by_priority[rule.priority] = []
                by_priority[rule.priority].append(rule)

            # Check for conflicts within same priority
            for priority, same_priority_rules in by_priority.items():
                if len(same_priority_rules) <= 1:
                    continue

                # Check if they have different account codes
                account_codes = {rule.account_code for rule in same_priority_rules}
                if len(account_codes) > 1:
                    # Conflict: same condition, same priority, different account codes
                    rule_ids = ", ".join([rule.rule_id for rule in same_priority_rules])
                    errors.append(
                        ValidationError(
                            row_number=0,
                            field_name="condition,account_code",
                            error_type="rule_conflict",
                            error_message=(
                                f"Multiple rules with same condition and priority ({priority}) "
                                f"but different account codes: {', '.join(account_codes)}. "
                                f"Rule IDs: {rule_ids}"
                            ),
                            actual_value=normalized_condition,
                            entry_id=rule_ids,
                        )
                    )

        return errors

    def _validate_priorities(
        self, rules: list[MappingRule]
    ) -> list[ValidationError]:
        """
        Validate rule priorities.

        Currently, we allow duplicate priorities (conflicts are handled separately).
        This method can be extended to enforce unique priorities if needed.

        Args:
            rules: List of MappingRule objects

        Returns:
            List of ValidationError objects for priority issues
        """
        errors: list[ValidationError] = []

        # For now, we don't enforce unique priorities
        # Duplicate priorities are allowed, and conflicts are detected separately
        # This gives flexibility - rules can have same priority if they don't conflict

        # Could add validation here if needed:
        # - Check for priority ranges
        # - Warn about duplicate priorities
        # - etc.

        return errors
