"""Quarterly aggregation for veritas-accounting."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import pandas as pd

from veritas_accounting.models.account import AccountHierarchy
from veritas_accounting.models.ledger import LedgerEntry


@dataclass
class QuarterlyAggregation:
    """
    Quarterly aggregation result for a single account.

    Contains totals and statistics for an account in a specific quarter.
    """

    account_code: str
    account_path: str
    quarter: int
    year: int
    total_amount: Decimal
    cr_amount: Decimal  # Credit amount
    dr_amount: Decimal  # Debit amount
    entry_count: int
    level: int


@dataclass
class HierarchicalTotals:
    """
    Hierarchical totals at a specific level.

    Contains aggregated totals for all accounts at a hierarchy level.
    """

    level: int
    quarter: int
    year: int
    total_amount: Decimal
    account_count: int
    accounts: list[QuarterlyAggregation]


class QuarterlyAggregator:
    """
    Generates quarterly aggregations from ledger entries.

    Groups ledger entries by account and quarter, calculates totals,
    and generates hierarchical summaries.
    """

    def __init__(self, account_hierarchy: AccountHierarchy | None = None) -> None:
        """
        Initialize QuarterlyAggregator.

        Args:
            account_hierarchy: AccountHierarchy object (optional, for hierarchical totals)
        """
        self.account_hierarchy = account_hierarchy

    def aggregate(
        self, ledger_entries: list[LedgerEntry]
    ) -> list[QuarterlyAggregation]:
        """
        Aggregate ledger entries by account and quarter.

        Args:
            ledger_entries: List of LedgerEntry objects

        Returns:
            List of QuarterlyAggregation objects
        """
        if not ledger_entries:
            return []

        # Convert to DataFrame for efficient aggregation
        df = self._ledger_entries_to_dataframe(ledger_entries)

        # Group by account_code, quarter, and year
        # Calculate CR and DR amounts separately
        grouped = df.groupby(["account_code", "quarter", "year"]).agg(
            {
                "amount": ["sum", "count"],
            }
        )

        # Flatten column names
        grouped.columns = ["total_amount", "entry_count"]
        grouped = grouped.reset_index()

        # Calculate CR and DR amounts separately
        cr_grouped = df[df["ledger_type"] == "CR"].groupby(["account_code", "quarter", "year"]).agg(
            {"amount": "sum"}
        ).reset_index()
        cr_grouped.columns = ["account_code", "quarter", "year", "cr_amount"]
        
        dr_grouped = df[df["ledger_type"] == "DR"].groupby(["account_code", "quarter", "year"]).agg(
            {"amount": "sum"}
        ).reset_index()
        dr_grouped.columns = ["account_code", "quarter", "year", "dr_amount"]

        # Merge CR and DR amounts
        merged = grouped.merge(
            cr_grouped,
            on=["account_code", "quarter", "year"],
            how="left"
        ).merge(
            dr_grouped,
            on=["account_code", "quarter", "year"],
            how="left"
        )
        
        # Fill NaN with 0 for CR/DR amounts
        merged["cr_amount"] = merged["cr_amount"].fillna(0)
        merged["dr_amount"] = merged["dr_amount"].fillna(0)

        # IMPORTANT: compute signed net amount instead of raw sum
        #
        # Our ledger entries store amounts as positive numbers with a separate
        # `ledger_type` field indicating CR or DR. For correct accounting-style
        # "net" values we:
        #   - treat CR as +amount
        #   - treat DR as -amount
        # so that:
        #   net_amount = CR_amount - DR_amount
        #
        # This makes:
        #   - pure income accounts (only CR) → positive net
        #   - pure expense accounts (only DR) → negative net
        #   - accounts with equal CR/DR over the period → net = 0
        #
        # Previously `total_amount` was just the sum of absolute amounts
        # (CR + DR), which doubled the effective magnitude and made balances
        # look "wrong" compared to accounting expectations.
        merged["total_amount"] = merged["cr_amount"] - merged["dr_amount"]

        # Get account paths and levels from hierarchy
        aggregations: list[QuarterlyAggregation] = []
        for _, row in merged.iterrows():
            account_code = row["account_code"]
            account_path = self._get_account_path(account_code)
            level = self._get_account_level(account_code)

            aggregation = QuarterlyAggregation(
                account_code=account_code,
                account_path=account_path,
                quarter=int(row["quarter"]),
                year=int(row["year"]),
                total_amount=Decimal(str(row["total_amount"])),
                cr_amount=Decimal(str(row["cr_amount"])),
                dr_amount=Decimal(str(row["dr_amount"])),
                entry_count=int(row["entry_count"]),
                level=level,
            )
            aggregations.append(aggregation)

        return aggregations

    def aggregate_by_level(
        self, ledger_entries: list[LedgerEntry]
    ) -> dict[int, HierarchicalTotals]:
        """
        Generate hierarchical totals by level.

        Args:
            ledger_entries: List of LedgerEntry objects

        Returns:
            Dictionary mapping level (1-4) to HierarchicalTotals
        """
        if not self.account_hierarchy:
            # If no hierarchy, return empty dict
            return {}

        aggregations = self.aggregate(ledger_entries)
        level_totals: dict[int, HierarchicalTotals] = {}

        # Group aggregations by level and quarter/year
        for level in [1, 2, 3, 4]:
            level_aggregations = [a for a in aggregations if a.level == level]

            if not level_aggregations:
                continue

            # Group by quarter and year
            by_quarter: dict[tuple[int, int], list[QuarterlyAggregation]] = {}
            for agg in level_aggregations:
                key = (agg.quarter, agg.year)
                if key not in by_quarter:
                    by_quarter[key] = []
                by_quarter[key].append(agg)

            # Create HierarchicalTotals for each quarter/year
            for (quarter, year), aggs in by_quarter.items():
                total_amount = sum(a.total_amount for a in aggs)
                account_count = len(aggs)

                if level not in level_totals:
                    level_totals[level] = HierarchicalTotals(
                        level=level,
                        quarter=quarter,
                        year=year,
                        total_amount=total_amount,
                        account_count=account_count,
                        accounts=aggs,
                    )
                else:
                    # Merge with existing totals (if multiple quarters)
                    existing = level_totals[level]
                    existing.total_amount += total_amount
                    existing.account_count += account_count
                    existing.accounts.extend(aggs)

        return level_totals

    def aggregate_to_dataframe(
        self, ledger_entries: list[LedgerEntry]
    ) -> pd.DataFrame:
        """
        Aggregate ledger entries and return as DataFrame.

        Args:
            ledger_entries: List of LedgerEntry objects

        Returns:
            DataFrame with columns: account_code, account_path, quarter, year,
            total_amount, cr_amount, dr_amount, entry_count, level
        """
        aggregations = self.aggregate(ledger_entries)

        data = [
            {
                "account_code": agg.account_code,
                "account_path": agg.account_path,
                "quarter": agg.quarter,
                "year": agg.year,
                "total_amount": float(agg.total_amount),
                "cr_amount": float(agg.cr_amount),
                "dr_amount": float(agg.dr_amount),
                "entry_count": agg.entry_count,
                "level": agg.level,
            }
            for agg in aggregations
        ]

        return pd.DataFrame(data)

    def _ledger_entries_to_dataframe(
        self, ledger_entries: list[LedgerEntry]
    ) -> pd.DataFrame:
        """
        Convert list of LedgerEntry objects to DataFrame.

        Args:
            ledger_entries: List of LedgerEntry objects

        Returns:
            DataFrame with ledger entry data
        """
        data = [
            {
                "account_code": entry.account_code,
                "quarter": entry.quarter,
                "year": entry.year,
                "amount": float(entry.amount),
                "ledger_type": entry.ledger_type or "",
            }
            for entry in ledger_entries
        ]

        return pd.DataFrame(data)

    def _get_account_path(self, account_code: str) -> str:
        """
        Get account path from hierarchy or use account_code.

        Args:
            account_code: Account code

        Returns:
            Account path string
        """
        if self.account_hierarchy:
            try:
                return self.account_hierarchy.get_full_path(account_code)
            except ValueError:
                return account_code
        return account_code

    def _get_account_level(self, account_code: str) -> int:
        """
        Get account level from hierarchy or return 0.

        Args:
            account_code: Account code

        Returns:
            Account level (1-4) or 0 if not found
        """
        if self.account_hierarchy:
            account = self.account_hierarchy.get_account(account_code)
            if account:
                return account.level
        return 0

    def validate_totals(
        self, aggregations: list[QuarterlyAggregation]
    ) -> tuple[bool, list[str]]:
        """
        Validate that hierarchical totals balance correctly.

        Args:
            aggregations: List of QuarterlyAggregation objects

        Returns:
            Tuple of (is_valid, errors)
        """
        errors: list[str] = []

        if not self.account_hierarchy:
            # Can't validate without hierarchy
            return True, []

        # Group by quarter and year
        by_quarter: dict[tuple[int, int], list[QuarterlyAggregation]] = {}
        for agg in aggregations:
            key = (agg.quarter, agg.year)
            if key not in by_quarter:
                by_quarter[key] = []
            by_quarter[key].append(agg)

        # Validate each quarter
        for (quarter, year), aggs in by_quarter.items():
            # Check that level 4 totals sum to level 3 totals
            # Check that level 3 totals sum to level 2 totals
            # Check that level 2 totals sum to level 1 totals
            for level in [4, 3, 2]:
                level_aggs = [a for a in aggs if a.level == level]
                parent_level = level - 1

                # Get parent accounts for this level
                parent_totals: dict[str, Decimal] = {}
                for agg in level_aggs:
                    if self.account_hierarchy:
                        account = self.account_hierarchy.get_account(agg.account_code)
                        if account and account.parent_code:
                            parent_code = account.parent_code
                            if parent_code not in parent_totals:
                                parent_totals[parent_code] = Decimal("0")
                            parent_totals[parent_code] += agg.total_amount

                # Check against parent level totals
                parent_aggs = [a for a in aggs if a.level == parent_level]
                for parent_agg in parent_aggs:
                    calculated_total = parent_totals.get(parent_agg.account_code, Decimal("0"))
                    if abs(calculated_total - parent_agg.total_amount) > Decimal("0.01"):
                        errors.append(
                            f"Level {parent_level} account {parent_agg.account_code} "
                            f"total mismatch: expected {calculated_total}, got {parent_agg.total_amount} "
                            f"(Q{quarter} {year})"
                        )

        return len(errors) == 0, errors






