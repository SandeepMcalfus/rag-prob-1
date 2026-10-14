# Defense Guide

Likely review questions with answers grounded in this project's code and results. Each answer cites where the evidence lives. Do not memorise these; run the commands and look at the outputs yourself until you can say them in your own words.

---

## 1. Why did you choose each strategy?

**Extraction: type-aware parsers.**
Each source type has different noise, and one generic parser would keep all of it. E1 shows the payoff: sparse-fact Hit@5 goes from 0.60 (naive) to 0.87 (type-aware), because Slack threads are grouped and filler is removed. Type-aware extraction also recovers dates, which the temporal stage needs: CurFirst is 0.47 naive vs 0.73 aware with the full pipeline.
*Evidence:* `rag/extract.py`, E1 in the report.

**Chunking: structure-aware, with a contextual header.**
Chunks follow the author's units (section, Q&A pair, Slack thread, group of transcript turns). The header `[title | type | date] heading` puts the service name and date into every chunk. Strategies were close in E2. I chose structure because it was best on conflicting information (CurFirst 0.80 vs 0.73 for fixed), gives one-section citations, and never mixes an old and a new statement in a single window.
*Be honest:* fixed-size was nearly tied once I fixed a bug (F7). On longer real documents I expect structure to win by more, but that needs checking.

**Retrieval: hybrid → rerank → temporal.**
- BM25 is the best single retriever because questions are identifier-heavy (MRR 0.71).
- Dense covers paraphrases BM25 misses.
- RRF fuses ranks without score calibration.
- The reranker fixes the precision that fusion lost (MRR 0.64 → 0.76).
- The temporal stage fixes conflicting information (CurFirst 0.40 → 0.80).

**Vector store: in-memory numpy.**
With 621 chunks, exact cosine search takes milliseconds. A vector database adds a service to run with no benefit at this scale. The `Index` class is the swap point if the corpus grows.

## 2. How did you validate your approach?

- **Ground truth comes from one facts table** (`scripts/facts.py`) that generates both the documents and the answers, so the two cannot drift apart.
- **Tests validate the evaluation itself** (`tests/test_pipeline.py`). Every relevant doc exists, every answer keyword is actually in its relevant doc, and every "current" doc is newer than its "stale" docs. A broken question would silently distort every metric.
- **Two levels of metrics.**
  - Retrieval metrics: Hit@5, MRR, nDCG, plus Evid@5, which checks that the answer *text* was retrieved, not just the right file.
  - End-to-end answer grading: `eval/answer_eval.py`, where an LLM judge explicitly penalises outdated values presented as current.
- **Controlled experiments.** Only one factor changes per experiment: E1 changes extraction, E2 chunking, E3 retrieval.
- **Anomalies are investigated per question.** The E1 anomaly led to bug F7.
- **Noise awareness.** One question is worth 0.067 per category. I don't claim differences smaller than that.

## 3. What failed and how did you fix it?

See `docs/DECISION_LOG.md`. The three best stories:

1. **F2, stale docs won on current-state questions.** Recency alone was not enough, because clean outdated PDFs beat noisy new Slack messages on relevance. Adding change-language detection ("stopped", "migrated", "no longer") fixed it: 0.40 → 0.80.
2. **F5, hybrid was worse than BM25.** RRF with a weak dense list hurts ranking. The lesson is that hybrid is for recall and the reranker is for precision.
3. **F7, the chunker dropped headings.** Naive extraction beat type-aware on semantic questions, which made no sense. A per-question diff showed the fixed chunker was discarding section headings. My first explanation had been wrong.

## 4. What are the trade-offs in your design?

| Decision | Gain | Cost |
|---|---|---|
| Abstain threshold 0.30 | only 7% of real questions wrongly flagged | catches only 60% of no-answer questions (0.50 would catch 93% but flag 21%) |
| Temporal re-ranking only on temporal-intent queries | no regression elsewhere | misses implicit current-state questions; mitigated by the timeline tool |
| Return evidence, not answers, from MCP | every claim is traceable and the agent reasons over it | more tokens and more tool calls for the agent |
| Keep stale docs, don't delete them | historical questions still work; the agent can explain conflicts | the agent must do the conflict reasoning |
| Offline fallbacks (LSA, heuristic reranker) | runs anywhere with zero downloads | weaker on paraphrases (semantic Hit@5 0.73) |
| Structure-aware vs hierarchical | half the chunks, simpler | hierarchical slightly better on sparse facts (1.00 vs 0.93) |

## 5. How would you debug a bad answer?

Work down the stack and stop at the first layer that is wrong:

1. **Agent trace.** What did the agent search for? Did it ignore the guidance or skip the timeline? (`agent/traces/`)
2. **Retrieval.** Run the same query directly:
   `python -c "from mcp_server import server as s; import json; print(json.dumps(s.search_knowledge_base('...'), indent=1))"`.
   Is the right doc in the top 10? If yes but ranked low, it's a ranking problem: check the BM25-only and dense-only ranks to see which list missed it.
3. **Chunk.** Find the chunk that should match. Is the fact split across two chunks, or is the header missing?
4. **Extraction.** Run `extract_aware(path, type)` on the source file. Was the text lost, garbled, or misdated?
5. **Source.** Is the document itself wrong or outdated? Then the system is behaving correctly, and the fix is in the content.

Then add the failing question to `eval/questions.json` so it becomes a regression test.

## 6. Questions you might get, with short answers

- **"Why not just use an LLM to resolve conflicts at index time?"** It would be expensive, and it would hide its reasoning. Deciding at query time with dates visible is auditable, and the right answer can depend on the question ("what did we use *before*?").
- **"Why is the semantic score lowest?"** Questions with zero word overlap ("sign in" vs "log in") plus offline embeddings. The fix is neural embeddings, then query rewriting. Agent rephrasing already helps in practice.
- **"Your dataset is synthetic. Does this prove anything?"** It proves the pipeline handles the stated failure modes in a controlled way, with exact ground truth. The real dataset is the next validation step, and the README lists what to check.
- **"How does the agent know when to stop?"** When answerability is high and the evidence addresses every part of the question. If answerability is still low after 1–2 rephrasings, it reports that the answer isn't in the knowledge base. This behaviour is stated in the tool descriptions and the system prompt.
- **"How would this scale to 10× or 100× the documents?"** Swap in an ANN index (LanceDB or Qdrant), build incrementally per document (doc_ids are stable), cache embeddings, and run the cross-encoder only on the top 30. The extraction and chunking code is already per-document.
