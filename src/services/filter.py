from typing import List
from src.utils.persian import contains_any_keyword
from src.utils.logger import logger


class KeywordFilter:
    @staticmethod
    def should_process(text: str, keywords: List[str]) -> bool:
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
