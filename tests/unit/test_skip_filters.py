"""Tests for veritas_accounting.utils.skip_filters."""

from datetime import datetime
from decimal import Decimal

from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.utils.skip_filters import (
    filter_skipped_journal_entries,
    should_skip_entry,
)


def _entry(**kwargs) -> JournalEntry:
    defaults = dict(
        entry_id="E1",
        year=2024,
        description="normal",
        old_type="OL",
        amount=Decimal("100"),
        date=datetime(2024, 6, 1),
    )
    defaults.update(kwargs)
    return JournalEntry(**defaults)


class TestShouldSkipEntry:
    def test_zero_decimal_skipped(self) -> None:
        assert should_skip_entry(_entry(amount=Decimal("0"))) is True

    def test_negative_amount_not_skipped_by_zero_rule(self) -> None:
        assert should_skip_entry(_entry(amount=Decimal("-50"))) is False

    def test_yulibao_redemption_phrase_skipped(self) -> None:
        assert (
            should_skip_entry(
                _entry(description="余利宝-基金赎回，转账到支付宝")
            )
            is True
        )

    def test_yulibao_auto_transfer_skipped(self) -> None:
        assert should_skip_entry(_entry(description="余利宝自动转入")) is True

    def test_other_yulibao_text_not_skipped(self) -> None:
        assert should_skip_entry(_entry(description="余利宝收益发放")) is False

    def test_other_internal_transfer_descriptions_not_skipped(self) -> None:
        assert should_skip_entry(_entry(description="支付宝余额自动转入")) is False
        assert should_skip_entry(_entry(description="基金申购，转入基金账户")) is False


class TestFilterSkippedJournalEntries:
    def test_filters_list(self) -> None:
        entries = [
            _entry(entry_id="a"),
            _entry(entry_id="b", amount=Decimal("0")),
            _entry(entry_id="c", description="余利宝自动转入"),
        ]
        out = filter_skipped_journal_entries(entries)
        assert len(out) == 1
        assert out[0].entry_id == "a"
