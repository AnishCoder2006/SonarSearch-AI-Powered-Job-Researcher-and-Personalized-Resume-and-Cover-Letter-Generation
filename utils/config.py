import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
TEMPERATURE=0.3
GEMINI_MODEL="gemini-2.5-flash"
DATA_DIR = Path(__file__).parent.parent / "data"
    
DATA_DIR.mkdir(parents=True, exist_ok=True)
COVER_LETTERS_DIR = DATA_DIR / "cover_letters"

RESUME_PATH = DATA_DIR / "sample_resume.txt"
APPLICATIONS_LOG_PATH = DATA_DIR / "applications_log.csv"

# Ensure directories exist
COVER_LETTERS_DIR.mkdir(parents=True, exist_ok=True)
