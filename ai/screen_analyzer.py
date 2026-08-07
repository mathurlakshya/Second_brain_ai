from PIL import Image
from ai.gemini import model


def analyze_screen(image_path):

    try:

        image = Image.open(image_path)

        response = model.generate_content([
            """
You are JARVIS inside Second Brain AI.

Analyze this computer screen.

Reply in exactly this format:

Current App:
What the user is doing:
Possible Goal:
Potential Problem:

Keep it under 120 words.
""",
            image
        ])

        return response.text

    except Exception as e:
        return f"Vision Error:\n{e}"