import chromadb
from backend.agents.llm import get_llm
from langchain_core.messages import HumanMessage

CHROMA_PATH = "storage/chroma_db"
COLLECTION_NAME = "research_papers"

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)

def generate_multi_queries(query: str) -> list:
    llm = get_llm()
    prompt = f"""Generate 3 different search queries to find research papers about:
"{query}"
Return ONLY 3 queries, one per line, no numbering."""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
        return [query] + queries[:3]
    except:
        return [query]

def generate_hyde_doc(query: str) -> str:
    llm = get_llm()
    prompt = f"""Write a 3-sentence hypothetical research paper abstract answering:
"{query}"
Write only the abstract."""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except:
        return query

def retrieve(query: str, top_k: int = 5) -> list:
    collection = get_collection()

    if collection.count() == 0:
        return []

    queries = generate_multi_queries(query)
    hyde_doc = generate_hyde_doc(query)
    all_queries = queries + [hyde_doc]

    seen_ids = set()
    candidates = []
    n_results = min(8, collection.count())

    for q in all_queries:
        try:
            results = collection.query(
                query_texts=[q],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                uid = f"{meta.get('arxiv_id','')}_{meta.get('chunk_index','')}"
                if uid not in seen_ids:
                    seen_ids.add(uid)
                    candidates.append({
                        "text": doc,
                        "metadata": meta,
                        "rerank_score": round(1 - float(dist), 3),
                    })
        except Exception as e:
            print(f"Query error: {e}")
            continue

    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]