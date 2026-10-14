"""Run all experiments and write docs/results/{results.json, tables.md}.

    python -m eval.run_experiments            # all experiments
    python -m eval.run_experiments --only E3  # one experiment

Metrics (doc-level unless noted):
  Hit@5        fraction of required evidence groups with >=1 relevant doc in the top-5 documents
  MRR          1 / rank of the first relevant document (top-10)
  nDCG@10      binary relevance over all relevant docs
  Evid@5       fraction of answer-keyword groups present in the top-5 retrieved chunk texts
               (checks the *answer text* was retrieved, not just the right file)
  CurFirst     temporal only: the doc holding the up-to-date statement ranks above every stale doc
  Abstain      no_answer only: confidence < threshold (system correctly says "not found")
  FalseAbst    answerable questions wrongly abstained on
"""
import argparse
import json
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path

from rag.build import build
from rag.embeddings import Embedder
from rag.retrieval import Retriever

ROOT = Path(__file__).resolve().parent.parent
CATS = ["direct", "semantic", "temporal", "multi_doc", "sparse", "no_answer"]
ABSTAIN_THRESHOLD = 0.30


def doc_ranking(hits):
    out = []
    for h in hits:
        if h["chunk"].doc_id not in out:
            out.append(h["chunk"].doc_id)
    return out


def score_question(q, hits, conf):
    docs = doc_ranking(hits)
    m = {"conf": conf, "abstain": conf < ABSTAIN_THRESHOLD}
    if q["category"] == "no_answer":
        return m
    top5 = docs[:5]
    m["hit5"] = sum(any(d in top5 for d in g) for g in q["relevant"]) / len(q["relevant"])
    rel = {d for g in q["relevant"] for d in g}
    m["mrr"] = next((1 / (r + 1) for r, d in enumerate(docs[:10]) if d in rel), 0.0)
    dcg = sum(1 / math.log2(r + 2) for r, d in enumerate(docs[:10]) if d in rel)
    idcg = sum(1 / math.log2(r + 2) for r in range(min(len(rel), 10)))
    m["ndcg10"] = dcg / idcg
    text = " ".join(h["chunk"].body.lower() for h in hits[:5])
    m["evid5"] = sum(any(k in text for k in g) for g in q["keywords"]) / len(q["keywords"])
    if q["category"] == "temporal":
        rank = {d: r for r, d in enumerate(docs)}
        cur = rank.get(q["current"], math.inf)
        m["cur_first"] = float(cur < min([rank.get(s, math.inf) for s in q["stale"]] + [math.inf]) and cur < 5)
    return m


def evaluate(retriever, questions, method, k=10):
    rows, lat = [], []
    for q in questions:
        t = time.perf_counter()
        hits, conf = retriever.search(q["question"], method=method, k=k)
        lat.append((time.perf_counter() - t) * 1000)
        rows.append({"id": q["id"], "category": q["category"], **score_question(q, hits, conf),
                     "top_docs": doc_ranking(hits)[:5]})
    return summarize(rows, lat), rows


def summarize(rows, lat):
    s = {}
    for cat in CATS + ["overall"]:
        rs = [r for r in rows if cat == "overall" or r["category"] == cat]
        ans = [r for r in rs if r["category"] != "no_answer"]
        d = {"n": len(rs)}
        for k in ("hit5", "mrr", "ndcg10", "evid5"):
            if ans:
                d[k] = round(statistics.mean(r[k] for r in ans), 3)
        if cat in ("temporal", "overall"):
            t = [r["cur_first"] for r in rs if "cur_first" in r]
            if t:
                d["cur_first"] = round(statistics.mean(t), 3)
        na = [r for r in rs if r["category"] == "no_answer"]
        if na:
            d["abstain"] = round(statistics.mean(r["abstain"] for r in na), 3)
        if ans:
            d["false_abstain"] = round(statistics.mean(r["abstain"] for r in ans), 3)
        s[cat] = d
    s["latency_ms_p50"] = round(statistics.median(lat), 1)
    s["latency_ms_p95"] = round(sorted(lat)[int(len(lat) * .95) - 1], 1)
    return s


EXPERIMENTS = {
    "E1": ("Extraction strategy (chunking=fixed; retrieval=hybrid, then full pipeline)",
           [("naive", "fixed", "hybrid"), ("aware", "fixed", "hybrid"),
            ("naive", "fixed", "hybrid_rerank_temporal"), ("aware", "fixed", "hybrid_rerank_temporal")]),
    "E2": ("Chunking strategy (extraction=aware, retrieval=hybrid)",
           [("aware", c, "hybrid") for c in ("fixed", "structure", "semantic", "hierarchical")]),
    "E3": ("Retrieval method (extraction=aware, chunking=structure)",
           [("aware", "structure", m) for m in ("bm25", "dense", "hybrid", "hybrid_rerank", "hybrid_rerank_temporal")]),
    "E4": ("Retrieval method on hierarchical chunks (extraction=aware, chunking=hierarchical)",
           [("aware", "hierarchical", m) for m in ("hybrid", "hybrid_rerank", "hybrid_rerank_temporal")]),
}


def table(title, results):
    lines = [f"### {title}", "",
             "| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, s in results:
        lines.append(f"| {name} | {s['direct']['hit5']:.2f} | {s['semantic']['hit5']:.2f} | {s['temporal']['cur_first']:.2f} | "
                     f"{s['multi_doc']['hit5']:.2f} | {s['sparse']['hit5']:.2f} | {s['no_answer']['abstain']:.2f} | "
                     f"{s['overall']['hit5']:.2f} | {s['overall']['mrr']:.2f} | {s['overall']['ndcg10']:.2f} | "
                     f"{s['overall']['evid5']:.2f} | {s['overall']['false_abstain']:.2f} | {s['latency_ms_p50']} |")
    return "\n".join(lines) + "\n"


def detail_table(name, s):
    lines = [f"#### {name} — per category", "", "| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in CATS + ["overall"]:
        d = s[c]
        g = lambda k: f"{d[k]:.2f}" if k in d else "–"
        lines.append(f"| {c} | {d['n']} | {g('hit5')} | {g('mrr')} | {g('ndcg10')} | {g('evid5')} | {g('cur_first')} | {g('abstain')} | {g('false_abstain')} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--embedder", default="auto")
    ap.add_argument("--reranker", default="auto")
    a = ap.parse_args()
    questions = json.loads((ROOT / "eval" / "questions.json").read_text())
    out_dir = ROOT / "docs" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    all_res, md, cache = {}, ["# Experiment results (auto-generated)\n"], {}
    emb_probe = Embedder(a.embedder)
    md.append(f"Embedder: `{emb_probe.name}` · Abstain threshold: {ABSTAIN_THRESHOLD} · {len(questions)} questions\n")
    for ename, (title, configs) in EXPERIMENTS.items():
        if a.only and ename not in a.only:
            continue
        res = []
        for ext, ch, method in configs:
            key = (ext, ch)
            if key not in cache:
                ix = build(extraction=ext, chunking=ch, embedder=a.embedder)
                cache[key] = (ix, Retriever(ix, reranker=a.reranker))
            ix, r = cache[key]
            name = f"{ext}/{ch}/{method}"
            s, rows = evaluate(r, questions, method)
            s["config"] = {**ix.config, "method": method, "reranker": r.reranker.name}
            all_res[f"{ename}:{name}"] = {"summary": s, "rows": rows}
            res.append((name, s))
            print(f"{ename} {name:45s} overall hit5={s['overall']['hit5']:.3f} mrr={s['overall']['mrr']:.3f} "
                  f"temporal={s['temporal']['cur_first']:.2f} abstain={s['no_answer']['abstain']:.2f} chunks={ix.config['n_chunks']}")
        md.append(table(f"{ename}: {title}", res))
        for name, s in res:
            md.append(detail_table(name, s))
    # E5: abstention threshold sweep on the final configuration
    final = all_res.get("E3:aware/structure/hybrid_rerank_temporal")
    if final:
        md.append("### E5: Abstention threshold sweep (aware/structure/hybrid_rerank_temporal)\n")
        md.append("| Threshold | No-answer correctly abstained | Answerable wrongly abstained | Accuracy (all 90) |")
        md.append("|---|---|---|---|")
        rows = final["rows"]
        for t in (0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6):
            na = [r for r in rows if r["category"] == "no_answer"]
            an = [r for r in rows if r["category"] != "no_answer"]
            tp = statistics.mean(r["conf"] < t for r in na)
            fp = statistics.mean(r["conf"] < t for r in an)
            acc = statistics.mean((r["conf"] < t) == (r["category"] == "no_answer") for r in rows)
            md.append(f"| {t:.2f}{' (used)' if t == ABSTAIN_THRESHOLD else ''} | {tp:.2f} | {fp:.2f} | {acc:.2f} |")
        md.append("")
    (out_dir / "results.json").write_text(json.dumps(all_res, indent=1, default=str))
    (out_dir / "tables.md").write_text("\n".join(md))
    print(f"wrote {out_dir}/tables.md")


if __name__ == "__main__":
    main()
