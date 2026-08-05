from pyrogram import Client, filters, types
from src.db.database import curator_db
from src.services.filter import KeywordFilter
from src.services.rewriter.manager import rewrite_manager
from src.services.publisher import PublisherService
from src.utils.logger import logger


def register_monitor(app: Client, publisher: PublisherService) -> None:

    @app.on_message(filters.channel & ~filters.me)
    async def on_channel_post(client: Client, message: types.Message):
        chat = message.chat
        source_id = f"@{chat.username}" if chat.username else str(chat.id)

        monitored_sources = await curator_db.get_sources()
        is_monitored = False
        for src in monitored_sources:
            if src.lower() in (source_id.lower(), str(chat.id), f"@{chat.username or ''}".lower()):
                is_monitored = True
                break

        if not is_monitored:
            return

        if await curator_db.is_post_processed(source_id, message.id):
            logger.debug("Post %d from %s already processed; skipping.", message.id, source_id)
            return

        raw_text = message.text or message.caption or ""
        if not raw_text.strip():
            logger.debug("Skipping media-only post %d with no caption from %s", message.id, source_id)
            return

        keywords = await curator_db.get_keywords()
        if not KeywordFilter.should_process(raw_text, keywords):
            return

        logger.info("New matching post detected from %s (MsgID: %d)", source_id, message.id)

        from src.handlers.commands import ACTIVE_LLM_PROMPT, ACTIVE_PUBLISHING_MODE
        rewritten_content = await rewrite_manager.process_text(
            raw_text,
            custom_prompt=ACTIVE_LLM_PROMPT
        )

        draft_id = await curator_db.record_draft(
            source_channel=source_id,
            source_msg_id=message.id,
            original_text=raw_text,
            rewritten_text=rewritten_content,
            status="PENDING_REVIEW"
        )

        await publisher.dispatch_post(
            draft_id=draft_id,
            source_channel=source_id,
            rewritten_text=rewritten_content,
            mode=ACTIVE_PUBLISHING_MODE
        )
