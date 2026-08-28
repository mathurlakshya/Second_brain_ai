from google import genai
from google.genai import types
from PIL import Image

from config import GEMINI_API_KEY
from ai.prompts import SYSTEM_PROMPT
from database.query import get_recent_memories

import time


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-3.7-flash"
# Your existing API key from config.py
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Check your config.py / environment variable."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)

print("✅ Gemini client initialized")


# ============================================================
# GLOBAL STATE
# ============================================================

CURRENT_CONTEXT = ""

CHAT_HISTORY = []

MEMORY_CHAT_HISTORY = []


# ============================================================
# GEMINI REQUEST HELPER
# ============================================================

def generate_content(contents, thinking_level="low", max_retries=2):

    models_to_try = [
        MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(max_retries):

            try:

                print(
                    f"🚀 Gemini request: {model_name} "
                    f"(attempt {attempt + 1})"
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(
                            thinking_level=thinking_level
                        )
                    )
                )

                print(
                    f"✅ Gemini response received "
                    f"from {model_name}"
                )

                return response

            except Exception as e:

                last_error = e
                error_text = str(e)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    wait_time = 2 ** attempt

                    print(
                        f"⚠️ {model_name} unavailable."
                    )

                    print(
                        f"⏳ Retrying in {wait_time}s..."
                    )

                    time.sleep(wait_time)

                    continue

                if (
                    "401" in error_text
                    or "UNAUTHENTICATED" in error_text
                ):

                    raise

                raise

        print(
            f"⚠️ Switching from {model_name} "
            f"to fallback model..."
        )

    raise RuntimeError(
        f"All Gemini models failed. Last error: {last_error}"
    )


# ============================================================
# NORMAL JARVIS CHAT
# ============================================================

def ask_jarvis(question):

    global CHAT_HISTORY

    print("📩 User asked:", question)

    history = ""

    for role, text in CHAT_HISTORY:

        history += f"{role}: {text}\n"

    prompt = f"""
{SYSTEM_PROMPT}

Previous Conversation:

{history}

User:

{question}
"""

    print("🚀 Sending request to Gemini...")

    try:

        response = generate_content(
            prompt,
            thinking_level="low"
        )

        print("✅ Gemini responded")

        answer = response.text or "I couldn't generate a response."

        CHAT_HISTORY.append(
            ("User", question)
        )

        CHAT_HISTORY.append(
            ("JARVIS", answer)
        )

        # Keep last 20 messages
        if len(CHAT_HISTORY) > 20:

            CHAT_HISTORY = CHAT_HISTORY[-20:]

        return answer

    except Exception as e:

        print(
            f"❌ JARVIS ERROR: "
            f"{type(e).__name__}: {e}"
        )

        return (
            "Sorry, I couldn't connect to Gemini right now.\n\n"
            f"Error: {e}"
        )


# ============================================================
# SCREEN ANALYSIS
# ============================================================

def analyze_screen(image_path):

    try:

        print(
            f"👁️ Analyzing screen: {image_path}"
        )

        image = Image.open(image_path)

        prompt = """
You are JARVIS, an intelligent desktop AI assistant.

Carefully analyze EVERYTHING visible on the user's screen.

Identify:

• Application or website
• Main topic
• Text
• Code
• Programming questions
• Mathematical equations
• MCQs
• Charts
• Graphs
• Tables
• Diagrams
• Images
• Slides
• PDF content
• UI elements

If a question is visible,
understand it completely but DO NOT solve it yet.

If code is visible,
understand its purpose.

If a graph is visible,
understand what it represents.

If a slide is visible,
summarize it.

Return a detailed explanation of everything you understand.

This analysis will later be used to answer user questions.
"""

        response = generate_content(
            [
                image,
                prompt
            ],
            thinking_level="low"
        )

        return response.text or ""

    except Exception as e:

        print(
            f"❌ Vision analysis failed: {e}"
        )

        return f"Vision Error: {e}"


# ============================================================
# SCREEN SUMMARY
# ============================================================

def summarize_screen(
    image_path,
    ocr_text=""
):

    try:

        image = Image.open(image_path)

        prompt = f"""
You are JARVIS.

Below is OCR text extracted from the screenshot.

Use BOTH:

1. Screenshot
2. OCR text

to produce the most accurate summary.

OCR:

{ocr_text}

Explain:

• What document is open
• What coding task is happening
• What topic is being studied
• Any important code
• Any errors
• Important facts

Keep it concise.
"""

        response = generate_content(
            [
                image,
                prompt
            ],
            thinking_level="low"
        )

        return response.text or ""

    except Exception as e:

        print(
            f"❌ Screen summary failed: {e}"
        )

        return f"Summary Error: {e}"


# ============================================================
# SAVE CURRENT SCREEN CONTEXT
# ============================================================

def save_context(text):

    global CURRENT_CONTEXT

    CURRENT_CONTEXT = text


# ============================================================
# ASK ABOUT CURRENT SCREEN
# ============================================================

def ask_about_screen(question):

    global CURRENT_CONTEXT

    prompt = f"""
You are JARVIS.

You have already analyzed the user's screen.

Here is your complete analysis:

{CURRENT_CONTEXT}

The user is now asking a question about that screen.

Question:

{question}

Rules:

- Answer ONLY using the analyzed screen.
- If there is a math question, solve it step by step.
- If there is programming code, explain or debug it.
- If there is a DSA question, solve it.
- If there is an image, describe and explain it.
- If there is a graph, interpret it.
- If there is a diagram, explain it.
- If there is a slide, teach it simply.
- If there is an MCQ, explain why the correct answer is correct.
- If there is a table, analyze it.

Be detailed and educational.
"""

    try:

        response = generate_content(
            prompt,
            thinking_level="medium"
        )

        return response.text or ""

    except Exception as e:

        print(
            f"❌ Current screen question failed: {e}"
        )

        return (
            "I couldn't analyze the current screen right now.\n\n"
            f"Error: {e}"
        )


# ============================================================
# ASK ABOUT RECENT MEMORIES
# ============================================================

def ask_memory(question):

    memories = get_recent_memories()

    memory_text = ""

    for (
        time_value,
        app,
        title,
        screenshot,
        summary
    ) in memories:

        memory_text += f"""
Time:
{time_value}

Application:
{app}

Window:
{title}

Summary:
{summary}

-----------------------------------
"""

    prompt = f"""
You are JARVIS.

Below is the user's computer history.

{memory_text}

Answer ONLY using these memories.

Question:

{question}
"""

    try:

        response = generate_content(
            prompt,
            thinking_level="medium"
        )

        return response.text or ""

    except Exception as e:

        print(
            f"❌ Memory question failed: {e}"
        )

        return (
            "I couldn't search your memories right now.\n\n"
            f"Error: {e}"
        )


# ============================================================
# SEMANTIC MEMORY CHAT
# ============================================================

def ask_memory_chat(question):

    from database.semantic_search import semantic_search

    memories = semantic_search(question)

    memory_text = ""

    for (
        score,
        time_value,
        app,
        title,
        summary,
        ocr
    ) in memories:

        memory_text += f"""

Time:
{time_value}

Application:
{app}

Title:
{title}

Summary:
{summary}

Screen Text:
{ocr}

-----------------------------------

"""

    global MEMORY_CHAT_HISTORY

    history = ""

    for role, text in MEMORY_CHAT_HISTORY:

        history += f"{role}: {text}\n"

    prompt = f"""
You are JARVIS, the user's Second Brain.

Below are memories collected from the user's computer.

Each memory contains:

• Timestamp
• Application
• Window Title
• Summary
• Everything that was visible on the screen

The OCR text contains documents, browser pages, code,
terminal output, PDFs, emails, notes, filenames,
URLs and anything readable.

Use BOTH the summaries and OCR text to answer.

If the answer exists anywhere inside OCR,
quote the relevant part.

If multiple memories contain pieces of the answer,
combine them.

Never ignore OCR text.

Use ONLY these memories to answer the user's question.

If multiple memories are related,
combine them into one clear answer.

If the answer isn't present in the memories,
say:

"I couldn't find enough information in your recorded memories."

Previous Conversation:

{history}

Relevant Memories:

{memory_text}

These memories were selected using semantic similarity.

They are already the most relevant memories.

Use them to answer accurately.

User Question:

{question}

Give a detailed, easy-to-read answer.
"""

    try:

        response = generate_content(
            prompt,
            thinking_level="medium"
        )

        answer = response.text or ""

        MEMORY_CHAT_HISTORY.append(
            ("User", question)
        )

        MEMORY_CHAT_HISTORY.append(
            ("JARVIS", answer)
        )

        # Keep last 100 messages
        if len(MEMORY_CHAT_HISTORY) > 100:

            MEMORY_CHAT_HISTORY = (
                MEMORY_CHAT_HISTORY[-100:]
            )

        return answer

    except Exception as e:

        print(
            f"❌ Memory chat failed: {e}"
        )

        return (
            "I couldn't answer from your memories right now.\n\n"
            f"Error: {e}"
        )
