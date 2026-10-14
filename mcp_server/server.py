"""Engineering Knowledge MCP server.

Run (stdio, for Claude Desktop / any MCP client):
    python -m mcp_server.server
Env:
    RAG_INDEX_DIR   index directory (default: indexes/default; built on first run if missing)
    RAG_RAW_DIR     raw corpus directory (default: data/raw)

Tool design: the agent gets NO context, only these tools. They are shaped around the decisions
an agent has to make: what to search for and how narrowly (search_knowledge_base filters),
whether sources disagree over time (get_topic_timeline), whether a hit needs more context
(get_chunk_context / get_document), and whether the answer exists at all (answerability).
"""
import os
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.build import build  # noqa: E402
from rag.retrieval import Index, Retriever, has_temporal_intent  # noqa: E402

INDEX_DIR = Path(os.environ.get("RAG_INDEX_DIR", ROOT / "indexes" / "default"))
RAW_DIR = os.environ.get("RAG_RAW_DIR", str(ROOT / "data" / "raw"))
ANSWERABILITY_LOW = 0.30
MAX_TEXT = 1500

mcp = FastMCP("engineering-knowledge")
_state = {}


def retriever() -> Retriever:
    if "r" not in _state:
        if (INDEX_DIR / "index.pkl").exists():
            ix = Index.load(INDEX_DIR)
        else:
            print(f"[mcp] building index at {INDEX_DIR}", file=sys.stderr)
            ix = build(RAW_DIR, "aware", "structure")
            ix.save(INDEX_DIR)
        _state["r"] = Retriever(ix)
    return _state["r"]


def _hit(rank, h):
    c = h["chunk"]
    out = {"rank": rank, "chunk_id": c.chunk_id, "doc_id": c.doc_id, "title": c.title, "source_type": c.source_type,
           "date": c.date or "unknown", "date_source": c.date_source, "section": c.heading,
           "score": round(float(h["score"]), 4), "text": c.body[:MAX_TEXT]}
    if not c.date:
        out["freshness_warning"] = "Undated source: cannot verify it is still current."
    return out


def _label(conf):
    return "high" if conf >= 0.6 else "medium" if conf >= ANSWERABILITY_LOW else "low"


@mcp.tool()
def search_knowledge_base(query: str, top_k: int = 6, source_types: Optional[list[str]] = None,
                          after: Optional[str] = None, before: Optional[str] = None,
                          service: Optional[str] = None) -> dict:
    """Search the engineering knowledge base (architecture PDFs, markdown docs, runbooks, FAQ pages,
    meeting transcripts, Slack threads) with hybrid keyword + semantic retrieval and reranking.

    Every result carries its source type and date. Sources can disagree or be outdated: when a
    question is about the CURRENT state ("does X still...", "what do we use now"), compare dates and
    prefer the newest explicit statement; call get_topic_timeline to see how a fact changed.

    Args:
        query: natural-language question or keywords. Use specific identifiers when you know them
               (service names like payment-service, error messages, job names).
        top_k: results to return (1-15). Use 3-5 for a lookup, 8-12 for broad or multi-part questions.
        source_types: optional filter, any of: pdf, markdown, runbook, faq, transcript, slack.
               e.g. ["runbook"] for procedures, ["slack", "transcript"] for recent decisions.
        after / before: optional ISO dates (YYYY-MM-DD) to restrict to dated sources in a window.
        service: optional service name filter, e.g. "payment-service".

    Returns results plus `answerability` (how well the query's specific terms are covered by the top
    evidence). Low answerability after 1-2 rephrasings usually means the knowledge base does not
    contain the answer: say so rather than guessing.
    """
    r = retriever()
    top_k = max(1, min(int(top_k), 15))
    hits, conf = r.search(query, k=top_k, source_types=source_types, after=after, before=before, service=service)
    dates = sorted(h["chunk"].date for h in hits if h["chunk"].date)
    guidance = []
    if conf < ANSWERABILITY_LOW:
        guidance.append("Low answerability: the specific terms of this question barely appear in the evidence. "
                        "Rephrase once or twice (synonyms, service names); if still low, report that the knowledge "
                        "base does not contain the answer.")
    temporal = has_temporal_intent(query)
    if temporal:
        guidance.append("Current-state question detected: results are re-ranked to favour newer, explicitly dated "
                        "statements and statements describing a change. Verify with get_topic_timeline and cite dates.")
    if any(not h["chunk"].date for h in hits):
        guidance.append("Some results are undated (often runbooks); treat them as possibly stale if a dated source disagrees.")
    if len(dates) > 1 and dates[0][:7] != dates[-1][:7]:
        guidance.append(f"Evidence spans {dates[0]} to {dates[-1]}.")
    return {"query": query, "answerability": {"score": conf, "level": _label(conf)}, "temporal_intent": temporal,
            "results": [_hit(i + 1, h) for i, h in enumerate(hits)], "guidance": guidance}


@mcp.tool()
def get_topic_timeline(topic: str, max_items: int = 8) -> dict:
    """Show how statements about a topic evolved over time, oldest first, undated sources last.

    Use this to resolve contradictions ("does payment still use Redis?", "which broker does
    notification use now?"): later explicit decisions (meetings, Slack announcements, migration
    notes) usually supersede older architecture docs. Each entry has the date, source and text.
    """
    r = retriever()
    hits, conf = r.search(topic, method="hybrid_rerank", k=max(4, min(int(max_items) * 2, 20)))
    if not hits:
        return {"topic": topic, "timeline": []}
    best = hits[0]["score"]
    keep = [h for h in hits if h["score"] >= 0.6 * best][:max_items]   # only clearly relevant evidence
    keep.sort(key=lambda h: (h["chunk"].date is None, h["chunk"].date or ""))
    tl = [{"date": h["chunk"].date or "unknown", "source_type": h["chunk"].source_type, "doc_id": h["chunk"].doc_id,
           "title": h["chunk"].title, "chunk_id": h["chunk"].chunk_id, "text": h["chunk"].body[:900]} for h in keep]
    return {"topic": topic, "answerability": {"score": conf, "level": _label(conf)}, "timeline": tl,
            "how_to_read": "Oldest first. The latest dated statement that addresses the topic is the best evidence "
                           "of current state; mention older conflicting sources and their dates in the answer."}


@mcp.tool()
def get_chunk_context(chunk_id: str, window: int = 1) -> dict:
    """Expand a search hit: returns the neighbouring chunks of the same document (window before/after).
    Use when a hit is cut off, refers to "the above", or is a Slack reply / transcript turn that needs
    the surrounding conversation."""
    r = retriever()
    ix = r.ix
    pool = list(ix.parents.values()) if ix.parents and chunk_id in ix.parents else ix.chunks
    by_doc = [c for c in pool if c.doc_id == chunk_id.split("#")[0]]
    pos = next((i for i, c in enumerate(by_doc) if c.chunk_id == chunk_id), None)
    if pos is None:
        return {"error": f"unknown chunk_id {chunk_id}"}
    lo, hi = max(0, pos - window), min(len(by_doc), pos + window + 1)
    return {"doc_id": by_doc[pos].doc_id, "title": by_doc[pos].title, "date": by_doc[pos].date or "unknown",
            "chunks": [{"chunk_id": c.chunk_id, "section": c.heading, "is_requested": c.chunk_id == chunk_id,
                        "text": c.body} for c in by_doc[lo:hi]]}


@mcp.tool()
def get_document(doc_id: str, max_chars: int = 8000) -> dict:
    """Return a whole document (all sections in order) by doc_id. Use for short docs such as a runbook
    or FAQ page when you need the full procedure, not for long transcripts."""
    ix = retriever().ix
    pool = list(ix.parents.values()) if ix.parents else ix.chunks
    cs = [c for c in pool if c.doc_id == doc_id]
    if not cs:
        return {"error": f"unknown doc_id {doc_id}"}
    seen, parts = set(), []
    for c in cs:
        if c.body not in seen:
            seen.add(c.body)
            parts.append(f"## {c.heading}\n{c.body}")
    text = "\n\n".join(parts)
    return {"doc_id": doc_id, "title": cs[0].title, "source_type": cs[0].source_type, "date": cs[0].date or "unknown",
            "truncated": len(text) > max_chars, "text": text[:max_chars]}


@mcp.tool()
def list_sources(source_type: Optional[str] = None, limit: int = 50) -> dict:
    """Catalog of the knowledge base: document counts and date ranges per source type, plus a list of
    documents (doc_id, title, date). Use to orient yourself or to find a specific runbook/FAQ by name."""
    ix = retriever().ix
    docs = {}
    for c in ix.chunks:
        docs.setdefault(c.doc_id, (c.title, c.source_type, c.date))
    summary = {}
    for t, st, d in docs.values():
        s = summary.setdefault(st, {"documents": 0, "earliest": None, "latest": None, "undated": 0})
        s["documents"] += 1
        if d:
            s["earliest"] = min(filter(None, [s["earliest"], d]))
            s["latest"] = max(filter(None, [s["latest"], d]))
        else:
            s["undated"] += 1
    listing = [{"doc_id": k, "title": t, "source_type": st, "date": d or "unknown"}
               for k, (t, st, d) in sorted(docs.items()) if not source_type or st == source_type]
    return {"summary": summary, "documents": listing[:limit], "total_matching": len(listing)}


def main():
    retriever()        # load index before accepting requests
    mcp.run()


if __name__ == "__main__":
    main()
