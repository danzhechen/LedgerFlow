"""Rule engine integration for veritas-accounting."""

from typing import Any

from rule_engine import Rule

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.utils.exceptions import RuleError


class RuleEvaluator:
    """
    Evaluates mapping rule conditions against journal entries.

    Wraps the rule-engine library to provide a clean interface for rule evaluation.
    """

    def __init__(self) -> None:
        """Initialize RuleEvaluator."""
        self._compiled_rules: dict[str, Rule] = {}

    def evaluate(
        self, rule: MappingRule, entry: JournalEntry
    ) -> tuple[bool, str | None]:
        """
        Evaluate a rule condition against a journal entry.

        Args:
            rule: MappingRule to evaluate
            entry: JournalEntry to evaluate against

        Returns:
            Tuple of (matches: bool, error_message: str | None)
            - matches: True if rule condition matches entry, False otherwise
            - error_message: Error message if evaluation failed, None if successful

        Raises:
            RuleError: If rule syntax is invalid and cannot be compiled
        """
        try:
            # Get or compile the rule
            compiled_rule = self._get_compiled_rule(rule)

            # Convert journal entry to dictionary for rule evaluation
            entry_dict = self._entry_to_dict(entry)

            # Evaluate the rule
            result = compiled_rule.matches(entry_dict)

            return bool(result), None

        except Exception as e:
            error_msg = (
                f"Error evaluating rule {rule.rule_id}: {str(e)}. "
                f"Condition: {rule.condition}"
            )
            return False, error_msg

    def _get_compiled_rule(self, rule: MappingRule) -> Rule:
        """
        Get compiled rule, compiling if necessary.

        Args:
            rule: MappingRule to compile

        Returns:
            Compiled Rule object

        Raises:
            RuleError: If rule cannot be compiled
        """
        # Use rule_id as cache key
        cache_key = rule.rule_id

        if cache_key not in self._compiled_rules:
            try:
                # Compile the rule condition
                compiled = Rule(rule.condition)
                self._compiled_rules[cache_key] = compiled
            except Exception as e:
                raise RuleError(
                    f"Invalid rule syntax in rule {rule.rule_id}: {str(e)}. "
                    f"Condition: {rule.condition}"
                ) from e

        return self._compiled_rules[cache_key]

    def _entry_to_dict(self, entry: JournalEntry) -> dict[str, Any]:
        """
        Convert JournalEntry to dictionary for rule evaluation.

        Args:
            entry: JournalEntry to convert

        Returns:
            Dictionary representation of the entry
        """
        # Use model_dump() to get all fields as dict
        entry_dict = entry.model_dump()

        # Ensure all values are rule-engine compatible
        # Convert Decimal to float for rule-engine
        from decimal import Decimal

        for key, value in entry_dict.items():
            if isinstance(value, Decimal):
                entry_dict[key] = float(value)

        return entry_dict

    def clear_cache(self) -> None:
        """Clear the compiled rules cache."""
        self._compiled_rules.clear()

    def compile_rules(self, rules: list[MappingRule]) -> dict[str, str]:
        """
        Pre-compile all rules and return any compilation errors.

        Args:
            rules: List of MappingRule objects to compile

        Returns:
            Dictionary mapping rule_id to error message (empty if no errors)
        """
        errors: dict[str, str] = {}

        for rule in rules:
            try:
                self._get_compiled_rule(rule)
            except RuleError as e:
                errors[rule.rule_id] = str(e)

        return errors
