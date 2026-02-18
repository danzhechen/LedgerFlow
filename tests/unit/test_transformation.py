"""Unit tests for transformation logic."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.transformation.aggregator import QuarterlyAggregator
from veritas_accounting.transformation.journal_to_ledger import (
    JournalToLedgerTransformer,
)
from veritas_accounting.utils.exceptions import TransformationError


class TestJournalToLedgerTransformer:
    """Test cases for JournalToLedgerTransformer."""

    def test_basic_transformation(self) -> None:
        """Test basic journal to ledger transformation."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        transformer = JournalToLedgerTransformer([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entries, unmatched = transformer.transform([entry])

        assert len(ledger_entries) == 1
        assert len(unmatched) == 0
        assert ledger_entries[0].source_entry_id == "JE-001"
        assert ledger_entries[0].rule_applied == "R-001"

    def test_unmatched_entry(self) -> None:
        """Test transformation with unmatched entry."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        transformer = JournalToLedgerTransformer([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OTHER",  # Doesn't match
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entries, unmatched = transformer.transform([entry])

        assert len(ledger_entries) == 0
        assert len(unmatched) == 1
        assert unmatched[0].entry_id == "JE-001"

    def test_one_to_many_mapping(self) -> None:
        """Test one-to-many mapping (one journal entry → multiple ledger entries)."""
        rule1 = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        rule2 = MappingRule(
            rule_id="R-002",
            condition="old_type == 'OL'",
            account_code="A2",
            priority=2,
        )
        transformer = JournalToLedgerTransformer([rule1, rule2])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entries, unmatched = transformer.transform([entry])

        # With generic rules (no CR/DR), only the first matching rule is applied (backward compatibility)
        # Rules are sorted by priority in reverse (higher priority number first)
        assert len(ledger_entries) == 1
        assert len(unmatched) == 0
        assert ledger_entries[0].account_code == "A2"  # First rule in sorted order

    def test_with_account_hierarchy(self) -> None:
        """Test transformation with account hierarchy."""
        accounts = [
            Account(
                code="A1",
                name="Level1",
                level=1,
                full_path="Level1",
            ),
        ]
        hierarchy = AccountHierarchy(accounts)

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        transformer = JournalToLedgerTransformer([rule], hierarchy)

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entries, unmatched = transformer.transform([entry])

        assert len(ledger_entries) == 1
        assert ledger_entries[0].account_path == "Level1"

    def test_transformation_validation(self) -> None:
        """Test transformation validation."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        transformer = JournalToLedgerTransformer([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        ledger_entries, _ = transformer.transform([entry])

        is_valid, errors = transformer.validate_transformation(entry, ledger_entries)

        assert is_valid is True
        assert len(errors) == 0

    def test_transformation_validation_amount_mismatch(self) -> None:
        """Test transformation validation detects amount mismatch."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        transformer = JournalToLedgerTransformer([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        # Create ledger entry with wrong amount
        ledger_entry = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",
            account_path="A1",
            amount=Decimal("2000"),  # Wrong amount
            date=entry.date,
            description=entry.description,
            source_entry_id=entry.entry_id,
            rule_applied="R-001",
            quarter=1,
            year=entry.year,
        )

        is_valid, errors = transformer.validate_transformation(entry, [ledger_entry])

        assert is_valid is False
        assert len(errors) > 0
        assert any("Amount mismatch" in error for error in errors)


class TestQuarterlyAggregator:
    """Test cases for QuarterlyAggregator."""

    def test_basic_aggregation(self) -> None:
        """Test basic quarterly aggregation."""
        aggregator = QuarterlyAggregator()

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                description="Test 1",
                source_entry_id="JE-001",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",  # Credit entry
            ),
            LedgerEntry(
                entry_id="LE-002",
                account_code="A1",
                account_path="A1",
                amount=Decimal("2000"),
                date=datetime(2024, 2, 15),
                description="Test 2",
                source_entry_id="JE-002",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",  # Credit entry
            ),
        ]

        aggregations = aggregator.aggregate(ledger_entries)

        assert len(aggregations) == 1
        assert aggregations[0].account_code == "A1"
        assert aggregations[0].quarter == 1
        assert aggregations[0].year == 2024
        # Net amount = CR - DR = 3000 - 0 = 3000
        assert aggregations[0].total_amount == Decimal("3000")
        assert aggregations[0].cr_amount == Decimal("3000")
        assert aggregations[0].dr_amount == Decimal("0")
        assert aggregations[0].entry_count == 2

    def test_multiple_accounts_aggregation(self) -> None:
        """Test aggregation with multiple accounts."""
        aggregator = QuarterlyAggregator()

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",
            ),
            LedgerEntry(
                entry_id="LE-002",
                account_code="A2",
                account_path="A2",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 15),
                description="Test",
                source_entry_id="JE-002",
                rule_applied="R-002",
                quarter=1,
                year=2024,
                ledger_type="DR",
            ),
        ]

        aggregations = aggregator.aggregate(ledger_entries)

        assert len(aggregations) == 2
        account_codes = {agg.account_code for agg in aggregations}
        assert account_codes == {"A1", "A2"}
        
        # Check A1 (CR only)
        a1_agg = next(agg for agg in aggregations if agg.account_code == "A1")
        assert a1_agg.cr_amount == Decimal("1000")
        assert a1_agg.dr_amount == Decimal("0")
        assert a1_agg.total_amount == Decimal("1000")
        
        # Check A2 (DR only)
        a2_agg = next(agg for agg in aggregations if agg.account_code == "A2")
        assert a2_agg.cr_amount == Decimal("0")
        assert a2_agg.dr_amount == Decimal("2000")
        assert a2_agg.total_amount == Decimal("-2000")

    def test_multiple_quarters_aggregation(self) -> None:
        """Test aggregation with multiple quarters."""
        aggregator = QuarterlyAggregator()

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",
            ),
            LedgerEntry(
                entry_id="LE-002",
                account_code="A1",
                account_path="A1",
                amount=Decimal("2000"),
                date=datetime(2024, 4, 15),
                description="Test",
                source_entry_id="JE-002",
                rule_applied="R-001",
                quarter=2,
                year=2024,
                ledger_type="CR",
            ),
        ]

        aggregations = aggregator.aggregate(ledger_entries)

        assert len(aggregations) == 2
        quarters = {agg.quarter for agg in aggregations}
        assert quarters == {1, 2}

    def test_hierarchical_totals(self) -> None:
        """Test hierarchical totals by level."""
        accounts = [
            Account(code="A1", name="L1", level=1, full_path="L1"),
            Account(
                code="A1-1", name="L2", level=2, parent_code="A1", full_path="L1/L2"
            ),
        ]
        hierarchy = AccountHierarchy(accounts)
        aggregator = QuarterlyAggregator(hierarchy)

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1-1",
                account_path="L1/L2",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",
            ),
        ]

        level_totals = aggregator.aggregate_by_level(ledger_entries)

        assert 2 in level_totals
        assert level_totals[2].level == 2
        assert level_totals[2].total_amount == Decimal("1000")

    def test_aggregate_to_dataframe(self) -> None:
        """Test aggregation to DataFrame."""
        aggregator = QuarterlyAggregator()

        ledger_entries = [
            LedgerEntry(
                entry_id="LE-001",
                account_code="A1",
                account_path="A1",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
                description="Test",
                source_entry_id="JE-001",
                rule_applied="R-001",
                quarter=1,
                year=2024,
                ledger_type="CR",
            ),
        ]

        df = aggregator.aggregate_to_dataframe(ledger_entries)

        assert len(df) == 1
        assert "account_code" in df.columns
        assert "quarter" in df.columns
        assert "year" in df.columns
        assert "total_amount" in df.columns
        assert "cr_amount" in df.columns
        assert "dr_amount" in df.columns






