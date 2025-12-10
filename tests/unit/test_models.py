"""Unit tests for Pydantic data models."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from veritas_accounting.models.account import Account, AccountHierarchy
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.ledger import LedgerEntry
from veritas_accounting.models.rule import MappingRule


class TestJournalEntry:
    """Test cases for JournalEntry model."""

    def test_valid_journal_entry(self) -> None:
        """Test creating a valid journal entry."""
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="Test entry",
            old_type="OL",
            amount=Decimal("1000.50"),
            date=datetime(2024, 1, 15),
        )
        assert entry.entry_id == "JE-001"
        assert entry.year == 2024
        assert entry.amount == Decimal("1000.50")

    def test_chinese_text_support(self) -> None:
        """Test that Chinese text is supported in description."""
        entry = JournalEntry(
            entry_id="JE-002",
            year=2024,
            description="测试条目",
            old_type="OL",
            amount=Decimal("2000"),
            date=datetime(2024, 1, 15),
        )
        assert entry.description == "测试条目"

    def test_optional_fields(self) -> None:
        """Test optional fields (quarter, notes)."""
        entry = JournalEntry(
            entry_id="JE-003",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
            quarter=1,
            notes="Some notes",
        )
        assert entry.quarter == 1
        assert entry.notes == "Some notes"

    def test_invalid_year_range(self) -> None:
        """Test validation of year range."""
        with pytest.raises(ValidationError) as exc_info:
            JournalEntry(
                entry_id="JE-004",
                year=1999,  # Too low
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date=datetime(2024, 1, 15),
            )
        errors = exc_info.value.errors()
        assert any("year" in str(e.get("loc", [])) for e in errors)

    def test_invalid_amount_format(self) -> None:
        """Test validation of amount format."""
        with pytest.raises(ValidationError) as exc_info:
            JournalEntry(
                entry_id="JE-005",
                year=2024,
                description="Test",
                old_type="OL",
                amount="not a number",  # type: ignore
                date=datetime(2024, 1, 15),
            )
        errors = exc_info.value.errors()
        assert any("amount" in str(e.get("loc", [])) for e in errors)

    def test_date_parsing_from_string(self) -> None:
        """Test parsing date from string."""
        entry = JournalEntry(
            entry_id="JE-006",
            year=2024,
            description="Test",
            old_type="OL",
            amount=Decimal("1000"),
            date="2024-01-15",  # type: ignore
        )
        assert entry.date == datetime(2024, 1, 15)

    def test_invalid_date_format(self) -> None:
        """Test validation of invalid date format."""
        with pytest.raises(ValidationError) as exc_info:
            JournalEntry(
                entry_id="JE-007",
                year=2024,
                description="Test",
                old_type="OL",
                amount=Decimal("1000"),
                date="invalid-date",  # type: ignore
            )
        errors = exc_info.value.errors()
        assert any("date" in str(e.get("loc", [])) for e in errors)


class TestLedgerEntry:
    """Test cases for LedgerEntry model."""

    def test_valid_ledger_entry(self) -> None:
        """Test creating a valid ledger entry."""
        entry = LedgerEntry(
            entry_id="LE-001",
            account_code="A1",
            account_path="Level1/Level2/Level3/Level4",
            amount=Decimal("1000.50"),
            date=datetime(2024, 1, 15),
            description="Test ledger entry",
            source_entry_id="JE-001",
            rule_applied="R-001",
            quarter=1,
            year=2024,
        )
        assert entry.entry_id == "LE-001"
        assert entry.account_code == "A1"
        assert entry.source_entry_id == "JE-001"

    def test_chinese_text_support(self) -> None:
        """Test that Chinese text is supported."""
        entry = LedgerEntry(
            entry_id="LE-002",
            account_code="A1",
            account_path="一级/二级/三级/四级",
            amount=Decimal("2000"),
            date=datetime(2024, 1, 15),
            description="测试分类账条目",
            source_entry_id="JE-002",
            rule_applied="R-001",
            quarter=1,
            year=2024,
        )
        assert entry.description == "测试分类账条目"
        assert entry.account_path == "一级/二级/三级/四级"


class TestMappingRule:
    """Test cases for MappingRule model."""

    def test_valid_mapping_rule(self) -> None:
        """Test creating a valid mapping rule."""
        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL' and year == 2024",
            old_type="OL",
            account_code="A1",
            priority=1,
        )
        assert rule.rule_id == "R-001"
        assert rule.condition == "old_type == 'OL' and year == 2024"
        assert rule.priority == 1

    def test_optional_fields(self) -> None:
        """Test optional fields (new_type, description)."""
        rule = MappingRule(
            rule_id="R-002",
            condition="old_type == 'OL'",
            old_type="OL",
            new_type="NEW",
            account_code="A1",
            priority=2,
            description="Test rule description",
        )
        assert rule.new_type == "NEW"
        assert rule.description == "Test rule description"

    def test_one_to_many_flag(self) -> None:
        """Test generates_multiple flag."""
        rule = MappingRule(
            rule_id="R-003",
            condition="old_type == 'OL'",
            old_type="OL",
            account_code="A1",
            priority=3,
            generates_multiple=True,
        )
        assert rule.generates_multiple is True

    def test_empty_condition_validation(self) -> None:
        """Test validation of empty condition."""
        with pytest.raises(ValidationError) as exc_info:
            MappingRule(
                rule_id="R-004",
                condition="",  # Empty condition
                account_code="A1",
                priority=1,
            )
        errors = exc_info.value.errors()
        assert any("condition" in str(e.get("loc", [])) for e in errors)

    def test_invalid_priority_range(self) -> None:
        """Test validation of priority range."""
        with pytest.raises(ValidationError) as exc_info:
            MappingRule(
                rule_id="R-005",
                condition="old_type == 'OL'",
                account_code="A1",
                priority=0,  # Too low
            )
        errors = exc_info.value.errors()
        assert any("priority" in str(e.get("loc", [])) for e in errors)


class TestAccount:
    """Test cases for Account model."""

    def test_valid_account(self) -> None:
        """Test creating a valid account."""
        account = Account(
            code="A1",
            name="Test Account",
            level=1,
            full_path="Level1",
        )
        assert account.code == "A1"
        assert account.level == 1
        assert account.parent_code is None

    def test_account_with_parent(self) -> None:
        """Test account with parent."""
        account = Account(
            code="A1-1",
            name="Child Account",
            level=2,
            parent_code="A1",
            full_path="Level1/Level2",
        )
        assert account.parent_code == "A1"
        assert account.level == 2

    def test_chinese_text_support(self) -> None:
        """Test that Chinese text is supported."""
        account = Account(
            code="A1",
            name="测试账户",
            level=1,
            full_path="一级",
        )
        assert account.name == "测试账户"

    def test_level_1_no_parent_validation(self) -> None:
        """Test that level 1 accounts cannot have parent."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                code="A1",
                name="Test",
                level=1,
                parent_code="PARENT",  # Should not have parent
                full_path="Level1",
            )
        errors = exc_info.value.errors()
        assert any("parent_code" in str(e.get("loc", [])) for e in errors)

    def test_level_2_requires_parent_validation(self) -> None:
        """Test that level 2+ accounts must have parent."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                code="A1-1",
                name="Test",
                level=2,
                parent_code=None,  # Should have parent
                full_path="Level1/Level2",
            )
        errors = exc_info.value.errors()
        assert any("parent_code" in str(e.get("loc", [])) for e in errors)

    def test_invalid_level_range(self) -> None:
        """Test validation of level range."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                code="A1",
                name="Test",
                level=5,  # Too high
                full_path="Level1",
            )
        errors = exc_info.value.errors()
        assert any("level" in str(e.get("loc", [])) for e in errors)


class TestAccountHierarchy:
    """Test cases for AccountHierarchy manager."""

    def test_create_hierarchy(self) -> None:
        """Test creating an account hierarchy."""
        accounts = [
            Account(code="A1", name="Level1", level=1, full_path="Level1"),
            Account(
                code="A1-1",
                name="Level2",
                level=2,
                parent_code="A1",
                full_path="Level1/Level2",
            ),
        ]
        hierarchy = AccountHierarchy(accounts)
        assert hierarchy.get_account("A1") is not None
        assert hierarchy.get_account("A1-1") is not None

    def test_get_children(self) -> None:
        """Test getting child accounts."""
        accounts = [
            Account(code="A1", name="Parent", level=1, full_path="Parent"),
            Account(
                code="A1-1",
                name="Child1",
                level=2,
                parent_code="A1",
                full_path="Parent/Child1",
            ),
            Account(
                code="A1-2",
                name="Child2",
                level=2,
                parent_code="A1",
                full_path="Parent/Child2",
            ),
        ]
        hierarchy = AccountHierarchy(accounts)
        children = hierarchy.get_children("A1")
        assert len(children) == 2
        assert {c.code for c in children} == {"A1-1", "A1-2"}

    def test_get_by_level(self) -> None:
        """Test getting accounts by level."""
        accounts = [
            Account(code="A1", name="L1", level=1, full_path="L1"),
            Account(code="A2", name="L1-2", level=1, full_path="L1-2"),
            Account(
                code="A1-1", name="L2", level=2, parent_code="A1", full_path="L1/L2"
            ),
        ]
        hierarchy = AccountHierarchy(accounts)
        level1 = hierarchy.get_by_level(1)
        assert len(level1) == 2
        level2 = hierarchy.get_by_level(2)
        assert len(level2) == 1

    def test_duplicate_code_validation(self) -> None:
        """Test validation of duplicate account codes."""
        accounts = [
            Account(code="A1", name="Test1", level=1, full_path="Test1"),
            Account(code="A1", name="Test2", level=1, full_path="Test2"),  # Duplicate
        ]
        with pytest.raises(ValueError, match="Duplicate account code"):
            AccountHierarchy(accounts)

    def test_invalid_parent_reference(self) -> None:
        """Test validation of invalid parent reference."""
        accounts = [
            Account(
                code="A1-1",
                name="Child",
                level=2,
                parent_code="NONEXISTENT",  # Invalid parent
                full_path="Parent/Child",
            ),
        ]
        with pytest.raises(ValueError, match="non-existent parent"):
            AccountHierarchy(accounts)

    def test_invalid_parent_level(self) -> None:
        """Test validation of parent level mismatch."""
        accounts = [
            Account(code="A1", name="L1", level=1, full_path="L1"),
            Account(
                code="A1-1",
                name="L2",
                level=3,  # Should be level 2
                parent_code="A1",
                full_path="L1/L2",
            ),
        ]
        with pytest.raises(ValueError, match="invalid parent level"):
            AccountHierarchy(accounts)
