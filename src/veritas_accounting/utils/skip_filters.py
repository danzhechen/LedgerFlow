"""
Journal entries excluded from rule application and ledger generation.

Certain rows are pure internal movements or placeholders and should not appear
in the output workbook at all (per product rules).
"""

from __future__ import annotations

from decimal import Decimal

from veritas_accounting.models.journal import JournalEntry


def should_skip_entry(entry: JournalEntry) -> bool:
    """
    Return True if this journal row must not produce ledger lines.

    Skips:
    - Zero amount (no economic substance for double-entry output).
    - Descriptions containing 余利宝-基金赎回 or 余利宝自动转入 (asset-internal;
      omit entirely rather than bank DR/CR noise).

    All other internal-transfer patterns remain handled by mapping rules.
    """
    try:
        amt = entry.amount
        if isinstance(amt, Decimal):
            if amt == 0:
                return True
        elif float(amt) == 0.0:
            return True
    except Exception:
        pass

    desc = (entry.description or "").strip()
    if "余利宝-基金赎回" in desc or "余利宝自动转入" in desc:
        return True
    return False


def filter_skipped_journal_entries(entries: list[JournalEntry]) -> list[JournalEntry]:
    """Return a copy of the list with skipped entries removed."""
    return [e for e in entries if not should_skip_entry(e)]
