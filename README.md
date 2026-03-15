# 🔬 ResearchCopilot

> AI-powered research assistant · arXiv RAG + HyDE + Multi-query · Citation Network · Document Chat

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 Paper Search | Find relevant arXiv papers using RAG + HyDE + Multi-query |
| 🕸️ Citation Network | Analyze citation impact via Semantic Scholar |
| 🕳️ Gap Finder | Discover unexplored research areas |
| 📚 Literature Review | Generate structured academic reviews |
| ⚙️ Methodology | Extract research methods from papers |
| 📋 Doc Summary | Upload PDF/DOCX/TXT and get AI summary |
| 💬 Doc Chat | Ask questions about your uploaded document |

---

## 🛠️ Tech Stack

- **Frontend** — Streamlit
- **Backend** — FastAPI + Uvicorn
- **LLM** — Groq (`llama-3.3-70b-versatile`)
- **Vector DB** — ChromaDB
- **Embeddings** — `BAAI/bge-small-en-v1.5`
- **Reranker** — `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Citations** — Semantic Scholar API (free)

---

## ⚡ Quick Start

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/researchcopilot.git
cd researchcopilot
```

### 2. Virtual environment
```bash
python -m venv myenv
myenv\Scripts\activate        # Windows
source myenv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add API key
Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Ingest papers
```bash
python -m backend.rag.ingest
```

### 6. Run backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 7. Run frontend (new terminal)
```bash
streamlit run frontend/app.py
```

---

## 📁 Project Structure

```
researchcopilot/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── citation_agent.py
│   │   ├── gap_agent.py
│   │   ├── literature_agent.py
│   │   ├── llm.py
│   │   ├── methodology_agent.py
│   │   ├── paper_agent.py
│   │   └── retrieval_agent.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py
│   │   └── query.py
│   ├── __init__.py
│   └── main.py
├── frontend/
│   └── app.py
├── .env               ← NOT committed (you create this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

| Variable | Where to get it |
|----------|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |