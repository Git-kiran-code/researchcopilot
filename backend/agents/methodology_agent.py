# backend/agents/methodology_agent.py
from backend.agents.llm import get_llm
from backend.rag.query import retrieve
from langchain_core.messages import HumanMessage

def extract_methodology(query: str) -> dict:
    llm = get_llm()
    docs = retrieve(query)

    if not docs:
        return {"methodology": "No papers found."}

    context = "\n\n".join([d["text"][:400] for d in docs])

    prompt = f"""From these research papers on "{query}", extract:

1. Datasets used
2. Methods / models / algorithms
3. Evaluation metrics
4. Key results / numbers

Papers:
{context}

Be specific and concise."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"query": query, "methodology": response.content}
