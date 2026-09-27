import json
import os
import sqlite3

from database.users import create_users_table
from config import DB_PATH

DB_NAME = DB_PATH
SCHEMA_VERSION = 2


def _connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def _ensure_thought_thread_columns(cursor):
    cursor.execute("PRAGMA table_info(memories)")
    columns = {column[1] for column in cursor.fetchall()}
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN user_id INTEGER")
    if "thread_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN thread_id INTEGER")


def _run_migrations(cursor):
    cursor.execute("PRAGMA user_version")
    version = cursor.fetchone()[0]
    if version < 1:
        cursor.execute("PRAGMA user_version = 1")
        version = 1
    if version < 2:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_timestamp ON memories(user_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_thread ON memories(user_id, thread_id)")
        cursor.execute("PRAGMA user_version = 2")


def create_database():
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                app_name TEXT,
                window_title TEXT,
                timestamp TEXT,
                screenshot TEXT,
                summary TEXT,
                ocr_text TEXT,
                embedding TEXT,
                contains_error INTEGER,
                error_text TEXT,
                thread_id INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                save_screenshots INTEGER DEFAULT 0
            )
        """)
        _ensure_thought_thread_columns(cursor)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thought_threads(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                memory_count INTEGER NOT NULL DEFAULT 0,
                centroid_embedding TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'active'
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_thread_id ON memories(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_user_updated ON thought_threads(user_id, updated_at DESC)")
        _run_migrations(cursor)
        conn.commit()
    finally:
        conn.close()
    create_users_table()


def save_memory(user_id, app, title, now, screenshot_path, summary, ocr_text,
                embedding="", contains_error=0, error_text=""):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories(
                user_id, app_name, window_title, timestamp, screenshot,
                summary, ocr_text, embedding, contains_error, error_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, app, title, now, screenshot_path, summary, ocr_text,
              json.dumps(embedding), contains_error, error_text))
        memory_id = cursor.lastrowid
        conn.commit()
        return memory_id
    finally:
        conn.close()


def search_memories(query, user_id=None):
    conn = _connect()
    try:
        cursor = conn.cursor()
        params = [f"%{query}%"] * 4
        user_clause = ""
        if user_id is not None:
            user_clause = "AND user_id = ?"
            params.append(user_id)
        cursor.execute(f"""
            SELECT app_name, window_title, timestamp, summary, ocr_text, screenshot
            FROM memories
            WHERE (app_name LIKE ? OR window_title LIKE ? OR summary LIKE ? OR ocr_text LIKE ?)
            {user_clause}
            ORDER BY id DESC LIMIT 10
        """, params)
        return cursor.fetchall()
    finally:
        conn.close()


def get_user_setting(user_id):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT save_screenshots FROM user_settings WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return bool(row[0]) if row else False
    finally:
        conn.close()


def set_user_setting(user_id, save_screenshots):
    conn = _connect()
    try:
        conn.execute("""
            INSERT INTO user_settings(user_id, save_screenshots)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET save_screenshots = excluded.save_screenshots
        """, (user_id, 1 if save_screenshots else 0))
        conn.commit()
    finally:
        conn.close()


def get_recent_memories(user_id=None, limit=50):
    conn = _connect()
    try:
        if user_id is None:
            return conn.execute("""
                SELECT timestamp, app_name, window_title, summary, screenshot
                FROM memories ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return conn.execute("""
            SELECT timestamp, app_name, window_title, summary, screenshot
            FROM memories WHERE user_id = ? ORDER BY id DESC LIMIT ?
        """, (user_id, limit)).fetchall()
    finally:
        conn.close()


def create_pending_memory(user_id, app, title, now, screenshot=""):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories(
                user_id, app_name, window_title, timestamp, screenshot,
                summary, ocr_text, embedding, contains_error, error_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, app, title, now, screenshot, "Processing...", "", "", 0, ""))
        memory_id = cursor.lastrowid
        conn.commit()
        return memory_id
    finally:
        conn.close()


def update_memory(memory_id, summary, ocr_text, embedding, contains_error=0, error_text=""):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE memories
            SET summary = ?, ocr_text = ?, embedding = ?,
                contains_error = ?, error_text = ?
            WHERE id = ?
        """, (summary, ocr_text, json.dumps(embedding), contains_error, error_text, memory_id))
        memory = cursor.execute(
            "SELECT user_id, app_name, window_title, timestamp FROM memories WHERE id = ?",
            (memory_id,),
        ).fetchone()
        conn.commit()
    finally:
        conn.close()

    if memory and embedding:
        try:
            from memory.thought_threads import assign_memory_to_thread
            user_id, app, title, timestamp = memory
            assign_memory_to_thread(memory_id, user_id, app, title, timestamp, summary, embedding)
        except Exception as exc:
            print(f"⚠️ Thought thread assignment skipped: {type(exc).__name__}")


def export_user_memories(user_id, output_path):
    conn = _connect()
    try:
        rows = conn.execute("""
            SELECT timestamp, app_name, window_title, summary, ocr_text,
                   contains_error, error_text
            FROM memories WHERE user_id = ? ORDER BY id ASC
        """, (user_id,)).fetchall()
    finally:
        conn.close()

    payload = {
        "format": "second-brain-memory-export",
        "version": 1,
        "memories": [
            {
                "timestamp": row[0],
                "application": row[1],
                "window_title": row[2],
                "summary": row[3],
                "screen_text": row[4],
                "contains_error": bool(row[5]),
                "error_text": row[6],
            }
            for row in rows
        ],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def delete_user_memories(user_id):
    conn = _connect()
    try:
        paths = [
            row[0] for row in conn.execute(
                "SELECT screenshot FROM memories WHERE user_id = ? AND screenshot != ?",
                (user_id, ""),
            ).fetchall()
        ]
        conn.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM thought_threads WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()

    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def get_memory_counts(user_id):
    conn = _connect()
    try:
        memories = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        threads = conn.execute(
            "SELECT COUNT(*) FROM thought_threads WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        return memories, threads
    finally:
        conn.close()
