import json
import os
import hashlib
import secrets
import sqlite3
from datetime import datetime

DB_NAME = "second_brain.db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(BASE_DIR, "session.json")


def save_session(user):
    """
    Save the currently logged-in user locally.

    This stores only basic user information:
    - id
    - username

    The password is NEVER stored.
    """

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(user, f)


def load_session():
    """
    Load the locally saved session.
    """

    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return None


def clear_session():
    """
    Remove the local session.
    """

    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except OSError:
            pass


# ---------------------------------------------------------
# TRUSTED DEVICE
# ---------------------------------------------------------

def _get_token_file():
    """
    Device-specific token file.

    The token is stored separately from the normal session.
    """

    return os.path.join(BASE_DIR, "device_token.json")


def _hash_token(token):
    """
    Hash the device token before it is stored in the database.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_trusted_device(user_id):
    """
    Create a new trusted-device token for the user.

    Returns:
        token
    """

    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trusted_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            last_used TEXT NOT NULL
        )
    """)

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO trusted_devices (
            user_id,
            token_hash,
            created_at,
            last_used
        )
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        token_hash,
        now,
        now
    ))

    conn.commit()
    conn.close()

    with open(_get_token_file(), "w", encoding="utf-8") as f:
        json.dump({
            "user_id": user_id,
            "token": token
        }, f)

    return token


def load_trusted_device():
    """
    Load the locally stored trusted-device information.

    Returns:
        {
            "user_id": ...,
            "token": ...
        }

    or None.
    """

    token_file = _get_token_file()

    if not os.path.exists(token_file):
        return None

    try:
        with open(token_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data.get("user_id") or not data.get("token"):
            return None

        return data

    except (json.JSONDecodeError, OSError):
        return None


def validate_trusted_device():
    """
    Check whether this device still has a valid trusted session.

    Returns the user information if valid.
    Otherwise returns None.
    """

    device = load_trusted_device()

    if not device:
        return None

    user_id = device["user_id"]
    token = device["token"]

    token_hash = _hash_token(token)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trusted_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            last_used TEXT NOT NULL
        )
    """)

    cursor.execute("""
        SELECT users.id, users.username
        FROM trusted_devices
        JOIN users
            ON trusted_devices.user_id = users.id
        WHERE trusted_devices.user_id = ?
          AND trusted_devices.token_hash = ?
    """, (
        user_id,
        token_hash
    ))

    user = cursor.fetchone()

    if user is None:
        conn.close()

        # Invalid token — remove local token.
        clear_trusted_device()

        return None

    now = datetime.now().isoformat()

    cursor.execute("""
        UPDATE trusted_devices
        SET last_used = ?
        WHERE user_id = ?
          AND token_hash = ?
    """, (
        now,
        user_id,
        token_hash
    ))

    conn.commit()
    conn.close()

    return {
        "id": user[0],
        "username": user[1]
    }


def clear_trusted_device():
    """
    Remove the trusted device from both:
    - local machine
    - database
    """

    device = load_trusted_device()

    if not device:
        return

    user_id = device.get("user_id")
    token = device.get("token")

    if user_id and token:

        token_hash = _hash_token(token)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM trusted_devices
                WHERE user_id = ?
                  AND token_hash = ?
            """, (
                user_id,
                token_hash
            ))

            conn.commit()
            conn.close()

        except sqlite3.Error:
            pass

    token_file = _get_token_file()

    if os.path.exists(token_file):
        try:
            os.remove(token_file)
        except OSError:
            pass
