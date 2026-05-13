import os
from dotenv import load_dotenv

load_dotenv()

# --- API ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"
MAX_TOKENS = 1024

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

CHROMA_DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "chroma_db")
USERS_CSV_PATH = os.path.join(DATA_DIR, "users.csv")
BUDGETS_CSV_PATH = os.path.join(DATA_DIR, "budgets.csv")
LOANS_CSV_PATH = os.path.join(DATA_DIR, "sacco_loans.csv")

# --- RAG ---
CHROMA_COLLECTION_NAME = "sacco_docs"
RAG_NUM_RESULTS = 3

# --- App ---
APP_TITLE = "SACCO Financial Assistant"
APP_CURRENCY = "UGX"
