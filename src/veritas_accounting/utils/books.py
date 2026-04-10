"""Helpers for locating human reference account books."""

from __future__ import annotations

from pathlib import Path


def find_reference_book(books_dir: Path, year: int) -> Path:
    """
    Find a reference account book for a given year inside BOOKS/.

    Supports common downloaded filename variants such as:
    - '{year}Veritas China Account book.xlsx'
    - '{year}Veritas China Account book (1).xlsx'
    - '{year}*Account book*.xlsx'
    """
    if not books_dir.exists():
        raise FileNotFoundError(f"BOOKS directory not found: {books_dir}")

    exact = books_dir / f"{year}Veritas China Account book.xlsx"
    if exact.exists():
        return exact

    # Common browser download variant
    variant = books_dir / f"{year}Veritas China Account book (1).xlsx"
    if variant.exists():
        return variant

    # Best-effort fallback: anything that looks like the right year + account book
    candidates = sorted(
        books_dir.glob(f"{year}*Account book*.xlsx"),
        key=lambda p: (len(p.name), p.name),
    )
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        f"Reference book for year {year} not found in {books_dir}. "
        f"Expected something like '{exact.name}'."
    )

