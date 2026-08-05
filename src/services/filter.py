"""
Keyword Filtering Service
=========================
Evaluates incoming Telegram channel posts against configured keyword rules
using Persian/Arabic character normalization.
"""

from typing import List
from src.utils.persian import contains_any_keyword
from src.utils.logger import logger


class KeywordFilter:
    """
    Evaluates whether a message body contains target keywords.
    """
    @staticmethod
    def should_process(text: str, keywords: List[str]) -> bool:
        """
        Determine if the post matches any active keywords.
        If no keywords are configured, returns True (accepts all posts from monitored channels).
        """
        if not text:
            return False

        if not keywords:
            logger.debug("No keyword filters configured; accepting post by default.")
            return True

        matched = contains_any_keyword(text, keywords)
        if matched:
            logger.info("Post matched target keyword filters.")
        else:
            logger.debug("Post ignored: did not match any active keywords.")

        return matched
