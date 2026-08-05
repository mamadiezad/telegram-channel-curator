"""
Application Configuration Loader
================================
Manages environment variables and application defaults with Pydantic Settings.
Supports type validation for Telegram API credentials, LLM configuration, and workflow modes.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """
    Settings for Telegram Channel Auto-Curator & AI Rewriter.
    Loads from .env file or environment variables.
    """
    # Telegram API Credentials
    telegram_api_id: int = Field(default=0, description="Telegram API ID from my.telegram.org")
    telegram_api_hash: str = Field(default="", description="Telegram API Hash from my.telegram.org")
    telegram_phone_number: Optional[str] = Field(
        default=None,
        description="Phone number for initial session authentication"
    )
    session_name: str = Field(default="channel_curator_session", description="Session filename")

    # Publishing & Admin Target
    target_channel: str = Field(
        default="@MyTechNewsChannel",
        description="Target channel ID or @username where posts are published"
    )
    admin_user_id: int = Field(
        default=0,
        description="Admin Telegram ID for draft review and management commands"
    )
    publishing_mode: str = Field(
        default="review",
        description="Workflow mode: 'review' (requires approval) or 'auto' (instant post)"
    )

    # LLM Rewriting Engine
    openai_api_key: Optional[str] = Field(
        default=None,
        description="API key for OpenAI, DeepSeek, or OpenRouter"
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for LLM API (compatible with OpenAI format)"
    )
    llm_model_name: str = Field(default="gpt-4o-mini", description="LLM model identifier")
    default_llm_prompt: str = Field(
        default=(
            "Rewrite the following Telegram post in Persian with an engaging, professional tone. "
            "Summarize the key takeaways, remove external URLs and competitor IDs, "
            "add 2-3 relevant hashtags, and keep it clean."
        ),
        description="Default system prompt for AI rewriting"
    )

    # Output Formatting
    channel_signature: str = Field(
        default="@MyTechNewsChannel",
        description="Footer signature appended to each rewritten post"
    )

    # Database & Logs
    database_path: str = Field(default="data/curator.db", description="SQLite database path")
    log_level: str = Field(default="INFO", description="Logging verbosity")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def is_telegram_configured(self) -> bool:
        """Verify that basic Telegram API credentials are provided."""
        return self.telegram_api_id > 0 and bool(self.telegram_api_hash)

    def is_llm_configured(self) -> bool:
        """Check whether an API key has been provided for LLM rewriting."""
        return bool(self.openai_api_key and self.openai_api_key.strip())


config = AppConfig()

# Ensure required directories exist
Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
