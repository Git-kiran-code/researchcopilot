# backend/agents/paper_agent.py
from backend.agents.llm import get_llm
from backend.rag.query import retrieve
from langchain.schema import HumanMessage

def recommend_papers(query: str) -> dict:
    """Retrieve and summarize top papers for a query."""
    llm = get_llm()
    docs = retrieve(query)

    if not docs:
        return {"query": query, "papers": [], "summary": "No papers found."}

    context = "\n\n".join([
        f"Title: {d['metadata'].get('title', 'Unknown')}\n"
        f"Authors: {d['metadata'].get('authors', '')}\n"
        f"Published: {d['metadata'].get('published', '')}\n"
        f"Excerpt: {d['text'][:300]}"
        for d in docs
    ])

    prompt = f"""You are a research assistant. Based on the research papers below, answer the query in plain English.

Query: "{query}"

Papers:
{context}

Write a clean, structured analysis with these sections:

**Top Relevant Papers**
For each paper, write 1-2 sentences explaining why it is relevant to the query. Do NOT copy the abstract verbatim.

**Key Findings**
Summarize the main insights across all papers in 3-5 bullet points. Use plain English — no LaTeX, no math symbols, no formulas.

**Recommended Reading Order**
List the papers in the order someone should read them, with one sentence explaining why.

Important: Do not include any mathematical notation, LaTeX, or raw formulas. Explain concepts in plain language only."""

    response = llm.invoke([HumanMessage(content=prompt)])

    seen = set()
    papers = []
    for d in docs:
        aid = d["metadata"].get("arxiv_id", "")
        if aid not in seen:
            seen.add(aid)
            papers.append({
                "title": d["metadata"].get("title", ""),
                "authors": d["metadata"].get("authors", ""),
                "published": d["metadata"].get("published", ""),
                "arxiv_id": aid,
                "score": round(d["rerank_score"], 3),
                "url": f"https://arxiv.org/abs/{aid}",
            })

    return {"query": query, "papers": papers, "summary": response.content}