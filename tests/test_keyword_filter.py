"""
Unit tests for KeywordFilter service.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.filter import KeywordFilter


def test_should_process_no_keywords():
    # When no keywords are configured, all posts should be accepted
    assert KeywordFilter.should_process("Any random post text", []) is True
    assert KeywordFilter.should_process("", []) is False


def test_should_process_with_matching_keywords():
    keywords = ["هوش مصنوعی", "پایتون", "اخبار"]
    post_text_1 = "این خبر جدید درباره پایتون است."
    post_text_2 = "هوش مصنوعی دنیا را تغییر می‌دهد."
    post_text_none = "یک مطلب درباره آشپزی و ورزش."

    assert KeywordFilter.should_process(post_text_1, keywords) is True
    assert KeywordFilter.should_process(post_text_2, keywords) is True
    assert KeywordFilter.should_process(post_text_none, keywords) is False


def test_case_and_arabic_persian_normalization():
    keywords = ["هوش مصنوعی", "کدنویسی"]
    # Using Arabic Kaf and Yeh in incoming text
    post_text = "آموزش جديد هوش مصنوعي و كدنویسی پیشرفته"
    assert KeywordFilter.should_process(post_text, keywords) is True
