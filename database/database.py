import json
import sqlite3

DB_NAME = "second_brain.db"

def save_memory(
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

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

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

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS memories(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

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