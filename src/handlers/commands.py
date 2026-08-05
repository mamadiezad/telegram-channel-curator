from pyrogram import Client, filters, types
from config import config
from src.db.database import curator_db
from src.services.rewriter.manager import rewrite_manager
from src.utils.logger import logger

ACTIVE_PUBLISHING_MODE: str = config.publishing_mode.lower()
ACTIVE_LLM_PROMPT: str = config.default_llm_prompt

FOOTER_ATTRIBUTION = (
    "──────────────────────────────\n"
    "🌟 **Made ❤️ by [Mohammad](https://t.me/llllxyz)** | `@llllxyz`"
)


def register_commands(app: Client) -> None:

    @app.on_message(filters.me & filters.command(["start", "help", "curator_help"], prefixes=["/", ".", "!"]))
    async def handle_help_command(client: Client, message: types.Message):
        help_text = (
            "🤖 **ربات ادمین و بازنویس هوشمند کانال تلگرام (Telegram Auto-Curator)**\n"
            "──────────────────────────────\n"
            "این ربات پست‌ها را از کانال‌های مبدا مانیتور کرده، بر اساس کلیدواژه‌های شما فیلتر می‌کند "
            "و با هوش مصنوعی (یا موتور قالبی) بازنویسی و در کانال شما منتشر می‌کند.\n\n"
            "📌 **دستورات مدیریت کانال‌های مبدا (Sources):**\n"
            "• `/add_source @ChannelUsername` : افزودن کانال برای مانیتورینگ\n"
            "• `/remove_source @ChannelUsername` : حذف کانال مبدا\n"
            "• `/list_sources` : مشاهده لیست کانال‌های تحت نظر\n\n"
            "📌 **دستورات فیلتر کلیدواژه‌ها (Keywords):**\n"
            "• `/add_keyword هوش مصنوعی` : افزودن کلمه کلیدی\n"
            "• `/remove_keyword هوش مصنوعی` : حذف کلمه کلیدی\n"
            "• `/list_keywords` : نمایش کلمات کلیدی فعال\n\n"
            "📌 **دستورات انتشار و بررسی پیش‌نویس‌ها (Drafts):**\n"
            "• `/pub <id>` : تایید و انتشار فوری پیش‌نویس شماره id در کانال\n"
            "• `/rej <id>` : رد کردن و لغو پیش‌نویس شماره id\n"
            "• `/regen <id>` : بازنویسی مجدد پیش‌نویس با هوش مصنوعی\n\n"
            "📌 **دستورات تنظیمات و آمار:**\n"
            "• `/mode auto` یا `/mode review` : تغییر حالت انتشار\n"
            "• `/set_prompt <متن>` : تغییر دستورالعمل هوش مصنوعی\n"
            "• `/stats` : نمایش آمار کلی\n"
            f"{FOOTER_ATTRIBUTION}"
        )
        await message.edit_text(help_text, disable_web_page_preview=True)

    @app.on_message(filters.me & filters.command(["pub", "publish"], prefixes=["/", ".", "!"]))
    async def handle_publish_draft(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ شناسه پیش‌نویس را وارد کنید. مثال: `/pub 15`")
            return
        try:
            draft_id = int(message.command[1])
        except ValueError:
            await message.edit_text("❌ شناسه باید عدد باشد.")
            return

        draft = await curator_db.get_draft(draft_id)
        if not draft:
            await message.edit_text("⚠️ پیش‌نویس در پایگاه داده یافت نشد.")
            return

        from src.services.publisher import PublisherService
        publisher = PublisherService(client)
        success = await publisher.publish_to_channel(draft_id, draft["rewritten_text"], status="PUBLISHED")
        if success:
            await message.edit_text(
                f"✅ **[منتشر شد - Published #{draft_id}]**\n"
                "──────────────────────────────\n"
                f"{draft['rewritten_text']}\n"
                f"{FOOTER_ATTRIBUTION}",
                disable_web_page_preview=True
            )
        else:
            await message.edit_text("❌ خطا در انتشار پست در کانال هدف.")

    @app.on_message(filters.me & filters.command(["rej", "reject"], prefixes=["/", ".", "!"]))
    async def handle_reject_draft(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ شناسه پیش‌نویس را وارد کنید. مثال: `/rej 15`")
            return
        try:
            draft_id = int(message.command[1])
        except ValueError:
            await message.edit_text("❌ شناسه باید عدد باشد.")
            return

        await curator_db.update_draft_status(draft_id, "REJECTED")
        await message.edit_text(
            f"❌ **[رد شد - Rejected #{draft_id}]**\n"
            "──────────────────────────────\n"
            f"پیش‌نویس شماره {draft_id} توسط ادمین لغو شد.\n"
            f"{FOOTER_ATTRIBUTION}"
        )

    @app.on_message(filters.me & filters.command(["regen", "regenerate"], prefixes=["/", ".", "!"]))
    async def handle_regen_draft(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ شناسه پیش‌نویس را وارد کنید. مثال: `/regen 15`")
            return
        try:
            draft_id = int(message.command[1])
        except ValueError:
            await message.edit_text("❌ شناسه باید عدد باشد.")
            return

        draft = await curator_db.get_draft(draft_id)
        if not draft:
            await message.edit_text("⚠️ پیش‌نویس در پایگاه داده یافت نشد.")
            return

        await message.edit_text("⏳ در حال بازنویسی مجدد پیش‌نویس با هوش مصنوعی...")
        new_rewritten = await rewrite_manager.process_text(
            draft["original_text"],
            custom_prompt=ACTIVE_LLM_PROMPT
        )
        if new_rewritten:
            await curator_db.update_draft_text(draft_id, new_rewritten)
            review_message = (
                f"📝 **پیش‌نویس بازنویسی‌شده جدید (Draft #{draft_id})**\n"
                "──────────────────────────────\n"
                f"📡 **کانال منبع:** `{draft['source_channel']}`\n"
                "──────────────────────────────\n\n"
                f"{new_rewritten[:3000]}\n\n"
                "──────────────────────────────\n"
                "💡 **دستورات سریع مدیریت این پیش‌نویس:**\n"
                f"• انتشار در کانال ➔ `/pub {draft_id}`\n"
                f"• رد کردن پیش‌نویس ➔ `/rej {draft_id}`\n"
                f"• بازنویسی مجدد با AI ➔ `/regen {draft_id}`\n"
                f"{FOOTER_ATTRIBUTION}"
            )
            await message.edit_text(review_message, disable_web_page_preview=True)
        else:
            await message.edit_text("❌ خطا در بازنویسی مجدد.")

    @app.on_message(filters.me & filters.command(["add_source"], prefixes=["/", ".", "!"]))
    async def handle_add_source(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا نام کاربری کانال را وارد کنید. مثال: `/add_source @TechNewsFA`")
            return
        channel_name = message.command[1].strip()
        if not channel_name.startswith("@") and not channel_name.startswith("-100"):
            channel_name = f"@{channel_name}"
        added = await curator_db.add_source(channel_name)
        if added:
            await message.edit_text(f"✅ کانال `{channel_name}` با موفقیت به لیست مانیتورینگ اضافه شد.\n{FOOTER_ATTRIBUTION}")
        else:
            await message.edit_text(f"ℹ️ کانال `{channel_name}` از قبل در لیست وجود دارد.\n{FOOTER_ATTRIBUTION}")

    @app.on_message(filters.me & filters.command(["remove_source"], prefixes=["/", ".", "!"]))
    async def handle_remove_source(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا نام کانال را وارد کنید. مثال: `/remove_source @TechNewsFA`")
            return
        channel_name = message.command[1].strip()
        removed = await curator_db.remove_source(channel_name)
        if removed:
            await message.edit_text(f"✅ کانال `{channel_name}` از لیست مانیتورینگ حذف شد.\n{FOOTER_ATTRIBUTION}")
        else:
            await message.edit_text(f"❌ کانال `{channel_name}` در لیست یافت نشد.")

    @app.on_message(filters.me & filters.command(["list_sources"], prefixes=["/", ".", "!"]))
    async def handle_list_sources(client: Client, message: types.Message):
        sources = await curator_db.get_sources()
        if not sources:
            await message.edit_text(f"📭 لیست کانال‌های مبدا خالی است. با `/add_source` کانال جدید اضافه کنید.\n{FOOTER_ATTRIBUTION}")
            return
        text = "📡 **کانال‌های مبدا تحت مانیتورینگ:**\n──────────────────────────────\n"
        for idx, src in enumerate(sources, 1):
            text += f"**{idx}.** `{src}`\n"
        text += f"{FOOTER_ATTRIBUTION}"
        await message.edit_text(text, disable_web_page_preview=True)

    @app.on_message(filters.me & filters.command(["add_keyword"], prefixes=["/", ".", "!"]))
    async def handle_add_keyword(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا کلمه کلیدی را وارد کنید. مثال: `/add_keyword پایتون`")
            return
        word = " ".join(message.command[1:]).strip()
        added = await curator_db.add_keyword(word)
        if added:
            await message.edit_text(f"✅ کلمه کلیدی «`{word}`» به فیلترها اضافه شد.\n{FOOTER_ATTRIBUTION}")
        else:
            await message.edit_text(f"ℹ️ کلمه «`{word}`» از قبل در لیست فیلترها وجود دارد.")

    @app.on_message(filters.me & filters.command(["remove_keyword"], prefixes=["/", ".", "!"]))
    async def handle_remove_keyword(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا کلمه کلیدی را وارد کنید. مثال: `/remove_keyword پایتون`")
            return
        word = " ".join(message.command[1:]).strip()
        removed = await curator_db.remove_keyword(word)
        if removed:
            await message.edit_text(f"✅ کلمه کلیدی «`{word}`» حذف شد.\n{FOOTER_ATTRIBUTION}")
        else:
            await message.edit_text(f"❌ کلمه «`{word}`» در لیست یافت نشد.")

    @app.on_message(filters.me & filters.command(["list_keywords"], prefixes=["/", ".", "!"]))
    async def handle_list_keywords(client: Client, message: types.Message):
        keywords = await curator_db.get_keywords()
        if not keywords:
            await message.edit_text(f"🟢 لیست کلیدواژه‌ها خالی است (تمام پست‌های کانال‌های مبدا پردازش می‌شوند).\n{FOOTER_ATTRIBUTION}")
            return
        text = "🔑 **کلیدواژه‌های فعال فیلترینگ:**\n──────────────────────────────\n"
        for idx, kw in enumerate(keywords, 1):
            text += f"**{idx}.** `{kw}`\n"
        text += f"{FOOTER_ATTRIBUTION}"
        await message.edit_text(text, disable_web_page_preview=True)

    @app.on_message(filters.me & filters.command(["mode", "set_mode"], prefixes=["/", ".", "!"]))
    async def handle_set_mode(client: Client, message: types.Message):
        global ACTIVE_PUBLISHING_MODE
        if len(message.command) < 2 or message.command[1].lower() not in ("auto", "review"):
            await message.edit_text(
                f"ℹ️ **حالت فعلی انتشار:** `{ACTIVE_PUBLISHING_MODE.upper()}`\n\n"
                "برای تغییر حالت از یکی از دستورات زیر استفاده کنید:\n"
                "• `/mode auto` : انتشار کاملاً خودکار در کانال هدف\n"
                "• `/mode review` : ارسال پیش‌نویس به ادمین همراه با دستورات انتشار\n"
                f"{FOOTER_ATTRIBUTION}"
            )
            return
        new_mode = message.command[1].lower()
        ACTIVE_PUBLISHING_MODE = new_mode
        mode_fa = "انتشار خودکار (Auto)" if new_mode == "auto" else "تایید ادمین (Review)"
        await message.edit_text(f"⚙️ حالت انتشار با موفقیت به **{mode_fa}** تغییر یافت.\n{FOOTER_ATTRIBUTION}")

    @app.on_message(filters.me & filters.command(["set_prompt"], prefixes=["/", ".", "!"]))
    async def handle_set_prompt(client: Client, message: types.Message):
        global ACTIVE_LLM_PROMPT
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا متن دستورالعمل جدید هوش مصنوعی را وارد کنید.")
            return
        new_prompt = " ".join(message.command[1:]).strip()
        ACTIVE_LLM_PROMPT = new_prompt
        await message.edit_text(
            f"🧠 **دستورالعمل بازنویسی هوش مصنوعی به‌روزرسانی شد:**\n\n`{new_prompt}`\n{FOOTER_ATTRIBUTION}"
        )

    @app.on_message(filters.me & filters.command(["stats", "curator_stats"], prefixes=["/", ".", "!"]))
    async def handle_stats(client: Client, message: types.Message):
        stats = await curator_db.get_summary_stats()
        text = (
            "📊 **آمار عملکرد ربات بازنویس هوشمند کانال (Curator Stats)**\n"
            "──────────────────────────────\n"
            f"📥 **کل پست‌های پردازش‌شده:** `{stats['total_processed']:,}`\n"
            f"🚀 **منتشرشده در کانال:** `{stats['total_published']:,}`\n"
            f"⏳ **در انتظار تایید ادمین:** `{stats['total_pending']:,}`\n"
            f"❌ **ردشده توسط ادمین:** `{stats['total_rejected']:,}`\n"
            f"{FOOTER_ATTRIBUTION}"
        )
        await message.edit_text(text, disable_web_page_preview=True)
