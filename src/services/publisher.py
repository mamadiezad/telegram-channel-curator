"""
Publisher & Draft Approval Service
==================================
Manages publishing workflows:
- 'review' mode: Sends draft preview to Admin with interactive inline buttons
  [✅ Approve & Publish] [❌ Reject] [🔄 Regenerate]
- 'auto' mode: Instantly publishes rewritten posts to the target channel
"""

from pyrogram import Client, types
from config import config
from src.db.database import curator_db
from src.utils.logger import logger


class PublisherService:
    """
    Handles publishing drafts to target channels or sending review prompts to admins.
    """
    def __init__(self, client: Client):
        self.client = client

    async def dispatch_post(
        self,
        draft_id: int,
        source_channel: str,
        rewritten_text: str,
        mode: str = "review"
    ) -> bool:
        """
        Dispatch the rewritten post according to the active workflow mode.
        """
        if not rewritten_text:
            logger.warning("Empty rewritten text for draft %s; skipping dispatch.", draft_id)
            return False

        if mode.lower() == "auto":
            return await self.publish_to_channel(draft_id, rewritten_text, status="AUTO_PUBLISHED")

        # Default: Review mode -> Send draft to Admin with inline buttons
        return await self.send_for_admin_review(draft_id, source_channel, rewritten_text)

    async def publish_to_channel(
        self,
        draft_id: int,
        text: str,
        status: str = "PUBLISHED"
    ) -> bool:
        """
        Publish the post directly to TARGET_CHANNEL and update SQLite record.
        """
        target = config.target_channel
        try:
            await self.client.send_message(
                chat_id=target,
                text=text,
                disable_web_page_preview=True
            )
            await curator_db.update_draft_status(draft_id, status=status)
            logger.info("Successfully published draft #%d to channel %s (%s)", draft_id, target, status)
            return True
        except Exception as exc:
            logger.error("Failed to publish draft #%d to %s: %s", draft_id, target, exc)
            return False

    async def send_for_admin_review(
        self,
        draft_id: int,
        source_channel: str,
        text: str
    ) -> bool:
        """
        Send a draft preview to ADMIN_USER_ID with an interactive inline keyboard.
        """
        admin_id = config.admin_user_id
        if not admin_id:
            logger.warning("ADMIN_USER_ID is not configured! Defaulting to AUTO publishing.")
            return await self.publish_to_channel(draft_id, text, status="AUTO_PUBLISHED")

        review_message = (
            f"📝 **پیش‌نویس جدید برای بررسی (Draft #{draft_id})**\n"
            "──────────────────────────────\n"
            f"📡 **کانال منبع:** `{source_channel}`\n"
            "──────────────────────────────\n\n"
            f"{text}\n\n"
            "──────────────────────────────\n"
            "🌟 **Made ❤️ by Mohammad** | `@llllxyz`"
        )

        keyboard = types.InlineKeyboardMarkup([
            [
                types.InlineKeyboardButton("✅ انتشار در کانال", callback_data=f"curator:pub:{draft_id}"),
                types.InlineKeyboardButton("❌ رد کردن", callback_data=f"curator:rej:{draft_id}")
            ],
            [
                types.InlineKeyboardButton("🔄 بازنویسی مجدد با AI", callback_data=f"curator:regen:{draft_id}")
            ]
        ])

        try:
            await self.client.send_message(
                chat_id=admin_id,
                text=review_message,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            logger.info("Draft #%d sent to admin %d for review.", draft_id, admin_id)
            return True
        except Exception as exc:
            logger.error("Failed to send draft #%d to admin %d: %s", draft_id, admin_id, exc)
            return False
