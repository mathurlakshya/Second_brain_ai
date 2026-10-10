import json
import sqlite3

import pytest

import database.database as db
import database.auth as auth
import database.users as users


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_NAME", str(db_path))
    monkeypatch.setattr(auth, "DB_NAME", str(db_path))
    monkeypatch.setattr(users, "DB_NAME", str(db_path))
    db.create_database()
    return db_path


def test_database_initializes_with_wal_and_schema(isolated_db):
    conn = sqlite3.connect(isolated_db)
    try:
        assert conn.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 2
        columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        assert "password_hash" in columns
        assert "password" not in columns
    finally:
        conn.close()


def test_user_authentication_round_trip(isolated_db):
    created, user_id = auth.create_user("launch-user", "launch@example.com", "correct-password")
    assert created is True
    assert user_id is not None

    assert auth.login_user("launch@example.com", "wrong-password") is None
    user = auth.login_user("launch@example.com", "correct-password")
    assert user == {"id": user_id, "username": "launch-user"}


def test_memories_are_isolated_by_user(isolated_db):
    db.save_memory(1, "chrome.exe", "User One", "2026-01-01 10:00:00", "", "one", "one")
    db.save_memory(2, "code.exe", "User Two", "2026-01-01 10:01:00", "", "two", "two")

    first = db.get_recent_memories(user_id=1)
    second = db.get_recent_memories(user_id=2)

    assert len(first) == 1
    assert first[0][2] == "User One"
    assert len(second) == 1
    assert second[0][2] == "User Two"


def test_export_and_delete_only_affect_current_user(isolated_db, tmp_path):
    db.save_memory(1, "chrome.exe", "One", "2026-01-01 10:00:00", "", "summary", "screen")
    db.save_memory(2, "code.exe", "Two", "2026-01-01 10:01:00", "", "private", "screen")

    export_path = tmp_path / "export.json"
    db.export_user_memories(1, export_path)

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert len(payload["memories"]) == 1
    assert payload["memories"][0]["window_title"] == "One"

    db.delete_user_memories(1)
    assert db.get_recent_memories(user_id=1) == []
    assert len(db.get_recent_memories(user_id=2)) == 1


def test_screenshot_setting_is_per_user(isolated_db):
    assert db.get_user_setting(1) is False
    db.set_user_setting(1, True)
    assert db.get_user_setting(1) is True
    assert db.get_user_setting(2) is False


def test_memory_search_returns_clear_result_when_no_matches(monkeypatch):
    import ai.thought_thread_chat as chat

    monkeypatch.setattr(chat, "semantic_search", lambda *args, **kwargs: [])
    # Isolate both retrieval sources: keyword search now scans the real memory DB.
    monkeypatch.setattr(chat, "_find_keyword_memories", lambda *args, **kwargs: [])
    result = chat.ask_memory_thread_chat("something I never recorded", user_id=1)

    assert result == "I couldn't find any matching recorded memories."
