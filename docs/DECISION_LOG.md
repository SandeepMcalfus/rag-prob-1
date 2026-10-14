# Decision & Failure Log

Running log of what broke during development and how it was fixed. Each entry is a real issue hit while building this system.

## F1 — PDF header stripping deleted the document title
**Symptom:** every architecture PDF came out with `title = <filename>`.
**Cause:** the repeated-header detector removed any line whose text appears on ≥50% of pages. The Confluence export prints the document title in the 8pt running header, so the 18pt title on page 1 matched the header text and was removed.
**Fix:** key repeated-line detection on `(normalised text, rounded font size)`. Headers are small and repeated; the title is large and appears once.
**Lesson:** boilerplate removal needs more than text equality; layout features (font size, position) disambiguate.

## F2 — Stale architecture docs beat newer statements on "current state" questions
**Symptom:** first run of `hybrid_rerank` put the correct up-to-date document above every stale one for only 6/15 temporal questions (CurFirst 0.40); a plain recency boost reached 0.60.
**Cause:** the outdated statement typically lives in a clean, on-topic architecture PDF or FAQ ("Search Service runs on Elasticsearch 7.10"), while the correction lives in a noisy Slack thread or meeting transcript. On relevance alone, the stale doc wins.
**Fix:** for queries with temporal intent ("currently", "now", "still", "today", "anymore"...), rescore the reranked candidates: `relevance × (1 + 1.0·recency + 0.3·[contains change language])`, minus 0.1 for undated chunks. Change language ("stopped", "migrated", "no longer", "decommissioned", "raised") marks a statement that *updates* an earlier state. Multiplicative, so an irrelevant new doc can't jump the queue.
**Result:** CurFirst 0.40 → 0.80 with no regression on other categories. Parameters chosen from the middle of a sweep (see report), not the maximum, to limit overfitting on 15 questions.
**Also:** the MCP server never hides the stale docs. It returns dates and a timeline tool, so the agent can say "the PDF says X (2024-01), but the Feb 2025 meeting says Y".

## F3 — Answerability signal abstained on 37% of answerable questions
**Symptom:** with "best single sentence covers the query" as the confidence signal (threshold 0.5), 14/15 no-answer questions were caught, but 28/75 answerable ones were wrongly flagged.
**Cause:** vocabulary mismatch. "What language is X *written* in?" vs the doc's "implemented in"; requiring one sentence to contain every rare term is far too strict.
**Fix:** compared 5 candidate signals by AUC on answerable vs no-answer questions. Chose idf-weighted coverage of query terms by the union of the top-3 chunks (AUC 0.905 vs 0.856 for the original), threshold 0.30. Terms that do not exist anywhere in the corpus get maximum idf, which is exactly what flags "GPU", "SIEM", "fraud-detection".
**Result:** at 0.30 the system catches 9/15 no-answer questions (60%) and wrongly abstains on 5/75 answerable ones (7%), versus 93% / 37% before. That is a deliberate trade: a false "not found" hides an answer that exists, which costs an engineer more than a weak result list the agent can still judge. The full sweep is in the report (E5).
**Design point:** the score is advisory and surfaced to the agent as `answerability`. Final abstention is the LLM's judgement after reading the evidence.

## F4 — Diagnostic prints would corrupt the MCP stdio transport
**Symptom (caught in review before the first MCP run):** the embedder and reranker printed fallback warnings to stdout.
**Cause:** MCP over stdio uses stdout for JSON-RPC frames; any stray print breaks the client's parser and the server looks "dead".
**Fix:** all library diagnostics go to stderr. Rule: in an MCP server, stdout belongs to the protocol.

## F5 — Hybrid (RRF) ranked *worse* than BM25 alone
**Symptom:** E3 showed BM25 MRR 0.71 but hybrid MRR 0.64, which is unexpected since hybrid is supposed to be the safe default.
**Cause:** Reciprocal Rank Fusion weights both lists equally. With the offline LSA embedder, the dense list is much weaker (MRR 0.59) on this identifier-heavy corpus (service names, ports, job names), so fusion pulls noisy dense hits into the top ranks.
**Fix:** keep hybrid for *recall* (it raises Hit@5 and covers paraphrases BM25 misses) and let the reranker fix *precision*: hybrid + rerank reaches MRR 0.76, and with the temporal stage 0.85. With a stronger dense model (bge-small) the dense list improves and RRF stops hurting; re-run E3 to confirm on your machine.
**Lesson:** hybrid is not automatically better; fusion is only as good as its weakest list, which is why a reranker sits on top.

## F6 — Paraphrase questions are the remaining weak spot (open)
**Symptom:** 4/15 semantic questions miss in the final config: "Nobody can sign in" (doc says "log in"), "too many requests" (doc says "429"), "undo a bad release" (doc says "roll back"), "major outage" (doc says "incident").
**Cause:** zero lexical overlap plus a weak offline embedder. This is exactly what a neural embedding model fixes.
**Mitigations in place:** (1) the MCP agent rephrases when answerability is low (it sees a low score and retries with synonyms); (2) `--embedder st` uses bge-small-en-v1.5 when available.
**Next step if more time:** LLM query rewriting inside `search_knowledge_base` (generate 2–3 paraphrases, fuse results), and a cross-encoder reranker (auto-enabled when sentence-transformers is installed).

## F7 — Fixed-size chunker silently dropped section headings (caught by investigating an anomaly)
**Symptom:** E1 showed naive extraction beating type-aware extraction on semantic questions (0.80 vs 0.67), which contradicted every other result.
**Investigation:** diffed the two runs per question. Both regressions were runbook questions whose answer is signalled mainly by the *section heading* ("Emails or SMS not delivered", "Incident Response Process").
**Cause:** type-aware extraction stores headings as metadata (`Section.heading`). The structure-aware chunker uses them, but the fixed-size chunker concatenated only section *bodies*, so headings vanished. Naive extraction kept the raw "## Heading" lines inline.
**Fix:** fixed-size chunking now writes headings inline before each section body.
**Lesson:** when a result contradicts the overall pattern, diff per question before explaining it. My first hypothesis for this anomaly was wrong.
