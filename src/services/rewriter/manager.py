from typing import Optional
from src.services.rewriter.llm import LLMRewriter
from src.services.rewriter.rule_based import RuleBasedRewriter
from src.utils.logger import logger


class RewriteManager:
    def __init__(self):
        self.llm_engine = LLMRewriter()

    async def process_text(self, raw_text: str, custom_prompt: Optional[str] = None) -> str:
        if not raw_text:
            return ""

        llm_result = await self.llm_engine.rewrite(raw_text, custom_prompt=custom_prompt)
        if llm_result:
            logger.info("Post successfully rewritten using LLM engine.")
            return llm_result

        logger.debug("Applying rule-based rewriter fallback.")
        return RuleBasedRewriter.rewrite(raw_text)


rewrite_manager = RewriteManager()
