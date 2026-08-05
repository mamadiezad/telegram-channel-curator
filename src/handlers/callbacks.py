"""
Admin Inline Keyboard Callback Handlers
=======================================
Processes interactive inline button actions on draft review cards:
- Approve and publish draft to the target channel
- Reject and discard draft
- Regenerate rewritten text using the AI engine
"""

from pyrogram import Client, types
from src.db.database import curator_db
from src.services.publisher import PublisherService
from src.services.rewriter.manager import rewrite_manager
from src.utils.logger import logger


def register_callbacks(app: Client, publisher: PublisherService) -> None:
    """Register callback query handlers for inline draft management buttons."""

    @app.on_callback_query()
    async def handle_inline_callback(client: Client, callback: types.CallbackQuery):
        data = callback.data or ""
        if not data.startswith("curator:"):
            return

        parts = data.split(":")
        if len(parts) < 3:
            await callback.answer("❌ داده نامعتبر.", show_alert=True)
            return

        action = parts[1]
        try:
            draft_id = int(parts[2])
        except ValueError:
            await callback.answer("❌ شناسه پیش‌نویس نامعتبر است.", show_alert=True)
            return

        draft = await curator_db.get_draft(draft_id)
        if not draft:
            await callback.answer("⚠️ این پیش‌نویس در پایگاه داده یافت نشد.", show_alert=True)
            return

        if action == "pub":
            success = await publisher.publish_to_channel(draft_id, draft["rewritten_text"], status="PUBLISHED")
            if success:
                await callback.answer("✅ پست با موفقیت در کانال منتشر شد!", show_alert=False)
                new_text = (
                    f"✅ **[منتشر شد - Published #{draft_id}]**\n"
                    "──────────────────────────────\n"
                    f"{draft['rewritten_text']}\n"
                    "──────────────────────────────\n"
                    "🌟 **Made ❤️ by Mohammad** | `@llllxyz`"
                )
                try:
                    await callback.message.edit_text(new_text, reply_markup=None, disable_web_page_preview=True)
                except Exception:
                    pass
            else:
                await callback.answer("❌ خطا در انتشار در کانال هدف. دسترسی ربات را بررسی کنید.", show_alert=True)

        elif action == "rej":
            await curator_db.update_draft_status(draft_id, "REJECTED")
            await callback.answer("❌ پست رد شد و از لیست انتشار حذف گردید.", show_alert=False)
            new_text = (
                f"❌ **[رد شد - Rejected #{draft_id}]**\n"
                "──────────────────────────────\n"
                f"پیش‌نویس شماره {draft_id} توسط ادمین لغو شد.\n"
                "──────────────────────────────\n"
                "🌟 **Made ❤️ by Mohammad** | `@llllxyz`"
            )
            try:
                await callback.message.edit_text(new_text, reply_markup=None)
            except Exception:
                pass

        elif action == "regen":
            await callback.answer("⏳ در حال بازنویسی مجدد با هوش مصنوعی...", show_alert=False)
            from src.handlers.commands import ACTIVE_LLM_PROMPT
            new_rewritten = await rewrite_manager.process_text(
                draft["original_text"],
                custom_prompt=ACTIVE_LLM_PROMPT
            )
            if new_rewritten:
                await curator_db.update_draft_text(draft_id, new_rewritten)
                keyboard = types.InlineKeyboardMarkup([
                    [
                        types.InlineKeyboardButton("✅ انتشار در کانال", callback_data=f"curator:pub:{draft_id}"),
                        types.InlineKeyboardButton("❌ رد کردن", callback_data=f"curator:rej:{draft_id}")
                    ],
                    [
                        types.InlineKeyboardButton("🔄 بازنویسی مجدد با AI", callback_data=f"curator:regen:{draft_id}")
                    ]
                ])
                review_message = (
                    f"📝 **پیش‌نویس بازنویسی‌شده جدید (Draft #{draft_id})**\n"
                    "──────────────────────────────\n"
                    f"📡 **کانال منبع:** `{draft['source_channel']}`\n"
                    "──────────────────────────────\n\n"
                    f"{new_rewritten}\n\n"
                    "──────────────────────────────\n"
                    "🌟 **Made ❤️ by Mohammad** | `@llllxyz`"
                )
                try:
                    await callback.message.edit_text(
                        review_message,
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                except Exception as exc:
                    logger.debug("Failed to update regenerated card: %s", exc)
            else:
                await callback.answer("❌ خطا در بازنویسی مجدد.", show_alert=True)
