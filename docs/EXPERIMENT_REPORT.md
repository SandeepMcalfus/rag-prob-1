# Experiment Report: Engineering Knowledge Assistant

**Setup.** 167 documents (14 PDF, 30 markdown, 16 runbooks, 4 FAQ pages, 30 meeting transcripts, 73 Slack channel-days), with 10 planted temporal conflicts and 15 facts that appear exactly once. 90 test questions, 15 per category. All numbers are produced by `python -m eval.run_experiments`; full per-category tables for every configuration are in [`results/tables.md`](results/tables.md) and raw per-question rows in `results/results.json`.

**Important caveat on models.** These runs used the offline fallbacks: LSA embeddings (TF-IDF + SVD, 256-d) and the feature-based reranker, because the build environment could not download models. With `sentence-transformers` installed, the same command uses `bge-small-en-v1.5` and `bge-reranker-base`. The *design comparisons* below are valid as relative comparisons; absolute numbers, especially for dense retrieval and the semantic category, should be refreshed on the final setup.

**Metrics.** Hit@5 = fraction of required evidence covered by the top-5 documents · MRR / nDCG@10 = ranking quality · Evid@5 = answer keywords present in top-5 chunk text · CurFirst = for temporal questions, the up-to-date document ranks above every outdated one (and in the top 5) · Abstain = no-answer questions correctly flagged · False abstain = answerable questions wrongly flagged. With 15 questions per category, one question = 0.067, so differences under ~0.07 are noise.

---

## E1: Extraction (naive dump vs type-aware)

Chunking held constant (fixed-size), so only extraction varies. Rows 1–2 use plain hybrid retrieval; rows 3–4 use the full pipeline, which can exploit dates.

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| naive/fixed/hybrid | 1.00 | 0.80 | 0.20 | 0.90 | 0.60 | 0.67 | 0.85 | 0.60 | 0.67 | 0.84 | 0.11 | 3.0 |
| aware/fixed/hybrid | 1.00 | 0.73 | 0.20 | 0.87 | 0.87 | 0.67 | 0.89 | 0.67 | 0.73 | 0.87 | 0.09 | 2.4 |
| naive/fixed/hybrid_rerank_temporal | 1.00 | 0.80 | 0.47 | 0.93 | 0.87 | 0.67 | 0.92 | 0.76 | 0.80 | 0.91 | 0.07 | 9.2 |
| aware/fixed/hybrid_rerank_temporal | 1.00 | 0.73 | 0.73 | 0.97 | 0.93 | 0.67 | 0.93 | 0.83 | 0.85 | 0.93 | 0.05 | 8.0 |

**Findings.**
- **Sparse facts benefit most from clean extraction: Hit@5 0.60 → 0.87.** Sparse facts live in Slack threads and transcripts. Naive extraction keeps user IDs, emoji codes, "+1"/"ack" noise and splits threads across windows; type-aware extraction groups threads, resolves names and drops filler, so the one sentence that matters is not diluted.
- **Dates are only valuable if extraction recovers them.** With the full pipeline, CurFirst is 0.47 for naive vs **0.73** for type-aware. Naive extraction has no dates, so only the change-language signal works; type-aware adds recency.
- Ranking quality improves throughout: MRR 0.60 → 0.67 (hybrid) and 0.76 → 0.83 (full pipeline).
- Semantic Hit@5 is one question lower for type-aware (0.73 vs 0.80). It was originally two questions; investigating it exposed a real bug (the fixed chunker dropped section headings, decision log F7). The remaining one-question gap is within noise.

## E2: Chunking strategy

Type-aware extraction, plain hybrid retrieval.

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/fixed/hybrid | 1.00 | 0.73 | 0.20 | 0.87 | 0.87 | 0.67 | 0.89 | 0.67 | 0.73 | 0.87 | 0.09 | 2.3 |
| aware/structure/hybrid | 1.00 | 0.73 | 0.13 | 0.90 | 0.87 | 0.60 | 0.89 | 0.64 | 0.71 | 0.79 | 0.09 | 2.3 |
| aware/semantic/hybrid | 1.00 | 0.67 | 0.13 | 0.90 | 0.87 | 0.53 | 0.87 | 0.64 | 0.70 | 0.77 | 0.20 | 2.3 |
| aware/hierarchical/hybrid | 1.00 | 0.73 | 0.20 | 0.93 | 0.87 | 0.60 | 0.89 | 0.68 | 0.73 | 0.85 | 0.09 | 2.5 |

**Findings.**
- With plain hybrid retrieval, **chunking choice moves overall Hit@5 by only ±0.02** (0.87–0.89). Most sections in this corpus are short, so all strategies produce similar units.
- **Fixed-size is surprisingly competitive once headings are kept** (MRR 0.67, Evid@5 0.87). Larger windows simply contain more of the answer text.
- **Semantic chunking was worst** (Hit@5 0.87, Evid@5 0.77, false abstain 0.20). Sentence-level similarity from LSA embeddings is noisy, so boundaries land in odd places. It also costs an embedding call per sentence at index time.
- **Hierarchical has the best MRR (0.68).** Matching on small children is more precise, while returning the parent keeps context.

**Full-pipeline comparison (fixed vs structure, both with rerank + temporal):** fixed reaches Hit@5 0.93, MRR 0.83, CurFirst 0.73, Evid@5 0.93; structure reaches Hit@5 0.93, MRR **0.85**, CurFirst **0.80**, Evid@5 0.87. These are essentially tied.

**Why we still default to structure-aware:** (1) it is better on the hardest category, conflicting information, because a fixed window can straddle two sections and mix an old and a new statement in one chunk; (2) each result maps to exactly one section, so citations are clean and the agent can quote a heading; (3) the advantage of structure grows with document length, and the real dataset's PDFs will be longer than the synthetic ones. This should be re-checked on the real data.

## E3: Retrieval method

Type-aware extraction, structure-aware chunks.

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/structure/bm25 | 1.00 | 0.80 | 0.13 | 0.87 | 0.93 | 0.60 | 0.88 | 0.71 | 0.75 | 0.81 | 0.05 | 0.8 |
| aware/structure/dense | 1.00 | 0.53 | 0.13 | 0.93 | 0.87 | 0.60 | 0.85 | 0.59 | 0.66 | 0.73 | 0.17 | 1.5 |
| aware/structure/hybrid | 1.00 | 0.73 | 0.13 | 0.90 | 0.87 | 0.60 | 0.89 | 0.64 | 0.71 | 0.79 | 0.09 | 2.2 |
| aware/structure/hybrid_rerank | 1.00 | 0.73 | 0.40 | 0.97 | 0.93 | 0.60 | 0.93 | 0.76 | 0.80 | 0.84 | 0.07 | 4.5 |
| aware/structure/hybrid_rerank_temporal | 1.00 | 0.73 | 0.80 | 0.97 | 0.93 | 0.60 | 0.93 | 0.85 | 0.86 | 0.87 | 0.07 | 4.7 |

**Findings.**
- **BM25 is the strongest single retriever here (MRR 0.71 vs dense 0.59).** Engineering questions are identifier-heavy (service names, ports, job names, flags), and the tokenizer keeps identifiers intact.
- **Dense helps exactly where BM25 cannot**, on paraphrases with no shared words, but the offline LSA embedder is weak, which is why dense alone has the lowest semantic score.
- **Naive hybrid (RRF) ranked worse than BM25 (MRR 0.64 vs 0.71).** Equal-weight fusion with a weak dense list pulls noisy hits up. This was a key learning (decision log F5): hybrid is used for *recall*, and the reranker restores *precision*.
- **Reranking is the largest single gain:** MRR 0.64 → 0.76, Hit@5 0.89 → 0.93, multi-doc 0.90 → 0.97.
- **The temporal stage fixes conflicting-information questions: CurFirst 0.40 → 0.80**, with no regression in any other category (it only activates on temporal intent), and overall MRR rises to 0.85.
- Latency stays under 5 ms p50 for the full pipeline with the heuristic reranker. A cross-encoder will add roughly 50–150 ms on CPU for 30 pairs, still well within an interactive agent loop.

## E4: Full pipeline on hierarchical chunks

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/hierarchical/hybrid | 1.00 | 0.73 | 0.20 | 0.93 | 0.87 | 0.60 | 0.89 | 0.68 | 0.73 | 0.85 | 0.09 | 2.6 |
| aware/hierarchical/hybrid_rerank | 1.00 | 0.73 | 0.40 | 0.93 | 1.00 | 0.60 | 0.93 | 0.76 | 0.80 | 0.87 | 0.07 | 4.1 |
| aware/hierarchical/hybrid_rerank_temporal | 1.00 | 0.73 | 0.80 | 0.93 | 1.00 | 0.60 | 0.93 | 0.84 | 0.85 | 0.90 | 0.07 | 4.3 |

**Findings.** With reranking and temporal handling, hierarchical and structure-aware chunks perform the same within noise (Hit@5 0.93 both, MRR 0.84 vs 0.85). Hierarchical is slightly better on sparse facts (1.00 vs 0.93) and Evid@5 (0.90 vs 0.87); structure-aware is slightly better on multi-doc (0.97 vs 0.93). **We keep structure-aware as the default** for its simpler index (621 vs 1039 chunks) and one-section-per-citation results; hierarchical is a one-flag switch.

## E5: Abstention threshold (no-answer questions)

| Threshold | No-answer correctly abstained | Answerable wrongly abstained | Accuracy (all 90) |
|---|---|---|---|
| 0.10 | 0.20 | 0.00 | 0.87 |
| 0.20 | 0.40 | 0.03 | 0.88 |
| 0.25 | 0.53 | 0.04 | 0.89 |
| 0.30 (used) | 0.60 | 0.07 | 0.88 |
| 0.35 | 0.73 | 0.12 | 0.86 |
| 0.40 | 0.80 | 0.15 | 0.84 |
| 0.50 | 0.93 | 0.21 | 0.81 |
| 0.60 | 0.93 | 0.36 | 0.69 |

**Findings.** The answerability signal separates answerable from unanswerable questions with AUC ≈ 0.90, but no threshold is perfect. **We chose 0.30:** it catches 60% of no-answer questions while wrongly flagging only 7% of answerable ones. Raising it to 0.50 catches 93% but flags 21% of real questions. Our reasoning is that a false "not found" hides an answer that exists, which costs an engineer more than an extra weak result. The signal is advisory: the LLM agent reads the evidence and makes the final call, so end-to-end abstention should be higher than this retrieval-only number (measure it with `eval/answer_eval.py`).

The hardest no-answer questions are **near-misses**, where every word exists in the corpus but the fact does not: "What is the database connection pool size for the *shipping* service?" (pool sizes exist, but only for inventory). Term-coverage signals cannot catch these; the agent must notice that the evidence is about a different service.

---

## Final configuration and per-category results

`aware` extraction · `structure` chunking · `hybrid` (BM25 + dense, RRF) → rerank → temporal stage.

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.88 | 0.91 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.63 | 0.66 | 0.60 | – | – | 0.27 |
| temporal | 15 | 1.00 | 0.86 | 0.89 | 1.00 | 0.80 | – | 0.00 |
| multi_doc | 15 | 0.97 | 1.00 | 0.92 | 0.80 | – | – | 0.00 |
| sparse | 15 | 0.93 | 0.88 | 0.91 | 0.93 | – | – | 0.00 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.93 | 0.85 | 0.86 | 0.87 | 0.80 | 0.60 | 0.07 |

## What failed and what is still weak

1. **Paraphrase questions (semantic Hit@5 0.73).** Four misses, all with zero word overlap between question and document: "sign in" vs "log in", "too many requests" vs "429", "undo a release" vs "roll back", "major outage" vs "incident". Fixes, in order of cost: neural embeddings (installed → automatic), agent rephrasing (already prompted by low answerability), LLM query expansion in the search tool.
2. **Temporal: 3/15 still not current-first.** Two of the three are about token signing, where the stale FAQ is a perfect Q&A match ("How are access tokens signed?") and outranks the newer Slack announcement even after rescoring. In these cases the new statement still appears in the top 5, and `get_topic_timeline` shows both in date order, so the agent can still answer correctly. See the agent traces.
3. **Near-miss no-answer questions** (see E5).
4. **Evaluation size.** 15 questions per category is enough to see large effects (reranking, temporal stage, extraction on sparse data) but not to separate configurations within ±0.07. Parameters (temporal weights, abstain threshold) were chosen from the middle of sweeps, not at their maxima, to limit overfitting to this set.

## How to reproduce

```bash
python scripts/generate_dataset.py      # corpus + manifest
python scripts/build_questions.py       # 90 questions
python -m pytest -q tests               # validates ground truth + extraction + MCP tools
python -m eval.run_experiments          # E1–E5, writes docs/results/
python -m eval.answer_eval --limit 30   # optional, needs ANTHROPIC_API_KEY
```
