# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.paper_agent import recommend_papers
from backend.agents.gap_agent import find_gaps
from backend.agents.literature_agent import generate_literature_review
from backend.agents.methodology_agent import extract_methodology
from backend.agents.citation_agent import analyze_citation_network
from backend.agents.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI(title="ResearchCopilot API")

class QueryRequest(BaseModel):
    query: str
    length: str = "medium"

class ChatRequest(BaseModel):
    system: str
    message: str

class CitationRequest(BaseModel):
    papers: list[dict]

@app.get("/")
def root():
    return {"status": "ResearchCopilot running"}

@app.post("/papers")
def papers(req: QueryRequest):
    return recommend_papers(req.query)

@app.post("/gaps")
def gaps(req: QueryRequest):
    return find_gaps(req.query)

@app.post("/literature")
def literature(req: QueryRequest):
    return generate_literature_review(req.query, req.length)

@app.post("/methodology")
def methodology(req: QueryRequest):
    return extract_methodology(req.query)

@app.post("/chat")
def chat(req: ChatRequest):
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=req.system),
        HumanMessage(content=req.message),
    ])
    return {"response": response.content}

@app.post("/citations")
def citations(req: CitationRequest):
    return analyze_citation_network(req.papers)
