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
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
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


def test_recording_is_opt_in_by_default(isolated_db):
    assert db.get_recording_preferences(1) == {
        "consent": False,
        "auto_start": False,
    }


def test_auto_start_recording_requires_explicit_consent(isolated_db):
    db.set_recording_preferences(1, consent=False, auto_start=True)
    assert db.get_recording_preferences(1) == {
        "consent": False,
        "auto_start": False,
    }

    db.set_recording_preferences(1, consent=True, auto_start=True)
    assert db.get_recording_preferences(1) == {
        "consent": True,
        "auto_start": True,
    }

    db.set_recording_preferences(1, consent=False, auto_start=True)
    assert db.get_recording_preferences(1) == {
        "consent": False,
        "auto_start": False,
    }


def test_memory_search_returns_clear_result_when_no_matches(monkeypatch):
    import ai.thought_thread_chat as chat

    monkeypatch.setattr(chat, "semantic_search", lambda *args, **kwargs: [])
    # Isolate both retrieval sources: keyword search now scans the real memory DB.
    monkeypatch.setattr(chat, "_find_keyword_memories", lambda *args, **kwargs: [])
    result = chat.ask_memory_thread_chat("something I never recorded", user_id=1)

    assert result == "I couldn't find any matching recorded memories."


def test_jarvis_checks_memories_internally_then_answers_general_question(monkeypatch):
    import ai.jarvis_router as router
    import ai.gemini as gemini

    calls = []
    monkeypatch.setattr(gemini, "is_gemini_available", lambda: True)
    monkeypatch.setattr(
        "ai.thought_thread_chat.ask_memory_thread_chat",
        lambda question, user_id: calls.append(("memory", question, user_id))
        or "I couldn't find any matching recorded memories.",
    )
    monkeypatch.setattr(
        "ai.gemini.ask_jarvis",
        lambda question: calls.append(("general", question)) or "General answer.",
    )

    result = router.ask_jarvis_unified("Explain recursion", user_id=7)

    assert calls == [
        ("memory", "Explain recursion", 7),
        ("general", "Explain recursion"),
    ]
    assert result == "General answer."
    assert "memory" not in result.lower()


def test_jarvis_uses_local_memory_answer_without_gemini(monkeypatch):
    import ai.jarvis_router as router
    import ai.gemini as gemini

    monkeypatch.setattr(gemini, "is_gemini_available", lambda: False)
    monkeypatch.setattr(
        "ai.thought_thread_chat.ask_memory_thread_chat",
        lambda question, user_id: "You were working in TypeRacing.",
    )
    monkeypatch.setattr(
        "ai.gemini.ask_jarvis",
        lambda question: pytest.fail("General AI must not be called without Gemini."),
    )

    assert router.ask_jarvis_unified("What was I doing?", user_id=7) == (
        "You were working in TypeRacing."
    )


def test_jarvis_explains_missing_general_ai_configuration_without_memory_narration(monkeypatch):
    import ai.jarvis_router as router
    import ai.gemini as gemini

    calls = []
    monkeypatch.setattr(gemini, "is_gemini_available", lambda: False)
    monkeypatch.setattr(
        "ai.thought_thread_chat.ask_memory_thread_chat",
        lambda question, user_id: calls.append((question, user_id))
        or "I couldn't find any matching recorded memories.",
    )

    result = router.ask_jarvis_unified("Explain recursion", user_id=7)

    assert calls == [("Explain recursion", 7)]
    assert "GEMINI_API_KEY" in result
    assert "General AI answers aren't configured yet." in result
    assert "recorded memor" not in result.lower()


def test_quota_error_shows_simple_retry_time_without_provider_details():
    from ai.gemini import format_api_error

    message = format_api_error(
        "429 RESOURCE_EXHAUSTED {'message': 'Quota exceeded', "
        "'retryDelay': '57033s'}"
    )

    assert "You've exceeded your usage limits. Please try again at" in message
    assert "Gemini" not in message
    assert "API" not in message
    assert "ai.dev" not in message
    assert "15h 50m" not in message


def test_quota_error_without_retry_delay_is_still_simple():
    from ai.gemini import format_api_error

    message = format_api_error("429 RESOURCE_EXHAUSTED Quota exceeded")

    assert message == "You've exceeded your usage limits. Please try again later."
    assert "Gemini" not in message


def test_continuous_activity_updates_one_memory_and_tracks_end_time(isolated_db):
    memory_id = db.create_pending_memory(
        1,
        "chrome.exe",
        "YouTube - Example video",
        "2026-10-14 14:10:00",
        activity_id="single-video-session",
    )

    db.update_memory(
        memory_id,
        "Watching a video",
        "First caption",
        [],
        last_seen="2026-10-14 14:10:05",
        assign_to_thread=False,
    )
    db.update_memory(
        memory_id,
        "Watching a video",
        "First caption\\n\\nSecond caption",
        [],
        last_seen="2026-10-14 14:40:00",
        assign_to_thread=False,
    )

    conn = sqlite3.connect(isolated_db)
    try:
        rows = conn.execute(
            "SELECT timestamp, last_seen, activity_id, ocr_text FROM memories WHERE user_id = ?",
            (1,),
        ).fetchall()
    finally:
        conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "2026-10-14 14:10:00"
    assert rows[0][1] == "2026-10-14 14:40:00"
    assert rows[0][2] == "single-video-session"
    assert "Second caption" in rows[0][3]


def test_thought_threads_count_repeated_activity_sessions_not_screenshots():
    from memory.thought_threads import _count_context_sessions

    repeated_site_sessions = [
        (1, "2026-10-14 14:00:00", "chrome.exe", "YouTube", "summary", "[]", "visit-a"),
        (2, "2026-10-14 14:15:00", "chrome.exe", "YouTube", "summary", "[]", "visit-b"),
        (3, "2026-10-14 14:30:00", "chrome.exe", "YouTube", "summary", "[]", "visit-c"),
    ]
    assert _count_context_sessions(repeated_site_sessions) == 3

    # Legacy screenshot rows without activity IDs are grouped by contiguous context.
    legacy_screenshots = [
        (4, "2026-10-14 14:00:00", "chrome.exe", "YouTube", "summary", "[]"),
        (5, "2026-10-14 14:00:02", "chrome.exe", "YouTube", "summary", "[]"),
        (6, "2026-10-14 14:00:04", "chrome.exe", "YouTube", "summary", "[]"),
    ]
    assert _count_context_sessions(legacy_screenshots) == 1
