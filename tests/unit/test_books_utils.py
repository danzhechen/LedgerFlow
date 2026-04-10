from pathlib import Path

import pytest

from veritas_accounting.utils.books import find_reference_book


def test_find_reference_book_prefers_exact_name(tmp_path: Path) -> None:
    books = tmp_path / "BOOKS"
    books.mkdir()
    exact = books / "2022Veritas China Account book.xlsx"
    exact.write_bytes(b"")
    other = books / "2022Veritas China Account book (1).xlsx"
    other.write_bytes(b"")

    assert find_reference_book(books, 2022) == exact


def test_find_reference_book_accepts_download_variant(tmp_path: Path) -> None:
    books = tmp_path / "BOOKS"
    books.mkdir()
    variant = books / "2022Veritas China Account book (1).xlsx"
    variant.write_bytes(b"")

    assert find_reference_book(books, 2022) == variant


def test_find_reference_book_globs_fallback(tmp_path: Path) -> None:
    books = tmp_path / "BOOKS"
    books.mkdir()
    candidate = books / "2022 - Veritas China Account book - final.xlsx"
    candidate.write_bytes(b"")

    assert find_reference_book(books, 2022) == candidate


def test_find_reference_book_raises_if_missing(tmp_path: Path) -> None:
    books = tmp_path / "BOOKS"
    books.mkdir()
    with pytest.raises(FileNotFoundError):
        find_reference_book(books, 2022)

