import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from src.client import create_client, initialize_app
from src.db.database import curator_db
from src.utils.logger import logger

ASCII_BANNER = """
================================================================
   _______ _                                 ______  __  __ 
  |__   __(_)                               |  ____|/ / / / 
     | |   _   __ _  ___  _ __ __ _ _ __    | |__  / /_/ /  
     | |  | | / _` |/ _ \\| '__/ _` | '_ \\   |  __|/ '_ \\/ /   
     | |  | || (_| | (_) | | | (_| | | | |  | |  / (_) / /    
     |_|  |_| \\__, |\\___/|_|  \\__,_|_| |_|  |_|  \\___//_/     
               __/ |                                        
              |___/     TELEGRAM CHANNEL AUTO-CURATOR BOT     
================================================================
               Made ❤️ by Mohammad | Telegram: @llllxyz      
================================================================
"""


async def start_database():
    await curator_db.init_db()


def main():
    print(ASCII_BANNER)
    logger.info("Starting Telegram Channel Auto-Curator Bot...")

    try:
        asyncio.run(start_database())
    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
        sys.exit(1)

    if not config.is_telegram_configured():
        logger.error(
            "CRITICAL: TELEGRAM_API_ID and TELEGRAM_API_HASH are not configured. "
            "Please copy .env.example to .env and insert your API credentials from my.telegram.org."
        )
        sys.exit(1)

    app = create_client()
    initialize_app(app)

    logger.info("Connecting to Telegram servers...")
    logger.info("Send /help or /curator_help to your account to view admin management commands.")
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Shutting down cleanly.")
    except Exception as exc:
        logger.critical("Fatal error in Telegram client loop: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
