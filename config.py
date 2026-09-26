import os
from dotenv import load_dotenv

load_dotenv()

# Optional cloud intelligence. The desktop app must remain usable without it.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or None

# Cloud AI is opt-in/available when configured; local recording and search do
# not depend on this flag.
GEMINI_ENABLED = bool(GEMINI_API_KEY)
