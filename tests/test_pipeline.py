"""Sanity tests: ground truth is valid, extraction removes noise, MCP tools respond.
    python -m pytest -q tests
"""
import json
from pathlib import Path

import pytest

from rag.extract import extract_corpus, extract_pdf, extract_slack, extract_transcript
from rag.model import tokenize

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
QS = json.loads((ROOT / "eval" / "questions.json").read_text())


@pytest.fixture(scope="module")
def corpus():
    return {d.doc_id: d.full_text().lower() for d in extract_corpus(RAW, "aware")}


def test_question_counts():
    assert len(QS) == 90
    for c in ["direct", "semantic", "temporal", "multi_doc", "sparse", "no_answer"]:
        assert sum(q["category"] == c for q in QS) == 15


def test_every_relevant_doc_exists(corpus):
    for q in QS:
        for g in q["relevant"]:
            for d in g:
                assert d in corpus, (q["id"], d)


def test_answer_keywords_are_in_relevant_docs(corpus):
    """Each keyword group must be findable in at least one relevant doc, otherwise the
    Evid@5 metric could never be satisfied and the question is broken."""
    for q in QS:
        rel_text = " ".join(corpus[d] for g in q["relevant"] for d in g)
        for kw in q["keywords"]:
            assert any(k in rel_text for k in kw), (q["id"], kw)


def test_no_answer_questions_have_unique_terms_missing(corpus):
    """Every no-answer question must contain at least one content word absent from the corpus OR be a
    known near-miss (all words present, fact absent) - we just make sure none is accidentally answerable
    by an exact phrase."""
    all_text = " ".join(corpus.values())
    for q in [q for q in QS if q["category"] == "no_answer"]:
        assert q["question"].lower().rstrip("?") not in all_text


def test_temporal_current_doc_is_newest(corpus):
    from rag.extract import extract_corpus as ec
    dates = {d.doc_id: d.date for d in ec(RAW, "aware")}
    for q in [q for q in QS if q["category"] == "temporal"]:
        cur = dates[q["current"]]
        for s in q["stale"]:
            assert dates[s] is None or dates[s] < cur, (q["id"], s)


def test_pdf_noise_removed():
    d = extract_pdf(RAW / "pdf" / "arch_payment-service.pdf")
    txt = d.full_text()
    assert d.title == "Payment Service Architecture" and d.date == "2024-01-15"
    assert "INTERNAL - DO NOT DISTRIBUTE" not in txt and "Page 1" not in txt and "......" not in txt


def test_transcript_date_formats():
    for p in (RAW / "transcripts").glob("*.txt"):
        assert extract_transcript(p).date is not None, p.name


def test_slack_threads_keep_parent_context():
    d = extract_slack(RAW / "slack" / "engagement" / "2024-09-17.json")
    sec = next(s for s in d.sections if "notifications.v2" in s.text)
    assert "↳" in sec.text and "<@" not in sec.text      # reply shown under its parent, mentions resolved


def test_tokenizer_keeps_identifiers():
    t = tokenize("sync payment-service-prod and pay.3ds.enforce at /health/ready")
    assert "payment-service-prod" in t and "payment" in t and "pay.3ds.enforce" in t and "ready" in t


def test_mcp_tools_direct_call():
    from mcp_server import server
    r = server.search_knowledge_base("Does the payment service currently use Redis?", top_k=3)
    assert r["temporal_intent"] and r["results"][0]["doc_id"] == "transcript_payments_arch_sync_2025-02-12"
    tl = server.get_topic_timeline("payment service Redis sessions")
    dated = [e["date"] for e in tl["timeline"] if e["date"] != "unknown"]
    assert dated == sorted(dated)
    assert server.search_knowledge_base("Which vendor provides our SIEM?")["answerability"]["level"] == "low"
    assert "text" in server.get_document("runbook_redis_outage")
    assert server.list_sources()["summary"]["slack"]["documents"] > 50
