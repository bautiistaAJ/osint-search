import aiosqlite
from datetime import datetime
from typing import Optional

DB_PATH = "osint_search.db"

async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                query_value TEXT NOT NULL,
                results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                query_value TEXT NOT NULL,
                label TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_history(query_type: str, query_value: str, results: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO search_history (query_type, query_value, results) VALUES (?, ?, ?)",
            (query_type, query_value, results)
        )
        await db.commit()
        return db.total_changes

async def get_history(limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM search_history ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def add_favorite(query_type: str, query_value: str, label: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO favorites (query_type, query_value, label) VALUES (?, ?, ?)",
            (query_type, query_value, label)
        )
        await db.commit()
        return db.lastrowid

async def get_favorites():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM favorites ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

async def delete_favorite(fav_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM favorites WHERE id = ?", (fav_id,))
        await db.commit()
