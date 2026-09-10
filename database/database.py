import json
import sqlite3

from database.users import create_users_table

DB_NAME = "second_brain.db"


def _ensure_thought_thread_columns(cursor):
    cursor.execute("PRAGMA table_info(memories)")
    columns = {column[1] for column in cursor.fetchall()}
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN user_id INTEGER")
    if "thread_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN thread_id INTEGER")


def create_database():
    conn = sqlite3.connect(DB_NAME)
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

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_thread_id ON memories(thread_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_threads_user_updated ON thought_threads(user_id, updated_at DESC)"
    )

    conn.commit()
    conn.close()
    create_users_table()


def save_memory(
    user_id,
    app,
    title,
    now,
    screenshot_path,
    summary,
    ocr_text,
    embedding="",
    contains_error=0,
    error_text=""
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    embedding_json = json.dumps(embedding)

    cursor.execute("""
        INSERT INTO memories(
            user_id, app_name, window_title, timestamp, screenshot,
            summary, ocr_text, embedding, contains_error, error_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, app, title, now, screenshot_path,
        summary, ocr_text, embedding_json, contains_error, error_text
    ))

    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id


def search_memories(query, user_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    user_clause = ""
    params = [f"%{query}%"] * 4
    if user_id is not None:
        user_clause = "AND user_id = ?"
        params.append(user_id)

    cursor.execute(f"""
        SELECT app_name, window_title, timestamp, summary, ocr_text, screenshot
        FROM memories
        WHERE (
            app_name LIKE ? OR window_title LIKE ? OR summary LIKE ? OR ocr_text LIKE ?
        )
        {user_clause}
        ORDER BY id DESC
        LIMIT 10
    """, params)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_setting(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT save_screenshots FROM user_settings WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False


def set_user_setting(user_id, save_screenshots):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_settings(user_id, save_screenshots)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            save_screenshots = excluded.save_screenshots
    """, (user_id, 1 if save_screenshots else 0))
    conn.commit()
    conn.close()


def get_recent_memories(user_id=None, limit=50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if user_id is None:
        cursor.execute("""
            SELECT timestamp, app_name, window_title, summary, screenshot
            FROM memories
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
    else:
        cursor.execute("""
            SELECT timestamp, app_name, window_title, summary, screenshot
            FROM memories
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def create_pending_memory(user_id, app, title, now, screenshot=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memories(
            user_id, app_name, window_title, timestamp, screenshot,
            summary, ocr_text, embedding, contains_error, error_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, app, title, now, screenshot,
        "Processing...", "", "", 0, ""
    ))

    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id


def update_memory(
    memory_id,
    summary,
    ocr_text,
    embedding,
    contains_error=0,
    error_text=""
):
    embedding_json = json.dumps(embedding)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE memories
        SET summary = ?, ocr_text = ?, embedding = ?,
            contains_error = ?, error_text = ?
        WHERE id = ?
    """, (
        summary, ocr_text, embedding_json,
        contains_error, error_text, memory_id
    ))

    cursor.execute(
        "SELECT user_id, app_name, window_title, timestamp FROM memories WHERE id = ?",
        (memory_id,)
    )
    memory = cursor.fetchone()
    conn.commit()
    conn.close()

    # Thread assignment is local and embedding-based; it does not add a Gemini call.
    if memory and embedding:
        try:
            from memory.thought_threads import assign_memory_to_thread
            user_id, app, title, timestamp = memory
            assign_memory_to_thread(
                memory_id=memory_id,
                user_id=user_id,
                app=app,
                window_title=title,
                timestamp=timestamp,
                summary=summary,
                embedding=embedding,
            )
        except Exception as e:
            print(f"⚠️ Thought thread assignment skipped: {e}")
