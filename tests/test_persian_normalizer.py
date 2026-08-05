"""
Unit tests for Persian normalization and digit conversion utilities.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.persian import (
    normalize_persian_text,
    convert_english_to_persian_digits,
    convert_persian_to_english_digits,
    contains_any_keyword,
)


def test_normalize_persian_text():
    raw_arabic = "هوش مصنوعي و كد نويسي"
    normalized = normalize_persian_text(raw_arabic)
    assert "ی" in normalized
    assert "ک" in normalized
    assert "ي" not in normalized
    assert "ك" not in normalized


def test_digit_conversions():
    assert convert_english_to_persian_digits("2026") == "۲۰۲۶"
    assert convert_persian_to_english_digits("۲۰۲۶") == "2026"
    assert convert_persian_to_english_digits("٢٠٢٦") == "2026"  # Arabic digits


def test_contains_any_keyword():
    text = "این یک پست جدید درباره هوش‌مصنوعی و توسعه پایتون است."
    keywords_match = ["هوش مصنوعی", "جاوا"]
    keywords_no_match = ["بلاکچین", "رمزارز"]

    assert contains_any_keyword(text, keywords_match) is True
    assert contains_any_keyword(text, keywords_no_match) is False
