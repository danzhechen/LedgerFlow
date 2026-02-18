"""Output data validation for veritas-accounting."""

from decimal import Decimal
from random import sample

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.transformation.aggregator import QuarterlyAggregation
from veritas_accounting.validation.error_detector import ERROR_TYPE_OUTPUT
from veritas_accounting.validation.input_validator import ValidationError


class OutputValidator:
    """
    Validates final output data (ledger entries and aggregations).

    Ensures correctness, completeness, and consistency of generated output.
    """

    def __init__(self, account_hierarchy: AccountHierarchy | None = None):
        """
        Initialize OutputValidator.

        Args:
            account_hierarchy: Optional AccountHierarchy for validation
        """
        self.account_hierarchy = account_hierarchy

    def validate_output(
        self,
        journal_entries: list[JournalEntry],
        ledger_entries: list[LedgerEntry],
        aggregations: list[QuarterlyAggregation] | None = None,
    ) -> list[ValidationError]:
        """
        Validate output data comprehensively.

        Args:
            journal_entries: Original journal entries
            ledger_entries: Generated ledger entries
            aggregations: Optional quarterly aggregations

        Returns:
            List of ValidationError objects found during validation
        """
        errors: list[ValidationError] = []

        # 1. Completeness validation
        completeness_errors = self._validate_completeness(journal_entries, ledger_entries)
        errors.extend(completeness_errors)

        # 2. Consistency validation
        consistency_errors = self._validate_consistency(ledger_entries, aggregations)
        errors.extend(consistency_errors)

        # 3. Accuracy validation
        accuracy_errors = self._validate_accuracy(journal_entries, ledger_entries)
        errors.extend(accuracy_errors)

        # 4. Account structure validation
        account_errors = self._validate_account_structure(ledger_entries)
        errors.extend(account_errors)

        # 5. Quarterly totals validation
        if aggregations:
            totals_errors = self._validate_quarterly_totals(aggregations)
            errors.extend(totals_errors)

        return errors

    def _validate_completeness(
        self, journal_entries: list[JournalEntry], ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate completeness: all journal entries processed, no entries lost.

        Args:
            journal_entries: Original journal entries
            ledger_entries: Generated ledger entries

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Build set of journal entry IDs
        journal_entry_ids = {entry.entry_id for entry in journal_entries}
        ledger_source_ids = {entry.source_entry_id for entry in ledger_entries}

        # Check for missing entries (entries that weren't processed)
        missing_entries = journal_entry_ids - ledger_source_ids
        for entry_id in missing_entries:
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name="completeness",
                    error_type="missing_entry",
                    error_message=(
                        f"Journal entry {entry_id} was not transformed to any ledger entries. "
                        "Entry may have had no matching rules or transformation failed."
                    ),
                    actual_value=entry_id,
                    entry_id=entry_id,
                )
            )

        # Check for orphaned ledger entries (entries with invalid source IDs)
        orphaned_entries = ledger_source_ids - journal_entry_ids
        for source_id in orphaned_entries:
            errors.append(
                ValidationError(
                    row_number=0,
                    field_name="completeness",
                    error_type="orphaned_entry",
                    error_message=(
                        f"Ledger entry references source entry {source_id} "
                        "which does not exist in journal entries."
                    ),
                    actual_value=source_id,
                )
            )

        return errors

    def _validate_consistency(
        self,
        ledger_entries: list[LedgerEntry],
        aggregations: list[QuarterlyAggregation] | None,
    ) -> list[ValidationError]:
        """
        Validate consistency: totals balance, hierarchy sums correctly.

        Args:
            ledger_entries: Generated ledger entries
            aggregations: Optional quarterly aggregations

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        if not self.account_hierarchy:
            # Can't validate hierarchy without account hierarchy
            return errors

        # Validate hierarchical totals if aggregations provided
        if aggregations:
            # Group aggregations by quarter and year
            by_quarter: dict[tuple[int, int], list[QuarterlyAggregation]] = {}
            for agg in aggregations:
                key = (agg.quarter, agg.year)
                if key not in by_quarter:
                    by_quarter[key] = []
                by_quarter[key].append(agg)

            # Check that level totals sum correctly
            for (quarter, year), aggs in by_quarter.items():
                # Check levels 4 → 3 → 2 → 1
                for level in [4, 3, 2]:
                    level_aggs = [a for a in aggs if a.level == level]
                    parent_level = level - 1

                    # Calculate totals by parent
                    parent_totals: dict[str, Decimal] = {}
                    for agg in level_aggs:
                        account = self.account_hierarchy.get_account(agg.account_code)
                        if account and account.parent_code:
                            parent_code = account.parent_code
                            if parent_code not in parent_totals:
                                parent_totals[parent_code] = Decimal("0")
                            parent_totals[parent_code] += agg.total_amount

                    # Check against parent level aggregations
                    parent_aggs = {a.account_code: a for a in aggs if a.level == parent_level}
                    for parent_code, calculated_total in parent_totals.items():
                        if parent_code in parent_aggs:
                            parent_agg = parent_aggs[parent_code]
                            if abs(calculated_total - parent_agg.total_amount) > Decimal("0.01"):
                                errors.append(
                                    ValidationError(
                                        row_number=0,
                                        field_name="consistency",
                                        error_type="hierarchy_mismatch",
                                        error_message=(
                                            f"Level {parent_level} account {parent_code} total mismatch "
                                            f"in Q{quarter} {year}: expected {calculated_total} "
                                            f"(sum of level {level} accounts), got {parent_agg.total_amount}"
                                        ),
                                        actual_value=f"calculated={calculated_total}, actual={parent_agg.total_amount}",
                                    )
                                )

        return errors

    def _validate_accuracy(
        self, journal_entries: list[JournalEntry], ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate accuracy: amounts match source, dates preserved, descriptions correct.

        Args:
            journal_entries: Original journal entries
            ledger_entries: Generated ledger entries

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Build mapping of journal entries by ID
        journal_by_id = {entry.entry_id: entry for entry in journal_entries}

        # Group ledger entries by source entry
        ledger_by_source: dict[str, list[LedgerEntry]] = {}
        for ledger in ledger_entries:
            source_id = ledger.source_entry_id
            if source_id not in ledger_by_source:
                ledger_by_source[source_id] = []
            ledger_by_source[source_id].append(ledger)

        # Sample check: validate a subset of entries (or all if small)
        sample_size = min(10, len(journal_by_id))
        sample_ids = sample(list(journal_by_id.keys()), sample_size) if len(journal_by_id) > 10 else list(journal_by_id.keys())

        for journal_id in sample_ids:
            journal = journal_by_id[journal_id]
            ledgers = ledger_by_source.get(journal_id, [])

            if not ledgers:
                continue  # Already reported in completeness check

            # Check amount preservation (sum of ledger amounts = journal amount)
            total_ledger_amount = sum(Decimal(str(ledger.amount)) for ledger in ledgers)
            journal_amount = Decimal(str(journal.amount))
            if abs(total_ledger_amount - journal_amount) > Decimal("0.01"):
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="accuracy",
                        error_type="amount_mismatch",
                        error_message=(
                            f"Amount mismatch for entry {journal_id}: "
                            f"journal amount {journal_amount} != "
                            f"sum of ledger entries {total_ledger_amount}"
                        ),
                        actual_value=f"journal={journal_amount}, ledger_sum={total_ledger_amount}",
                        entry_id=journal_id,
                    )
                )

            # Check date preservation (at least one ledger should have same date)
            journal_date = journal.date.date()
            ledger_dates = {ledger.date.date() for ledger in ledgers}
            if journal_date not in ledger_dates:
                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="accuracy",
                        error_type="date_mismatch",
                        error_message=(
                            f"Date mismatch for entry {journal_id}: "
                            f"journal date {journal_date} not found in ledger entries "
                            f"(ledger dates: {sorted(ledger_dates)})"
                        ),
                        actual_value=f"journal={journal_date}, ledger={sorted(ledger_dates)}",
                        entry_id=journal_id,
                    )
                )

        return errors

    def _validate_account_structure(
        self, ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate account structure: all account codes valid, hierarchy relationships correct.

        Args:
            ledger_entries: Generated ledger entries

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        if not self.account_hierarchy:
            # Can't validate without hierarchy
            return errors

        # Check all account codes exist in hierarchy
        unique_codes = {entry.account_code for entry in ledger_entries}
        for code in unique_codes:
            account = self.account_hierarchy.get_account(code)
            if account is None:
                # Find entries with this code for error context
                entries_with_code = [e for e in ledger_entries if e.account_code == code]
                source_ids = {e.source_entry_id for e in entries_with_code[:5]}  # Limit to 5

                errors.append(
                    ValidationError(
                        row_number=0,
                        field_name="account_structure",
                        error_type="invalid_account_code",
                        error_message=(
                            f"Account code '{code}' used in {len(entries_with_code)} ledger entry(ies) "
                            f"does not exist in account hierarchy. "
                            f"Affected source entries: {', '.join(sorted(source_ids))}"
                        ),
                        actual_value=code,
                    )
                )

        return errors

    def _validate_quarterly_totals(
        self, aggregations: list[QuarterlyAggregation]
    ) -> list[ValidationError]:
        """
        Validate quarterly totals: aggregations sum correctly, no double-counting.

        Args:
            aggregations: Quarterly aggregations

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Group by quarter and year
        by_quarter: dict[tuple[int, int], list[QuarterlyAggregation]] = {}
        for agg in aggregations:
            key = (agg.quarter, agg.year)
            if key not in by_quarter:
                by_quarter[key] = []
            by_quarter[key].append(agg)

        # Check for duplicate aggregations (same account, quarter, year)
        for (quarter, year), aggs in by_quarter.items():
            seen: dict[str, QuarterlyAggregation] = {}
            for agg in aggs:
                if agg.account_code in seen:
                    existing = seen[agg.account_code]
                    errors.append(
                        ValidationError(
                            row_number=0,
                            field_name="quarterly_totals",
                            error_type="duplicate_aggregation",
                            error_message=(
                                f"Duplicate aggregation for account {agg.account_code} "
                                f"in Q{quarter} {year}: total {existing.total_amount} and {agg.total_amount}"
                            ),
                            actual_value=f"account={agg.account_code}, quarter={quarter}, year={year}",
                        )
                    )
                seen[agg.account_code] = agg

        return errors

    def validate_accounting_equation(
        self, ledger_entries: list[LedgerEntry]
    ) -> list[ValidationError]:
        """
        Validate accounting equation: debits = credits (if applicable).

        Note: This is a placeholder for accounting equation validation.
        Actual implementation depends on account type (debit/credit) which isn't in current model.

        Args:
            ledger_entries: Generated ledger entries

        Returns:
            List of ValidationError objects
        """
        errors: list[ValidationError] = []

        # Accounting equation validation requires knowledge of account types
        # (whether accounts are debit or credit accounts)
        # This would be implemented when account types are added to the model
        # For now, return empty list

        return errors








