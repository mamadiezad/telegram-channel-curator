"""
Persian Text Normalization & Helper Module
==========================================
Provides utility methods to normalize Persian/Arabic characters, unify spacing,
and convert numerals for reliable keyword matching and text cleaning.
"""

import re
from typing import List


def normalize_persian_text(text: str) -> str:
    """
    Normalize Persian/Arabic characters and spacing for accurate comparison.
    - Converts Arabic Yeh ('ي') and Alef Maksura ('ى') to Persian Yeh ('ی')
    - Converts Arabic Kaf ('ك') to Persian Kaf ('ک')
    - Replaces zero-width non-joiner (ZWNJ / نیم‌فاصله) with standard space for matching
    - Converts multiple consecutive spaces into a single space
    """
    if not text:
        return ""

    text = text.replace("ي", "ی").replace("ى", "ی")
    text = text.replace("ك", "ک")
    # Replace zero-width non-joiner with space for keyword search
    text = text.replace("\u200c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def convert_english_to_persian_digits(text: str) -> str:
    """
    Convert English digits to Persian numerals for display in final posts.
    Example: '2026' -> '۲۰۲۶'
    """
    english_digits = "0123456789"
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"

    for e, p in zip(english_digits, persian_digits):
        text = text.replace(e, p)
    return text


def convert_persian_to_english_digits(text: str) -> str:
    """
    Convert Persian and Arabic numerals to English digits.
    """
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"

    for p, e in zip(persian_digits, english_digits):
        text = text.replace(p, e)
    for a, e in zip(arabic_digits, english_digits):
        text = text.replace(a, e)
    return text


def contains_any_keyword(text: str, keywords: List[str]) -> bool:
    """
    Check whether any of the target keywords appear in the given text.
    Both the text and keywords are normalized prior to matching.
    """
    if not text or not keywords:
        return False

    normalized_text = normalize_persian_text(text)
    for keyword in keywords:
        norm_kw = normalize_persian_text(keyword)
        if norm_kw and norm_kw in normalized_text:
            return True

    return False
