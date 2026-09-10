"""Thought Threads: group nearby memories into coherent streams of work.

The recorder already creates an embedding for every memory.  This module uses
those embeddings locally, so creating a thread does not require an additional
Gemini request every five seconds.
"""

import json
import re
import sqlite3
from datetime import datetime

import numpy as np

DB_NAME = "second_brain.db"
THREAD_WINDOW_MINUTES = 45
THREAD_SIMILARITY = 0.62
MAX_CANDIDATE_THREADS = 12


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _ensure_schema(conn):
    cursor = conn.cursor()

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS thought_threads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            memory_count INTEGER NOT NULL DEFAULT 0,
            centroid_embedding TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'active'
        )"""
    )

    cursor.execute("PRAGMA table_info(memories)")
    columns = {row[1] for row in cursor.fetchall()}
    if "thread_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN thread_id INTEGER")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_memories_thread_id ON memories(thread_id)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_threads_user_updated ON thought_threads(user_id, updated_at DESC)"
    )
    conn.commit()


def ensure_thought_threads_schema():
    conn = sqlite3.connect(DB_NAME)
    try:
        _ensure_schema(conn)
    finally:
        conn.close()


def _parse_embedding(value):
    if not value:
        return None
    try:
        vector = np.asarray(json.loads(value), dtype=float)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if vector.ndim != 1 or vector.size == 0:
        return None
    norm = np.linalg.norm(vector)
    if norm == 0:
        return None
    return vector / norm


def _similarity(a, b):
    if a is None or b is None:
        return -1.0
    if a.shape != b.shape:
        return -1.0
    return float(np.dot(a, b))


def _title_from_memory(app, window_title, summary):
    """Create a stable human-readable title without another LLM call."""
    title = (window_title or "").strip()
    app = (app or "").strip()
    summary = re.sub(r"\s+", " ", (summary or "").strip())

    generic_titles = {"", "unknown", "new tab", "home"}
    if title.lower() not in generic_titles:
        title = re.sub(r"\s+[-|•]\s+.*$", "", title).strip()
        if title:
            return title[:72]

    if summary:
        first_sentence = re.split(r"(?<=[.!?])\s+", summary)[0]
        first_sentence = first_sentence.strip(" -•")
        if first_sentence:
            return first_sentence[:72]

    return app[:72] if app else "Untitled thought"


def assign_memory_to_thread(
    memory_id,
    user_id,
    app,
    window_title,
    timestamp,
    summary,
    embedding,
):
    """Attach a memory to the best recent semantic thread or start a new one."""
    ensure_thought_threads_schema()

    vector = np.asarray(embedding, dtype=float)
    if vector.ndim != 1 or vector.size == 0:
        return None
    norm = np.linalg.norm(vector)
    if norm == 0:
        return None
    vector = vector / norm

    conn = sqlite3.connect(DB_NAME)
    try:
        _ensure_schema(conn)
        cursor = conn.cursor()
        now = _now()

        cursor.execute(
            """SELECT id, title, last_seen, memory_count, centroid_embedding
               FROM thought_threads
               WHERE user_id = ?
                 AND status = 'active'
               ORDER BY last_seen DESC
               LIMIT ?""",
            (user_id, MAX_CANDIDATE_THREADS),
        )
        candidates = cursor.fetchall()

        best_id = None
        best_score = -1.0

        current_time = datetime.fromisoformat(timestamp)
        for thread_id, title, last_seen, count, centroid_json in candidates:
            try:
                last_time = datetime.fromisoformat(last_seen)
            except (TypeError, ValueError):
                continue

            age_minutes = (current_time - last_time).total_seconds() / 60.0
            if age_minutes < -5 or age_minutes > THREAD_WINDOW_MINUTES:
                continue

            centroid = _parse_embedding(centroid_json)
            score = _similarity(vector, centroid)
            if score > best_score:
                best_id = thread_id
                best_score = score

        if best_id is not None and best_score >= THREAD_SIMILARITY:
            cursor.execute(
                """SELECT memory_count, centroid_embedding
                   FROM thought_threads WHERE id = ?""",
                (best_id,),
            )
            row = cursor.fetchone()
            count, centroid_json = row
            centroid = _parse_embedding(centroid_json)
            if centroid is None:
                new_centroid = vector
            else:
                # Incremental centroid; normalize after each update.
                new_centroid = (centroid * count + vector) / (count + 1)
                new_centroid /= max(np.linalg.norm(new_centroid), 1e-12)

            cursor.execute(
                """UPDATE thought_threads
                   SET updated_at = ?, last_seen = ?, memory_count = ?,
                       centroid_embedding = ?, status = 'active'
                   WHERE id = ?""",
                (
                    now,
                    timestamp,
                    count + 1,
                    json.dumps(new_centroid.tolist()),
                    best_id,
                ),
            )
            thread_id = best_id
        else:
            title = _title_from_memory(app, window_title, summary)
            cursor.execute(
                """INSERT INTO thought_threads(
                    user_id, title, created_at, updated_at, last_seen,
                    memory_count, centroid_embedding, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')""",
                (
                    user_id,
                    title,
                    now,
                    now,
                    timestamp,
                    1,
                    json.dumps(vector.tolist()),
                ),
            )
            thread_id = cursor.lastrowid

        cursor.execute(
            "UPDATE memories SET thread_id = ? WHERE id = ? AND user_id = ?",
            (thread_id, memory_id, user_id),
        )
        conn.commit()
        return thread_id
    finally:
        conn.close()


def refresh_thread_status(user_id):
    """Pause threads that have been inactive for longer than the thread window."""
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute(
            "SELECT id, last_seen FROM thought_threads WHERE user_id = ? AND status = 'active'",
            (user_id,),
        )
        for thread_id, last_seen in cursor.fetchall():
            try:
                age = (now - datetime.fromisoformat(last_seen)).total_seconds() / 60.0
            except (TypeError, ValueError):
                continue
            if age > THREAD_WINDOW_MINUTES:
                cursor.execute(
                    "UPDATE thought_threads SET status = 'paused' WHERE id = ?",
                    (thread_id,),
                )
        conn.commit()
    finally:
        conn.close()


def get_thought_threads(user_id, limit=30):
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, title, created_at, updated_at, last_seen, memory_count, status
               FROM thought_threads
               WHERE user_id = ?
               ORDER BY updated_at DESC
               LIMIT ?""",
            (user_id, limit),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_thread_memories(user_id, thread_id, limit=25):
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT timestamp, app_name, window_title, summary, ocr_text
               FROM memories
               WHERE user_id = ? AND thread_id = ?
               ORDER BY id DESC
               LIMIT ?""",
            (user_id, thread_id, limit),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_active_thread(user_id):
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, title, last_seen, memory_count
               FROM thought_threads
               WHERE user_id = ? AND status = 'active'
               ORDER BY last_seen DESC
               LIMIT 1""",
            (user_id,),
        )
        return cursor.fetchone()
    finally:
        conn.close()
