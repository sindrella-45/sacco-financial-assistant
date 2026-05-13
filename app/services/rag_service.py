import os
import chromadb
from app.config.settings import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, RAG_NUM_RESULTS

USE_MOCK = not os.path.exists(CHROMA_DB_PATH)


def query(question: str) -> str:
    if USE_MOCK:
        return _mock_query(question)
    return _chroma_query(question)


def _chroma_query(question: str) -> str:
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(CHROMA_COLLECTION_NAME)

        results = collection.query(
            query_texts=[question],
            n_results=RAG_NUM_RESULTS
        )

        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs) if docs else "No relevant documents found."

    except Exception as e:
        return f"RAG query failed: {str(e)}. Run ingest.py first."


def _mock_query(question: str) -> str:
    q = question.lower()

    if "loan" in q or "interest" in q:
        return "SACCO loans have 15–24% reducing balance interest rate."

    if "budget" in q:
        return "Use 50/20/20/10 budgeting rule for financial stability."

    if "save" in q:
        return "Save at least 10–20% of monthly income consistently."

    return "SACCOs help members save and access affordable loans."