import os
from app.config.settings import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, RAG_NUM_RESULTS

# Toggle this to False once Person 1 has run ingest.py
USE_MOCK = not os.path.exists(CHROMA_DB_PATH)


def query(question: str) -> str:
    """
    Search SACCO documents for content relevant to the question.

    Args:
        question: The user's question as a string

    Returns:
        Relevant text from SACCO documents as a single string.
        Returns a placeholder if the vector store is not ready yet.
    """
    if USE_MOCK:
        return _mock_query(question)
    return _chroma_query(question)


def _chroma_query(question: str) -> str:
    """Real ChromaDB query — used once ingest.py has been run."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
        results = collection.query(query_texts=[question], n_results=RAG_NUM_RESULTS)
        documents = results.get("documents", [[]])[0]
        return "\n\n".join(documents) if documents else "No relevant documents found."
    except Exception as e:
        return f"RAG query failed: {str(e)}. Please ensure ingest.py has been run."


def _mock_query(question: str) -> str:
    """
    Temporary mock responses used before ChromaDB is ready.
    Returns basic SACCO financial knowledge based on keywords.
    """
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
            "Financial experts recommend saving at least 10–20% of monthly income. "
            "SACCO members can open a savings account and set up automatic deductions "
            "each month to build a habit. Even small consistent savings grow over time."
        )

    return (
        "SACCOs (Savings and Credit Cooperatives) help members access affordable loans "
        "and build savings. Members are encouraged to attend financial literacy sessions "
        "at their branch for personalised guidance."
    )
