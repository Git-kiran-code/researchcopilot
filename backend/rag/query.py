# backend/rag/query.py
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from backend.agents.llm import get_llm
from langchain.schema import HumanMessage

CHROMA_PATH = "storage/chroma_db"
COLLECTION_NAME = "research_papers"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

embedder = SentenceTransformer(EMBED_MODEL)
reranker = CrossEncoder(RERANK_MODEL)

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)

def generate_multi_queries(query: str) -> list[str]:
    """Use LLM to generate 3 query variants."""
    llm = get_llm()
    prompt = f"""Generate 3 different search queries for finding research papers about:
"{query}"

Return ONLY the 3 queries, one per line, no numbering, no explanation."""
    response = llm.invoke([HumanMessage(content=prompt)])
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return [query] + queries[:3]  # original + 3 variants

def generate_hyde_doc(query: str) -> str:
    """Generate a hypothetical paper abstract for HyDE."""
    llm = get_llm()
    prompt = f"""Write a short hypothetical research paper abstract (3-4 sentences) that would perfectly answer this query:
"{query}"

Write only the abstract, no title, no explanation."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()

def retrieve(query: str, top_k: int = 10) -> list[dict]:
    """Multi-query + HyDE retrieval with reranking."""
    collection = get_collection()

    # Step 1: generate query variants
    queries = generate_multi_queries(query)
    print(f"Multi-queries: {queries}")

    # Step 2: HyDE — generate hypothetical doc and add its embedding
    hyde_doc = generate_hyde_doc(query)
    print(f"HyDE doc generated.")

    # Step 3: embed all queries + hyde doc
    all_queries = queries + [hyde_doc]
    all_embeddings = embedder.encode(all_queries).tolist()

    # Step 4: retrieve from ChromaDB for each embedding
    seen_ids = set()
    candidates = []

    for emb in all_embeddings:
        results = collection.query(
            query_embeddings=[emb],
            n_results=min(top_k, collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunk_id = meta.get("arxiv_id", "") + str(meta.get("chunk_index", ""))
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                candidates.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                })

    print(f"Total unique candidates: {len(candidates)}")

    # Step 5: rerank with cross-encoder
    if not candidates:
        return []

    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    scores = 1 / (1 + np.exp(-scores))  # sigmoid → converts raw logits to 0.0–1.0

    for i, c in enumerate(candidates):
        c["rerank_score"] = float(scores[i])

    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:5]  # top 5 after reranking