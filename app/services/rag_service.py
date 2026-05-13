"""
app/services/rag_service.py  —  Person 1 responsibility
=========================================================
RAG (Retrieval-Augmented Generation) layer for the SACCO knowledge base.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HANDSHAKE 1  —  Person 1 → Person 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Person 2, this is all you need:

     from app.services.rag_service import query

     context = query("How is loan interest calculated?")
     # Returns: str — relevant passages from the PDF knowledge base
     # Pass this string into your LLM prompt as retrieved knowledge.

 The function always returns a string and never raises an exception,
 so your code will not crash even if the index is not yet built.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pre-requisite: run  python ingest.py  once before using this module.
"""

from __future__ import annotations

import pickle
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent.parent  # sacco-financial-assistant/
INDEX_FILE = BASE_DIR / "chroma_db" / "knowledge_base.pkl"

TOP_K             = 4
SIMILARITY_CUTOFF = 0.05  # minimum cosine similarity to include a result

# ── Module-level cache — loaded once, reused for every query ──────────────────
_kb = None


def _load_kb() -> dict:
    """Load the knowledge base from disk into memory (cached after first call)."""
    global _kb
    if _kb is not None:
        return _kb
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at {INDEX_FILE}.\n"
            "Please run  python ingest.py  first to build it."
        )
    with open(INDEX_FILE, "rb") as f:
        _kb = pickle.load(f)
    return _kb


# ── Public API ─────────────────────────────────────────────────────────────────

def query(question: str, top_k: int = TOP_K) -> str:
    """
    Search the SACCO PDF knowledge base for passages relevant to *question*.

    Parameters
    ----------
    question : str
        A natural-language question or topic string.
        Examples:
            "How is reducing-balance interest calculated?"
            "What is the 50/20/20/10 budget rule for SACCO members?"
            "What happens if I miss a loan repayment?"

    top_k : int, optional
        Number of text passages to retrieve (default 4).
        Increase for broader context, decrease for tighter focus.

    Returns
    -------
    str
        Relevant passages from the knowledge base PDFs, each labelled with
        its source document and separated by '---'.

        If the knowledge base is not yet built, returns an informative
        fallback string instead of raising — so Person 2's LLM calls
        continue to work during development.

    Usage example (Person 2)
    ------------------------
    >>> from app.services.rag_service import query
    >>> context = query("How do I calculate my monthly loan repayment?")
    >>> # Inject `context` into your Jinja2 prompt template
    """
    if not question or not question.strip():
        return "No question provided."

    # Load the knowledge base — return a safe fallback if not yet built
    try:
        kb = _load_kb()
    except FileNotFoundError as e:
        return (
            "[Knowledge base not yet available — please run: python ingest.py]\n"
            f"Detail: {e}"
        )
    except Exception as e:
        return f"[RAG load error: {e}]"

    # Perform cosine similarity search against all chunks
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = kb["vectorizer"]
        matrix     = kb["tfidf_matrix"]
        chunks     = kb["chunks"]
        metadata   = kb["metadata"]

        # Convert the question to a TF-IDF vector
        query_vec = vectorizer.transform([question.strip()])

        # Score every chunk and rank highest first
        scores  = cosine_similarity(query_vec, matrix).flatten()
        top_idx = scores.argsort()[::-1][:top_k]

        # Build the output — skip chunks below the similarity threshold
        passages = []
        for idx in top_idx:
            if scores[idx] < SIMILARITY_CUTOFF:
                continue
            source = (
                metadata[idx]
                .get("doc_name", "unknown")
                .replace("_", " ")
                .title()
            )
            passages.append(f"[Source: {source}]\n{chunks[idx].strip()}")

        if not passages:
            return (
                "No closely relevant information found in the knowledge base "
                "for that question. Please answer using your general knowledge "
                "of SACCOs and personal finance in Uganda."
            )

        return "\n\n---\n\n".join(passages)

    except Exception as e:
        return f"[Query failed: {e}]"


def get_kb_stats() -> dict:
    """
    Return basic statistics about the knowledge base.

    Returns a dict with keys:
        status       — 'ready', 'not_ingested', or 'error'
        total_chunks — number of text chunks in the index
        num_pdfs     — number of PDFs that were ingested
        version      — index version string
        index_path   — path to the knowledge_base.pkl file

    Useful for a settings panel or debug page in the UI.
    """
    try:
        kb = _load_kb()
        return {
            "status":       "ready",
            "total_chunks": kb.get("total_chunks", len(kb.get("chunks", []))),
            "num_pdfs":     kb.get("num_pdfs", "?"),
            "version":      kb.get("version", "?"),
            "index_path":   str(INDEX_FILE),
        }
    except FileNotFoundError:
        return {
            "status":  "not_ingested",
            "message": "Run  python ingest.py  first.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}