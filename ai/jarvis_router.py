"""Route dashboard JARVIS messages to memory recall or general AI chat."""
import re


_MEMORY_CUES = (
    "what was i", "what did i", "what have i", "where was i", "when did i",
    "what was i doing", "what was i working", "my last", "my previous",
    "my recent", "yesterday", "last time", "earlier", "before", "resume",
    "continue where", "remember when", "did i work", "was i working",
    "what was discussed", "conversation with chatgpt", "my activity",
    "my history", "my work", "my memories", "recorded", "typeracing",
    "what website", "which website", "what app", "what application",
)


def _needs_memory(question):
    normalized = re.sub(r"\s+", " ", question.lower()).strip()
    if any(cue in normalized for cue in _MEMORY_CUES):
        return True
    # First-person references often imply personal-history recall.
    return bool(re.search(r"\b(my|i was|i did|i used|i opened|i visited)\b", normalized))


def ask_jarvis_unified(question, user_id):
    """One JARVIS interface for personal memory recall and general questions."""
    if _needs_memory(question):
        from ai.thought_thread_chat import ask_memory_thread_chat
        memory_answer = ask_memory_thread_chat(question, user_id)
        # Retrieval backend returns this exact response when no matching memory exists.
        if memory_answer and "couldn't find any matching recorded memories" not in memory_answer.lower():
            return memory_answer
        # Don't fabricate recall; let the model answer generally but disclose no history was found.
        from ai.gemini import ask_jarvis
        general = ask_jarvis(question)
        return (
            "I couldn't find a matching recorded memory for that question. "
            "Here's what I can offer without a confirmed memory:\n\n" + general
        )

    from ai.gemini import ask_jarvis
    return ask_jarvis(question)
