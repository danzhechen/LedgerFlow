"""Transformation validation for veritas-accounting."""

from decimal import Decimal

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.applicator import RuleApplicationResult
from veritas_accounting.rules.engine import RuleEvaluator
from veritas_accounting.validation.error_detector import ERROR_TYPE_TRANSFORMATION
from veritas_accounting.validation.input_validator import ValidationError


class TransformationValidator:
    """
    Validates transformation from journal entries to ledger entries.

    Performs real-time validation during transformation to catch mapping errors
    and ensure rules are applied correctly.
    """

    def __init__(self, account_hierarchy: AccountHierarchy | None = None):
        """
        Initialize TransformationValidator.

        Args:
            account_hierarchy: Optional AccountHierarchy for account code validation
        """
        self.account_hierarchy = account_hierarchy
        self.evaluator = RuleEvaluator()
        self.errors: list[ValidationError] = []

    def validate_transformation(
        self,
        entry: JournalEntry,
        result: RuleApplicationResult,
        rules: list[MappingRule],
    ) -> list[ValidationError]:
        """
        Validate transformation for a single journal entry.

        Args:
            entry: Source JournalEntry
            result: RuleApplicationResult from rule application
            rules: List of all mapping rules (for reference)

        Returns:
            List of ValidationError objects found during validation
        """
        errors: list[ValidationError] = []

        # 1. Rule match validation
        match_errors = self._validate_rule_match(entry, result)
        errors.extend(match_errors)

        # 2. Rule correctness validation
        if not result.no_match:
            correctness_errors = self._validate_rule_correctness(
                entry, result, rules
            )
            errors.extend(correctness_errors)

        # 3. Account code validation
        if result.ledger_entries:
            account_errors = self._validate_account_codes(result.ledger_entries)
            errors.extend(account_errors)

        # 4. Amount preservation validation
        if result.ledger_entries:
            amount_errors = self._validate_amount_preservation(
                entry, result.ledger_entries
            )
            errors.extend(amount_errors)

        # 5. Completeness validation
        if result.ledger_entries:
            completeness_errors = self._validate_completeness(entry, result, rules)
            errors.extend(completeness_errors)

        return errors

    def _validate_rule_match(
        self, entry: JournalEntry, result: RuleApplicationResult
    ) -> list[ValidationError]:
        """
        Validate that every journal entry has matching rules or explicit no-match flag.

        Args:
            entry: JournalEntry being validated
            result: RuleApplicationResult

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # No-match case is expected and handled by the system (not an error)
        # But we can flag it for review if needed
        # For now, we'll only error if there's an unexpected state
        if result.no_match and result.ledger_entries:
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name="rule_match",
                    error_type="unexpected_state",
                    error_message=(
                        f"Entry {entry.entry_id} marked as no-match but has ledger entries. "
                        "This indicates a logic error."
                    ),
                    actual_value=f"no_match={result.no_match}, entries={len(result.ledger_entries)}",
                    entry_id=entry.entry_id,
                )
            )

        return errors

    def _validate_rule_correctness(
        self,
        entry: JournalEntry,
        result: RuleApplicationResult,
        all_rules: list[MappingRule],
    ) -> list[ValidationError]:
        """
        Verify rule conditions actually match entry data.

        Args:
            entry: JournalEntry
            result: RuleApplicationResult
            all_rules: All mapping rules

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Verify each applied rule actually matches the entry
        for rule in result.applied_rules:
            matches, error_msg = self.evaluator.evaluate(rule, entry)

            if error_msg:
                # Rule evaluation error
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="rule_evaluation",
                        error_type="rule_evaluation_error",
                        error_message=(
                            f"Error evaluating rule {rule.rule_id} for entry {entry.entry_id}: {error_msg}"
                        ),
                        actual_value=rule.condition,
                        entry_id=entry.entry_id,
                    )
                )
            elif not matches:
                # Rule was applied but doesn't actually match
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="rule_correctness",
                        error_type="rule_mismatch",
                        error_message=(
                            f"Rule {rule.rule_id} was applied to entry {entry.entry_id} "
                            f"but condition '{rule.condition}' does not match entry data"
                        ),
                        actual_value=rule.condition,
                        entry_id=entry.entry_id,
                    )
                )

        return errors

    def _validate_account_codes(
        self, ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate that all generated account codes exist in hierarchy.

        Args:
            ledger_entries: Generated LedgerEntry objects

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        if not self.account_hierarchy:
            # Can't validate without hierarchy
            return errors

        for ledger in ledger_entries:
            account = self.account_hierarchy.get_account(ledger.account_code)
            if account is None:
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="account_code",
                        error_type="invalid_account_code",
                        error_message=(
                            f"Account code '{ledger.account_code}' in ledger entry "
                            f"{ledger.entry_id} does not exist in account hierarchy"
                        ),
                        actual_value=ledger.account_code,
                        entry_id=ledger.source_entry_id,
                    )
                )

        return errors

    def _validate_amount_preservation(
        self, entry: JournalEntry, ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate that amounts are preserved correctly (no data loss in transformation).

        For one-to-many mappings, sum of ledger amounts should equal journal entry amount.

        Args:
            entry: Source JournalEntry
            ledger_entries: Generated LedgerEntry objects

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        if not ledger_entries:
            return errors

        # Calculate sum of ledger entry amounts
        total_ledger_amount = sum(Decimal(str(ledger.amount)) for ledger in ledger_entries)
        journal_amount = Decimal(str(entry.amount))

        # Allow small floating point differences (0.01)
        difference = abs(total_ledger_amount - journal_amount)
        if difference > Decimal("0.01"):
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name="amount_preservation",
                    error_type="amount_mismatch",
                    error_message=(
                        f"Amount mismatch for entry {entry.entry_id}: "
                        f"journal entry amount {journal_amount} != "
                        f"sum of ledger entries {total_ledger_amount} "
                        f"(difference: {difference})"
                    ),
                    actual_value=f"journal={journal_amount}, ledger_sum={total_ledger_amount}",
                    entry_id=entry.entry_id,
                )
            )

        return errors

    def _validate_completeness(
        self,
        entry: JournalEntry,
        result: RuleApplicationResult,
        all_rules: list[MappingRule],
    ) -> list[ValidationError]:
        """
        Validate that all expected ledger entries were created.

        For one-to-many rules (generates_multiple=True), verify all expected entries created.

        Args:
            entry: Source JournalEntry
            result: RuleApplicationResult
            all_rules: All mapping rules

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Check if any applied rule is a one-to-many rule
        one_to_many_rules = [
            rule for rule in result.applied_rules if rule.generates_multiple
        ]

        # If one-to-many rules exist, we expect multiple ledger entries
        # The exact count depends on rule specification
        # For now, we'll check that if generates_multiple is True, we have multiple entries
        for rule in one_to_many_rules:
            if len(result.ledger_entries) <= 1:
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="completeness",
                        error_type="incomplete_one_to_many",
                        error_message=(
                            f"Rule {rule.rule_id} has generates_multiple=True for entry {entry.entry_id}, "
                            f"but only {len(result.ledger_entries)} ledger entry(ies) were created. "
                            "Expected multiple ledger entries."
                        ),
                        actual_value=f"entries_created={len(result.ledger_entries)}",
                        entry_id=entry.entry_id,
                    )
                )

        return errors

    def validate_batch(
        self,
        entries: list[JournalEntry],
        results: list[RuleApplicationResult],
        rules: list[MappingRule],
    ) -> list[ValidationError]:
        """
        Validate transformation for a batch of journal entries.

        Args:
            entries: List of source JournalEntry objects
            results: List of RuleApplicationResult objects (one per entry)
            rules: List of all mapping rules

        Returns:
            List of all ValidationError objects from batch validation
        """
        all_errors: list[ValidationError] = []

        if len(entries) != len(results):
            # Mismatch in counts
            all_errors.append(
                ValidationError(
                    row_number=0,
                    field_name="batch_consistency",
                    error_type="batch_mismatch",
                    error_message=(
                        f"Batch validation error: {len(entries)} entries but {len(results)} results"
                    ),
                    actual_value=f"entries={len(entries)}, results={len(results)}",
                )
            )
            return all_errors

        # Validate each entry
        for entry, result in zip(entries, results):
            entry_errors = self.validate_transformation(entry, result, rules)
            all_errors.extend(entry_errors)

        return all_errors
