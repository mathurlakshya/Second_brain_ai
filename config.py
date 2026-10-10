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

# Support both developer .env files and a user-level .env in AppData.
load_dotenv()
load_dotenv(APP_DATA_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or None
GEMINI_ENABLED = bool(GEMINI_API_KEY)

DB_PATH = str(APP_DATA_DIR / "second_brain.db")
SCREENSHOT_DIR = str(APP_DATA_DIR / "screenshots")
