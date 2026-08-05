# 📡 Telegram Channel Auto-Curator & AI Rewriter — Smart Aggregator & Post Curator Bot

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Pyrogram MTProto](https://img.shields.io/badge/Pyrogram-MTProto-0088cc.svg)](https://docs.pyrogram.org/)
[![LLM Ready](https://img.shields.io/badge/AI-OpenAI%20%7C%20DeepSeek-412991.svg)](https://openai.com/)
[![SQLite Audit](https://img.shields.io/badge/Database-SQLite%20Async-003B57.svg)](https://www.sqlite.org/index.html)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Telegram Support](https://img.shields.io/badge/Telegram-%40llllxyz-2CA5E0?style=flat&logo=telegram)](https://t.me/llllxyz)

> **A production-ready Telegram MTProto bot that monitors multiple source channels, filters incoming posts by target keywords, rewrites them using LLMs (OpenAI, DeepSeek, OpenRouter) or a rule-based template cleaner, and publishes them to your Telegram channel.**  
> *(برای مشاهده مستندات کامل فارسی به [README_FA.md](./README_FA.md) مراجعه کنید).*

---

### **Made ❤️ by [Mohammad](https://t.me/llllxyz)**  
**Telegram ID:** [@llllxyz](https://t.me/llllxyz)

---

## 📑 Table of Contents
- [Why Use an MTProto Channel Curator?](#why-use-an-mtproto-channel-curator)
- [Key Features & Architecture](#key-features--architecture)
- [System Workflow & Diagram](#system-workflow--diagram)
- [Quickstart Guide (Local & Docker)](#quickstart-guide-local--docker)
- [Interactive Admin Commands](#interactive-admin-commands)
- [Draft Review & Publishing Modes](#draft-review--publishing-modes)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
- [Search Keywords & Indexing](#search-keywords--indexing)
- [Contact & Support](#contact--support)

---

## 📌 Why Use an MTProto Channel Curator?

Managing an active Telegram channel often requires monitoring dozens of external news feeds, industry blogs, and competitor channels, extracting relevant updates, rewriting them in your own voice, and publishing them on schedule. Doing this manually takes hours every day.

Standard Telegram bot accounts (`@BotFather` tokens) cannot read posts from channels unless they are added as administrators. By using an **MTProto Userbot Client (Pyrogram)**, this application can observe public source channels without administrative permissions, filter posts by keywords in real time, rewrite them automatically, and publish to your target channel.

---

## 🌟 Key Features & Architecture

- **📡 Multi-Source Monitoring:**  
  Add or remove source channels on the fly using `/add_source` and `/remove_source`.
- **🔑 Smart Keyword Filtering:**  
  Configure required keywords (`/add_keyword`). Only posts containing at least one matching word are processed. Includes automatic normalization of Persian and Arabic characters (`ي/ی`, `ك/ک`, zero-width spaces).
- **🧠 Hybrid AI & Rule-Based Rewriter:**  
  - **LLM Mode:** Connects to OpenAI, DeepSeek, OpenRouter, or Ollama to summarize, paraphrase, and format posts.
  - **Rule-Based Fallback:** If the AI API key is missing or an API call fails, the bot automatically falls back to a deterministic cleaner that strips competitor URLs and mentions, generates hashtags, and formats paragraphs.
- **🛡 Human-in-the-Loop Review Mode (`/mode review`):**  
  Sends a draft preview to the administrator with interactive inline buttons:
  `[✅ Approve & Publish] [❌ Reject] [🔄 Regenerate with AI]`.
- **⚡ Fully Automated Mode (`/mode auto`):**  
  Optionally publish rewritten posts immediately without manual approval.
- **📊 SQLite Persistence & Deduplication:**  
  Tracks processed message IDs in SQLite (`aiosqlite`) to prevent reposting duplicate content across restarts.
- **🆓 100% Free & Open Source:**  
  Free for everyone to use, modify, and self-host without license restrictions.

---

## 🏛 System Workflow & Diagram

```
+-----------------------------------------------------------------------------------+
|                        SOURCE TELEGRAM CHANNELS (PUBLIC)                          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v  New Message Event
+-----------------------------------------------------------------------------------+
|                       PYROGRAM ASYNC MTPROTO USERBOT CLIENT                       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           KEYWORD FILTERING ENGINE                                |
|   - Normalizes Persian/Arabic characters ('ي'->'ی', 'ك'->'ک')                      |
|   - Checks against SQLite keyword list (accepts all if list is empty)             |
+-----------------------------------------------------------------------------------+
                                         |
                                         v  Match found
+-----------------------------------------------------------------------------------+
|                           REWRITE MANAGER (HYBRID)                                |
|   1. Try LLM API (OpenAI / DeepSeek / OpenRouter) with custom prompt              |
|   2. Fallback to Rule-Based Cleaner (strip URLs/mentions, append signature)       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v  Save Draft in SQLite
+-----------------------------------------------------------------------------------+
|                         PUBLISHER & WORKFLOW ROUTER                               |
+-----------------------------------------------------------------------------------+
             /                                                   \
            /  mode = "review"                                    \  mode = "auto"
           v                                                       v
+------------------------------------+           +----------------------------------+
|      ADMIN USER TELEGRAM CHAT      |           |      TARGET TELEGRAM CHANNEL     |
|  Inline buttons:                   |           |  Direct instant publication      |
|  [✅ Publish] [❌ Reject] [🔄 Regen] |           |  with channel footer signature    |
+------------------------------------+           +----------------------------------+
```

---

## 🚀 Quickstart Guide (Local & Docker)

### 1️⃣ Obtain Telegram Credentials
1. Log in to [https://my.telegram.org/apps](https://my.telegram.org/apps).
2. Create an application to get your `API_ID` and `API_HASH`.

### 2️⃣ Configure Environment Variables
Clone the repository and copy the example configuration file:

```bash
git clone https://github.com/mamadiezad/telegram-channel-curator.git
cd telegram-channel-curator
cp .env.example .env
```

Edit `.env` and set your credentials and preferences:
```ini
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_telegram_api_hash
TARGET_CHANNEL=@MyTechNewsChannel
ADMIN_USER_ID=123456789
PUBLISHING_MODE=review
OPENAI_API_KEY=sk-your_api_key_here
LLM_MODEL_NAME=gpt-4o-mini
CHANNEL_SIGNATURE=@MyTechNewsChannel
```

### 3️⃣ Running Locally with Makefile

```bash
# Create local virtual environment and install dependencies
make install

# Run automated unit tests
make test

# Start the bot
make run
```
*On first execution, Pyrogram will ask for the verification code sent to your Telegram account to generate your `.session` file.*

### 4️⃣ Running with Docker Compose

```bash
# Build and run the container in detached mode
docker-compose up -d --build

# Inspect real-time colored logs
docker-compose logs -f
```

---

## 💬 Interactive Admin Commands

Send these commands from your Telegram account in any chat with the bot (or Saved Messages):

| Command | Arguments | Example | Description |
| :--- | :--- | :--- | :--- |
| `/add_source` | `<@channel>` | `/add_source @TechNewsFA` | Add a source channel to monitor. |
| `/remove_source` | `<@channel>` | `/remove_source @TechNewsFA` | Remove a monitored source channel. |
| `/list_sources` | *None* | `/list_sources` | List all monitored source channels. |
| `/add_keyword` | `<word>` | `/add_keyword پایتون` | Add a keyword filter rule. |
| `/remove_keyword` | `<word>` | `/remove_keyword پایتون` | Remove a keyword filter rule. |
| `/list_keywords` | *None* | `/list_keywords` | View active keywords (if empty, all posts are processed). |
| `/mode` | `<auto \| review>` | `/mode review` | Switch between instant posting (`auto`) and admin approval (`review`). |
| `/set_prompt` | `<text>` | `/set_prompt Rewrite casually in Persian` | Customize the LLM system prompt instructions. |
| `/stats` | *None* | `/stats` | Display processed, published, pending, and rejected post statistics. |
| `/start` or `/help` | *None* | `/help` | Display interactive bilingual help menu. |

---

## ❓ Frequently Asked Questions (FAQ)

### Q1: Can I monitor public Telegram channels where I am not an administrator?
**A:** Yes. Because this bot uses an MTProto user session (via Pyrogram), it can observe any public Telegram channel that your account can read.

### Q2: What happens if my OpenAI or DeepSeek API key is invalid or the server is down?
**A:** The bot will catch the API exception, log a warning, and automatically switch to the deterministic Rule-Based Rewriter. This fallback strips competitor usernames and links, cleans paragraph formatting, generates hashtags, and appends your channel signature so your publishing workflow never stops.

### Q3: How does the Human-in-the-Loop review mode work?
**A:** When `PUBLISHING_MODE=review` is set, every matching post is rewritten and sent as a draft message to your `ADMIN_USER_ID` with inline keyboard buttons. You can click **[✅ Publish]** to post it immediately to `TARGET_CHANNEL`, **[❌ Reject]** to discard it, or **[🔄 Regenerate]** to run the AI rewriter again.

### Q4: How do I prevent the bot from posting duplicate news?
**A:** The bot records every processed `(source_channel, source_msg_id)` pair in its SQLite database (`aiosqlite`). Even if the bot is restarted, it will never process or publish the same source post twice.

---

## 🔎 Search Keywords & Indexing

This repository is optimized for developers and community managers searching for:
- `telegram-channel-curator`, `telegram-auto-curator`, `telegram-aggregator-bot`, `telegram-post-rewriter`
- `ai-telegram-bot`, `openai-telegram-bot`, `deepseek-telegram-bot`, `pyrogram-channel-bot`
- `telegram-mtproto-userbot`, `telegram-channel-admin-bot`, `telegram-rss-to-channel`
- `persian-telegram-bot`, `telegram-content-automation`, `telegram-auto-poster`

---

## 📬 Contact & Support

- **Made ❤️ by [Mohammad](https://t.me/llllxyz)**
- **Telegram ID:** [@llllxyz](https://t.me/llllxyz)
- **100% Free & Open Source:** Free for everyone to use and contribute!
