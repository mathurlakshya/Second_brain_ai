import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_image(image_path):

    try:

        image = Image.open(image_path)

        response = model.generate_content([
            "Describe in one short sentence what the user is doing on this computer screen.",
            image
        ])

        return response.text

    except Exception as e:

        return f"Vision Error: {e}"