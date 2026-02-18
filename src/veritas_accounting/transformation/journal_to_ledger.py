"""Journal to Ledger transformation for veritas-accounting."""

from typing import Any

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.applicator import RuleApplicator, RuleApplicationResult
from veritas_accounting.utils.exceptions import TransformationError


class JournalToLedgerTransformer:
    """
    Transforms journal entries to ledger entries using mapping rules.

    Applies mapping rules to journal entries and generates ledger entries
    with hierarchical account structure.
    """

    def __init__(
        self,
        rules: list[MappingRule],
        account_hierarchy: AccountHierarchy | None = None,
    ) -> None:
        """
        Initialize JournalToLedgerTransformer.

        Args:
            rules: List of MappingRule objects to apply
            account_hierarchy: AccountHierarchy object (optional, for validation)
        """
        self.rules = rules
        self.account_hierarchy = account_hierarchy
        self.applicator = RuleApplicator(rules)

    def transform(
        self, entries: list[JournalEntry]
    ) -> tuple[list[LedgerEntry], list[JournalEntry]]:
        """
        Transform journal entries to ledger entries.

        Args:
            entries: List of JournalEntry objects to transform

        Returns:
            Tuple of (ledger_entries, unmatched_entries) where:
            - ledger_entries: List of generated LedgerEntry objects
            - unmatched_entries: List of JournalEntry objects that had no matching rules

        Raises:
            TransformationError: If transformation fails
        """
        all_ledger_entries: list[LedgerEntry] = []
        unmatched_entries: list[JournalEntry] = []

        try:
            # Apply rules to all entries
            results = self.applicator.apply_rules_batch(
                entries, self.account_hierarchy
            )

            # Collect ledger entries and unmatched entries
            for i, result in enumerate(results):
                if result.no_match:
                    unmatched_entries.append(entries[i])
                else:
                    all_ledger_entries.extend(result.ledger_entries)

            return all_ledger_entries, unmatched_entries

        except Exception as e:
            raise TransformationError(
                f"Error transforming journal entries to ledger entries: {str(e)}"
            ) from e

    def transform_entry(
        self, entry: JournalEntry
    ) -> tuple[list[LedgerEntry], bool]:
        """
        Transform a single journal entry to ledger entries.

        Args:
            entry: JournalEntry to transform

        Returns:
            Tuple of (ledger_entries, no_match) where:
            - ledger_entries: List of generated LedgerEntry objects
            - no_match: True if no rules matched

        Raises:
            TransformationError: If transformation fails
        """
        try:
            result = self.applicator.apply_rules(entry, self.account_hierarchy)

            return result.ledger_entries, result.no_match

        except Exception as e:
            raise TransformationError(
                f"Error transforming journal entry {entry.entry_id}: {str(e)}"
            ) from e

    def validate_transformation(
        self, entry: JournalEntry, ledger_entries: list[LedgerEntry]
    ) -> tuple[bool, list[str]]:
        """
        Validate that transformation maintains data integrity.

        Args:
            entry: Source JournalEntry
            ledger_entries: Generated LedgerEntry objects

        Returns:
            Tuple of (is_valid, errors) where:
            - is_valid: True if transformation is valid
            - errors: List of error messages
        """
        errors: list[str] = []

        # Check that amounts balance (for one-to-many mappings)
        total_amount = sum(ledger.amount for ledger in ledger_entries)
        if abs(total_amount - entry.amount) > 0.01:  # Allow small floating point differences
            errors.append(
                f"Amount mismatch: journal entry amount {entry.amount} != "
                f"sum of ledger entries {total_amount}"
            )

        # Check that all ledger entries reference the source entry
        for ledger in ledger_entries:
            if ledger.source_entry_id != entry.entry_id:
                errors.append(
                    f"Ledger entry {ledger.entry_id} does not reference source entry {entry.entry_id}"
                )

        # Check that account codes exist in hierarchy (if hierarchy provided)
        if self.account_hierarchy:
            for ledger in ledger_entries:
                account = self.account_hierarchy.get_account(ledger.account_code)
                if account is None:
                    errors.append(
                        f"Account code {ledger.account_code} not found in hierarchy"
                    )

        return len(errors) == 0, errors



