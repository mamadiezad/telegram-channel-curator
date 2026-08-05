"""
Unit tests for the Rule-Based Rewriter and Template Cleaner.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.rewriter.rule_based import RuleBasedRewriter


def test_rule_based_strips_mentions_and_urls():
    raw_post = (
        "سلام دوستان! اخبار جدید هوش مصنوعی منتشر شد.\n"
        "منبع: @CompetitorChannel\n"
        "لینک خبر: https://t.me/example/123\n"
    )

    cleaned = RuleBasedRewriter.rewrite(raw_post, signature="@MyTechNewsChannel")
    assert "@CompetitorChannel" not in cleaned
    assert "https://t.me/example/123" not in cleaned
    assert "@MyTechNewsChannel" in cleaned
    assert "#هوش_مصنوعی" in cleaned or "#AI" in cleaned


def test_empty_post():
    assert RuleBasedRewriter.rewrite("") == ""
