import json
import sqlite3
from database.users import create_users_table

DB_NAME = "second_brain.db"

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
            user_id,
            app_name,
            window_title,
            timestamp,
            screenshot,
            summary,
            ocr_text,
            embedding,
            contains_error,
            error_text
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
            user_id,
            app,
            title,
            now,
            screenshot_path,
            summary,
            ocr_text,
            embedding_json,
            contains_error,
            error_text
        ))

    conn.commit()
    conn.close()

def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---------------- USERS ---------------- #

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password_hash TEXT NOT NULL,

        created_at TEXT

    )
    """)

    # ---------------- MEMORIES ---------------- #

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
    error_text TEXT
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,

            created_at TEXT

        )
        """)
    # Add user_id to an OLD memories table if it doesn't have it
    cursor.execute("PRAGMA table_info(memories)")
    columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in columns:

        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN user_id INTEGER
        """)
    try:
        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN user_id INTEGER
        """)
    except sqlite3.OperationalError:
      pass

    conn.commit()
    conn.close()

    create_users_table()

    
def search_memories(query):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            app_name,
            window_title,
            timestamp,
            summary,
            ocr_text,
            screenshot

        FROM memories

        WHERE

            app_name LIKE ?

            OR window_title LIKE ?

            OR summary LIKE ?

            OR ocr_text LIKE ?

        ORDER BY id DESC

        LIMIT 10

    """, (

        f"%{query}%",
        f"%{query}%",
        f"%{query}%",
        f"%{query}%"

    ))

    rows = cursor.fetchall()

    conn.close()

    return rows    