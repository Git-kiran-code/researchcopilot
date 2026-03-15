# backend/agents/citation_agent.py
import re
import requests
import time

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"


def clean_arxiv_id(arxiv_id: str) -> str:
    """
    Normalize arxiv ID for Semantic Scholar API.
    Handles all formats your ingest pipeline may produce:
      2301.12345v2   → 2301.12345
      2301_12345v1   → 2301.12345
      cs_0501023v1   → cs/0501023
    """
    # Replace underscores that were used as dot/slash substitutes
    # Format: YYMM_NNNNN → YYMM.NNNNN
    arxiv_id = re.sub(r'^(\d{4})_(\d+)', r'\1.\2', arxiv_id)
    # Format: cs_NNNNN → cs/NNNNN (old-style category IDs)
    arxiv_id = re.sub(r'^([a-z]+)_(\w+)', r'\1/\2', arxiv_id)
    # Remove version suffix: v1, v2, v3 etc.
    arxiv_id = re.sub(r'v\d+$', '', arxiv_id.strip())
    return arxiv_id


def get_citation_data(arxiv_id: str) -> dict:
    """Fetch citation data from Semantic Scholar for a given arxiv ID."""
    try:
        clean_id = clean_arxiv_id(arxiv_id)
        url = f"{SEMANTIC_SCHOLAR_API}/paper/arXiv:{clean_id}"
        params = {
            "fields": "title,authors,year,citationCount,referenceCount,citations,references,influentialCitationCount,url"
        }
        res = requests.get(url, params=params, timeout=10)

        if res.status_code == 200:
            data = res.json()
            return {
                "arxiv_id":                  arxiv_id,
                "title":                     data.get("title", ""),
                "citation_count":            data.get("citationCount", 0),
                "influential_citation_count": data.get("influentialCitationCount", 0),
                "reference_count":           data.get("referenceCount", 0),
                "semantic_scholar_url":      data.get("url", ""),
                "top_citations": [
                    {"title": c.get("title", ""), "paperId": c.get("paperId", "")}
                    for c in data.get("citations", [])[:5]
                ],
                "references": [
                    {"title": r.get("title", ""), "paperId": r.get("paperId", "")}
                    for r in data.get("references", [])[:5]
                ],
            }
        elif res.status_code == 404:
            return {"arxiv_id": arxiv_id, "citation_count": None, "error": "Not found in Semantic Scholar"}
        elif res.status_code == 429:
            # Rate limited — wait and skip
            time.sleep(5)
            return {"arxiv_id": arxiv_id, "citation_count": None, "error": "Rate limited"}
        else:
            return {"arxiv_id": arxiv_id, "citation_count": None, "error": f"HTTP {res.status_code}"}

    except Exception as e:
        return {"arxiv_id": arxiv_id, "citation_count": None, "error": str(e)}


def analyze_citation_network(papers: list[dict]) -> dict:
    """
    Given a list of papers (with arxiv_ids), fetch citation data for each
    and return a full network analysis.
    """
    enriched = []
    for p in papers:
        arxiv_id = p.get("arxiv_id", "")
        if not arxiv_id:
            continue
        citation_data = get_citation_data(arxiv_id)
        enriched.append({**p, **citation_data})
        time.sleep(0.5)  # respect Semantic Scholar rate limit

    if not enriched:
        return {"papers": [], "network_summary": {}}

    # Only keep papers where citation data was found
    valid = [p for p in enriched if p.get("citation_count") is not None]
    not_found = len(enriched) - len(valid)

    if not valid:
        return {
            "papers": [],
            "network_summary": {
                "total_papers_analyzed": 0,
                "total_citations_across_results": 0,
                "most_cited_paper": {},
                "insight": (
                    f"No citation data found for these {len(enriched)} papers. "
                    "This usually means the papers are very recent (indexed within last few weeks) "
                    "and Semantic Scholar hasn't processed them yet. Try again in a few days."
                ),
            }
        }

    # Sort by citation count descending
    valid_sorted = sorted(valid, key=lambda x: x.get("citation_count", 0), reverse=True)

    # Assign roles based on citation impact
    for i, p in enumerate(valid_sorted):
        count       = p.get("citation_count", 0)
        influential = p.get("influential_citation_count", 0)
        if i == 0 and count > 50:
            p["role"] = "⭐ Foundational Work"
        elif influential > 10:
            p["role"] = "🔥 Highly Influential"
        elif count > 20:
            p["role"] = "📈 Well Cited"
        elif count < 5:
            p["role"] = "🆕 Emerging Work"
        else:
            p["role"] = "📄 Standard Paper"

    total_citations = sum(p.get("citation_count", 0) for p in valid_sorted)
    most_cited      = valid_sorted[0]
    least_cited     = valid_sorted[-1]

    network_summary = {
        "total_papers_analyzed":           len(valid_sorted),
        "total_citations_across_results":  total_citations,
        "papers_not_found":                not_found,
        "most_cited_paper": {
            "title":     most_cited.get("title", ""),
            "citations": most_cited.get("citation_count", 0),
            "arxiv_id":  most_cited.get("arxiv_id", ""),
        },
        "least_cited_paper": {
            "title":     least_cited.get("title", ""),
            "citations": least_cited.get("citation_count", 0),
            "arxiv_id":  least_cited.get("arxiv_id", ""),
        },
        "insight": _generate_insight(valid_sorted, not_found),
    }

    return {"papers": valid_sorted, "network_summary": network_summary}


def _generate_insight(papers: list[dict], not_found: int = 0) -> str:
    """Generate a plain English insight about the citation network."""
    if not papers:
        return "No citation data available."

    counts = [p.get("citation_count", 0) for p in papers]
    avg    = sum(counts) / len(counts)
    top    = papers[0]

    if avg > 200:
        trend = "This is a highly mature, landmark research area with seminal works."
    elif avg > 50:
        trend = "This is a well-established research area with strong foundational papers."
    elif avg > 10:
        trend = "This is an active research area with solid published work."
    else:
        trend = "This appears to be an emerging or specialized research area."

    insight = (
        f"{trend} The most cited paper is '{top.get('title', 'Unknown')}' "
        f"with {top.get('citation_count', 0):,} citations."
    )

    if not_found > 0:
        insight += f" ({not_found} paper(s) not yet indexed by Semantic Scholar.)"

    return insight