"""Bounded web search and text analysis; no credentials are stored here."""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse


class ResearchTools:
    def __init__(self, client, max_searches=4):
        self.client = client
        self.max_searches = max_searches
        self.search_count = 0
        self.sources = {}
        self.warnings = []

    def search(self, query: str) -> dict:
        """Search public web pages and return evidence with stable source IDs."""
        if self.search_count >= self.max_searches:
            return {"error": "Search budget reached. Use the evidence already retrieved."}
        self.search_count += 1
        try:
            response = self.client.search(
                query=query, max_results=5, search_depth="basic",
                include_raw_content=True, include_answer=False, timeout=30,
            )
        except Exception:
            # Avoid putting provider exceptions (which may contain credentials) into reports.
            self.warnings.append("A web search failed; evidence may be incomplete.")
            return {"error": "Web search failed. Retry within the remaining search budget."}
        results = []
        for item in response.get("results", []):
            url = item.get("url", "")
            if urlparse(url).scheme not in {"http", "https"}:
                continue
            if url not in self.sources:
                sid = f"S{len(self.sources) + 1}"
                self.sources[url] = {
                    "id": sid, "title": item.get("title") or url,
                    "url": url,
                    "text": (item.get("raw_content") or item.get("content") or "")[:6000],
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }
            results.append(self.sources[url])
        return {"query": query, "sources": results}


def analyze_text(text: str) -> dict:
    """Count words, sentences and frequent terms; this does not verify factual claims."""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    stop = {"the", "and", "that", "this", "with", "from", "have", "for", "are", "was"}
    counts = {}
    for word in words:
        if len(word) > 3 and word not in stop:
            counts[word] = counts.get(word, 0) + 1
    return {
        "word_count": len(words),
        "sentence_count": len([s for s in re.split(r"[.!?]+", text) if s.strip()]),
        "frequent_terms": sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:10],
    }


def citation_warnings(report: str, sources: list) -> list:
    """Check citation IDs only, not whether a source supports a claim."""
    known = {s["id"] for s in sources}
    used = set(re.findall(r"\[(S\d+)\]", report))
    warnings = []
    if not used:
        warnings.append("The generated report contains no inline source citations.")
    unknown = sorted(used - known)
    if unknown:
        warnings.append("Unrecognized citation IDs: " + ", ".join(unknown))
    return warnings
