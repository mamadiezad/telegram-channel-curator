import re
from typing import List
from config import config
from src.utils.persian import normalize_persian_text


class RuleBasedRewriter:
    @classmethod
    def rewrite(cls, text: str, signature: str = "") -> str:
        if not text:
            return ""

        clean_text = re.sub(
            r"https?://\S+|t\.me/\S+|telegram\.me/\S+|www\.\S+",
            "",
            text,
            flags=re.IGNORECASE
        )
        clean_text = re.sub(r"@[A-Za-z0-9_]{4,}", "", clean_text)

        lines = [line.strip() for line in clean_text.splitlines()]
        non_empty_lines = [l for l in lines if l]

        hashtags = cls._extract_hashtags(" ".join(non_empty_lines))

        formatted_body = "\n\n".join(non_empty_lines)
        if hashtags:
            formatted_body += f"\n\n{' '.join(hashtags)}"

        final_signature = signature or config.channel_signature
        if final_signature and final_signature not in formatted_body:
            formatted_body += f"\n\n{final_signature}"

        return formatted_body.strip()

    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
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
