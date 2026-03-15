# backend/agents/literature_agent.py
from backend.agents.llm import get_llm
from backend.rag.query import retrieve
from langchain.schema import HumanMessage

def generate_literature_review(query: str, length: str = "medium") -> dict:
    llm = get_llm()
    docs = retrieve(query)

    if not docs:
        return {"review": "No papers found."}

    context = "\n\n".join([
        f"[{d['metadata'].get('title', '')}] {d['text'][:350]}"
        for d in docs
    ])

    length_map = {"short": "2 paragraphs", "medium": "4 paragraphs", "long": "6 paragraphs"}
    length_str = length_map.get(length, "4 paragraphs")

    prompt = f"""Write a {length_str} academic literature review on "{query}".

Use these papers as sources. Cite them by title in brackets.

Papers:
{context}

Write in formal academic style."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"query": query, "length": length, "review": response.content}