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
modell = 'gemini-3.1-flash-lite'
def ask_jarvis(question):
    
    print("📩 User asked:", question)

    global CHAT_HISTORY
    global modell

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
        model=modell,
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
    global modell
    try:

        image = Image.open(image_path)

        response = client.models.generate_content(

           model=modell,

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
    
def summarize_screen(image_path):
    global modell
    try:

        image = Image.open(image_path)

        response = client.models.generate_content(

            model=modell,

            contents=[
                image,
                """
You are JARVIS, an AI Memory Assistant.

This summary will be stored forever inside the user's Second Brain.

Carefully inspect EVERYTHING visible on the screen.

Describe:

1. Which application is open.
2. What the user is currently doing.
3. If code is visible:
   - programming language
   - filename
   - function/class names
4. If terminal is visible:
   - important commands
   - outputs
5. If an error is visible:
   - copy the EXACT error message
   - explain what probably caused it
6. If documentation or YouTube is open:
   - explain the topic
7. Mention the user's likely goal.

Write a professional summary of about 150–250 words.

If an error is present, always include:

ERROR DETECTED:
<exact error>

This summary will later be searched by AI.
"""
            ]
        )

        return response.text

    except Exception as e:

        return f"Summary Error: {e}"    
    
def save_context(text):

    global CURRENT_CONTEXT

    CURRENT_CONTEXT = text    

def ask_about_screen(question):

    global CURRENT_CONTEXT
    global modell

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
        model=modell,
        contents=prompt
    )

    return response.text

from database.query import get_recent_memories

def ask_memory(question):
    global modell
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
            model=modell,
            contents=prompt
        )

        return response.text

    except Exception as e:
        return str(e)

def ask_memory_chat(question):
    
    memories = get_recent_memories()

    memory_text = ""

    for time, app, title, *_ in memories:

        memory_text += f"""
    Time: {time}
    App: {app}
    Title: {title}

    """

    global MEMORY_CHAT_HISTORY
    global modell
    
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
• AI-generated Summary

Use ONLY these memories to answer the user's question.

If multiple memories are related,
combine them into one clear answer.

If the answer isn't present in the memories,
say:

"I couldn't find enough information in your recorded memories."

Previous Conversation:

{history}

Recorded Memories:

{memory_text}

User Question:

{question}

Give a detailed, easy-to-read answer.
"""
    response = client.models.generate_content(
    model=modell,
    contents=prompt
    )

    answer = response.text

    MEMORY_CHAT_HISTORY.append(
    ("User", question)
    )

    MEMORY_CHAT_HISTORY.append(
        ("JARVIS", answer)
    )

    if len(MEMORY_CHAT_HISTORY) > 20:
     MEMORY_CHAT_HISTORY = MEMORY_CHAT_HISTORY[-20:]

    return answer 