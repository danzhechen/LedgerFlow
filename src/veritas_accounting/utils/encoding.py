"""Encoding utilities for Chinese text support in veritas-accounting."""

import sys
from pathlib import Path
from typing import Optional

try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False


def ensure_utf8_encoding() -> None:
    """
    Ensure UTF-8 encoding is set for stdout/stderr.

    This helps ensure Chinese text displays correctly in console/terminal.
    """
    if sys.stdout.encoding != "utf-8":
        # Try to set UTF-8 encoding
        try:
            if sys.platform == "win32":
                # Windows: Set console code page to UTF-8
                import codecs

                sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
                sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
            else:
                # Unix-like: Usually already UTF-8, but ensure it
                import locale

                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except Exception:
            # If we can't set encoding, continue anyway
            # Most modern systems handle UTF-8 correctly
            pass


def detect_file_encoding(file_path: Path) -> Optional[str]:
    """
    Detect the encoding of a text file.

    Args:
        file_path: Path to the file

    Returns:
        Detected encoding (e.g., 'utf-8', 'gb2312') or None if detection fails
    """
    if not HAS_CHARDET:
        # If chardet is not available, assume UTF-8 for Excel files
        return "utf-8"

    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            return result.get("encoding") if result else None
    except Exception:
        return None


def validate_utf8_text(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate that text can be encoded as UTF-8.

    Args:
        text: Text to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        text.encode("utf-8")
        return True, None
    except UnicodeEncodeError as e:
        return False, f"Text contains characters that cannot be encoded as UTF-8: {e}"


def normalize_chinese_text(text: str) -> str:
    """
    Normalize Chinese text (handle both simplified and traditional).

    Args:
        text: Chinese text to normalize

    Returns:
        Normalized text
    """
    # For now, just return as-is
    # In the future, could add conversion between simplified/traditional
    return text


def safe_encode(text: str, encoding: str = "utf-8", errors: str = "replace") -> bytes:
    """
    Safely encode text with error handling.

    Args:
        text: Text to encode
        encoding: Target encoding (default: utf-8)
        errors: Error handling strategy ('strict', 'ignore', 'replace')

    Returns:
        Encoded bytes
    """
    return text.encode(encoding, errors=errors)


def safe_decode(
    data: bytes, encoding: str = "utf-8", errors: str = "replace"
) -> str:
    """
    Safely decode bytes to text with error handling.

    Args:
        data: Bytes to decode
        encoding: Source encoding (default: utf-8)
        errors: Error handling strategy ('strict', 'ignore', 'replace')

    Returns:
        Decoded text
    """
    return data.decode(encoding, errors=errors)








