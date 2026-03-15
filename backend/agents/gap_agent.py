# backend/agents/gap_agent.py
from backend.agents.llm import get_llm
from backend.rag.query import retrieve
from langchain.schema import HumanMessage

def find_gaps(query: str) -> dict:
    llm = get_llm()
    docs = retrieve(query)

    if not docs:
        return {"gaps": [], "summary": "No papers found to analyze."}

    context = "\n\n".join([d["text"][:400] for d in docs])

    prompt = f"""Analyze these research paper excerpts on "{query}" and identify:

1. Research gaps — what problems are unsolved?
2. Contradictions — where do papers disagree?
3. Future directions — what should be studied next?

Papers:
{context}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"query": query, "summary": response.content}