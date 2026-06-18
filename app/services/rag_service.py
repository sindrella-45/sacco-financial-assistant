import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.config.settings import CHROMA_DB_PATH

KB_PATH = os.path.join(CHROMA_DB_PATH, "knowledge_base.pkl")

_kb = None

def _load_kb():
    global _kb
    if _kb is None:
        if not os.path.exists(KB_PATH):
            print(f"⚠️  RAG: knowledge_base.pkl not found at {KB_PATH}")
            return None
        with open(KB_PATH, "rb") as f:
            _kb = pickle.load(f)
        print(f"✅ RAG: Loaded knowledge base. Keys: {list(_kb.keys())}")
        print(f"✅ RAG: {len(_kb['chunks'])} chunks available")
    return _kb


def query(question: str) -> str:
    kb = _load_kb()

    if kb is None:
        print("⚠️  RAG: falling back to mock — no knowledge base")
        return _mock_query(question)

    try:
        chunks = kb["chunks"]
        tfidf  = kb["vectorizer"]
        matrix = kb["tfidf_matrix"]

        q_vec   = tfidf.transform([question])
        scores  = cosine_similarity(q_vec, matrix).flatten()
        top_idx = np.argsort(scores)[::-1][:3]

        # Fix: explicitly convert to float to avoid numpy array ambiguity
        results = [chunks[i] for i in top_idx if float(scores[i]) > 0.0]

        if not results:
            print("⚠️  RAG: query returned no results, using mock")
            return _mock_query(question)

        print(f"✅ RAG: returning {len(results)} real chunks for: '{question[:50]}'")
        return "\n\n".join(results)

    except Exception as e:
        print(f"⚠️  RAG error: {e} — falling back to mock")
        return _mock_query(question)


def _mock_query(question: str) -> str:
    question_lower = question.lower()
    if any(word in question_lower for word in ["interest", "rate", "loan"]):
        return (
            "SACCO loans typically charge interest rates between 15% and 24% per annum "
            "on a reducing balance. Members are encouraged to repay promptly to reduce "
            "the total interest paid. Early repayment is allowed without penalty."
        )
    if any(word in question_lower for word in ["budget", "spend", "expenses"]):
        return (
            "A healthy budget allocates 50% of income to needs (rent, food, transport), "
            "20% to loan repayments, 20% to savings, and 10% to personal wants. "
            "Tracking daily expenses in a notebook helps members stay on budget."
        )
    if any(word in question_lower for word in ["save", "savings", "goal"]):
        return (
            "Financial experts recommend saving at least 10-20% of monthly income. "
            "SACCO members can open a savings account and set up automatic deductions "
            "each month to build a habit. Even small consistent savings grow over time."
        )
    return (
        "SACCOs help members access affordable loans and build savings. "
        "Members are encouraged to attend financial literacy sessions at their branch."
    )