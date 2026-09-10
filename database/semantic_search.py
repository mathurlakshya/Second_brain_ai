import sqlite3
import json
import numpy as np

from ai.embeddings import create_embedding

DB_NAME = "second_brain.db"


def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def semantic_search(question, user_id=None, limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if user_id is None:
        cursor.execute("""
            SELECT id, timestamp, app_name, window_title,
                   summary, ocr_text, embedding, thread_id
            FROM memories
        """)
        rows = cursor.fetchall()
    else:
        cursor.execute("""
            SELECT id, timestamp, app_name, window_title,
                   summary, ocr_text, embedding, thread_id
            FROM memories
            WHERE user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

    conn.close()

    question_embedding = create_embedding(question)
    scored_memories = []

    for row in rows:
        memory_id, timestamp, app, title, summary, ocr, embedding_json, thread_id = row

        if not embedding_json:
            continue

        try:
            embedding = json.loads(embedding_json)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

        score = cosine_similarity(question_embedding, embedding)

        scored_memories.append(
            (score, memory_id, timestamp, app, title, summary, ocr, thread_id)
        )

    scored_memories.sort(key=lambda x: x[0], reverse=True)
    return [
        (score, timestamp, app, title, summary, ocr)
        for score, _, timestamp, app, title, summary, ocr, _ in scored_memories[:limit]
    ]
