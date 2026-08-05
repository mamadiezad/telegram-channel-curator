from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    telegram_api_id: int = Field(default=0)
    telegram_api_hash: str = Field(default="")
    telegram_phone_number: Optional[str] = Field(default=None)
    session_name: str = Field(default="channel_curator_session")
    target_channel: str = Field(default="@MyTechNewsChannel")
    admin_user_id: int = Field(default=0)
    publishing_mode: str = Field(default="review")
    openai_api_key: Optional[str] = Field(default=None)
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    llm_model_name: str = Field(default="gpt-4o-mini")
    default_llm_prompt: str = Field(
        default=(
            "Rewrite the following Telegram post in Persian with an engaging, professional tone. "
            "Summarize the key takeaways, remove external URLs and competitor IDs, "
            "add 2-3 relevant hashtags, and keep it clean."
        )
    )
    channel_signature: str = Field(default="@MyTechNewsChannel")
    database_path: str = Field(default="data/curator.db")
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def is_telegram_configured(self) -> bool:
        return self.telegram_api_id > 0 and bool(self.telegram_api_hash)

    def is_llm_configured(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


config = AppConfig()
Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
