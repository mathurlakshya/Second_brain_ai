import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("Loaded API Key:", GEMINI_API_KEY[:10])