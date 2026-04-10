"""
Tests for veritas_accounting.inference.type_inferrer.

Covers:
- keyword extraction from rule conditions
- suggestion with matching keywords
- confidence capping for single-keyword matches
- high-confidence auto-apply path (via processor helper)
- low-confidence suggestion-in-notes path
- empty / no-keyword-rules edge cases
- review_preview surfaces note-based suggestion in MISSING_TYPE reason
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from veritas_accounting.inference import TypeInferrer, TypeSuggestion
from veritas_accounting.models.journal import JournalEntry
from veritas_accounting.models.rule import MappingRule


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_rule(rule_id: str, old_type: str, condition: str) -> MappingRule:
    return MappingRule(
        rule_id=rule_id,
        old_type=old_type,
        condition=condition,
        account_code="1000",
        priority=10,
    )


def _make_entry(
    entry_id: str = "JE-001",
    old_type: str = "__MISSING_TYPE__",
    description: str = "test entry",
    notes: str | None = None,
) -> JournalEntry:
    return JournalEntry(
        entry_id=entry_id,
        year=2024,
        description=description,
        old_type=old_type,
        amount=Decimal("100.00"),
        date=datetime(2024, 1, 15),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# TypeInferrer.has_index / indexed_keyword_count
# ---------------------------------------------------------------------------

class TestTypeInferrerIndex:
    def test_empty_rules_has_no_index(self):
        inferrer = TypeInferrer([])
        assert not inferrer.has_index
        assert inferrer.indexed_keyword_count == 0

    def test_rules_without_keywords_have_no_index(self):
        rules = [
            _make_rule("R1", "OL", 'old_type == "OL" and year == 2024'),
            _make_rule("R2", "CR", 'old_type == "CR"'),
        ]
        inferrer = TypeInferrer(rules)
        assert not inferrer.has_index

    def test_keyword_rules_build_index(self):
        rules = [
            _make_rule("R1", "OL", 'old_type == "OL" and "支付宝" in description'),
            _make_rule("R2", "CR", 'old_type == "CR" and "微信" in description'),
        ]
        inferrer = TypeInferrer(rules)
        assert inferrer.has_index
        assert inferrer.indexed_keyword_count == 2

    def test_missing_type_rule_is_skipped(self):
        """Rules with old_type == __MISSING_TYPE__ must not pollute the index."""
        rules = [
            _make_rule("R1", "__MISSING_TYPE__", '"支付宝" in description'),
            _make_rule("R2", "OL", '"微信" in description'),
        ]
        inferrer = TypeInferrer(rules)
        assert inferrer.indexed_keyword_count == 1  # only 微信 → OL

    def test_duplicate_keywords_deduplicated_per_type(self):
        rules = [
            _make_rule("R1", "OL", '"支付宝" in description'),
            _make_rule("R2", "OL", '"支付宝" in description and year == 2024'),
        ]
        inferrer = TypeInferrer(rules)
        assert inferrer.indexed_keyword_count == 1


# ---------------------------------------------------------------------------
# TypeInferrer.suggest — matches
# ---------------------------------------------------------------------------

class TestTypeInferrerSuggest:
    def test_suggest_returns_none_if_no_index(self):
        inferrer = TypeInferrer([])
        assert inferrer.suggest("支付宝转账") is None

    def test_suggest_returns_none_if_no_match(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        inferrer = TypeInferrer(rules)
        assert inferrer.suggest("普通转账") is None

    def test_suggest_single_keyword_match(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        inferrer = TypeInferrer(rules)
        result = inferrer.suggest("支付宝转账到余额宝")
        assert result is not None
        assert result.suggested_type == "OL"
        assert "支付宝" in result.matched_keywords

    def test_single_keyword_confidence_capped_below_threshold(self):
        """A single keyword hit should not auto-apply (capped at 0.65)."""
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        inferrer = TypeInferrer(rules)
        result = inferrer.suggest("支付宝转账")
        assert result is not None
        assert result.confidence <= 0.65
        assert not result.is_high_confidence

    def test_multi_keyword_same_type_high_confidence(self):
        """Multiple keywords all pointing to the same type → high confidence."""
        rules = [
            _make_rule("R1", "OL", '"支付宝" in description'),
            _make_rule("R2", "OL", '"余额宝" in description'),
            _make_rule("R3", "OL", '"转账" in description'),
        ]
        inferrer = TypeInferrer(rules)
        result = inferrer.suggest("支付宝余额宝转账")
        assert result is not None
        assert result.suggested_type == "OL"
        # All 3 keywords matched and all vote OL → confidence = 3/3 = 1.0
        assert result.confidence == pytest.approx(1.0)
        assert result.is_high_confidence

    def test_conflicting_keywords_lowers_confidence(self):
        """Keywords pointing to different types reduce confidence of the winner."""
        rules = [
            _make_rule("R1", "OL", '"支付宝" in description'),
            _make_rule("R2", "CR", '"微信" in description'),
            _make_rule("R3", "OL", '"余额宝" in description'),
        ]
        inferrer = TypeInferrer(rules)
        # description matches 支付宝 (→OL) and 微信 (→CR): OL gets 2 votes, CR gets 1
        result = inferrer.suggest("支付宝微信余额宝")
        assert result is not None
        assert result.suggested_type == "OL"
        # 2 OL + 1 CR = 3 total; OL confidence = 2/3 ≈ 0.667 < HIGH_CONFIDENCE_THRESHOLD
        assert result.confidence == pytest.approx(2 / 3)
        assert not result.is_high_confidence

    def test_suggest_empty_description_returns_none(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        inferrer = TypeInferrer(rules)
        assert inferrer.suggest("") is None

    def test_reason_contains_keyword(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        inferrer = TypeInferrer(rules)
        result = inferrer.suggest("支付宝收款")
        assert result is not None
        assert "支付宝" in result.reason


# ---------------------------------------------------------------------------
# Integration: processor._run_type_inference
# ---------------------------------------------------------------------------

class TestProcessorTypeInferencePipeline:
    """Test the _run_type_inference method of ProcessingPipeline indirectly."""

    def _build_pipeline(self, rules: list[MappingRule]):
        """Build a minimal ProcessingPipeline without reading files."""
        from unittest.mock import MagicMock
        from veritas_accounting.cli.processor import ProcessingPipeline

        config = MagicMock()
        config.input = MagicMock()
        config.input.journal_file = "dummy.xlsx"
        config.validation = MagicMock()
        config.validation.level = "lenient"
        pipeline = ProcessingPipeline.__new__(ProcessingPipeline)
        pipeline.config = config
        pipeline._rules_from_journal_to_ledger = False
        return pipeline

    def test_high_confidence_auto_applies_type(self):
        rules = [
            _make_rule("R1", "OL", '"支付宝" in description'),
            _make_rule("R2", "OL", '"余额宝" in description'),
            _make_rule("R3", "OL", '"转账" in description'),
        ]
        pipeline = self._build_pipeline(rules)
        entry = _make_entry(description="支付宝余额宝转账")
        result = pipeline._run_type_inference([entry], rules)
        assert result[0].old_type == "OL"
        assert result[0].notes is None  # no note added, type was applied

    def test_low_confidence_adds_note_not_changes_type(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        pipeline = self._build_pipeline(rules)
        entry = _make_entry(description="支付宝收款")
        result = pipeline._run_type_inference([entry], rules)
        # Type unchanged
        assert result[0].old_type == "__MISSING_TYPE__"
        # Suggestion in notes
        assert result[0].notes is not None
        assert "型别建议/Type suggestion" in result[0].notes

    def test_no_match_leaves_entry_unchanged(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        pipeline = self._build_pipeline(rules)
        entry = _make_entry(description="普通收款")
        result = pipeline._run_type_inference([entry], rules)
        assert result[0].old_type == "__MISSING_TYPE__"
        assert result[0].notes is None

    def test_non_missing_entries_skipped(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        pipeline = self._build_pipeline(rules)
        entry = _make_entry(old_type="OL", description="支付宝收款")
        result = pipeline._run_type_inference([entry], rules)
        # Should not change since old_type is already set
        assert result[0].old_type == "OL"

    def test_empty_rules_returns_entries_unchanged(self):
        pipeline = self._build_pipeline([])
        entry = _make_entry(description="支付宝收款")
        result = pipeline._run_type_inference([entry], [])
        assert result[0].old_type == "__MISSING_TYPE__"

    def test_existing_notes_preserved_with_hint_prepended(self):
        rules = [_make_rule("R1", "OL", '"支付宝" in description')]
        pipeline = self._build_pipeline(rules)
        entry = _make_entry(description="支付宝收款", notes="original note")
        result = pipeline._run_type_inference([entry], rules)
        assert "original note" in result[0].notes
        assert "型别建议/Type suggestion" in result[0].notes


# ---------------------------------------------------------------------------
# Integration: review_preview shows suggestion in MISSING_TYPE reason
# ---------------------------------------------------------------------------

class TestReviewPreviewSuggestionInNote:
    def test_missing_type_with_note_hint_appears_in_flag_reason(self):
        from veritas_accounting.reporting.review_preview import (
            ReviewPreviewGenerator,
            ReviewStatus,
        )

        entry = _make_entry(
            notes="[型别建议/Type suggestion: OL (65%) — 关键词匹配 / Keyword match: 支付宝]"
        )
        generator = ReviewPreviewGenerator()
        generator._analyze_entries([], [entry])

        missing_flags = [
            f for f in generator.review_flags if f.status == ReviewStatus.MISSING_TYPE
        ]
        assert len(missing_flags) == 1
        assert "型别建议/Type suggestion" in missing_flags[0].reason

    def test_missing_type_without_note_has_standard_reason(self):
        from veritas_accounting.reporting.review_preview import (
            ReviewPreviewGenerator,
            ReviewStatus,
        )

        entry = _make_entry()  # no notes
        generator = ReviewPreviewGenerator()
        generator._analyze_entries([], [entry])

        missing_flags = [
            f for f in generator.review_flags if f.status == ReviewStatus.MISSING_TYPE
        ]
        assert len(missing_flags) == 1
        # No suggestion present → standard message
        assert "型别建议/Type suggestion" not in missing_flags[0].reason
        assert "classify" in missing_flags[0].reason.lower() or "类型" in missing_flags[0].reason
