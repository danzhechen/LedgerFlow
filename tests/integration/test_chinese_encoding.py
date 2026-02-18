"""Integration tests for Chinese text encoding support."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from veritas_accounting.excel.reader import ExcelReader
from veritas_accounting.excel.writer import ExcelWriter
from veritas_accounting.excel.journal_reader import JournalEntryReader
from veritas_accounting.excel.rule_reader import MappingRuleReader
from veritas_accounting.models.account import Account
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule


class TestChineseTextEncoding:
    """Integration tests for Chinese text encoding across the system."""

    def test_excel_reader_chinese_text(self, tmp_path: Path) -> None:
        """Test that ExcelReader handles Chinese text correctly."""
        # Create test Excel file with Chinese text
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["测试条目"],
                "old_type": ["OL"],
                "amount": [1000.50],
                "date": ["2024-01-15"],
            }
        )
        test_file = tmp_path / "chinese_test.xlsx"
        df.to_excel(test_file, index=False, engine="openpyxl")

        # Read back
        reader = ExcelReader()
        read_df = reader.read_file(test_file)

        assert "测试条目" in read_df["description"].values
        assert read_df["description"].iloc[0] == "测试条目"

    def test_excel_writer_chinese_text(self, tmp_path: Path) -> None:
        """Test that ExcelWriter handles Chinese text correctly."""
        writer = ExcelWriter()
        df = pd.DataFrame(
            {
                "名称": ["测试", "数据"],
                "金额": [100, 200],
            }
        )
        output_file = tmp_path / "chinese_output.xlsx"

        writer.write_file(df, output_file)

        # Read back and verify
        reader = ExcelReader()
        read_df = reader.read_file(output_file)

        assert "测试" in read_df["名称"].values
        assert "数据" in read_df["名称"].values

    def test_journal_entry_reader_chinese_text(self, tmp_path: Path) -> None:
        """Test that JournalEntryReader handles Chinese text correctly."""
        # Create test Excel file
        df = pd.DataFrame(
            {
                "entry_id": ["JE-001"],
                "year": [2024],
                "description": ["测试条目描述"],
                "old_type": ["OL"],
                "amount": [1000],
                "date": ["2024-01-15"],
            }
        )
        test_file = tmp_path / "chinese_journal.xlsx"
        df.to_excel(test_file, index=False, engine="openpyxl")

        # Read using JournalEntryReader
        reader = JournalEntryReader()
        entries, errors = reader.read_journal_entries(test_file)

        assert len(entries) == 1
        assert len(errors) == 0
        assert entries[0].description == "测试条目描述"

    def test_rule_reader_chinese_text(self, tmp_path: Path) -> None:
        """Test that MappingRuleReader handles Chinese text correctly."""
        # Create test Excel file
        df = pd.DataFrame(
            {
                "rule_id": ["R-001"],
                "condition": ["old_type == 'OL'"],
                "account_code": ["A1"],
                "priority": [1],
                "description": ["测试规则描述"],
            }
        )
        test_file = tmp_path / "chinese_rules.xlsx"
        df.to_excel(test_file, index=False, engine="openpyxl")

        # Read using MappingRuleReader
        reader = MappingRuleReader()
        rules, errors = reader.read_rules(test_file)

        assert len(rules) == 1
        assert len(errors) == 0
        assert rules[0].description == "测试规则描述"

    def test_chinese_text_preservation_through_transformation(self) -> None:
        """Test that Chinese text is preserved through data model transformations."""
        # Create journal entry with Chinese text
        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="测试条目",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        # Convert to dict and back (simulating transformation)
        entry_dict = entry.model_dump()
        entry_json = entry.model_dump_json()

        # Verify Chinese text is preserved
        assert entry_dict["description"] == "测试条目"
        assert "测试条目" in entry_json

    def test_chinese_text_in_error_messages(self) -> None:
        """Test that error messages can contain Chinese text."""
        from veritas_accounting.validation.input_validator import ValidationError

        error = ValidationError(
            row_number=5,
            field_name="description",
            error_type="validation_error",
            error_message="描述字段不能为空",
            actual_value=None,
        )

        error_str = str(error)
        assert "描述字段不能为空" in error_str
        # Should be valid UTF-8
        assert error_str.encode("utf-8")

    def test_chinese_text_in_account_hierarchy(self) -> None:
        """Test that Chinese text works in account hierarchy."""
        accounts = [
            Account(
                code="A1",
                name="一级账户",
                level=1,
                full_path="一级账户",
            ),
            Account(
                code="A1-1",
                name="二级账户",
                level=2,
                parent_code="A1",
                full_path="一级账户/二级账户",
            ),
        ]

        from veritas_accounting.models.account import AccountHierarchy

        hierarchy = AccountHierarchy(accounts)
        account = hierarchy.get_account("A1")
        assert account is not None
        assert account.name == "一级账户"
        assert account.full_path == "一级账户"

    def test_simplified_and_traditional_chinese(self) -> None:
        """Test that both simplified and traditional Chinese work."""
        # Simplified Chinese
        simplified = "测试"
        # Traditional Chinese
        traditional = "測試"

        # Both should work in models
        entry_simplified = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description=simplified,
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        entry_traditional = JournalEntry(
            entry_id="JE-002",
            year=2024,
            description=traditional,
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )

        assert entry_simplified.description == simplified
        assert entry_traditional.description == traditional

    def test_chinese_text_in_excel_round_trip(self, tmp_path: Path) -> None:
        """Test complete round-trip: write Chinese text to Excel, read it back."""
        writer = ExcelWriter()
        reader = ExcelReader()

        # Create DataFrame with Chinese text
        df = pd.DataFrame(
            {
                "编号": ["001", "002"],
                "名称": ["测试项目", "数据条目"],
                "金额": [1000, 2000],
                "描述": ["这是一个测试", "这是另一个测试"],
            }
        )

        output_file = tmp_path / "round_trip.xlsx"
        writer.write_file(df, output_file)

        # Read back
        read_df = reader.read_file(output_file)

        # Verify all Chinese text is preserved
        assert "测试项目" in read_df["名称"].values
        assert "数据条目" in read_df["名称"].values
        assert "这是一个测试" in read_df["描述"].values
        assert "这是另一个测试" in read_df["描述"].values








