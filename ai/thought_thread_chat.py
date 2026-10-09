import re
import sqlite3

from ai.gemini import generate_content, is_gemini_available
from config import DB_PATH
from database.semantic_search import semantic_search
from memory.thought_threads import get_thread_memories


def _memory_key(memory):
    """Stable-enough key for deduplicating search hits and thread expansions."""
    _, timestamp, app, title, _, _ = memory
    return (timestamp or "", app or "", title or "")


def _find_keyword_memories(question, user_id, limit=8):
    """Find exact/lexical matches too, including memories without embeddings."""
    words = list(dict.fromkeys(
        token for token in re.findall(r"[a-zA-Z0-9_-]{3,}", question.lower())
        if token not in {
            "what", "when", "where", "which", "with", "from", "that", "this",
            "have", "about", "show", "tell", "find", "remember", "memory",
            "memories", "please", "could", "would", "were", "was", "the",
        }
    ))
    if not words or user_id is None:
        return []

    clauses = []
    params = [user_id]
    for word in words:
        pattern = f"%{word}%"
        clauses.append(
            "(LOWER(COALESCE(app_name, '')) LIKE ? OR "
            "LOWER(COALESCE(window_title, '')) LIKE ? OR "
            "LOWER(COALESCE(summary, '')) LIKE ? OR "
            "LOWER(COALESCE(ocr_text, '')) LIKE ?)"
        )
        params.extend([pattern] * 4)

    sql = """
        SELECT timestamp, app_name, window_title, summary, ocr_text
        FROM memories
        WHERE user_id = ? AND (""" + " OR ".join(clauses) + """)
        ORDER BY timestamp DESC
        LIMIT ?
    """
    params.append(limit)

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    # Match the tuple shape returned by semantic_search. A neutral score keeps
    # lexical-only results usable even when their embedding is missing/poor.
    return [(0.5, timestamp, app, title, summary, ocr)
            for timestamp, app, title, summary, ocr in rows]


def ask_memory_thread_chat(question, user_id, max_threads=3, memories_per_thread=8):
    """Answer from all stored memories, using Thought Threads as extra context."""
    if user_id is None:
        return "Memory search requires an authenticated user."

    # Semantic search scores every embedded memory for this user, not just
    # threaded ones. Add lexical matches so exact terms such as game/site names
    # still work when embeddings are weak or a memory has no embedding.
    semantic_hits = semantic_search(question, user_id=user_id, limit=12)
    keyword_hits = _find_keyword_memories(question, user_id=user_id, limit=12)

    hits = []
    seen = set()
    for hit in semantic_hits + keyword_hits:
        key = _memory_key(hit)
        if key not in seen:
            seen.add(key)
            hits.append(hit)

    if not hits:
        return "I couldn't find any matching recorded memories."

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        thread_ids = []
        for _, timestamp, app, title, _, _ in hits:
            row = cursor.execute(
                """SELECT thread_id FROM memories
                   WHERE user_id = ? AND timestamp = ? AND app_name = ? AND window_title = ?
                   ORDER BY id DESC LIMIT 1""",
                (user_id, timestamp, app, title),
            ).fetchone()
            if row and row[0] and row[0] not in thread_ids:
                thread_ids.append(row[0])
            if len(thread_ids) >= max_threads:
                break
    finally:
        conn.close()

    # Thread expansion adds surrounding context, but never replaces the
    # individually matched memories (which may be unthreaded).
    context_parts = []
    context_seen = set()
    for thread_id in thread_ids:
        memories = get_thread_memories(user_id, thread_id, limit=memories_per_thread)
        if not memories:
            continue
        lines = []
        for timestamp, app, title, summary, ocr in memories:
            key = (timestamp or "", app or "", title or "")
            context_seen.add(key)
            lines.append(
                f"Time: {timestamp}\nApplication: {app}\nWindow: {title}\n"
                f"Summary: {summary or ''}\nScreen Text: {ocr or ''}"
            )
        context_parts.append("\n--- RELATED THOUGHT THREAD ---\n" + "\n\n".join(lines))

    # Always include direct matches, whether or not any of them belong to a thread.
    direct_lines = []
    for score, timestamp, app, title, summary, ocr in hits:
        if _memory_key((score, timestamp, app, title, summary, ocr)) in context_seen:
            continue
        direct_lines.append(
            f"Time: {timestamp}\nApplication: {app}\nWindow: {title}\n"
            f"Summary: {summary or ''}\nScreen Text: {ocr or ''}"
        )
    if direct_lines:
        context_parts.append("\n--- MATCHED INDIVIDUAL MEMORIES (threaded or unthreaded) ---\n"
                             + "\n\n".join(direct_lines))

    memory_context = "\n".join(context_parts)

    if not is_gemini_available():
        lines = ["I found these relevant memories:", ""]
        for score, timestamp, app, title, summary, ocr in hits:
            lines.extend([
                f"• {timestamp} — {app} — {title}",
                f"  Relevance: {score:.2f}",
                f"  {summary or ocr or 'No text summary available.'}",
                "",
            ])
        return "\n".join(lines)

    prompt = f"""
You are JARVIS, the user's Second Brain.

The context contains direct matches from the user's complete recorded-memory
collection, including memories that do not belong to a Thought Thread, plus
related thread context when available. Search all supplied context; do not
restrict your answer to Thought Threads.

Use only evidence in the context. If the memories do not support an answer,
say: "I couldn't find enough information in your recorded memories."

Recorded Memory Context:
{memory_context}

User Question:
{question}

Give a clear, useful answer grounded only in the recorded memories.
"""
    response = generate_content(prompt, thinking_level="medium")
    return response.text or ""
