# Telegram Channel Curator

A modular Telegram post aggregator and AI rewriter built with Pyrogram (MTProto). It observes source channels, filters incoming posts by keywords, rewrites them using LLMs (or a deterministic regex cleaner), and publishes to your channel with human-in-the-loop review.

Made ❤️ by [Mohammad](https://t.me/llllxyz) (`@llllxyz`)

---

## The Problem
Running an active Telegram channel takes hours of work every day. You have to monitor external news feeds, pick good posts, remove competitor links and usernames, rewrite the copy in your own style, and schedule the update.

Standard Telegram bots (Bot API) cannot read posts from channels where they are not administrators. You cannot simply point a `@bot` at public news feeds or competitor channels to aggregate content.

## The Solution
This project uses an **MTProto client** (`Pyrogram`), connecting as a regular Telegram user account. You do not need admin access in the source channels; any public channel can be monitored.

How the pipeline works:
1. Observes configured source channels in real time.
2. Normalizes Persian/Arabic text and matches incoming messages against your target keywords.
3. If a post matches, it is sent to an LLM endpoint (OpenAI / DeepSeek / OpenRouter) to be rewritten, summarized, and tagged.
4. If the LLM API is unreachable or no key is configured, a rule-based fallback cleaner strips competitor usernames/urls and appends your channel signature.
5. Sends a preview card to your Telegram account with interactive inline buttons:
   - `[✅ Publish to Channel]`
   - `[❌ Reject Draft]`
   - `[🔄 Regenerate with AI]`

---

## Architecture

```
[Public Source Channels] --(New Post)--> [Pyrogram MTProto Client]
                                                  |
                                                  v
                                      [Keyword Filter & Normalizer]
                                                  |
                                                  v
                                      [Rewrite Engine: LLM / Regex]
                                                  |
                                                  v
                                        [SQLite Draft Storage]
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                  (mode = review)                                   (mode = auto)
                         |                                                 |
                         v                                                 v
             [Admin Review via Inline Buttons]                    [Target Telegram Channel]
```

---

## Setup & Installation

### 1. Requirements
- Python 3.12+ (or Docker)
- Telegram API credentials (`API_ID` and `API_HASH`) from [my.telegram.org](https://my.telegram.org/apps)
- A Telegram account to authenticate the client

### 2. Configuration
Clone the repository and copy the example environment file:

```bash
git clone https://github.com/mamadiezad/telegram-channel-curator.git
cd telegram-channel-curator
cp .env.example .env
```

Edit `.env` and set your preferences:
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

### 3. Local Execution
```bash
# Install dependencies
make install

# Run automated tests
make test

# Start the bot
make run
```
*On first start, Pyrogram will prompt you for the verification code sent to your Telegram account to generate the `.session` file.*

### 4. Running with Docker Compose
```bash
docker-compose up -d --build
```

---

## Interactive Admin Commands

Send these commands from your authenticated admin account in any chat with the bot:

| Command | Description | Example |
| :--- | :--- | :--- |
| `/add_source <@username>` | Monitor a new source channel | `/add_source @TechNewsFA` |
| `/remove_source <@username>` | Stop monitoring a channel | `/remove_source @TechNewsFA` |
| `/list_sources` | List all monitored source channels | `/list_sources` |
| `/add_keyword <word>` | Add a required keyword rule | `/add_keyword python` |
| `/remove_keyword <word>` | Remove a keyword rule | `/remove_keyword python` |
| `/list_keywords` | List active keywords (empty list accepts all posts) | `/list_keywords` |
| `/mode <auto/review>` | Switch between instant posting and inline review | `/mode review` |
| `/set_prompt <text>` | Customize the LLM rewriting instruction | `/set_prompt Rewrite casually in Persian` |
| `/stats` | Show curation, publication, and rejection statistics | `/stats` |

---

## Testing

Run the automated test suite covering Persian normalization, keyword matching, and rule-based fallback cleaning:

```bash
pytest -v
```

---

## License & Support

This project is open-source and free to use for personal or commercial automation.

- **Made ❤️ by [Mohammad](https://t.me/llllxyz)**
- **Telegram:** `@llllxyz`
