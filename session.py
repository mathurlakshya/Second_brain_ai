import base64
import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime
from config import DB_PATH, APP_DATA_DIR

DB_NAME = DB_PATH
SESSION_FILE = os.path.join(APP_DATA_DIR, "session.json")
TOKEN_FILE = os.path.join(APP_DATA_DIR, "device_token.json")


def save_session(user):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"id": user["id"], "username": user["username"]}, f)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except OSError:
        pass


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _protect_secret(value):
    """Use Windows DPAPI for the trusted-device credential."""
    try:
        import win32crypt
        protected = win32crypt.CryptProtectData(
            value.encode("utf-8"),
            "Second Brain AI device token",
            None, None, None, 0,
        )[1]
        return {"format": "dpapi", "data": base64.b64encode(protected).decode("ascii")}
    except Exception:
        return {"format": "plain", "data": value}


def _unprotect_secret(payload):
    if not isinstance(payload, dict):
        return None
    try:
        if payload.get("format") == "dpapi":
            import win32crypt
            raw = base64.b64decode(payload["data"])
            return win32crypt.CryptUnprotectData(raw, None, None, None, 0)[1].decode("utf-8")
        if payload.get("format") == "plain":
            return payload.get("data")
    except Exception:
        return None
    return None


def create_trusted_device(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = _hash_token(token)

    conn = sqlite3.connect(DB_NAME)
    try:
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
            INSERT INTO trusted_devices (user_id, token_hash, created_at, last_used)
            VALUES (?, ?, ?, ?)
        """, (user_id, token_hash, now, now))
        conn.commit()
    finally:
        conn.close()

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_id": user_id, "credential": _protect_secret(token)}, f)

    return token


def load_trusted_device():
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        token = _unprotect_secret(data.get("credential"))
        if token and data.get("user_id"):
            return {"user_id": data["user_id"], "token": token}

        # Migrate the legacy plaintext token file.
        legacy_token = data.get("token")
        if legacy_token and data.get("user_id"):
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "user_id": data["user_id"],
                    "credential": _protect_secret(legacy_token),
                }, f)
            return {"user_id": data["user_id"], "token": legacy_token}
    except (json.JSONDecodeError, OSError, TypeError):
        pass
    return None


def validate_trusted_device():
    device = load_trusted_device()
    if not device:
        return None

    user_id = device["user_id"]
    token_hash = _hash_token(device["token"])

    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT users.id, users.username
            FROM trusted_devices
            JOIN users ON trusted_devices.user_id = users.id
            WHERE trusted_devices.user_id = ? AND trusted_devices.token_hash = ?
        """, (user_id, token_hash))
        user = cursor.fetchone()
        if user is None:
            return None

        cursor.execute("""
            UPDATE trusted_devices SET last_used = ?
            WHERE user_id = ? AND token_hash = ?
        """, (datetime.now().isoformat(), user_id, token_hash))
        conn.commit()
        return {"id": user[0], "username": user[1]}
    finally:
        conn.close()


def clear_trusted_device():
    device = load_trusted_device()
    if device:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM trusted_devices WHERE user_id = ? AND token_hash = ?",
                (device["user_id"], _hash_token(device["token"])),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass

    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
    except OSError:
        pass
