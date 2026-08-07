import sqlite3


def get_recent_memories(limit=200):

    conn = sqlite3.connect("second_brain.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            timestamp,
            app_name,
            window_title,
            screenshot,
            summary
        FROM memories
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    return rows