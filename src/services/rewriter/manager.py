"""
Rewrite Manager & Engine Orchestrator
=====================================
Orchestrates AI rewriting and fallback rule-based cleaning.
Attempts LLM rewriting first if configured; falls back automatically if the API fails
or is unavailable.
"""

from typing import Optional
from src.services.rewriter.llm import LLMRewriter
from src.services.rewriter.rule_based import RuleBasedRewriter
from src.utils.logger import logger


class RewriteManager:
    """
    Manages post rewriting across LLM and Rule-Based engines.
    """
    def __init__(self):
        self.llm_engine = LLMRewriter()

    async def process_text(self, raw_text: str, custom_prompt: Optional[str] = None) -> str:
        """
        Rewrite raw post text. Returns LLM output if available, otherwise rule-based clean text.
        """
        if not raw_text:
            return ""

        # Attempt LLM rewrite first
        llm_result = await self.llm_engine.rewrite(raw_text, custom_prompt=custom_prompt)
        if llm_result:
            logger.info("Post successfully rewritten using LLM engine.")
            return llm_result

        # Fallback to deterministic regex cleaner
        logger.debug("Applying rule-based rewriter fallback.")
        cleaned = RuleBasedRewriter.rewrite(raw_text)
        return cleaned


# Global rewrite orchestrator
rewrite_manager = RewriteManager()
