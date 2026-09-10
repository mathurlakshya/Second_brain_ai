from ai.gemini import generate_content
from database.semantic_search import semantic_search
from memory.thought_threads import get_thread_memories


def ask_memory_thread_chat(question, user_id, max_threads=3, memories_per_thread=8):
    """Answer using semantic hits expanded into their surrounding thought threads."""
    hits = semantic_search(question, user_id=user_id, limit=8)

    # semantic_search currently returns (score, timestamp, app, title, summary, ocr)
    # and the database lookup below finds the corresponding thread by timestamp/app/title.
    import sqlite3

    conn = sqlite3.connect("second_brain.db")
    cursor = conn.cursor()
    thread_ids = []

    for _, timestamp, app, title, _, _ in hits:
        cursor.execute(
            """SELECT thread_id FROM memories
               WHERE user_id = ? AND timestamp = ? AND app_name = ? AND window_title = ?
               ORDER BY id DESC LIMIT 1""",
            (user_id, timestamp, app, title),
        )
        row = cursor.fetchone()
        if row and row[0] and row[0] not in thread_ids:
            thread_ids.append(row[0])
        if len(thread_ids) >= max_threads:
            break
    conn.close()

    context_parts = []
    used_thread_ids = set()

    for thread_id in thread_ids:
        memories = get_thread_memories(user_id, thread_id, limit=memories_per_thread)
        if not memories:
            continue
        used_thread_ids.add(thread_id)
        lines = []
        for timestamp, app, title, summary, ocr in memories:
            lines.append(
                f"Time: {timestamp}\n"
                f"Application: {app}\n"
                f"Window: {title}\n"
                f"Summary: {summary or ''}\n"
                f"Screen Text: {ocr or ''}"
            )
        context_parts.append("\n--- THREAD ---\n" + "\n\n".join(lines))

    # Fall back to direct semantic hits when older memories have not been threaded yet.
    if not context_parts:
        for score, timestamp, app, title, summary, ocr in hits:
            context_parts.append(
                f"\nTime: {timestamp}\nApplication: {app}\nWindow: {title}\n"
                f"Summary: {summary or ''}\nScreen Text: {ocr or ''}\n"
            )

    memory_context = "\n".join(context_parts)

    prompt = f"""
You are JARVIS, the user's Second Brain.

Thought Threads are continuous streams of related work discovered from the
user's recorded computer activity. The context below contains the relevant
thread(s), not just isolated screenshots.

Use the thread context to understand what the user was doing before and after
a relevant moment. Connect related memories when answering.

Do not invent facts. If the requested information is not supported by the
recorded memories, say:

"I couldn't find enough information in your recorded memories."

Relevant Thought Threads:
{memory_context}

User Question:
{question}

Give a clear, useful answer grounded only in the recorded memories.
"""

    response = generate_content(prompt, thinking_level="medium")
    return response.text or ""
