"""
Admin Command Handlers
======================
Interactive Telegram command interface for managing monitored source channels,
keyword filters, AI prompt instructions, and publishing modes.
"""

from pyrogram import Client, filters, types
from config import config
from src.db.database import curator_db
from src.utils.logger import logger

# Active publishing mode in memory (defaults to config.publishing_mode)
ACTIVE_PUBLISHING_MODE: str = config.publishing_mode.lower()
ACTIVE_LLM_PROMPT: str = config.default_llm_prompt


def register_commands(app: Client) -> None:
    """Register all admin management command handlers."""

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
            "• `/add_keyword هوش مصنوعی` : افزودن کلمه کلیدی (در صورت خالی بودن لیست، تمام پست‌ها دریافت می‌شوند)\n"
            "• `/remove_keyword هوش مصنوعی` : حذف کلمه کلیدی\n"
            "• `/list_keywords` : نمایش کلمات کلیدی فعال\n\n"
            "📌 **دستورات تنظیمات انتشار و هوش مصنوعی:**\n"
            "• `/mode auto` یا `/mode review` : تغییر حالت بین «انتشار خودکار» و «تایید ادمین با دکمه شیشه‌ای»\n"
            "• `/set_prompt <متن دستور>` : تغییر دستورالعمل بازنویسی هوش مصنوعی\n"
            "• `/stats` : نمایش آمار کلی پست‌های بررسی‌شده و منتشرشده\n"
            "──────────────────────────────\n"
            "🌟 **Made ❤️ by [Mohammad](https://t.me/llllxyz)** | `@llllxyz`"
        )
        await message.edit_text(help_text, disable_web_page_preview=True)

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
            await message.edit_text(f"✅ کانال `{channel_name}` با موفقیت به لیست مانیتورینگ اضافه شد.")
        else:
            await message.edit_text(f"ℹ️ کانال `{channel_name}` از قبل در لیست وجود دارد.")

    @app.on_message(filters.me & filters.command(["remove_source"], prefixes=["/", ".", "!"]))
    async def handle_remove_source(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا نام کانال را وارد کنید. مثال: `/remove_source @TechNewsFA`")
            return
        channel_name = message.command[1].strip()
        removed = await curator_db.remove_source(channel_name)
        if removed:
            await message.edit_text(f"✅ کانال `{channel_name}` از لیست مانیتورینگ حذف شد.")
        else:
            await message.edit_text(f"❌ کانال `{channel_name}` در لیست یافت نشد.")

    @app.on_message(filters.me & filters.command(["list_sources"], prefixes=["/", ".", "!"]))
    async def handle_list_sources(client: Client, message: types.Message):
        sources = await curator_db.get_sources()
        if not sources:
            await message.edit_text("📭 لیست کانال‌های مبدا خالی است. با `/add_source` کانال جدید اضافه کنید.")
            return
        text = "📡 **کانال‌های مبدا تحت مانیتورینگ:**\n──────────────────────────────\n"
        for idx, src in enumerate(sources, 1):
            text += f"**{idx}.** `{src}`\n"
        await message.edit_text(text)

    @app.on_message(filters.me & filters.command(["add_keyword"], prefixes=["/", ".", "!"]))
    async def handle_add_keyword(client: Client, message: types.Message):
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا کلمه کلیدی را وارد کنید. مثال: `/add_keyword پایتون`")
            return
        word = " ".join(message.command[1:]).strip()
        added = await curator_db.add_keyword(word)
        if added:
            await message.edit_text(f"✅ کلمه کلیدی «`{word}`» به فیلترها اضافه شد.")
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
            await message.edit_text(f"✅ کلمه کلیدی «`{word}`» حذف شد.")
        else:
            await message.edit_text(f"❌ کلمه «`{word}`» در لیست یافت نشد.")

    @app.on_message(filters.me & filters.command(["list_keywords"], prefixes=["/", ".", "!"]))
    async def handle_list_keywords(client: Client, message: types.Message):
        keywords = await curator_db.get_keywords()
        if not keywords:
            await message.edit_text("🟢 لیست کلیدواژه‌ها خالی است (در این حالت **تمام پست‌های کانال‌های مبدا** پردازش می‌شوند).")
            return
        text = "🔑 **کلیدواژه‌های فعال فیلترینگ:**\n──────────────────────────────\n"
        for idx, kw in enumerate(keywords, 1):
            text += f"**{idx}.** `{kw}`\n"
        await message.edit_text(text)

    @app.on_message(filters.me & filters.command(["mode", "set_mode"], prefixes=["/", ".", "!"]))
    async def handle_set_mode(client: Client, message: types.Message):
        global ACTIVE_PUBLISHING_MODE
        if len(message.command) < 2 or message.command[1].lower() not in ("auto", "review"):
            await message.edit_text(
                f"ℹ️ **حالت فعلی انتشار:** `{ACTIVE_PUBLISHING_MODE.upper()}`\n\n"
                "برای تغییر حالت از یکی از دستورات زیر استفاده کنید:\n"
                "• `/mode auto` : انتشار کاملاً خودکار در کانال هدف\n"
                "• `/mode review` : ارسال پیش‌نویس به ادمین همراه با دکمه‌های تایید و رد"
            )
            return
        new_mode = message.command[1].lower()
        ACTIVE_PUBLISHING_MODE = new_mode
        mode_fa = "انتشار خودکار (Auto)" if new_mode == "auto" else "تایید ادمین با دکمه شیشه‌ای (Review)"
        await message.edit_text(f"⚙️ حالت انتشار با موفقیت به **{mode_fa}** تغییر یافت.")

    @app.on_message(filters.me & filters.command(["set_prompt"], prefixes=["/", ".", "!"]))
    async def handle_set_prompt(client: Client, message: types.Message):
        global ACTIVE_LLM_PROMPT
        if len(message.command) < 2:
            await message.edit_text("❌ لطفا متن دستورالعمل جدید هوش مصنوعی را وارد کنید.")
            return
        new_prompt = " ".join(message.command[1:]).strip()
        ACTIVE_LLM_PROMPT = new_prompt
        await message.edit_text(f"🧠 **دستورالعمل بازنویسی هوش مصنوعی به‌روزرسانی شد:**\n\n`{new_prompt}`")

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
            "──────────────────────────────\n"
            "🌟 **Made ❤️ by [Mohammad](https://t.me/llllxyz)** | `@llllxyz`"
        )
        await message.edit_text(text, disable_web_page_preview=True)
