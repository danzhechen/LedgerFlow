"""Worksheet selection helpers."""

from __future__ import annotations

import re
from typing import Iterable


_YEAR_SHEET_RE = re.compile(r"^20\d{2}$")


def detect_year_like_sheets(sheet_names: Iterable[str]) -> list[str]:
    """
    Return sheet names that look like years (e.g. '2022') in ascending order.

    If none look like years, returns an empty list.
    """
    years: list[tuple[int, str]] = []
    for name in sheet_names:
        s = str(name).strip()
        if _YEAR_SHEET_RE.match(s):
            years.append((int(s), s))
    return [s for _, s in sorted(years, key=lambda t: t[0])]


def default_sheets_to_process(sheet_names: Iterable[str]) -> list[str]:
    """
    Default sheet selection policy:
    - If year-like sheets exist, process only those (in year order).
    - Otherwise, process all sheets (original order preserved).
    """
    sheet_list = list(sheet_names)
    year_sheets = detect_year_like_sheets(sheet_list)
    return year_sheets if year_sheets else sheet_list

