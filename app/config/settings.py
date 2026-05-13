import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# BASE PATHS
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.parent  # project root
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
PROMPTS_DIR = APP_DIR / "prompts"
CHROMA_DIR = BASE_DIR / "chroma_db"

# ─────────────────────────────────────────────
# CSV FILES
# ─────────────────────────────────────────────
USERS_CSV    = DATA_DIR / "users.csv"
LOANS_CSV    = DATA_DIR / "sacco_loans.csv"
BUDGETS_CSV  = DATA_DIR / "budgets.csv"
PAYMENTS_CSV = DATA_DIR / "payments.csv"

# ─────────────────────────────────────────────
# API SETTINGS
# ─────────────────────────────────────────────
API_KEY    = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"
MAX_TOKENS = 1024

# ─────────────────────────────────────────────
# RAG SETTINGS
# ─────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "sacco_docs"
RAG_NUM_RESULTS = 3
RAG_SIMILARITY_CUTOFF = 0.05

# ─────────────────────────────────────────────
# AI SETTINGS (future upgrade support)
# ─────────────────────────────────────────────
AI_TEMPERATURE = 0.3

# ─────────────────────────────────────────────
# APP SETTINGS
# ─────────────────────────────────────────────
APP_TITLE = "SACCO Financial Assistant"
APP_CURRENCY = "UGX"
APP_PORT = int(os.getenv("APP_PORT", 7860))
