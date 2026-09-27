import sqlite3
from config import DB_PATH


class SearchEngine:

    def search(self, query, user_id):

        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute("""
        SELECT timestamp, app_name, window_title
        FROM memories
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 300
        """, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        query = query.lower()

        results = []

        for timestamp, app, title in rows:

            text = f"{timestamp} {app} {title}".lower()

            if query in text:

                results.append(
                    {
                        "time": timestamp,
                        "app": app,
                        "title": title
                    }
                )

        return results