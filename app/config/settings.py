import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Directory Paths ────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent.parent  # sacco-financial-assistant/
APP_DIR     = BASE_DIR / "app"
DATA_DIR    = APP_DIR / "data"
PDF_DIR     = DATA_DIR / "pdfs"
PROMPTS_DIR = APP_DIR / "prompts"
CHROMA_DIR  = BASE_DIR / "chroma_db"

# ── CSV File Paths ─────────────────────────────────────────────────────────────
USERS_CSV      = DATA_DIR / "users.csv"
USERS_CSV_PATH = USERS_CSV          # alias — used by memory_service
LOANS_CSV      = DATA_DIR / "sacco_loans.csv"
BUDGETS_CSV    = DATA_DIR / "budgets.csv"
PAYMENTS_CSV   = DATA_DIR / "payments.csv"

# ── RAG Settings (Person 1) ────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "sacco_docs"
RAG_NUM_RESULTS        = 3
RAG_TOP_K              = RAG_NUM_RESULTS
RAG_SIMILARITY_CUTOFF  = 0.05
INDEX_FILE             = CHROMA_DIR / "knowledge_base.pkl"

# ── AI / LLM Settings (Person 2 — Gemini) ─────────────────────────────────────
API_KEY        = os.getenv("GEMINI_API_KEY")
MODEL_NAME     = "gemini-1.5-flash"
MAX_TOKENS     = 1024
AI_TEMPERATURE = 0.3

# ── App Display Settings (Person 3) ───────────────────────────────────────────
APP_TITLE       = "SACCO Financial Assistant"
APP_CURRENCY    = "UGX"
CURRENCY        = "UGX"         # alias used by utils/constants.py
CURRENCY_SYMBOL = "UGX "
APP_PORT        = int(os.getenv("APP_PORT", 7860))
