import sqlite3
import hashlib

DB_NAME = "second_brain.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(username, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
        """, (
            username,
            email,
            hash_password(password)
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, email
        FROM users
        WHERE email = ? AND password = ?
    """, (
        email,
        hash_password(password)
    ))

    user = cursor.fetchone()

    conn.close()

    return user