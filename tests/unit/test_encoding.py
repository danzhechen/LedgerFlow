"""Unit tests for encoding utilities."""

import sys
from pathlib import Path

import pytest

from veritas_accounting.utils.encoding import (
    detect_file_encoding,
    normalize_chinese_text,
    safe_decode,
    safe_encode,
    validate_utf8_text,
)


class TestEncodingUtilities:
    """Test cases for encoding utilities."""

    def test_validate_utf8_text_valid(self) -> None:
        """Test validation of valid UTF-8 text."""
        text = "测试文本"
        is_valid, error = validate_utf8_text(text)
        assert is_valid is True
        assert error is None

    def test_validate_utf8_text_english(self) -> None:
        """Test validation of English text (also UTF-8)."""
        text = "Hello World"
        is_valid, error = validate_utf8_text(text)
        assert is_valid is True
        assert error is None

    def test_validate_utf8_text_mixed(self) -> None:
        """Test validation of mixed Chinese and English text."""
        text = "测试 Test 文本 Text"
        is_valid, error = validate_utf8_text(text)
        assert is_valid is True
        assert error is None

    def test_safe_encode_utf8(self) -> None:
        """Test safe encoding to UTF-8."""
        text = "测试文本"
        encoded = safe_encode(text, encoding="utf-8")
        assert isinstance(encoded, bytes)
        assert encoded.decode("utf-8") == text

    def test_safe_encode_with_errors_replace(self) -> None:
        """Test safe encoding with error replacement."""
        # This should work fine for UTF-8
        text = "测试文本"
        encoded = safe_encode(text, encoding="utf-8", errors="replace")
        assert isinstance(encoded, bytes)

    def test_safe_decode_utf8(self) -> None:
        """Test safe decoding from UTF-8."""
        text = "测试文本"
        encoded = text.encode("utf-8")
        decoded = safe_decode(encoded, encoding="utf-8")
        assert decoded == text

    def test_safe_decode_with_errors_replace(self) -> None:
        """Test safe decoding with error replacement."""
        # Invalid UTF-8 bytes
        invalid_bytes = b"\xff\xfe"
        decoded = safe_decode(invalid_bytes, encoding="utf-8", errors="replace")
        assert isinstance(decoded, str)
        # Should have replacement characters
        assert "\ufffd" in decoded or len(decoded) > 0

    def test_normalize_chinese_text_simplified(self) -> None:
        """Test normalization of simplified Chinese."""
        text = "测试"
        normalized = normalize_chinese_text(text)
        assert normalized == text

    def test_normalize_chinese_text_traditional(self) -> None:
        """Test normalization of traditional Chinese."""
        text = "測試"
        normalized = normalize_chinese_text(text)
        assert normalized == text

    def test_normalize_chinese_text_mixed(self) -> None:
        """Test normalization of mixed Chinese and English."""
        text = "测试 Test 測試"
        normalized = normalize_chinese_text(text)
        assert normalized == text

    def test_detect_file_encoding_nonexistent(self, tmp_path: Path) -> None:
        """Test encoding detection for non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        encoding = detect_file_encoding(file_path)
        # Should return None or default to utf-8
        assert encoding is None or encoding == "utf-8"

    def test_chinese_text_in_data_models(self) -> None:
        """Test that Chinese text works in data models."""
        from veritas_accounting.models.journal import JournalEntry
        from datetime import datetime
        from decimal import Decimal

        entry = JournalEntry(
            entry_id="JE-001",
            year=2024,
            description="测试条目",
            old_type="OL",
            amount=Decimal("1000"),
            date=datetime(2024, 1, 15),
        )
        assert entry.description == "测试条目"
        # Should be able to encode as UTF-8
        is_valid, _ = validate_utf8_text(entry.description)
        assert is_valid is True

    def test_chinese_text_in_rules(self) -> None:
        """Test that Chinese text works in mapping rules."""
        from veritas_accounting.models.rule import MappingRule

        rule = MappingRule(
            rule_id="R-001",
            condition="old_type == 'OL'",
            account_code="A1",
            priority=1,
            description="测试规则描述",
        )
        assert rule.description == "测试规则描述"
        # Should be able to encode as UTF-8
        is_valid, _ = validate_utf8_text(rule.description)
        assert is_valid is True

    def test_chinese_text_in_accounts(self) -> None:
        """Test that Chinese text works in account models."""
        from veritas_accounting.models.account import Account

        account = Account(
            code="A1",
            name="测试账户",
            level=1,
            full_path="一级",
        )
        assert account.name == "测试账户"
        assert account.full_path == "一级"
        # Should be able to encode as UTF-8
        is_valid, _ = validate_utf8_text(account.name)
        assert is_valid is True
