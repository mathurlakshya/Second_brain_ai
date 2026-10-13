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
        "I couldn't find a matching recorded memory, and JARVIS's AI engine "
        "isn't configured for general questions yet. Core recording and memory "
        "search still work locally.\n\n"
        "To enable general AI answers, create or edit this file:\n"
        "%LOCALAPPDATA%\\SecondBrainAI\\.env\n\n"
        "Add the line GEMINI_API_KEY=your_actual_api_key, save the file, "
        "and completely restart Second Brain AI. Keep your API key private."
    )


def ask_jarvis_unified(question, user_id):
    """Search local memories first; use Gemini only for general-answer fallback."""
    from ai.gemini import is_gemini_available

    # Local memory search must work even when the optional cloud AI is disabled.
    from ai.thought_thread_chat import ask_memory_thread_chat

    memory_answer = ask_memory_thread_chat(question, user_id)

    # A quota/service error is not a retrieval miss; don't waste another API call.
    if memory_answer and (
        "you've exceeded your usage limits" in memory_answer.lower()
        or "couldn't respond right now" in memory_answer.lower()
    ):
        return memory_answer

    # Preserve useful local retrieval results even without an API key. When
    # Gemini is available, the memory helper returns a grounded natural answer;
    # without it, it returns a local list of matching memories.
    if not _memory_answer_is_insufficient(memory_answer):
        return memory_answer

    if not is_gemini_available():
        return _configuration_help()

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
