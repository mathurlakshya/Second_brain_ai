import os
from pathlib import Path
from dotenv import load_dotenv

# User-writable application data directory. This keeps installed builds out of
# Program Files and prevents per-working-directory databases.
if os.name == "nt":
    APP_DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "SecondBrainAI"
else:
    APP_DATA_DIR = Path.home() / ".secondbrainai"

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load the installed app's user-level configuration first. The project-local
# .env remains a fallback for development, but must not shadow the installed
# app's AppData configuration.
load_dotenv(APP_DATA_DIR / ".env", override=False)
load_dotenv(override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or None
GEMINI_ENABLED = bool(GEMINI_API_KEY)

DB_PATH = str(APP_DATA_DIR / "second_brain.db")
SCREENSHOT_DIR = str(APP_DATA_DIR / "screenshots")
