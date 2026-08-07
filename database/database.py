import sqlite3

DB_NAME = "second_brain.db"


def save_memory(
    app_name,
    window_title,
    timestamp,
    screenshot="",
    summary="",
    ocr_text="",
    contains_error=0,
    error_text=""
):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memories(
            app_name,
            window_title,
            timestamp,
            screenshot,
            summary,
            ocr_text,
            contains_error,
            error_text
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        app_name,
        window_title,
        timestamp,
        screenshot,
        summary,
        ocr_text,
        contains_error,
        error_text

    ))

    conn.commit()
    conn.close()


def create_database():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS memories(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        app_name TEXT,

        window_title TEXT,

        timestamp TEXT,

        screenshot TEXT,

        summary TEXT,

        ocr_text TEXT,

        contains_error INTEGER,

        error_text TEXT

    )

    """)

    conn.commit()
    conn.close()


def get_all_memories():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            app_name,
            window_title,
            timestamp

        FROM memories

        ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows