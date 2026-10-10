"""Route every dashboard JARVIS message through memory-first retrieval."""


_NO_MEMORY_MARKERS = (
    "i couldn't find any matching recorded memories",
    "i couldn't find enough information in your recorded memories",
    "i could not find enough information in your recorded memories",
    "i couldn't find a matching recorded memory",
)


def _memory_answer_is_insufficient(answer):
    """Recognize retrieval misses so they can become ordinary AI questions."""
    normalized = (answer or "").strip().lower()
    return not normalized or any(marker in normalized for marker in _NO_MEMORY_MARKERS)


def ask_jarvis_unified(question, user_id):
    """Search the user's memories first; use general AI only when they don't answer."""
    from ai.thought_thread_chat import ask_memory_thread_chat

    memory_answer = ask_memory_thread_chat(question, user_id)
    if not _memory_answer_is_insufficient(memory_answer):
        return memory_answer

    # No relevant recorded memory was found. Treat the message as a general
    # question, while being transparent that this answer is not a recollection.
    from ai.gemini import ask_jarvis
    general_answer = ask_jarvis(question)
    if not general_answer:
        general_answer = "I couldn't generate a response right now."

    return (
        "I checked your recorded memories but couldn't find enough relevant "
        "information to answer from them. Answering this as a general question:\n\n"
        + general_answer
    )
