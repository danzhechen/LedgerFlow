"""Rule application logic for veritas-accounting."""

from dataclasses import dataclass
from typing import Any

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.engine import RuleEvaluator
from veritas_accounting.utils.exceptions import RuleError


@dataclass
class RuleApplicationResult:
    """
    Result of applying rules to a journal entry.

    Contains the generated ledger entries and metadata about which rules were applied.
    """

    ledger_entries: list[LedgerEntry]
    applied_rules: list[MappingRule]
    no_match: bool
    entry_id: str


class RuleApplicator:
    """
    Applies mapping rules to journal entries.

    Evaluates rules against journal entries, handles priority, and generates ledger entries.
    """

    def __init__(self, rules: list[MappingRule]) -> None:
        """
        Initialize RuleApplicator with a list of rules.

        Args:
            rules: List of MappingRule objects to apply
        """
        self.rules = rules
        self.evaluator = RuleEvaluator()

        # Pre-compile all rules to catch syntax errors early
        compilation_errors = self.evaluator.compile_rules(rules)
        if compilation_errors:
            error_messages = "\n".join(
                f"  Rule {rule_id}: {error}"
                for rule_id, error in compilation_errors.items()
            )
            raise RuleError(
                f"Rule compilation errors:\n{error_messages}"
            )

        # Sort rules by priority (higher priority first)
        self._sorted_rules = sorted(
            self.rules, key=lambda r: r.priority, reverse=True
        )

    def apply_rules(
        self, entry: JournalEntry, account_hierarchy: Any = None
    ) -> RuleApplicationResult:
        """
        Apply all rules to a journal entry.

        Args:
            entry: JournalEntry to apply rules to
            account_hierarchy: AccountHierarchy object (optional, for validation)

        Returns:
            RuleApplicationResult containing:
            - ledger_entries: List of generated LedgerEntry objects
            - applied_rules: List of rules that matched and were applied
            - no_match: True if no rules matched
            - entry_id: Journal entry ID
        """
        matching_rules: list[MappingRule] = []

        # Evaluate all rules against the entry
        for rule in self._sorted_rules:
            matches, error = self.evaluator.evaluate(rule, entry)

            if error:
                # Log error but continue with other rules
                # In production, might want to collect these errors
                continue

            if matches:
                matching_rules.append(rule)

        # Handle no-match case
        if not matching_rules:
            return RuleApplicationResult(
                ledger_entries=[],
                applied_rules=[],
                no_match=True,
                entry_id=entry.entry_id,
            )

        # Generate ledger entries from matching rules
        ledger_entries = self._generate_ledger_entries(
            entry, matching_rules, account_hierarchy
        )

        return RuleApplicationResult(
            ledger_entries=ledger_entries,
            applied_rules=matching_rules,
            no_match=False,
            entry_id=entry.entry_id,
        )

    def _generate_ledger_entries(
        self,
        entry: JournalEntry,
        rules: list[MappingRule],
        account_hierarchy: Any = None,
    ) -> list[LedgerEntry]:
        """
        Generate ledger entries from matching rules.

        Args:
            entry: JournalEntry source
            rules: List of matching MappingRule objects
            account_hierarchy: AccountHierarchy for validation (optional)

        Returns:
            List of generated LedgerEntry objects
        """
        ledger_entries: list[LedgerEntry] = []

        for rule in rules:
            # Validate account code exists in hierarchy (if provided)
            if account_hierarchy:
                account = account_hierarchy.get_account(rule.account_code)
                if account is None:
                    # Skip this rule if account doesn't exist
                    # In production, might want to log this as an error
                    continue
                account_path = account.full_path
            else:
                # If no hierarchy provided, use account_code as path
                account_path = rule.account_code

            # Determine quarter from entry date
            quarter = self._get_quarter(entry.date)

            # Create ledger entry
            ledger_entry = LedgerEntry(
                entry_id=f"LE-{entry.entry_id}-{rule.rule_id}",
                account_code=rule.account_code,
                account_path=account_path,
                amount=entry.amount,
                date=entry.date,
                description=entry.description,
                source_entry_id=entry.entry_id,
                rule_applied=rule.rule_id,
                quarter=quarter,
                year=entry.year,
            )

            ledger_entries.append(ledger_entry)

            # Handle one-to-many mappings
            if rule.generates_multiple:
                # For one-to-many, we might need to split the amount or create multiple entries
                # This is a simplified version - actual implementation might be more complex
                # based on specific business rules
                # For now, we create one entry per rule, but this could be extended
                pass

        return ledger_entries

    def _get_quarter(self, date: Any) -> int:
        """
        Get quarter (1-4) from a date.

        Args:
            date: datetime object

        Returns:
            Quarter number (1-4)
        """
        from datetime import datetime

        if isinstance(date, datetime):
            month = date.month
        else:
            # Try to extract month from other date types
            month = getattr(date, "month", 1)

        if month in (1, 2, 3):
            return 1
        elif month in (4, 5, 6):
            return 2
        elif month in (7, 8, 9):
            return 3
        else:
            return 4

    def apply_rules_batch(
        self, entries: list[JournalEntry], account_hierarchy: Any = None
    ) -> list[RuleApplicationResult]:
        """
        Apply rules to a batch of journal entries.

        Args:
            entries: List of JournalEntry objects
            account_hierarchy: AccountHierarchy object (optional)

        Returns:
            List of RuleApplicationResult objects, one per entry
        """
        results: list[RuleApplicationResult] = []

        for entry in entries:
            result = self.apply_rules(entry, account_hierarchy)
            results.append(result)

        return results
