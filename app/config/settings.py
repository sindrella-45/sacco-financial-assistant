"""
app/config/settings.py
========================
Central configuration for the SACCO Financial Assistant.
All teammates import paths and constants from here — never hardcode paths.

Owner: shared
  - Person 1 owns DATA_DIR / PDF_DIR / RAG settings
  - Person 2 fills in AI model settings
  - Person 3 reads SACCO_NAME / CURRENCY / APP_PORT for UI display
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Directory Paths ────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent.parent  # sacco-financial-assistant/
APP_DIR    = BASE_DIR / "app"
DATA_DIR   = APP_DIR / "data"
PDF_DIR    = DATA_DIR / "pdfs"
CHROMA_DIR = BASE_DIR / "chroma_db"

# ── CSV File Paths ─────────────────────────────────────────────────────────────
USERS_CSV    = DATA_DIR / "users.csv"
LOANS_CSV    = DATA_DIR / "loans.csv"
BUDGETS_CSV  = DATA_DIR / "budgets.csv"
PAYMENTS_CSV = DATA_DIR / "payments.csv"

# ── RAG Settings (Person 1) ───────────────────────────────────────────────────
INDEX_FILE            = CHROMA_DIR / "knowledge_base.pkl"
RAG_TOP_K             = 4
RAG_SIMILARITY_CUTOFF = 0.05

# ── AI Model Settings (Person 2) ─────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL          = "claude-sonnet-4-20250514"
AI_MAX_TOKENS     = 1024
AI_TEMPERATURE    = 0.3

# ── App Display Settings (Person 3) ──────────────────────────────────────────
SACCO_NAME      = os.getenv("SACCO_NAME", "Kampala Community SACCO")
CURRENCY        = "UGX"
CURRENCY_SYMBOL = "UGX "
APP_TITLE       = "SACCO Financial Assistant"
APP_PORT        = int(os.getenv("APP_PORT", 7860))
