"""Thought Threads: create a thread only after repeated related activity is detected.

A single memory is never enough to create a thread. We first look for at least
four recent, semantically related unthreaded memories. The current memory makes
five total; only then do those memories become a real Thought Thread.
No extra Gemini request is needed for thread creation.
"""

import json
import re
import sqlite3
from datetime import datetime

import numpy as np

DB_NAME = "second_brain.db"
THREAD_WINDOW_MINUTES = 45
THREAD_SIMILARITY = 0.62
MIN_THREAD_MEMORIES = 5
MAX_CANDIDATE_THREADS = 12
MAX_CANDIDATE_MEMORIES = 30


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _ensure_schema(conn):
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS thought_threads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        memory_count INTEGER NOT NULL DEFAULT 0,
        centroid_embedding TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL DEFAULT 'active'
    )""")

    cursor.execute("PRAGMA table_info(memories)")
    columns = {row[1] for row in cursor.fetchall()}
    if "thread_id" not in columns:
        cursor.execute("ALTER TABLE memories ADD COLUMN thread_id INTEGER")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_thread_id ON memories(thread_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_threads_user_updated ON thought_threads(user_id, updated_at DESC)")
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


def _normalise_embedding(embedding):
    vector = np.asarray(embedding, dtype=float)
    if vector.ndim != 1 or vector.size == 0:
        return None
    norm = np.linalg.norm(vector)
    if norm == 0:
        return None
    return vector / norm


def _similarity(a, b):
    if a is None or b is None or a.shape != b.shape:
        return -1.0
    return float(np.dot(a, b))


def _title_from_memory(app, window_title, summary):
    title = (window_title or "").strip()
    app = (app or "").strip()
    summary = re.sub(r"\s+", " ", (summary or "").strip())
    generic_titles = {"", "unknown", "new tab", "home"}

    if title.lower() not in generic_titles:
        title = re.sub(r"\s+[-|•]\s+.*$", "", title).strip()
        if title:
            return title[:72]

    if summary:
        first_sentence = re.split(r"(?<=[.!?])\s+", summary)[0].strip(" -•")
        if first_sentence:
            return first_sentence[:72]

    return app[:72] if app else "Untitled thought"


def _create_thread_from_memories(cursor, user_id, memory_rows, title):
    if len(memory_rows) < MIN_THREAD_MEMORIES:
        return None

    vectors = []
    for row in memory_rows:
        vector = _parse_embedding(row[5])
        if vector is not None:
            vectors.append(vector)

    if len(vectors) < MIN_THREAD_MEMORIES:
        return None

    centroid = np.mean(vectors, axis=0)
    norm = np.linalg.norm(centroid)
    if norm == 0:
        return None
    centroid = centroid / norm

    now = _now()
    timestamps = [row[1] for row in memory_rows if row[1]]
    last_seen = max(timestamps) if timestamps else now

    cursor.execute("""INSERT INTO thought_threads(
        user_id, title, created_at, updated_at, last_seen,
        memory_count, centroid_embedding, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'active')""", (
        user_id, title[:72], now, now, last_seen, len(memory_rows),
        json.dumps(centroid.tolist()),
    ))
    thread_id = cursor.lastrowid

    ids = [row[0] for row in memory_rows]
    cursor.executemany(
        "UPDATE memories SET thread_id = ? WHERE id = ? AND user_id = ?",
        [(thread_id, memory_id, user_id) for memory_id in ids],
    )
    return thread_id


def _find_repeated_memory_group(cursor, user_id, current_time, current_vector):
    """Find recent unthreaded memories semantically similar to the current one."""
    cursor.execute("""SELECT id, timestamp, app_name, window_title, summary, embedding
        FROM memories
        WHERE user_id = ? AND thread_id IS NULL
          AND embedding IS NOT NULL AND embedding != ''
        ORDER BY id DESC LIMIT ?""", (user_id, MAX_CANDIDATE_MEMORIES))
    rows = cursor.fetchall()

    matches = []
    for row in rows:
        try:
            memory_time = datetime.fromisoformat(row[1])
        except (TypeError, ValueError):
            continue

        age_minutes = abs((current_time - memory_time).total_seconds()) / 60.0
        if age_minutes > THREAD_WINDOW_MINUTES:
            continue

        vector = _parse_embedding(row[5])
        if vector is None:
            continue

        score = _similarity(current_vector, vector)
        if score >= THREAD_SIMILARITY:
            matches.append((score, row))

    matches.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in matches]


def assign_memory_to_thread(memory_id, user_id, app, window_title, timestamp, summary, embedding):
    """Attach a memory to a thread, but create a new thread only at five repeats."""
    ensure_thought_threads_schema()
    vector = _normalise_embedding(embedding)
    if vector is None:
        return None

    conn = sqlite3.connect(DB_NAME)
    try:
        _ensure_schema(conn)
        cursor = conn.cursor()
        current_time = datetime.fromisoformat(timestamp)
        now = _now()

        # Existing threads continue normally.
        cursor.execute("""SELECT id, last_seen, memory_count, centroid_embedding
            FROM thought_threads
            WHERE user_id = ? AND status = 'active'
            ORDER BY last_seen DESC LIMIT ?""", (user_id, MAX_CANDIDATE_THREADS))
        candidates = cursor.fetchall()

        best_id = None
        best_score = -1.0
        for thread_id, last_seen, count, centroid_json in candidates:
            try:
                age_minutes = (current_time - datetime.fromisoformat(last_seen)).total_seconds() / 60.0
            except (TypeError, ValueError):
                continue
            if age_minutes < -5 or age_minutes > THREAD_WINDOW_MINUTES:
                continue

            score = _similarity(vector, _parse_embedding(centroid_json))
            if score > best_score:
                best_id, best_score = thread_id, score

        if best_id is not None and best_score >= THREAD_SIMILARITY:
            cursor.execute(
                "SELECT memory_count, centroid_embedding FROM thought_threads WHERE id = ?",
                (best_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            count, centroid_json = row
            centroid = _parse_embedding(centroid_json)
            if centroid is None:
                new_centroid = vector
            else:
                new_centroid = (centroid * count + vector) / (count + 1)
                new_centroid /= max(np.linalg.norm(new_centroid), 1e-12)

            cursor.execute("""UPDATE thought_threads
                SET updated_at = ?, last_seen = ?, memory_count = ?, centroid_embedding = ?, status = 'active'
                WHERE id = ?""", (
                now, timestamp, count + 1, json.dumps(new_centroid.tolist()), best_id,
            ))
            cursor.execute(
                "UPDATE memories SET thread_id = ? WHERE id = ? AND user_id = ?",
                (best_id, memory_id, user_id),
            )
            conn.commit()
            return best_id

        # No thread yet: the current memory plus four matching memories creates the thread.
        group = _find_repeated_memory_group(cursor, user_id, current_time, vector)
        if len(group) + 1 < MIN_THREAD_MEMORIES:
            return None

        current_row = next((row for row in group if row[0] == memory_id), None)
        if current_row is None:
            current_row = (
                memory_id, timestamp, app, window_title, summary,
                json.dumps(vector.tolist()),
            )
            group.append(current_row)

        group = group[:MAX_CANDIDATE_MEMORIES]
        if len(group) < MIN_THREAD_MEMORIES:
            return None

        title = _title_from_memory(current_row[2], current_row[3], current_row[4])
        thread_id = _create_thread_from_memories(cursor, user_id, group, title)
        if thread_id is None:
            return None

        conn.commit()
        return thread_id
    finally:
        conn.close()


def rebuild_threads(user_id):
    """Build only five-or-more-memory threads from older memories."""
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM thought_threads WHERE user_id = ?", (user_id,))
        cursor.execute("UPDATE memories SET thread_id = NULL WHERE user_id = ?", (user_id,))
        cursor.execute("""SELECT id, timestamp, app_name, window_title, summary, embedding
            FROM memories WHERE user_id = ? AND embedding IS NOT NULL AND embedding != ''
            ORDER BY id ASC""", (user_id,))
        memories = cursor.fetchall()
    finally:
        conn.close()

    for memory_id, timestamp, app, title, summary, embedding_json in memories:
        embedding = _parse_embedding(embedding_json)
        if embedding is not None:
            try:
                assign_memory_to_thread(
                    memory_id, user_id, app, title, timestamp, summary,
                    embedding.tolist(),
                )
            except Exception as e:
                print(f"⚠️ Could not thread memory {memory_id}: {e}")


def refresh_thread_status(user_id):
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
    refresh_thread_status(user_id)
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, title, created_at, updated_at, last_seen, memory_count, status
            FROM thought_threads WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?""", (user_id, limit))
        return cursor.fetchall()
    finally:
        conn.close()


def get_thread_memories(user_id, thread_id, limit=25):
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT timestamp, app_name, window_title, summary, ocr_text
            FROM memories WHERE user_id = ? AND thread_id = ? ORDER BY id DESC LIMIT ?""", (user_id, thread_id, limit))
        return cursor.fetchall()
    finally:
        conn.close()


def get_active_thread(user_id):
    ensure_thought_threads_schema()
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, title, last_seen, memory_count
            FROM thought_threads WHERE user_id = ? AND status = 'active'
            ORDER BY last_seen DESC LIMIT 1""", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()
