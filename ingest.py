"""
ingest.py  —  Person 1 responsibility
=======================================
Run this ONCE before launching the app to build the knowledge base from PDFs.

    python ingest.py

What it does:
  1. Reads every PDF from app/data/pdfs/
  2. Splits the text into overlapping chunks
  3. Builds a TF-IDF vector index over all chunks
  4. Saves the index to chroma_db/knowledge_base.pkl

No internet connection required — uses scikit-learn which is already installed.
Once this has run, rag_service.query() works immediately.
"""

import os
import sys
import time
import pickle
from pathlib import Path

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
PDF_DIR       = BASE_DIR / "app" / "data" / "pdfs"
INDEX_DIR     = BASE_DIR / "chroma_db"
INDEX_FILE    = INDEX_DIR / "knowledge_base.pkl"
CHUNK_SIZE    = 500   # max characters per chunk
CHUNK_OVERLAP = 100   # characters of overlap between consecutive chunks


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF, labelling each page."""
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(f"[Page {i + 1}]\n{text.strip()}")
    return "\n\n".join(pages)


def chunk_text(text: str) -> list[str]:
    """
    Split text into overlapping chunks using paragraph boundaries.
    Overlap keeps context from one chunk to the next.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks  = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > CHUNK_SIZE and current:
            chunks.append(current.strip())
            # carry the tail of the previous chunk forward for overlap
            current = current[-CHUNK_OVERLAP:] + "\n\n" + para
        else:
            current = (current + "\n\n" + para).strip()

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  SACCO Financial Assistant — PDF Ingestion")
    print("=" * 55)

    # Validate the PDF directory exists and contains files
    if not PDF_DIR.exists():
        print(f"\n[ERROR] PDF folder not found: {PDF_DIR}")
        print("Make sure you have placed your PDFs in app/data/pdfs/")
        sys.exit(1)

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"\n[ERROR] No PDF files found in {PDF_DIR}")
        sys.exit(1)

    print(f"\nFound {len(pdf_files)} PDF(s):")
    for p in pdf_files:
        print(f"  • {p.name}")

    # Process each PDF into chunks
    all_chunks = []
    all_meta   = []

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        raw    = extract_text(pdf_path)
        chunks = chunk_text(raw)
        print(f"  {len(raw):,} characters  →  {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_meta.append({
                "source":       pdf_path.name,
                "doc_name":     pdf_path.stem,
                "chunk_index":  i,
                "total_chunks": len(chunks),
            })

    # Build TF-IDF index over all chunks
    print(f"\nBuilding TF-IDF index over {len(all_chunks)} chunks ...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),   # unigrams + bigrams for richer matching
        min_df=1,
        stop_words="english",
        max_features=50000,
    )
    matrix = vectorizer.fit_transform(all_chunks)
    print(f"  Index shape: {matrix.shape}  (chunks × vocabulary terms)")

    # Save index + chunks + metadata to disk
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "vectorizer":   vectorizer,
        "tfidf_matrix": matrix,
        "chunks":       all_chunks,
        "metadata":     all_meta,
        "version":      "1.0",
        "num_pdfs":     len(pdf_files),
        "total_chunks": len(all_chunks),
    }
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    size_kb = INDEX_FILE.stat().st_size / 1024
    print(f"\n{'=' * 55}")
    print(f"  Ingestion complete!")
    print(f"  PDFs processed : {len(pdf_files)}")
    print(f"  Total chunks   : {len(all_chunks)}")
    print(f"  Index size     : {size_kb:.1f} KB")
    print(f"  Saved to       : {INDEX_FILE}")
    print(f"{'=' * 55}")
    print("\nNext step: python run.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")