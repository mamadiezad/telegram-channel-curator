"""
Rule-Based Text Cleaner & Template Rewriter
===========================================
A deterministic fallback engine that cleans raw Telegram channel posts without requiring an LLM.
- Removes competitor `@username` mentions and URLs
- Normalizes spacing and paragraph formatting
- Adds automatically generated hashtags
- Appends the configured channel signature
"""

import re
from typing import List
from config import config
from src.utils.persian import normalize_persian_text


class RuleBasedRewriter:
    """
    Cleans and formats Telegram posts using regex and heuristic rules.
    """

    @classmethod
    def rewrite(cls, text: str, signature: str = "") -> str:
        """
        Clean the input text and attach the channel signature.
        """
        if not text:
            return ""

        # 1. Strip URLs (http, https, t.me, telegram.me)
        clean_text = re.sub(
            r"https?://\S+|t\.me/\S+|telegram\.me/\S+|www\.\S+",
            "",
            text,
            flags=re.IGNORECASE
        )

        # 2. Strip existing Telegram channel mentions (@username)
        clean_text = re.sub(r"@[A-Za-z0-9_]{4,}", "", clean_text)

        # 3. Clean consecutive spaces and trailing punctuation on empty lines
        lines = [line.strip() for line in clean_text.splitlines()]
        non_empty_lines = [l for l in lines if l]

        # 4. Generate basic hashtags based on content keywords
        hashtags = cls._extract_hashtags(" ".join(non_empty_lines))

        # 5. Build final post content
        formatted_body = "\n\n".join(non_empty_lines)
        if hashtags:
            formatted_body += f"\n\n{' '.join(hashtags)}"

        final_signature = signature or config.channel_signature
        if final_signature and final_signature not in formatted_body:
            formatted_body += f"\n\n{final_signature}"

        return formatted_body.strip()

    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
        """
        Heuristically assign hashtags based on common topic words in Persian.
        """
        norm = normalize_persian_text(text)
        tags: List[str] = []

        mapping = {
            "هوش مصنوعی": "#هوش_مصنوعی #AI",
            "پایتون": "#پایتون #Python",
            "برنامه نویسی": "#برنامه_نویسی #Programming",
            "تکنولوژی": "#تکنولوژی #Tech",
            "اخبار": "#اخبار",
            "بلاکچین": "#بلاکچین #Crypto",
            "لینوکس": "#لینوکس #Linux",
            "جاوا": "#جاوا",
        }

        for k, v in mapping.items():
            if k in norm and v not in tags:
                tags.extend(v.split())
                if len(tags) >= 3:
                    break

        return tags[:3]
