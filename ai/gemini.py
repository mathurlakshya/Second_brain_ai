from google import genai
from PIL import Image

from config import GEMINI_API_KEY
from ai.prompts import SYSTEM_PROMPT
from services.app_state import AppState
client = genai.Client(api_key=GEMINI_API_KEY)
print("✅ Gemini client initialized")
CURRENT_CONTEXT = ""
CHAT_HISTORY = []
MEMORY_CHAT_HISTORY = []
MODEL = 'gemini-3.1-flash-lite'
def ask_jarvis(question):
    
    print("📩 User asked:", question)

    global CHAT_HISTORY
    global MODEL

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

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    print("✅ Gemini responded")

    answer = response.text

    CHAT_HISTORY.append(("User", question))
    CHAT_HISTORY.append(("JARVIS", answer))

    if len(CHAT_HISTORY) > 20:
     CHAT_HISTORY = CHAT_HISTORY[-20:]

    return answer

    
def analyze_screen(image_path):
    global MODEL
    try:

        image = Image.open(image_path)

        response = client.models.generate_content(

           model=MODEL,

            contents=[
                image,
                
"""
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
    ]
)

        return response.text

    except Exception as e:
        return f"Vision Error: {e}"
    
def summarize_screen(image_path, ocr_text=""):
    global MODEL
    try:

        image = Image.open(image_path)

        response = client.models.generate_content(

            model=MODEL,

            contents=[

                image,
                f"""
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
"""            ]
        )

        return response.text

    except Exception as e:

        return f"Summary Error: {e}"    
    
def save_context(text):

    global CURRENT_CONTEXT

    CURRENT_CONTEXT = text    

def ask_about_screen(question):

    global CURRENT_CONTEXT
    global MODEL

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

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text

from database.query import get_recent_memories

def ask_memory(question):
    global MODEL
    memories = get_recent_memories()

    memory_text = ""

    for time, app, title, screenshot, summary in memories:

        memory_text += f"""
        Time: {time}

        Application: {app}

        Window: {title}

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

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text

    except Exception as e:
        return str(e)

def ask_memory_chat(question):
    
    from database.semantic_search import semantic_search

    memories = semantic_search(question)

    memory_text = ""

    for score, time, app, title, summary, ocr in memories:

      memory_text += f"""

        Time: {time}

        Application: {app}

        Title: {title}

        Summary:

        {summary}

        Screen Text:

        {ocr}

        """

    global MEMORY_CHAT_HISTORY
    global MODEL
    
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

The OCR text contains documents, browser pages, code, terminal output,
PDFs, emails, notes, filenames, URLs and anything readable.

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
    response = client.models.generate_content(
    model=MODEL,
    contents=prompt
    )

    answer = response.text

    MEMORY_CHAT_HISTORY.append(
    ("User", question)
    )

    MEMORY_CHAT_HISTORY.append(
        ("JARVIS", answer)
    )

    if len(MEMORY_CHAT_HISTORY) > 100:
     MEMORY_CHAT_HISTORY = MEMORY_CHAT_HISTORY[-100:]

    return answer 
