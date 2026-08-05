import aiosqlite
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from config import config
from src.utils.logger import logger


class CuratorDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.database_path

    async def init_db(self) -> None:
        queries = [
            """
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_username TEXT UNIQUE NOT NULL,
                added_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                added_at TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_channel TEXT NOT NULL,
                source_msg_id INTEGER NOT NULL,
                original_text TEXT,
                rewritten_text TEXT,
                status TEXT DEFAULT 'PENDING_REVIEW',
                created_at TEXT NOT NULL,
                published_at TEXT,
                UNIQUE(source_channel, source_msg_id)
            );
            """
        ]
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for query in queries:
                    await db.execute(query)
                await db.commit()
            logger.debug("Database initialized at %s", self.db_path)
        except Exception as exc:
            logger.error("Database initialization failed: %s", exc, exc_info=True)
            raise

    async def add_source(self, channel_username: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        query = "INSERT OR IGNORE INTO sources (channel_username, added_at) VALUES (?, ?)"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (channel_username.strip(), now))
            await db.commit()
            return cursor.rowcount > 0

    async def remove_source(self, channel_username: str) -> bool:
        query = "DELETE FROM sources WHERE channel_username = ?"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (channel_username.strip(),))
            await db.commit()
            return cursor.rowcount > 0

    async def get_sources(self) -> List[str]:
        query = "SELECT channel_username FROM sources ORDER BY id ASC"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def add_keyword(self, word: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        query = "INSERT OR IGNORE INTO keywords (word, added_at) VALUES (?, ?)"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (word.strip().lower(), now))
            await db.commit()
            return cursor.rowcount > 0

    async def remove_keyword(self, word: str) -> bool:
        query = "DELETE FROM keywords WHERE word = ?"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (word.strip().lower(),))
            await db.commit()
            return cursor.rowcount > 0

    async def get_keywords(self) -> List[str]:
        query = "SELECT word FROM keywords ORDER BY id ASC"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query)
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def is_post_processed(self, source_channel: str, source_msg_id: int) -> bool:
        query = "SELECT 1 FROM post_history WHERE source_channel = ? AND source_msg_id = ? LIMIT 1"
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (source_channel, source_msg_id))
            row = await cursor.fetchone()
            return row is not None

    async def record_draft(
        self,
        source_channel: str,
        source_msg_id: int,
        original_text: str,
        rewritten_text: str,
        status: str = "PENDING_REVIEW"
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        query = """
        INSERT INTO post_history (
            source_channel, source_msg_id, original_text, rewritten_text, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                query,
                (source_channel, source_msg_id, original_text, rewritten_text, status, now)
            )
            await db.commit()
            return cursor.lastrowid or 0

    async def get_draft(self, draft_id: int) -> Optional[Dict[str, Any]]:
        query = """
        SELECT id, source_channel, source_msg_id, original_text, rewritten_text, status, created_at
        FROM post_history
        WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, (draft_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_draft_status(self, draft_id: int, status: str) -> None:
        now = datetime.now(timezone.utc).isoformat() if status in ("PUBLISHED", "AUTO_PUBLISHED") else None
        query = "UPDATE post_history SET status = ?, published_at = ? WHERE id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (status, now, draft_id))
            await db.commit()

    async def update_draft_text(self, draft_id: int, new_rewritten_text: str) -> None:
        query = "UPDATE post_history SET rewritten_text = ? WHERE id = ?"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, (new_rewritten_text, draft_id))
            await db.commit()

    async def get_summary_stats(self) -> Dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT
                    COUNT(*) as total_processed,
                    SUM(CASE WHEN status IN ('PUBLISHED', 'AUTO_PUBLISHED') THEN 1 ELSE 0 END) as total_published,
                    SUM(CASE WHEN status = 'PENDING_REVIEW' THEN 1 ELSE 0 END) as total_pending,
                    SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as total_rejected
                FROM post_history
            """)
            row = await cursor.fetchone()
            if row:
                return {
                    "total_processed": row["total_processed"] or 0,
                    "total_published": row["total_published"] or 0,
                    "total_pending": row["total_pending"] or 0,
                    "total_rejected": row["total_rejected"] or 0,
                }
            return {"total_processed": 0, "total_published": 0, "total_pending": 0, "total_rejected": 0}


curator_db = CuratorDB()
