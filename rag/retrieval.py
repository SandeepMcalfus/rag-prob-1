"""Index + retrieval (experiment E3).

Methods:
  bm25                    lexical (Okapi BM25)
  dense                   cosine similarity over embeddings
  hybrid                  Reciprocal Rank Fusion of bm25 + dense (k=60)
  hybrid_rerank           hybrid candidates (top 30) re-scored by a reranker
  hybrid_rerank_temporal  + recency-aware re-scoring when the query has temporal intent
"""
import math
import pickle
import re
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from .model import sentences, tokenize

METHODS = ["bm25", "dense", "hybrid", "hybrid_rerank", "hybrid_rerank_temporal"]
TEMPORAL_RE = re.compile(r"\b(current(ly)?|now|today|still|latest|anymore|nowadays|these days|at the moment|presently|"
                         r"recent(ly)?|stopped|used to|always|when did|no longer|change[ds]?)\b", re.I)
CHANGE_RE = re.compile(r"\b(no longer|stopped|moved|switched|migrat\w+|now|raised|bumped|decommissioned|disabled|"
                       r"replaced|deprecated|completed|done)\b", re.I)
QUERY_NOISE = {"currently", "current", "today", "still", "latest", "anymore", "use", "uses", "used", "using",
               "service", "run", "runs", "running", "tell", "know", "get", "happens", "happen"}


def has_temporal_intent(q):
    return bool(TEMPORAL_RE.search(q))


def _ord(d):
    return date.fromisoformat(d).toordinal() if d else None


class Index:
    def __init__(self, chunks, parents, embedder, config):
        self.chunks, self.parents, self.embedder, self.config = chunks, parents, embedder, config
        t = time.time()
        self.tokens = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.tokens)
        self.token_sets = [set(x) for x in self.tokens]
        self.emb = embedder.encode_docs([c.text for c in chunks])
        self.max_idf = max(self.bm25.idf.values())
        ords = [_ord(c.date) for c in chunks if c.date]
        self.date_lo, self.date_hi = (min(ords), max(ords)) if ords else (0, 1)
        self.build_seconds = time.time() - t

    def idf(self, term):
        return self.bm25.idf.get(term, self.max_idf)   # unseen term = maximally informative

    def save(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "index.pkl", "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(Path(path) / "index.pkl", "rb") as f:
            return pickle.load(f)


# ---------------------------------------------------------------------------- rerankers
class HeuristicReranker:
    """Offline fallback reranker (no model download). Scores how well the chunk *answers* the query:
    idf-weighted query-term coverage of the whole chunk, of its single best sentence (answers are
    usually stated in one sentence) and of its heading, blended with the fused retrieval prior."""
    name = "heuristic"

    def __init__(self, index):
        self.ix = index

    def coverage(self, qterms, toks):
        tot = sum(self.ix.idf(t) for t in qterms) or 1.0
        return sum(self.ix.idf(t) for t in qterms if t in toks) / tot

    def best_sentence(self, qterms, text):
        return max((self.coverage(qterms, set(tokenize(s))) for s in sentences(text) or [text]), default=0.0)

    def score(self, query, cands, priors):
        qterms = [t for t in dict.fromkeys(tokenize(query)) if t not in QUERY_NOISE]
        out = []
        pmax = max(priors) or 1
        for i, p in zip(cands, priors):
            c = self.ix.chunks[i]
            s = (0.35 * self.coverage(qterms, self.ix.token_sets[i]) + 0.35 * self.best_sentence(qterms, c.body)
                 + 0.10 * self.coverage(qterms, set(tokenize(c.heading + " " + c.title))) + 0.20 * p / pmax)
            out.append(s)
        return out


class CrossEncoderReranker:
    name = "cross-encoder"

    def __init__(self, model="BAAI/bge-reranker-base"):
        from sentence_transformers import CrossEncoder
        self.model, self.name = CrossEncoder(model), f"cross-encoder:{model}"

    def score(self, query, cands, priors):
        pairs = [(query, self.ix.chunks[i].text) for i in cands]
        return [float(1 / (1 + math.exp(-s))) for s in self.model.predict(pairs)]


def make_reranker(index, kind="auto"):
    if kind in ("auto", "cross-encoder"):
        try:
            r = CrossEncoderReranker()
            r.ix = index
            return r
        except Exception as e:
            if kind == "cross-encoder":
                raise
            print(f"[rerank] cross-encoder unavailable ({type(e).__name__}); using heuristic reranker", file=sys.stderr)
    return HeuristicReranker(index)


# ---------------------------------------------------------------------------- retriever
class Retriever:
    def __init__(self, index, reranker="auto", rrf_k=60, n_candidates=50, n_rerank=30):
        self.ix, self.rrf_k, self.n_cand, self.n_rerank = index, rrf_k, n_candidates, n_rerank
        self.reranker = make_reranker(index, reranker)
        self.heur = self.reranker if isinstance(self.reranker, HeuristicReranker) else HeuristicReranker(index)

    # -- filters -----------------------------------------------------------------
    def _mask(self, source_types=None, after=None, before=None, service=None):
        n = len(self.ix.chunks)
        m = np.ones(n, dtype=bool)
        for i, c in enumerate(self.ix.chunks):
            if source_types and c.source_type not in source_types:
                m[i] = False
            elif after and (not c.date or c.date < after):
                m[i] = False
            elif before and (not c.date or c.date > before):
                m[i] = False
            elif service and service not in c.services and service not in c.text.lower():
                m[i] = False
        return m

    def _rank(self, scores, mask, n):
        s = np.where(mask, scores, -np.inf)
        idx = np.argsort(-s)[:n]
        return [int(i) for i in idx if np.isfinite(s[i])]

    def bm25_scores(self, q):
        return np.asarray(self.ix.bm25.get_scores(tokenize(q)))

    def dense_scores(self, q):
        return self.ix.emb @ self.ix.embedder.encode_query(q)

    # -- main entry ----------------------------------------------------------------
    def search(self, query, method="hybrid_rerank_temporal", k=8, **filters):
        mask = self._mask(**filters)
        if method == "bm25":
            b = self.bm25_scores(query)
            scored = [(i, float(b[i])) for i in self._rank(b, mask, self.n_cand)]
        elif method == "dense":
            d = self.dense_scores(query)
            scored = [(i, float(d[i])) for i in self._rank(d, mask, self.n_cand)]
        else:
            rb = self._rank(self.bm25_scores(query), mask, self.n_cand)
            rd = self._rank(self.dense_scores(query), mask, self.n_cand)
            fused = {}
            for lst in (rb, rd):
                for r, i in enumerate(lst):
                    fused[i] = fused.get(i, 0.0) + 1.0 / (self.rrf_k + r + 1)
            scored = sorted(fused.items(), key=lambda x: -x[1])
            if method.startswith("hybrid_rerank"):
                cands = [i for i, _ in scored[:self.n_rerank]]
                priors = [s for _, s in scored[:self.n_rerank]]
                new = self.reranker.score(query, cands, priors)
                scored = sorted(zip(cands, new), key=lambda x: -x[1])
                if method == "hybrid_rerank_temporal" and has_temporal_intent(query):
                    scored = self._temporal(scored)
        hits = self._collapse(scored)[:k]
        return hits, self.confidence(query, hits)

    # -- temporal re-scoring ---------------------------------------------------------
    def _temporal(self, scored, weight=1.0, change_boost=0.3, undated_penalty=0.1):
        """For 'current state' questions: among relevant candidates, prefer newer evidence and
        explicit change statements ("we stopped...", "moved to...", "is decommissioned").
        Multiplicative, so recency only reorders chunks that are already relevant; undated chunks
        get a small penalty because their freshness cannot be verified."""
        if not scored:
            return scored
        vals = [s for _, s in scored]
        lo, hi = min(vals), max(vals)
        span = (self.ix.date_hi - self.ix.date_lo) or 1
        out = []
        for i, s in scored:
            c = self.ix.chunks[i]
            rel = (s - lo) / ((hi - lo) or 1)
            d = _ord(c.date)
            rec = (d - self.ix.date_lo) / span if d else 0.0
            chg = change_boost if CHANGE_RE.search(c.body) else 0.0
            out.append((i, rel * (1 + weight * rec + chg) - (undated_penalty if d is None else 0)))
        return sorted(out, key=lambda x: -x[1])

    # -- hierarchical: return parents --------------------------------------------------
    def _collapse(self, scored):
        hits, seen = [], set()
        for rank, (i, s) in enumerate(scored):
            c = self.ix.chunks[i]
            if c.parent_id:
                if c.parent_id in seen:
                    continue
                seen.add(c.parent_id)
                p = self.ix.parents[c.parent_id]
                hits.append(dict(chunk=p, matched_child=c.body, score=s, index=i))
            else:
                hits.append(dict(chunk=c, score=s, index=i))
        return hits

    # -- answerability -----------------------------------------------------------------
    def confidence(self, query, hits, top=3):
        """Answerability signal in [0,1]: idf-weighted share of the query's content terms that appear
        in the top-3 retrieved chunks. Terms absent from the whole corpus get the maximum idf, so a
        question about something we have no documents on ("GPU", "SIEM", "fraud-detection") scores low.
        Advisory only: the agent makes the final call, the number tells it how hard to look."""
        qterms = [t for t in dict.fromkeys(tokenize(query)) if t not in QUERY_NOISE]
        if not qterms or not hits:
            return 0.0
        toks = set().union(*[set(tokenize(h["chunk"].text)) for h in hits[:top]])
        return round(self.heur.coverage(qterms, toks), 3)
