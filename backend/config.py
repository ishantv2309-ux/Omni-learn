import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Database URL - Defaults to local SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./omnilearn.db")

# Upload Storage Directory
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "storage" / "notes"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# External API Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX", "")
GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY", "")

# Mock Mode Configuration (Auto-enabled if keys are missing)
MOCK_GEMINI = os.getenv("MOCK_GEMINI", "auto").lower()
MOCK_YOUTUBE = os.getenv("MOCK_YOUTUBE", "auto").lower()
MOCK_SEARCH = os.getenv("MOCK_SEARCH", "auto").lower()

def is_gemini_mocked() -> bool:
    if MOCK_GEMINI == "true":
        return True
    if MOCK_GEMINI == "false":
        return False
    return not bool(GEMINI_API_KEY)

def is_youtube_mocked() -> bool:
    if MOCK_YOUTUBE == "true":
        return True
    if MOCK_YOUTUBE == "false":
        return False
    return not bool(YOUTUBE_API_KEY)

def is_search_mocked() -> bool:
    if MOCK_SEARCH == "true":
        return True
    if MOCK_SEARCH == "false":
        return False
    return not bool(GOOGLE_SEARCH_CX) or not bool(GOOGLE_SEARCH_KEY)
