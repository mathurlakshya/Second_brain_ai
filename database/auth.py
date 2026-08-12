import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "second_brain.db"


def create_user(username, email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:

        cursor.execute("""
            INSERT INTO users(
                username,
                email,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            datetime.now().isoformat()
        ))

        conn.commit()

        user_id = cursor.lastrowid

        return True, user_id

    except sqlite3.IntegrityError:

        return False, None

    finally:

        conn.close()


def login_user(email, password):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            password_hash

        FROM users

        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    user_id = user[0]
    username = user[1]
    password_hash = user[2]

    if bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    ):

        return {
            "id": user_id,
            "username": username
        }

    return None