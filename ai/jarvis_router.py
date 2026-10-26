"""Route dashboard JARVIS messages to memory search only when requested."""

_NO_MEMORY_MARKERS = (
    "i couldn't find any matching recorded memories",
    "i couldn't find enough information in your recorded memories",
    "i could not find enough information in your recorded memories",
    "i couldn't find a matching recorded memory",
)

# Keep ordinary requests (coding help, explanations, writing, etc.) in normal
# chat. The old router searched memory for every prompt and returned its result
# whenever any semantically similar recording existed, making unrelated chat
# look like a list of "relevant memories".
_MEMORY_INTENT_PHRASES = (
    "remember when",
    "remember what",
    "search my memor",
    "last memory",
    "latest memory",
    "most recent memory",
    "memory i made",
    "memory i created",
    "memory i have made",
    "memory on my computer",
    "what was the last memory",
    "what is my latest memory",
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
    "my memor",
    "recorded memor",
    "my past work",
    "my previous work",
    "my recent work",
    "my work history",
    "my browsing history",
    "from my history",
    "what was i working on",
    "what was i doing",
    "what did i do",
    "what did i open",
    "what did i search",
    "what did i watch",
    "what did i write",
    "what did i say",
    "what did we discuss",
    "where did i save",
    "where did i find",
    "where did i see",
    "when did i",
    "which app did i",
    "which website did i",
    "which site did i",
    "what was on my screen",
    "what was on my computer",
    "last time",
    "yesterday",
    "last week",
    "earlier today",
)


def _is_memory_question(question):
    """Return True only for prompts that explicitly ask about personal history."""
    normalized = (question or "").strip().lower()
    return any(phrase in normalized for phrase in _MEMORY_INTENT_PHRASES)


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
    """Use memory retrieval for personal-history questions, not every prompt."""
    from ai.gemini import is_gemini_available

    if _is_memory_question(question):
        from ai.thought_thread_chat import ask_memory_thread_chat

        memory_answer = ask_memory_thread_chat(question, user_id)

        # A quota/service error is not a retrieval miss; don't make another call.
        if memory_answer and (
            "you've exceeded your usage limits" in memory_answer.lower()
            or "couldn't respond right now" in memory_answer.lower()
        ):
            return memory_answer

        # For an explicit memory question, return a useful retrieval result.
        if not _memory_answer_is_insufficient(memory_answer):
            return memory_answer

    # Normal prompts go straight to general chat. A memory-search miss must not
    # cause a general answer to be framed as if it came from recorded history.
    if not is_gemini_available():
        return _configuration_help()

    from ai.gemini import ask_jarvis

    general_answer = ask_jarvis(question)
    if not general_answer:
        general_answer = "I couldn't generate a response right now."

    return general_answer
