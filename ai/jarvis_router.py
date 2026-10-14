"""Route dashboard JARVIS messages through memory retrieval and general AI."""

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


def _configuration_help():
    """Explain how to enable cloud chat without blocking local memory retrieval."""
    return (
        "General AI answers aren't configured yet. Core recording and memory "
        "search still work locally.\n\n"
        "To enable general AI answers, create or edit this file:\n"
        "%LOCALAPPDATA%\\SecondBrainAI\\.env\n\n"
        "Add the line GEMINI_API_KEY=your_actual_api_key, save the file, "
        "and completely restart Second Brain AI. Keep your API key private."
    )


def ask_jarvis_unified(question, user_id):
    """Use relevant memories when available; otherwise answer as general chat."""
    from ai.gemini import is_gemini_available

    # Search local memory first, but keep retrieval decisions invisible to the user.
    from ai.thought_thread_chat import ask_memory_thread_chat

    memory_answer = ask_memory_thread_chat(question, user_id)

    # A quota/service error is not a retrieval miss; don't waste another API call.
    if memory_answer and (
        "you've exceeded your usage limits" in memory_answer.lower()
        or "couldn't respond right now" in memory_answer.lower()
    ):
        return memory_answer

    # If retrieval produces a useful answer, preserve it. Otherwise answer the
    # user's question normally without narrating the internal memory check.
    if not _memory_answer_is_insufficient(memory_answer):
        return memory_answer

    if not is_gemini_available():
        return _configuration_help()

    from ai.gemini import ask_jarvis

    general_answer = ask_jarvis(question)
    if not general_answer:
        general_answer = "I couldn't generate a response right now."

    return general_answer
