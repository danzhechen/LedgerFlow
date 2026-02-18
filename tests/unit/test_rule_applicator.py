"""Unit tests for RuleApplicator."""

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule
from veritas_accounting.rules.applicator import RuleApplicator, RuleApplicationResult
from veritas_accounting.utils.exceptions import RuleError


class TestRuleApplicator:
    """Test cases for RuleApplicator."""

    def test_single_rule_match(self) -> None:
        """Test applying a single matching rule."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        applicator = RuleApplicator([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = applicator.apply_rules(entry)

        assert result.no_match is False
        assert len(result.applied_rules) == 1
        assert len(result.ledger_entries) == 1
        assert result.ledger_entries[0].account_code == "A1"
        assert result.ledger_entries[0].source_entry_id == "JE-001"

    def test_single_rule_no_match(self) -> None:
        """Test applying a rule that doesn't match."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        applicator = RuleApplicator([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OTHER",  # Doesn't match
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = applicator.apply_rules(entry)

        assert result.no_match is True
        assert len(result.applied_rules) == 0
        assert len(result.ledger_entries) == 0

    def test_multiple_rules_priority(self) -> None:
        """Test that rules are applied in priority order."""
        rule1 = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=2,  # Lower priority
        )
        rule2 = MappingRule(
            rule_id="R-002",
            condition="old_type == 'OL'",
            account_code="A2",
            priority=1,  # Higher priority (lower number = higher priority)
        )
        applicator = RuleApplicator([rule1, rule2])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = applicator.apply_rules(entry)

        assert result.no_match is False
        # With generic rules (no CR/DR), only the first matching rule is applied (backward compatibility)
        assert len(result.applied_rules) == 1
        # Rules are sorted by priority in reverse (higher priority number first)
        # So priority 2 (A1) comes before priority 1 (A2)
        assert result.applied_rules[0].priority == 2
        assert result.applied_rules[0].account_code == "A1"

    def test_one_to_many_mapping(self) -> None:
        """Test one-to-many mapping (one rule generates multiple entries)."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
            generates_multiple=True,
        )
        applicator = RuleApplicator([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = applicator.apply_rules(entry)

        assert result.no_match is False
        assert len(result.applied_rules) == 1
        assert result.applied_rules[0].generates_multiple is True

    def test_with_account_hierarchy(self) -> None:
        """Test rule application with account hierarchy."""
        accounts = [
            Account(
                code="A1",
                name="Level1",
                level=1,
                full_path="Level1",
            ),
            Account(
                code="A1-1",
                name="Level2",
                level=2,
                parent_code="A1",
                full_path="Level1/Level2",
            ),
        ]
        hierarchy = AccountHierarchy(accounts)

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1-1",
            priority=1,
        )
        applicator = RuleApplicator([rule])

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        result = applicator.apply_rules(entry, hierarchy)

        assert result.no_match is False
        assert len(result.ledger_entries) == 1
        assert result.ledger_entries[0].account_path == "Level1/Level2"

    def test_invalid_rule_compilation(self) -> None:
        """Test that invalid rules are caught during initialization."""
        invalid_rule = MappingRule(
            rule_id="R-001",
            condition="invalid syntax !!!",  # Invalid
            account_code="A1",
            priority=1,
        )

        with pytest.raises(RuleError, match="Rule compilation errors"):
            RuleApplicator([invalid_rule])

    def test_batch_application(self) -> None:
        """Test applying rules to multiple entries."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        applicator = RuleApplicator([rule])

        entries = [
            JournalEntry(
                entry_id="JE-001",
                year=2024,
                description="Test 1",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            ),
            JournalEntry(
                entry_id="JE-002",
                year=2024,
                description="Test 2",
                old_type="OL",
                amount=Decimal("2000"),
                date=datetime(2024, 1, 16),
            ),
        ]

        results = applicator.apply_rules_batch(entries)

        assert len(results) == 2
        assert all(not r.no_match for r in results)
        assert all(len(r.ledger_entries) == 1 for r in results)

    def test_quarter_calculation(self) -> None:
        """Test that quarter is calculated correctly from date."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
        )
        applicator = RuleApplicator([rule])

        # Q1 (January)
        entry_q1 = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )
        result_q1 = applicator.apply_rules(entry_q1)
        assert result_q1.ledger_entries[0].quarter == 1

        # Q2 (April)
        entry_q2 = JournalEntry(
            entry_id="JE-002",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 4, 15),
        )
        result_q2 = applicator.apply_rules(entry_q2)
        assert result_q2.ledger_entries[0].quarter == 2

        # Q3 (July)
        entry_q3 = JournalEntry(
            entry_id="JE-003",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 7, 15),
        )
        result_q3 = applicator.apply_rules(entry_q3)
        assert result_q3.ledger_entries[0].quarter == 3

        # Q4 (October)
        entry_q4 = JournalEntry(
            entry_id="JE-004",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 10, 15),
        )
        result_q4 = applicator.apply_rules(entry_q4)
        assert result_q4.ledger_entries[0].quarter == 4

    def test_deposit_refund_押金_flips_cr_dr(self) -> None:
        """押金 (deposit refund): 账目分类明细 uses opposite sides; we flip CR/DR."""
        cr_rule = MappingRule(
            rule_id="R-押金-CR",
            condition="old_type == '应付ol押金'",
            old_type="应付ol押金",
            account_code="2301",
            priority=10,
        )
        cr_rule.ledger_type = "CR"
        dr_rule = MappingRule(
            rule_id="R-押金-DR",
            condition="old_type == '应付ol押金'",
            old_type="应付ol押金",
            account_code="1100",
            priority=10,
        )
        dr_rule.ledger_type = "DR"
        applicator = RuleApplicator([cr_rule, dr_rule])
        accounts = [
            Account(code="1100", name="银行存款", level=1, full_path="资产 > 银行存款"),
            Account(code="2010", name="应付款", level=1, parent_code=None, full_path="应付款"),
            Account(code="2301", name="应付OL押金", level=2, parent_code="2010", full_path="应付款 > 应付OL押金"),
        ]
        hierarchy = AccountHierarchy(accounts)
        entry = JournalEntry(
            entry_id="JE-押金",
            year=2024,
            description="退还押金",
            old_type="应付ol押金",
            amount=Decimal("500"),
            date=datetime(2024, 3, 1),
        )
        result = applicator.apply_rules(entry, hierarchy)
        assert result.no_match is False
        assert len(result.ledger_entries) == 2
        by_account = {e.account_code: e.ledger_type for e in result.ledger_entries}
        # 押金 flip: CR rule → DR entry, DR rule → CR entry
        assert by_account["2301"] == "DR"
        assert by_account["1100"] == "CR"



