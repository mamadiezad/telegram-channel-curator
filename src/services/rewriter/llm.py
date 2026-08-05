from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from config import config
from src.utils.logger import logger


class LLMRewriter:
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        if config.is_llm_configured():
            try:
                self.client = AsyncOpenAI(
                    api_key=config.openai_api_key,
                    base_url=config.openai_base_url
                )
                logger.info("LLM client initialized with base URL: %s", config.openai_base_url)
            except Exception as exc:
                logger.error("Failed to initialize LLM client: %s", exc)

    async def rewrite(self, text: str, custom_prompt: Optional[str] = None) -> Optional[str]:
        if not self.client or not text:
            return None

        system_instruction = (
            custom_prompt
            or config.default_llm_prompt
            or (
                "Rewrite the following Telegram post in Persian in an engaging, professional tone. "
                "Summarize key points, strip competitor links/IDs, add 2-3 hashtags, and keep it readable."
            )
        )

        try:
            response = await self.client.chat.completions.create(
                model=config.llm_model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"RAW POST TO REWRITE:\n\n{text}"},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            rewritten_content = response.choices[0].message.content
            if rewritten_content:
                signature = config.channel_signature
                if signature and signature not in rewritten_content:
                    rewritten_content = f"{rewritten_content.strip()}\n\n{signature}"
                return rewritten_content.strip()
        except OpenAIError as exc:
            logger.warning("LLM API call failed (%s); falling back to rule-based rewriter.", exc)
        except Exception as exc:
            logger.error("Unexpected error during LLM rewriting: %s", exc, exc_info=True)

        return None
