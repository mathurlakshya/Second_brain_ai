import sqlite3


class SearchEngine:

    def search(self, query):

        conn = sqlite3.connect("second_brain.db")

        cursor = conn.cursor()

        cursor.execute("""
        SELECT timestamp,
               app_name,
               window_title
        FROM memories
        ORDER BY id DESC
        LIMIT 300
        """)

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