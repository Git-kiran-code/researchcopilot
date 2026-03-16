import streamlit as st
import requests
import re
import io
import time

API = "https://researchcopilot-1.onrender.com"  # v2

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchCopilot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --sidebar-bg:    #000000;
    --sidebar-bdr:   #2a2a2a;
    --main-bg:       #f7f8fc;
    --main-s1:       #ffffff;
    --main-s2:       #f0f2f9;
    --main-bdr:      #e4e8f5;
    --accent:        #4361ee;
    --accent2:       #7c3aed;
    --accent3:       #06b6d4;
    --green:         #10b981;
    --amber:         #f59e0b;
    --red:           #ef4444;
    --sidebar-text:  #ffffff;
    --sidebar-muted: #8a8fa8;
    --main-text:     #1a1d2e;
    --main-muted:    #6b7280;
    --radius:        12px;
    --radius-lg:     18px;
    --radius-xl:     24px;
    --shadow-sm:     0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow:        0 4px 16px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
    --shadow-lg:     0 10px 40px rgba(0,0,0,0.12), 0 4px 12px rgba(0,0,0,0.06);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.main { background: var(--main-bg) !important; }
.main .block-container {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1180px !important;
}
#MainMenu, footer, header, [data-testid="stDecoration"] { visibility: hidden; display: none; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--main-bdr); border-radius: 10px; }

/* ═══ SIDEBAR — force it open and styled ═══ */
[data-testid="stSidebar"] {
    background: #000000 !important;
    border-right: 1px solid #2a2a2a !important;
    min-width: 300px !important;
    max-width: 300px !important;
}
[data-testid="stSidebar"] > div {
    background: #000000 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: #000000 !important;
}
section[data-testid="stSidebar"] {
    background: #000000 !important;
    min-width: 300px !important;
}

/* Sidebar collapse button — keep visible but style it */
[data-testid="stSidebarCollapseButton"] {
    color: #888 !important;
}

/* ── Sidebar text colors ── */
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #cccccc !important;
}

/* ── Sidebar file uploader ── */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] > label {
    color: #aaaaaa !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
[data-testid="stSidebar"] [data-testid="stFileDropzone"] {
    background: #111111 !important;
    border: 1.5px dashed #3a3a3a !important;
    border-radius: 14px !important;
    padding: 1.5rem 1.2rem !important;
    transition: border-color 0.25s !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover,
[data-testid="stSidebar"] [data-testid="stFileDropzone"]:hover {
    border-color: var(--accent) !important;
    background: #0d0d0d !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    color: #dddddd !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
    color: #777777 !important;
    font-size: 0.72rem !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section button,
[data-testid="stSidebar"] [data-testid="stFileDropzone"] button {
    background: #1e1e1e !important;
    border: 1px solid #3a3a3a !important;
    border-radius: var(--radius) !important;
    color: #ffffff !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
    margin-top: 0.5rem !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section button:hover,
[data-testid="stSidebar"] [data-testid="stFileDropzone"] button:hover {
    background: #2a2a2a !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Sidebar primary button (Load & Summarize) ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    width: 100% !important;
    background: linear-gradient(135deg, #4361ee 0%, #7c3aed 100%) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(67,97,238,0.45) !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover,
[data-testid="stSidebar"] button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(67,97,238,0.55) !important;
}

/* ── MAIN AREA ── */
.app-header {
    background: var(--main-s1);
    border: 1px solid var(--main-bdr);
    border-radius: var(--radius-xl);
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.8rem;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
}
.app-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--main-text);
    margin: 0;
    line-height: 1.1;
    letter-spacing: -0.03em;
}
.app-title span {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.app-subtitle {
    font-size: 0.78rem;
    color: var(--main-muted);
    margin-top: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.02em;
}
.pill {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 5px;
    margin-top: 8px;
    letter-spacing: 0.02em;
    border: 1px solid;
}
.pill-blue   { background:#eff2ff; color:var(--accent);  border-color:#c7d2fe; }
.pill-purple { background:#f5f3ff; color:var(--accent2); border-color:#ddd6fe; }
.pill-cyan   { background:#ecfeff; color:#0891b2;        border-color:#a5f3fc; }
.pill-green  { background:#ecfdf5; color:var(--green);   border-color:#a7f3d0; }

[data-testid="stTabs"] > div:first-child {
    background: var(--main-s1) !important;
    border: 1px solid var(--main-bdr) !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.3rem 0.4rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: var(--shadow-sm) !important;
    gap: 2px !important;
}
button[data-baseweb="tab"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: var(--main-muted) !important;
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 0.5rem 0.9rem !important;
    transition: all 0.2s !important;
}
button[data-baseweb="tab"]:hover {
    color: var(--main-text) !important;
    background: var(--main-s2) !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent) !important;
    background: #eff2ff !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tabpanel"] { padding-top: 0 !important; }

.section-card {
    background: var(--main-s1);
    border: 1px solid var(--main-bdr);
    border-radius: var(--radius-xl);
    padding: 1.8rem 2rem;
    box-shadow: var(--shadow-sm);
}
.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--main-text);
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}
.section-desc {
    font-size: 0.82rem;
    color: var(--main-muted);
    margin-bottom: 0;
    line-height: 1.55;
}

[data-testid="stTextInput"] > div > div > input {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: var(--radius) !important;
    color: var(--main-text) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    height: 52px !important;
    padding: 0 1.1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(67,97,238,0.1), 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stTextInput"] label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: var(--main-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-family: 'JetBrains Mono', monospace !important;
    margin-bottom: 0.4rem !important;
}

.main [data-testid="stBaseButton-primary"],
.main button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    color: white !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.6rem !important;
    box-shadow: 0 4px 14px rgba(67,97,238,0.3) !important;
    transition: all 0.2s !important;
}
.main [data-testid="stBaseButton-primary"]:hover,
.main button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

.paper-card {
    background: var(--main-s1);
    border: 1px solid var(--main-bdr);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
    position: relative;
}
.paper-card:hover { border-color: #c7d2fe; box-shadow: var(--shadow); transform: translateY(-2px); }
.paper-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--accent), var(--accent2));
    border-radius: 3px 0 0 3px;
}
.paper-title { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 700; color: var(--main-text); margin-bottom: 0.3rem; line-height: 1.35; }
.paper-title a { color: var(--accent); text-decoration: none; }
.paper-title a:hover { text-decoration: underline; }
.paper-meta { font-size: 0.72rem; color: var(--main-muted); font-family: 'JetBrains Mono', monospace; }
.score-chip { display: inline-flex; flex-direction: column; align-items: center; background: linear-gradient(135deg, #eff2ff, #f5f3ff); border: 1px solid #c7d2fe; border-radius: 10px; padding: 6px 14px; min-width: 70px; }
.score-chip-label { font-size: 0.62rem; color: var(--main-muted); font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.06em; }
.score-chip-val { font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: var(--accent); line-height: 1.2; }

.output-card { background: var(--main-s1); border: 1px solid var(--main-bdr); border-radius: var(--radius-xl); padding: 1.8rem 2rem; margin-top: 1.2rem; box-shadow: var(--shadow-sm); font-size: 0.9rem; line-height: 1.8; color: var(--main-text); }
.output-card h3 { font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 700; color: var(--accent); margin: 1.2rem 0 0.4rem; }
.insight-box { background: linear-gradient(135deg, #f0f4ff, #f5f0ff); border: 1px solid #c7d2fe; border-left: 3px solid var(--accent); border-radius: var(--radius); padding: 1rem 1.2rem; margin: 1rem 0; font-size: 0.85rem; color: #4338ca; font-style: italic; }

[data-testid="stMetric"] { background: var(--main-s1) !important; border: 1px solid var(--main-bdr) !important; border-radius: var(--radius) !important; padding: 0.9rem 1.1rem !important; box-shadow: var(--shadow-sm) !important; }
[data-testid="stMetricLabel"] { color: var(--main-muted) !important; font-size: 0.68rem !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; }
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; }

[data-testid="stExpander"] { background: var(--main-s1) !important; border: 1px solid var(--main-bdr) !important; border-radius: var(--radius-lg) !important; margin-bottom: 0.5rem !important; box-shadow: var(--shadow-sm) !important; overflow: hidden !important; }
[data-testid="stExpander"] summary { font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 0.88rem !important; font-weight: 600 !important; color: var(--main-text) !important; padding: 0.9rem 1.2rem !important; }

[data-testid="stChatMessage"] { background: var(--main-s1) !important; border: 1px solid var(--main-bdr) !important; border-radius: var(--radius-lg) !important; margin-bottom: 0.6rem !important; box-shadow: var(--shadow-sm) !important; font-size: 0.9rem !important; }
[data-testid="stChatInput"] textarea { background: #ffffff !important; border: 1px solid #e5e7eb !important; border-radius: var(--radius-lg) !important; font-size: 0.9rem !important; color: var(--main-text) !important; }
[data-testid="stChatInput"] textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(67,97,238,0.1) !important; }

hr { border-color: var(--main-bdr) !important; margin: 1.2rem 0 !important; }

.empty-state { text-align: center; padding: 3rem 2rem; color: var(--main-muted); }
.empty-state-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
.empty-state-title { font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #374151; margin-bottom: 0.4rem; }
.empty-state-desc { font-size: 0.82rem; line-height: 1.5; }

/* Sidebar custom HTML elements */
.sb-wrap { padding: 1.4rem 1.3rem 0.5rem; }
.sb-logo { font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 800; background: linear-gradient(135deg, #818cf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.2rem; }
.sb-logo-sub { font-size: 0.7rem; color: #888888 !important; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.04em; margin-bottom: 0.5rem; }
.sb-section-label { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.14em; color: #666666 !important; margin: 1.2rem 0 0.7rem; }
.sb-divider { border-top: 1px solid #1e1e1e; margin: 1rem 0; }
.file-card { display: flex; align-items: center; gap: 0.75rem; background: #111111; border: 1px solid #2a2a2a; border-radius: var(--radius); padding: 0.9rem 1rem; margin: 0.6rem 0; }
.file-icon { font-size: 1.4rem; line-height: 1; flex-shrink: 0; }
.file-name { font-size: 0.82rem; font-weight: 600; color: #ffffff !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px; }
.file-size { font-size: 0.68rem; color: #888888 !important; font-family: 'JetBrains Mono', monospace; margin-top: 2px; }
.file-badge { margin-left: auto; font-size: 0.65rem; padding: 3px 9px; border-radius: 100px; background: #0a2010; color: #34d399 !important; border: 1px solid #065f46; font-family: 'JetBrains Mono', monospace; white-space: nowrap; flex-shrink: 0; }
.file-badge-ready { background: #1a1a2e; color: #818cf8 !important; border-color: #3730a3; }
.nav-item { display: flex; align-items: flex-start; gap: 0.7rem; padding: 0.55rem 0.5rem; border-radius: 10px; transition: background 0.15s; cursor: default; margin-bottom: 2px; }
.nav-item:hover { background: #141414; }
.nav-icon { font-size: 0.95rem; margin-top: 2px; flex-shrink: 0; }
.nav-text-title { font-size: 0.83rem; font-weight: 700; color: #ffffff !important; line-height: 1.2; }
.nav-text-desc { font-size: 0.7rem; color: #777777 !important; line-height: 1.4; margin-top: 2px; }

.role-badge { display: inline-block; padding: 3px 11px; border-radius: 100px; font-size: 0.7rem; font-weight: 600; margin-bottom: 0.6rem; border: 1px solid; }
.role-foundational { background:#ecfdf5; color:#059669; border-color:#a7f3d0; }
.role-influential   { background:#fef2f2; color:#dc2626; border-color:#fecaca; }
.role-cited         { background:#fffbeb; color:#d97706; border-color:#fde68a; }
.role-emerging      { background:#eff6ff; color:#2563eb; border-color:#bfdbfe; }
.role-standard      { background:#f9fafb; color:#6b7280; border-color:#e5e7eb; }

[data-testid="stProgress"] > div > div { background: linear-gradient(90deg, var(--accent), var(--accent2)) !important; border-radius: 100px !important; }
[data-testid="stAlert"] { border-radius: var(--radius) !important; font-size: 0.85rem !important; }
[data-testid="stSlider"] label { font-size: 0.75rem !important; font-weight: 600 !important; color: var(--main-muted) !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; font-family: 'JetBrains Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_text(file) -> str:
    try:
        import fitz, docx
        name = file.name.lower()
        if name.endswith(".pdf"):
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            return "\n\n".join(p.get_text() for p in pdf)
        elif name.endswith(".docx"):
            doc = docx.Document(io.BytesIO(file.read()))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        elif name.endswith(".txt"):
            return file.read().decode("utf-8")
        st.error("Unsupported file type.")
        return ""
    except ImportError as e:
        st.error(f"Missing library: {e}. Run: pip install pymupdf python-docx")
        return ""

def clean_text(text: str) -> str:
    text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
    text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)
    text = re.sub(r'\$[^$]+\$', '', text)
    text = re.sub(r'\\\(.*?\\\)', '', text, flags=re.DOTALL)
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    lines = text.split('\n')
    math_chars = set('∑∏∫⊗⊕≥≤≠∈∉∀∃∂∇×±∓∞√∼≈→←↔⟨⟩⌈⌉⌊⌋')
    clean_lines = [l for l in lines if sum(1 for c in l if c in math_chars) <= 3]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(clean_lines)).strip()

def call_llm(system: str, user: str) -> str:
    try:
        res = requests.post(f"{API}/chat", json={"system": system, "message": user}, timeout=120)
        res.raise_for_status()
        return res.json().get("response", "")
    except requests.exceptions.ConnectionError:
        st.error("⚡ Cannot connect to backend. Make sure uvicorn is running on port 8000.")
        return ""
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return ""

def file_icon(name: str) -> str:
    if name.endswith(".pdf"):  return "📕"
    if name.endswith(".docx"): return "📘"
    return "📄"

def fmt_size(n: int) -> str:
    if n < 1024:     return f"{n} B"
    if n < 1024**2:  return f"{n/1024:.1f} KB"
    return f"{n/1024**2:.1f} MB"

def role_class(role: str) -> str:
    if "Foundational" in role: return "role-foundational"
    if "Influential"  in role: return "role-influential"
    if "Well Cited"   in role: return "role-cited"
    if "Emerging"     in role: return "role-emerging"
    return "role-standard"

def empty_state(icon, title, desc):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{desc}</div>
    </div>""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("doc_text",""),("doc_summary",""),("chat_history",[]),
              ("doc_name",""),("doc_size",0),("last_papers",[])]:
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logo ──
    st.markdown("""
    <div class="sb-wrap">
        <div class="sb-logo">🔬 ResearchCopilot</div>
        <div class="sb-logo-sub">AI Research Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 1.3rem;">', unsafe_allow_html=True)

    # ── DOCUMENT PANEL label ──
    st.markdown('<div class="sb-section-label">Document Panel</div>', unsafe_allow_html=True)

    # ── File uploader ──
    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["pdf", "docx", "txt"],
        label_visibility="visible",
        help="Max 200MB · PDF, DOCX, TXT supported",
        key="file_uploader",
    )

    # ── Show "ready" card when file selected but not loaded ──
    if uploaded_file and not st.session_state.doc_name:
        icon  = file_icon(uploaded_file.name)
        size  = fmt_size(uploaded_file.size)
        st.markdown(f"""
        <div class="file-card">
            <div class="file-icon">{icon}</div>
            <div style="flex:1;min-width:0;">
                <div class="file-name">{uploaded_file.name}</div>
                <div class="file-size">{size}</div>
            </div>
            <div class="file-badge file-badge-ready">ready</div>
        </div>""", unsafe_allow_html=True)

    # ── Load & Summarize button ──
    if uploaded_file:
        if st.button("📥  Load & Summarize", type="primary", use_container_width=True, key="btn_load"):
            with st.spinner("Reading document…"):
                text = extract_text(uploaded_file)
            if text:
                st.session_state.doc_text    = text
                st.session_state.doc_name    = uploaded_file.name
                st.session_state.doc_size    = uploaded_file.size
                st.session_state.chat_history = []
                bar = st.progress(0, text="Generating summary…")
                for i in [20, 50, 75]:
                    time.sleep(0.25); bar.progress(i, text="Generating summary…")
                summary = call_llm(
                    system="You are a research assistant. Summarize documents clearly in plain English. No LaTeX or math symbols.",
                    user=f"Summarize this document clearly.\n\nStructure:\n**Overview** — 2-3 sentences\n**Key Contributions** — 3-5 bullet points\n**Methods Used**\n**Main Findings**\n**Limitations**\n\nDocument:\n{text[:6000]}"
                )
                bar.progress(100, text="Done!"); time.sleep(0.3); bar.empty()
                st.session_state.doc_summary = clean_text(summary)
                st.success("✅ Document ready!")

    # ── Show "loaded" card when doc is in session ──
    if st.session_state.doc_name:
        icon = file_icon(st.session_state.doc_name)
        size = fmt_size(st.session_state.doc_size)
        st.markdown(f"""
        <div class="file-card" style="border-color:#065f46; background:#021a10; margin-top:0.6rem;">
            <div class="file-icon">{icon}</div>
            <div style="flex:1;min-width:0;">
                <div class="file-name">{st.session_state.doc_name}</div>
                <div class="file-size">{size}</div>
            </div>
            <div class="file-badge">loaded</div>
        </div>""", unsafe_allow_html=True)

    # ── Divider ──
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── Navigation guide ──
    st.markdown('<div class="sb-section-label">Navigation Guide</div>', unsafe_allow_html=True)

    nav_items = [
        ("🔍", "Paper Search",       "Find relevant arXiv papers by topic"),
        ("🕸️", "Citation Network",   "Analyze citation impact of results"),
        ("🕳️", "Gap Finder",         "Discover unexplored research areas"),
        ("📚", "Literature Review",  "Generate structured academic review"),
        ("⚙️", "Methodology",        "Extract methods from papers"),
        ("📋", "My Doc Summary",     "AI summary of your document"),
        ("💬", "Chat with My Doc",   "Ask questions about your document"),
    ]
    for icon, title, desc in nav_items:
        st.markdown(f"""
        <div class="nav-item">
            <span class="nav-icon">{icon}</span>
            <div>
                <div class="nav-text-title">{title}</div>
                <div class="nav-text-desc">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close padding div


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <h1 class="app-title"><span>Research</span>Copilot</h1>
    <div class="app-subtitle">arXiv RAG + HyDE + Multi-query · Citation Network Analysis · Document Chat</div>
    <div style="margin-top:0.2rem;">
        <span class="pill pill-blue">RAG</span>
        <span class="pill pill-purple">HyDE</span>
        <span class="pill pill-blue">Multi-query</span>
        <span class="pill pill-cyan">Semantic Scholar</span>
        <span class="pill pill-green">Document Chat</span>
    </div>
</div>
""", unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "🔍 Paper Search", "🕸️ Citation Network", "🕳️ Gap Finder",
    "📚 Literature Review", "⚙️ Methodology", "📋 My Doc Summary", "💬 Chat",
])


# ── Tab 1: Paper Search ───────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🔍 Paper Search</div>
        <div class="section-desc">Search arXiv papers using RAG + HyDE + Multi-query retrieval pipeline. Results are semantically reranked using a cross-encoder model.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")

    query = st.text_input("Research Topic", placeholder="e.g. attention mechanisms in transformers", key="sq")
    if st.button("Search Papers", type="primary", key="b_search"):
        if not query:
            st.warning("Please enter a research topic.")
        else:
            with st.spinner("Retrieving papers…"):
                try:
                    res = requests.post(f"{API}/papers", json={"query": query}, timeout=120)
                    res.raise_for_status()
                    data = res.json()
                    papers = data.get("papers", [])
                    st.session_state.last_papers = papers

                    if papers:
                        st.markdown(f"<div style='font-size:0.78rem;color:var(--main-muted);margin:1rem 0 0.5rem;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:0.07em;'>Top {len(papers)} Results</div>", unsafe_allow_html=True)
                        for p in papers:
                            score = abs(round(float(p.get("score", 0)), 3))
                            st.markdown(f"""
                            <div class="paper-card">
                                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
                                    <div style="flex:1;">
                                        <div class="paper-title"><a href="{p['url']}" target="_blank">{p['title']}</a></div>
                                        <div class="paper-meta">{p['authors']} &nbsp;·&nbsp; {p['published']}</div>
                                    </div>
                                    <div class="score-chip">
                                        <span class="score-chip-label">Score</span>
                                        <span class="score-chip-val">{score}</span>
                                    </div>
                                </div>
                            </div>""", unsafe_allow_html=True)
                        st.info("💡 Switch to **🕸️ Citation Network** to analyze citation impact of these papers.")
                    else:
                        st.warning("No papers found. Run ingestion first.")

                    if data.get("summary"):
                        st.markdown("<div style='font-size:0.78rem;color:var(--main-muted);margin:1.5rem 0 0.5rem;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:0.07em;'>Analysis</div>", unsafe_allow_html=True)
                        st.markdown(f'<div class="output-card">{clean_text(data["summary"])}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Tab 2: Citation Network ───────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🕸️ Citation Network Analysis</div>
        <div class="section-desc">Analyzes citation impact, influence scores, and paper relationships using Semantic Scholar + arXiv. Run a Paper Search first.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")

    if not st.session_state.last_papers:
        empty_state("🕸️", "No papers to analyze", "Run a Paper Search first, then come back here to analyze citation impact.")
    else:
        st.markdown(f"<div style='font-size:0.78rem;color:var(--main-muted);margin-bottom:0.8rem;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:0.07em;'>{len(st.session_state.last_papers)} papers queued</div>", unsafe_allow_html=True)
        for p in st.session_state.last_papers:
            st.markdown(f'<div class="paper-card"><div class="paper-title">📄 {p["title"]}</div><div class="paper-meta">{p.get("authors","")} · {p.get("published","")}</div></div>', unsafe_allow_html=True)

        if st.button("🔍 Analyze Citation Network", type="primary", key="b_cite"):
            with st.spinner("Fetching citation data from Semantic Scholar…"):
                try:
                    res = requests.post(f"{API}/citations", json={"papers": st.session_state.last_papers}, timeout=120)
                    res.raise_for_status()
                    data = res.json()
                    papers = data.get("papers", [])
                    summary = data.get("network_summary", {})

                    if not papers:
                        st.warning("No citation data found — papers may be too recent for Semantic Scholar.")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1: st.metric("Papers Analyzed", summary.get("total_papers_analyzed", 0))
                        with c2: st.metric("Total Citations", summary.get("total_citations_across_results", 0))
                        with c3: st.metric("Top Paper Citations", summary.get("most_cited_paper", {}).get("citations", 0))
                        if summary.get("insight"):
                            st.markdown(f'<div class="insight-box">💡 {summary["insight"]}</div>', unsafe_allow_html=True)

                        st.markdown("<div style='font-size:0.78rem;color:var(--main-muted);margin:1.2rem 0 0.6rem;font-family:JetBrains Mono,monospace;text-transform:uppercase;letter-spacing:0.07em;'>Papers by Impact</div>", unsafe_allow_html=True)
                        for p in papers:
                            role = p.get("role", "📄 Standard Paper")
                            rc = role_class(role)
                            with st.expander(p.get("title", "Unknown")):
                                st.markdown(f'<span class="role-badge {rc}">{role}</span>', unsafe_allow_html=True)
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Citations", p.get("citation_count", "N/A"))
                                col2.metric("Influential", p.get("influential_citation_count", "N/A"))
                                col3.metric("References", p.get("reference_count", "N/A"))
                                links = []
                                if p.get("arxiv_id"): links.append(f"[arXiv ↗](https://arxiv.org/abs/{p['arxiv_id']})")
                                if p.get("semantic_scholar_url"): links.append(f"[Semantic Scholar ↗]({p['semantic_scholar_url']})")
                                if links: st.markdown("**Links:** " + "  ·  ".join(links))
                                cites = [c for c in p.get("top_citations", []) if c.get("title")]
                                if cites:
                                    st.markdown("**Cited by:**")
                                    for c in cites: st.markdown(f"  - {c['title']}")
                                refs = [r for r in p.get("references", []) if r.get("title")]
                                if refs:
                                    st.markdown("**Key references:**")
                                    for r in refs: st.markdown(f"  - {r['title']}")
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Tab 3: Gap Finder ─────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">🕳️ Research Gap Finder</div>
        <div class="section-desc">Identifies unexplored areas, open problems, and underrepresented topics in a research field by analyzing retrieved arXiv papers.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")
    query = st.text_input("Research Topic", placeholder="e.g. federated learning privacy", key="gq")
    if st.button("Find Research Gaps", type="primary", key="b_gap"):
        if not query: st.warning("Please enter a topic.")
        else:
            with st.spinner("Analyzing research landscape…"):
                try:
                    res = requests.post(f"{API}/gaps", json={"query": query}, timeout=120)
                    res.raise_for_status()
                    st.markdown(f'<div class="output-card">{clean_text(res.json().get("summary",""))}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")


# ── Tab 4: Literature Review ──────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">📚 Literature Review Generator</div>
        <div class="section-desc">Generates a structured, academic-style literature review synthesized from arXiv papers on your research topic.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")
    query = st.text_input("Research Topic", placeholder="e.g. graph neural networks", key="lq")
    length_val = st.slider("Review Depth", 1, 5, 3, help="1 = Brief · 5 = Comprehensive deep-dive")
    cols = st.columns(5)
    for i, (col, lbl) in enumerate(zip(cols, ["Brief","Short","Medium","Long","Deep"]), 1):
        col.markdown(f"<div style='text-align:center;font-size:0.65rem;font-family:JetBrains Mono,monospace;color:{'var(--accent)' if i==length_val else 'var(--main-muted)'};font-weight:{'700' if i==length_val else '400'};'>{lbl}</div>", unsafe_allow_html=True)
    length = {1:"short",2:"short",3:"medium",4:"long",5:"long"}[length_val]
    if st.button("Generate Review", type="primary", key="b_lit"):
        if not query: st.warning("Please enter a topic.")
        else:
            bar = st.progress(0, text="Retrieving papers…")
            time.sleep(0.3); bar.progress(25, text="Analyzing literature…")
            with st.spinner("Generating review…"):
                try:
                    res = requests.post(f"{API}/literature", json={"query": query, "length": length}, timeout=120)
                    res.raise_for_status()
                    bar.progress(90); time.sleep(0.25); bar.progress(100); time.sleep(0.3); bar.empty()
                    st.success("✅ Literature review generated!")
                    st.markdown(f'<div class="output-card">{clean_text(res.json().get("review",""))}</div>', unsafe_allow_html=True)
                except Exception as e:
                    bar.empty(); st.error(f"Error: {e}")


# ── Tab 5: Methodology ────────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">⚙️ Methodology Extractor</div>
        <div class="section-desc">Extracts, categorizes, and summarizes research methodologies and techniques from arXiv papers on your topic.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")
    query = st.text_input("Research Topic", placeholder="e.g. diffusion models image generation", key="mq")
    if st.button("Extract Methodology", type="primary", key="b_meth"):
        if not query: st.warning("Please enter a topic.")
        else:
            bar = st.progress(0, text="Retrieving papers…")
            time.sleep(0.3); bar.progress(40, text="Extracting methodology…")
            with st.spinner("Analyzing methods…"):
                try:
                    res = requests.post(f"{API}/methodology", json={"query": query}, timeout=120)
                    res.raise_for_status()
                    bar.progress(100); time.sleep(0.3); bar.empty()
                    st.success("✅ Methodology extracted!")
                    st.markdown(f'<div class="output-card">{clean_text(res.json().get("methodology",""))}</div>', unsafe_allow_html=True)
                except Exception as e:
                    bar.empty(); st.error(f"Error: {e}")


# ── Tab 6: My Doc Summary ─────────────────────────────────────────────────────
with tab6:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">📋 My Document Summary</div>
        <div class="section-desc">AI-generated structured summary of your uploaded research document — Overview, Contributions, Methods, Findings, and Limitations.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")

    if not st.session_state.doc_text:
        empty_state("📄", "No document loaded", "Upload a PDF, DOCX, or TXT from the sidebar and click Load & Summarize.")
    elif st.session_state.doc_summary:
        st.markdown(f'<div class="output-card">{st.session_state.doc_summary}</div>', unsafe_allow_html=True)
    else:
        empty_state("⏳", "Summary pending", "Click Load & Summarize in the sidebar to generate your document summary.")


# ── Tab 7: Chat ───────────────────────────────────────────────────────────────
with tab7:
    st.markdown("""
    <div class="section-card">
        <div class="section-title">💬 Chat with My Document</div>
        <div class="section-desc">Ask any question about your uploaded document. Answers are grounded exclusively in your document's content.</div>
    </div>""", unsafe_allow_html=True)
    st.write("")

    if not st.session_state.doc_text:
        empty_state("💬", "No document loaded", "Upload a document from the sidebar to start chatting with it.")
    else:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
            <span style="font-size:0.72rem;font-family:JetBrains Mono,monospace;color:var(--main-muted);text-transform:uppercase;letter-spacing:0.07em;">Chatting with</span>
            <span style="font-size:0.75rem;font-weight:700;color:var(--accent);background:#eff2ff;border:1px solid #c7d2fe;padding:2px 10px;border-radius:100px;font-family:JetBrains Mono,monospace;">{st.session_state.doc_name}</span>
        </div>""", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask anything about your document…")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    answer = call_llm(
                        system="You are a research assistant. Answer questions about the provided document accurately in plain English. No LaTeX or math symbols unless asked.",
                        user=f"Document:\n{st.session_state.doc_text[:6000]}\n\nQuestion: {user_input}\n\nAnswer based only on the document. If not found, say so clearly."
                    )
                    answer = clean_text(answer)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})