"""
Heuristic journal-type inference for veritas-accounting.

Phase 1 (no ML): builds a keyword → old_type lookup from existing mapping rules
by parsing the description-keyword patterns embedded in rule conditions.

Usage::

    inferrer = TypeInferrer(rules)
    suggestion = inferrer.suggest("余利宝-基金赎回，转账到支付宝")
    if suggestion and suggestion.confidence >= TypeInferrer.HIGH_CONFIDENCE_THRESHOLD:
        entry.old_type = suggestion.suggested_type  # auto-apply
    elif suggestion:
        # Show suggestion in review preview, human decides
        pass
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from veritas_accounting.models.rule import MappingRule

# Matches patterns like  '"支付宝" in description'  or  '"keyword" in description'
_KEYWORD_IN_DESC_RE = re.compile(r'"([^"]+)"\s+in\s+description', re.IGNORECASE)


@dataclass
class TypeSuggestion:
    """Result from TypeInferrer.suggest()."""

    suggested_type: str
    """The inferred old_type value."""

    confidence: float
    """0.0–1.0.  ≥ HIGH_CONFIDENCE_THRESHOLD → auto-apply; otherwise route to review."""

    matched_keywords: list[str] = field(default_factory=list)
    """Keywords from rule conditions that triggered this suggestion."""

    reason: str = ""
    """Human-readable explanation (Chinese-first)."""

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= TypeInferrer.HIGH_CONFIDENCE_THRESHOLD


class TypeInferrer:
    """
    Keyword-based type inference built from existing MappingRule conditions.

    Algorithm
    ---------
    1. For each rule that has a non-empty old_type, extract any keyword in
       conditions of the form ``"keyword" in description``.
    2. Build a dict  ``keyword → list[old_type]`` (de-duped per keyword).
    3. For a candidate description, collect all matching keywords and count
       votes per type.  Confidence = votes_for_best / total_votes.
    4. A single-keyword match is capped at 0.65 ("medium") so it stays below
       HIGH_CONFIDENCE_THRESHOLD and routes to review rather than auto-applying.
    """

    HIGH_CONFIDENCE_THRESHOLD: float = 0.8
    """Confidence level at or above which the suggestion is auto-applied."""

    def __init__(self, rules: list[MappingRule]) -> None:
        # keyword → set of old_type values (list to preserve insertion order)
        self._keyword_types: dict[str, list[str]] = {}
        self._build_index(rules)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def suggest(
        self,
        description: str,
        amount: Optional[float] = None,  # reserved for future scoring
        year: Optional[int] = None,  # reserved for future scoring
    ) -> Optional[TypeSuggestion]:
        """
        Suggest an old_type for the given description.

        Returns None if no keywords matched or the index is empty.
        """
        if not description or not self._keyword_types:
            return None

        type_scores: dict[str, int] = {}
        type_keywords: dict[str, list[str]] = {}

        for kw, types in self._keyword_types.items():
            if kw in description:
                for t in types:
                    type_scores[t] = type_scores.get(t, 0) + 1
                    type_keywords.setdefault(t, []).append(kw)

        if not type_scores:
            return None

        best_type = max(type_scores, key=lambda t: type_scores[t])
        best_score = type_scores[best_type]
        total_votes = sum(type_scores.values())

        confidence = best_score / total_votes if total_votes > 0 else 0.0

        # A single keyword match is inherently ambiguous → cap confidence so
        # the suggestion surfaces in the review sheet instead of auto-applying.
        if best_score == 1:
            confidence = min(confidence, 0.65)

        matched = type_keywords.get(best_type, [])
        reason = "关键词匹配 / Keyword match: " + "、".join(matched[:3])
        if len(matched) > 3:
            reason += f" 等（共 {len(matched)} 个）"

        return TypeSuggestion(
            suggested_type=best_type,
            confidence=confidence,
            matched_keywords=matched,
            reason=reason,
        )

    @property
    def has_index(self) -> bool:
        """True if any keyword rules were indexed (inference is meaningful)."""
        return bool(self._keyword_types)

    @property
    def indexed_keyword_count(self) -> int:
        return len(self._keyword_types)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_index(self, rules: list[MappingRule]) -> None:
        for rule in rules:
            old_type = (rule.old_type or "").strip()
            if not old_type or old_type == "__MISSING_TYPE__":
                continue
            for match in _KEYWORD_IN_DESC_RE.finditer(rule.condition):
                kw = match.group(1).strip()
                if not kw:
                    continue
                if kw not in self._keyword_types:
                    self._keyword_types[kw] = []
                if old_type not in self._keyword_types[kw]:
                    self._keyword_types[kw].append(old_type)
