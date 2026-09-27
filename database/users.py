import sqlite3

DB_NAME = "second_brain.db"


def hash_password(password):
    # Kept for backwards compatibility with older callers.
    # New authentication uses bcrypt in database.auth.
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()
