"""
Telegram Client & Application Factory
=====================================
Manages MTProto userbot client instantiation, registers command/callback/monitor handlers,
and initializes core curation services.
"""

from pyrogram import Client
from config import config
from src.services.publisher import PublisherService
from src.handlers.commands import register_commands
from src.handlers.callbacks import register_callbacks
from src.handlers.monitor import register_monitor
from src.utils.logger import logger


def create_client() -> Client:
    """Create and return a configured Pyrogram MTProto Client."""
    if not config.is_telegram_configured():
        logger.warning(
            "TELEGRAM_API_ID or TELEGRAM_API_HASH is missing in .env! "
            "Please configure your credentials from my.telegram.org."
        )

    app = Client(
        name=config.session_name,
        api_id=config.telegram_api_id,
        api_hash=config.telegram_api_hash,
        phone_number=config.telegram_phone_number,
        workdir=".",
    )
    return app


def initialize_app(app: Client) -> PublisherService:
    """Register all handlers and instantiate the publisher service."""
    logger.info("Initializing Telegram Channel Curator services...")
    publisher_service = PublisherService(client=app)

    # Register handlers
    register_commands(app)
    register_callbacks(app, publisher_service)
    register_monitor(app, publisher_service)

    logger.info("All handlers and aggregation pipelines registered successfully.")
    return publisher_service
