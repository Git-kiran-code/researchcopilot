# backend/rag/ingest.py
"""
ResearchCopilot — Ingestion Pipeline
Fetches papers from arXiv across multiple categories,
downloads full PDFs for rich text, chunks, embeds,
and stores in ChromaDB.

Run with:
    python -m backend.rag.ingest
"""

import os
import ssl
import time
import urllib.request
import arxiv
import fitz
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

CHROMA_PATH     = "storage/chroma_db"
COLLECTION_NAME = "research_papers"
EMBED_MODEL     = "BAAI/bge-small-en-v1.5"
DATA_PATH       = "data/papers"

# All 6 categories with smart queries to get broad + high-quality results
CATEGORY_QUERIES = [
    ("cs.AI",   "cat:cs.AI"),
    ("cs.LG",   "cat:cs.LG"),
    ("cs.CV",   "cat:cs.CV"),
    ("cs.CL",   "cat:cs.CL"),
    ("cs.RO",   "cat:cs.RO"),
    ("stat.ML", "cat:stat.ML"),
]

PAPERS_PER_CATEGORY = 34    # 34 × 6 = ~200 unique papers
CHUNK_SIZE          = 400   # words per chunk (using your original word-based chunking)
CHUNK_OVERLAP       = 50    # word overlap between chunks
PDF_DELAY           = 2.0   # seconds between PDF downloads

# Fix SSL on Windows (keeping your original fix)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_papers(query: str, max_results: int) -> list[dict]:
    """Fetch papers from arXiv sorted by relevance (not date) for better quality."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,   # ← KEY FIX: relevance not date
        sort_order=arxiv.SortOrder.Descending,
    )
    papers = []
    for result in client.results(search):
        papers.append({
            "title":     result.title,
            "abstract":  result.summary,
            "authors":   ", ".join(a.name for a in result.authors[:5]),
            "published": str(result.published.date()),
            "pdf_url":   result.pdf_url,
            "arxiv_id":  result.entry_id.split("/")[-1],
        })
    return papers


def download_pdf(pdf_url: str, arxiv_id: str) -> str | None:
    """Download PDF and return local path. Returns None on failure."""
    os.makedirs(DATA_PATH, exist_ok=True)
    path = os.path.join(DATA_PATH, f"{arxiv_id}.pdf")
    if os.path.exists(path):
        return path
    try:
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_context, timeout=20) as resp:
            with open(path, "wb") as f:
                f.write(resp.read())
        time.sleep(PDF_DELAY)
        return path
    except Exception as e:
        print(f"    ⚠ PDF download failed: {e}")
        return None


def parse_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"    ⚠ PDF parse failed: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    return chunks


# ── Main ingestion ────────────────────────────────────────────────────────────

def ingest():
    print("\n🔬 ResearchCopilot — Ingestion Pipeline")
    print("=" * 55)

    # Setup dirs
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(CHROMA_PATH, exist_ok=True)

    # Load embedder
    print("\n📦 Loading embedding model...")
    embedder = SentenceTransformer(EMBED_MODEL)
    print(f"   ✓ {EMBED_MODEL}")

    # ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"\n📂 Collection: '{COLLECTION_NAME}'")
    print(f"   Existing chunks: {collection.count()}")

    # Fetch all papers
    print(f"\n🌐 Fetching ~{PAPERS_PER_CATEGORY * len(CATEGORY_QUERIES)} papers across {len(CATEGORY_QUERIES)} categories...")
    all_papers = []
    seen_ids = set()

    for cat_name, query in CATEGORY_QUERIES:
        print(f"\n  [{cat_name}] Fetching {PAPERS_PER_CATEGORY} papers...")
        try:
            papers = fetch_papers(query, max_results=PAPERS_PER_CATEGORY)
            added = 0
            for p in papers:
                if p["arxiv_id"] not in seen_ids:
                    seen_ids.add(p["arxiv_id"])
                    all_papers.append(p)
                    added += 1
            print(f"  ✓ {added} new unique papers from {cat_name}")
        except Exception as e:
            print(f"  ✗ Failed to fetch {cat_name}: {e}")

    print(f"\n✓ Total unique papers: {len(all_papers)}")

    # Filter already-ingested
    already_ingested = set()
    if collection.count() > 0:
        try:
            existing = collection.get(include=["metadatas"])
            for meta in existing["metadatas"]:
                already_ingested.add(meta.get("arxiv_id", ""))
        except Exception:
            pass

    new_papers = [p for p in all_papers if p["arxiv_id"] not in already_ingested]
    skipped = len(all_papers) - len(new_papers)
    if skipped:
        print(f"  Skipping {skipped} already-ingested papers")
    print(f"  New papers to process: {len(new_papers)}")

    if not new_papers:
        print("\n✅ Nothing new to ingest.")
        return

    # Process each paper
    print(f"\n⚙️  Processing papers (downloading PDFs for full text)...")
    total_chunks = 0
    success = 0
    failed = 0

    for i, paper in enumerate(new_papers):
        arxiv_id = paper["arxiv_id"]
        print(f"\n  [{i+1}/{len(new_papers)}] {paper['title'][:65]}...")

        # Try PDF first for full text, fall back to abstract
        full_text = ""
        pdf_path = download_pdf(paper["pdf_url"], arxiv_id)
        if pdf_path:
            full_text = parse_pdf(pdf_path)

        if len(full_text) < 200:
            print(f"    → Using abstract (PDF unavailable or too short)")
            full_text = f"{paper['title']}. {paper['abstract']}"

        # Chunk
        chunks = chunk_text(full_text)
        if not chunks:
            print(f"    ⚠ No chunks generated, skipping.")
            failed += 1
            continue

        print(f"    → {len(chunks)} chunks")

        # Embed
        try:
            embeddings = embedder.encode(
                chunks,
                show_progress_bar=False,
                batch_size=32,
            ).tolist()
        except Exception as e:
            print(f"    ⚠ Embedding failed: {e}")
            failed += 1
            continue

        # Store in ChromaDB
        ids = [f"{arxiv_id}_chunk_{j}" for j in range(len(chunks))]
        metadatas = [{
            "title":       paper["title"],
            "authors":     paper["authors"],
            "published":   paper["published"],
            "arxiv_id":    arxiv_id,
            "chunk_index": j,
            "url":         f"https://arxiv.org/abs/{arxiv_id}",
        } for j in range(len(chunks))]

        try:
            collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas,
            )
            total_chunks += len(chunks)
            success += 1
            print(f"    ✓ Stored {len(chunks)} chunks")
        except Exception as e:
            print(f"    ⚠ ChromaDB store failed: {e}")
            failed += 1

    # Summary
    print(f"\n{'=' * 55}")
    print(f"✅ Ingestion complete!")
    print(f"   ✓ Papers ingested  : {success}")
    print(f"   ✗ Papers failed    : {failed}")
    print(f"   📄 Chunks created  : {total_chunks}")
    print(f"   💾 Total in DB     : {collection.count()}")
    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    ingest()