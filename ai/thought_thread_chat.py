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


def _find_keyword_memories(question, user_id, limit=12):
    """Find memories by text even when embedding generation/indexing is unavailable."""
    stopwords = {
        "what", "when", "where", "which", "with", "from", "that", "this",
        "have", "about", "show", "tell", "find", "remember", "memory",
        "memories", "please", "could", "would", "were", "was", "the", "and",
        "did", "does", "do", "for", "you", "your", "my", "me", "between",
        "last", "topic", "conversation", "previous", "recent", "just", "can",
        "u", "i", "on", "in", "of", "to", "it", "is", "are",
    }
    words = list(dict.fromkeys(
        token for token in re.findall(r"[a-zA-Z0-9_-]{3,}", (question or "").lower())
        if token not in stopwords
    ))
    if not words or user_id is None:
        return []

    # Expand common ways people refer to the same subject.
    expanded = list(words)
    joined = " ".join(words)
    if "llm" in joined or "llms" in joined or "language model" in joined:
        expanded.extend(["llm", "llms", "large language model", "large language models"])
    if "chatgpt" in joined or "chat gpt" in joined:
        expanded.extend(["chatgpt", "chat gpt", "openai"])
    words = list(dict.fromkeys(expanded))

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
        LIMIT 500
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower() or "no such column" in str(exc).lower():
            return []
        raise
    finally:
        conn.close()

    # Rank by how many query concepts occur in the record, then by recency.
    scored = []
    for timestamp, app, title, summary, ocr in rows:
        searchable = " ".join((app or "", title or "", summary or "", ocr or "")).lower()
        score = sum(1 for word in words if word in searchable)
        scored.append((score, timestamp or "", app or "", title or "", summary or "", ocr or ""))
    scored.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return [(min(0.99, 0.5 + score / max(1, len(words)) * 0.49), timestamp, app, title, summary, ocr)
            for score, timestamp, app, title, summary, ocr in scored[:limit]]

def _is_latest_memory_question(question):
    """Recognize requests for the newest recorded computer activity."""
    normalized = (question or "").strip().lower()
    latest_markers = (
        "last memory",
        "latest memory",
        "most recent memory",
        "memory i made",
        "memory i created",
        "memory i have made",
        "last thing recorded",
        "most recent thing i did",
        "latest thing i did",
        "last work i did",
        "last work i was doing",
        "brief me about the last work",
        "brief me on my last work",
        "last activity on my computer",
        "last thing i did on my computer",
        "what was my last activity",
        "what did i last work on",
        "activity i did",
        "tell me the activity i did",
        "can u tell the activity",
        "can you tell the activity",
        "what activity did i do",
        "what activity was i doing",
        "tell me what i did",
        "can u tell me what i did",
        "can you tell me what i did",
        "tell me about my activity",
    )
    return any(marker in normalized for marker in latest_markers)


def _answer_latest_matching_memory(question, user_id):
    """Answer 'last thing on <app/site>' from the newest matching saved record."""
    normalized = (question or "").lower()
    target_groups = (
        (("chatgpt", "chat gpt", "openai"), "ChatGPT"),
        (("vs code", "vscode", "visual studio code", "visual studio", "code.exe"), "VS Code"),
        (("youtube",), "YouTube"),
        (("chrome", "google chrome"), "Chrome"),
    )
    target = next(
        ((terms, label) for terms, label in target_groups
         if any(term in normalized for term in terms)),
        None,
    )
    if not target or not re.search(r"\b(last|latest|most recent|what did i do|what was i doing)\b", normalized):
        return None

    terms, label = target
    clauses = []
    params = [user_id]
    for term in terms:
        clauses.append(
            "(LOWER(COALESCE(app_name, '')) LIKE ? OR "
            "LOWER(COALESCE(window_title, '')) LIKE ? OR "
            "LOWER(COALESCE(summary, '')) LIKE ? OR "
            "LOWER(COALESCE(ocr_text, '')) LIKE ?)"
        )
        params.extend([f"%{term.lower()}%"] * 4)

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT timestamp, app_name, window_title, summary, ocr_text "
            "FROM memories WHERE user_id = ? AND (" + " OR ".join(clauses) + ") "
            "ORDER BY timestamp DESC, id DESC LIMIT 1",
            params,
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower() or "no such column" in str(exc).lower():
            return None
        raise
    finally:
        conn.close()

    if not row:
        return f"I couldn't find a saved activity matching {label}."
    timestamp, app, title, summary, ocr = row
    details = (ocr or summary or "").strip()
    if details.lower() == "processing...":
        details = ""
    if len(details) > 1200:
        details = details[:1197].rsplit(" ", 1)[0] + "..."
    lines = [f"Most recent saved activity matching {label}:"]
    if timestamp:
        lines.append(f"Time: {timestamp}")
    if app:
        lines.append(f"App: {app}")
    if title:
        lines.append(f"Window: {title}")
    if details:
        lines.append(f"Recorded details: {details}")
    else:
        lines.append("No readable screen details were captured for this record.")
    return "\\n".join(lines)


def _answer_with_latest_memory(user_id):
    """Return the newest completed memory; never present a placeholder as activity."""
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT timestamp, app_name, window_title, summary, ocr_text
            FROM memories
            WHERE user_id = ?
              AND LOWER(TRIM(COALESCE(summary, ''))) NOT IN ('processing...', '')
              AND (
                  TRIM(COALESCE(summary, '')) != ''
                  OR TRIM(COALESCE(ocr_text, '')) != ''
              )
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        # If no completed memory exists, report the newest incomplete record
        # honestly rather than telling the user that "Processing..." is the task.
        if not row:
            row = conn.execute(
                """
                SELECT timestamp, app_name, window_title, summary, ocr_text
                FROM memories
                WHERE user_id = ?
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
            if not row:
                return "I couldn't find any saved computer activity yet."

            timestamp, app, title, summary, ocr = row
            lines = ["I couldn't find a completed activity record yet."]
            if app or title:
                lines.append("Last record: " + " — ".join(
                    value for value in (app, title) if value
                ))
            if timestamp:
                lines.append(f"Time: {timestamp}")
            lines.append("Its screen details weren't saved. Restart memory recording and try again.")
            return "\n".join(lines)
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc).lower() or "no such column" in str(exc).lower():
            return "I couldn't find a saved activity database."
        raise
    finally:
        conn.close()

    timestamp, app, title, summary, ocr = row
    details = (ocr or summary or "").strip()
    if details.lower() == "processing...":
        details = ""

    # Keep activity answers useful at a glance; don't dump the entire OCR capture.
    if len(details) > 280:
        details = details[:277].rsplit(" ", 1)[0].rstrip() + "..."

    lines = ["Most recent completed computer activity:"]
    if timestamp:
        lines.append(f"Time: {timestamp}")
    if app:
        lines.append(f"App: {app}")
    if title:
        lines.append(f"Window: {title}")
    if details:
        lines.append(f"Details: {details}")
    else:
        lines.append("No readable screen details were captured.")
    return "\n".join(lines)

def ask_memory_thread_chat(question, user_id, max_threads=3, memories_per_thread=8):
    """Answer from all stored memories, using Thought Threads as extra context."""
    if user_id is None:
        return "Memory search requires an authenticated user."

    # "Last/latest memory" is a chronological question, not a semantic-search
    # question. Fetch the newest record directly so similar older memories
    # cannot be mistaken for the latest activity.
    # When a question names a particular app/site, scope "last" to that
    # target instead of incorrectly returning the latest activity anywhere.
    targeted_latest = _answer_latest_matching_memory(question, user_id)
    if targeted_latest:
        return targeted_latest

    if _is_latest_memory_question(question):
        latest_answer = _answer_with_latest_memory(user_id)
        if latest_answer:
            return latest_answer

    # Semantic search scores every embedded memory for this user, not just
    # threaded ones. Add lexical matches so exact terms such as game/site names
    # still work when embeddings are weak or a memory has no embedding.
    # Run lexical retrieval first so useful OCR records remain searchable even
    # if the local embedding model is missing, slow, or fails to initialize.
    keyword_hits = _find_keyword_memories(question, user_id=user_id, limit=12)
    try:
        semantic_hits = semantic_search(question, user_id=user_id, limit=12)
    except Exception as exc:
        print(f"⚠️ Semantic memory search unavailable; using text search: {type(exc).__name__}: {exc}")
        semantic_hits = []

    hits = []
    seen = set()
    for hit in keyword_hits + semantic_hits:
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
        for timestamp, last_seen, app, title, summary, ocr in memories:
            key = (timestamp or "", app or "", title or "")
            context_seen.add(key)
            time_range = timestamp if not last_seen or last_seen == timestamp else f"{timestamp} to {last_seen}"
            lines.append(
                f"Time: {time_range}\nApplication: {app}\nWindow: {title}\n"
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
        lines = ["Relevant saved memories:"]
        for score, timestamp, app, title, summary, ocr in hits[:3]:
            detail = (summary or ocr or "No details saved.").strip().replace("\\n", " ")
            if len(detail) > 180:
                detail = detail[:177].rsplit(" ", 1)[0] + "..."
            lines.append(f"• {timestamp} — {app} — {title}: {detail}")
        return "\n".join(lines)

    prompt = f"""
You are JARVIS, the user's Second Brain.

The context contains direct matches from the user's complete recorded-memory
collection, including memories that do not belong to a Thought Thread, plus
related thread context when available. Search all supplied context; do not
restrict your answer to Thought Threads.

Answer from the supplied saved memories, including OCR/screen text. If the question asks what the user learned or discussed, infer the topic only when the captured text supports it. If no matching record supports an answer, say: "I couldn't find enough information in your recorded memories." Do not claim that memories are inaccessible when retrieval returned records.

Recorded Memory Context:
{memory_context}

User Question:
{question}

Answer briefly and directly, usually in 1–4 sentences or a few short bullets. Only provide a long explanation if the user explicitly asks. Use only facts supported by the recorded memories.
"""
    try:
        response = generate_content(prompt, thinking_level="medium")
        return response.text or ""
    except Exception as exc:
        # Keep the desktop chat alive if Gemini quota or network limits are hit.
        from ai.gemini import format_api_error
        return format_api_error(exc)
