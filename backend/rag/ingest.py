import os
import ssl
import time
import urllib.request
import arxiv
import fitz
import chromadb
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH     = "storage/chroma_db"
COLLECTION_NAME = "research_papers"
DATA_PATH       = "data/papers"
CHUNK_SIZE      = 400
CHUNK_OVERLAP   = 50
PDF_DELAY       = 2.0

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fetch_papers(query: str, max_results: int) -> list:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
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

def download_pdf(pdf_url: str, arxiv_id: str) -> str:
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
        print(f"PDF download failed: {e}")
        return None

def parse_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"PDF parse failed: {e}")
        return ""

def chunk_text(text: str) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        if len(chunk.strip()) > 50:
            chunks.append(chunk)
    return chunks

def ingest(topic: str = None, max_results: int = 10):
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(CHROMA_PATH, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Determine what to fetch
    if topic:
        queries = [(topic, topic)]
    else:
        queries = [
            ("cs.AI",   "cat:cs.AI"),
            ("cs.LG",   "cat:cs.LG"),
            ("cs.CV",   "cat:cs.CV"),
            ("cs.CL",   "cat:cs.CL"),
            ("stat.ML", "cat:stat.ML"),
        ]
        max_results = 20

    all_papers = []
    seen_ids = set()

    for label, query in queries:
        print(f"Fetching: {label}")
        try:
            papers = fetch_papers(query, max_results)
            for p in papers:
                if p["arxiv_id"] not in seen_ids:
                    seen_ids.add(p["arxiv_id"])
                    all_papers.append(p)
        except Exception as e:
            print(f"Fetch failed for {label}: {e}")

    print(f"Total papers: {len(all_papers)}")

    # Skip already ingested
    already = set()
    if collection.count() > 0:
        try:
            existing = collection.get(include=["metadatas"])
            for meta in existing["metadatas"]:
                already.add(meta.get("arxiv_id", ""))
        except Exception:
            pass

    new_papers = [p for p in all_papers if p["arxiv_id"] not in already]
    print(f"New papers to process: {len(new_papers)}")

    total_chunks = 0

    for i, paper in enumerate(new_papers):
        arxiv_id = paper["arxiv_id"]
        print(f"[{i+1}/{len(new_papers)}] {paper['title'][:60]}...")

        full_text = ""
        pdf_path = download_pdf(paper["pdf_url"], arxiv_id)
        if pdf_path:
            full_text = parse_pdf(pdf_path)

        if len(full_text) < 200:
            full_text = f"{paper['title']}. {paper['abstract']}"

        chunks = chunk_text(full_text)
        if not chunks:
            continue

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
                ids=ids,
                metadatas=metadatas,
            )
            total_chunks += len(chunks)
            print(f"  Stored {len(chunks)} chunks")
        except Exception as e:
            print(f"  Store failed: {e}")

    print(f"Done. Total chunks in DB: {collection.count()}")

if __name__ == "__main__":
    topic = input("Enter topic: ").strip()
    ingest(topic, max_results=5)