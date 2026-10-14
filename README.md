# Engineering Knowledge Assistant: RAG + MCP (Problem 1)

An end-to-end RAG system over a messy engineering knowledge base (architecture PDFs, markdown docs, runbooks, FAQ pages, meeting transcripts, Slack exports), exposed through an MCP server so an AI agent can discover answers with no pre-loaded context.

| Deliverable | Where |
|---|---|
| 1. RAG pipeline (raw docs → retrieval-ready index) | `rag/` (`extract.py`, `chunking.py`, `embeddings.py`, `retrieval.py`, `build.py`) |
| 2. MCP server (local, stdio) | `mcp_server/server.py` |
| 3. Evaluation dataset (90 questions, 6 categories) | `eval/questions.json` (built by `scripts/build_questions.py`) |
| 4. Experiment report | `docs/EXPERIMENT_REPORT.md` (raw tables: `docs/results/`) |
| 5. Agent demonstration | `agent/run_agent.py` (LLM) and `agent/scripted_demo.py` (protocol demo); traces in `agent/traces/` |
| 6. Architecture document | `docs/ARCHITECTURE.md` |
| Extra: failures & fixes | `docs/DECISION_LOG.md` |
| Extra: review preparation | `docs/DEFENSE_GUIDE.md` |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# recommended: real neural models (bge-small embeddings + bge-reranker); without these
# the system falls back to offline LSA embeddings and a heuristic reranker
pip install sentence-transformers

make all          # dataset → questions → tests → index → experiments
```

Or step by step:

```bash
python scripts/generate_dataset.py          # 167 docs into data/raw + data/manifest.json
python scripts/build_questions.py           # eval/questions.json
python -m pytest -q tests                   # 10 tests: ground truth, extraction, MCP tools
python -m rag.build --out indexes/default   # build the index the MCP server uses
python -m eval.run_experiments              # E1–E5 → docs/results/tables.md
python -m agent.scripted_demo               # MCP protocol demo, no API key needed
```

## Running the agent demo

The agent works with **Groq** (free API key) or **Anthropic**. Set one key; the provider is detected automatically.

```bash
# Option A: Groq (free) - create a key at https://console.groq.com/keys
export GROQ_API_KEY="gsk_..."
export GROQ_MODEL="llama-3.3-70b-versatile"     # optional; any Groq model listed at console.groq.com/docs/models

# Option B: Anthropic - create a key at https://platform.claude.com (Settings -> API keys)
export ANTHROPIC_API_KEY="sk-ant-..."

python -m agent.run_agent --demo                                   # 5 showcase questions -> agent/traces/llm_*.md
python -m agent.run_agent "Does the payment service currently use Redis?"
python -m eval.answer_eval --limit 30                              # end-to-end answer accuracy (LLM judge)
```

If both keys are set, force one with `export LLM_PROVIDER=groq` (or `anthropic`). Any other OpenAI-compatible endpoint works with `LLM_PROVIDER=openai_compat` plus `OPENAI_BASE_URL`, `OPENAI_API_KEY` and `OPENAI_MODEL`. The agent gets only the question; it discovers the tools through MCP `list_tools` and chooses its own searches. Provider code lives in `agent/llm.py`.

**Groq free tier:** it has per-minute token limits. Tool results are capped at 6,000 characters (`MAX_TOOL_RESULT_CHARS`) and the client retries rate-limited calls automatically; if you still hit limits on `answer_eval`, use `--limit` or wait a minute between runs.

## Using the MCP server with Claude Desktop

Build the index first (`python -m rag.build --out indexes/default`), then add this to `claude_desktop_config.json` (an example file is in the repo root), using absolute paths:

```json
{
  "mcpServers": {
    "engineering-knowledge": {
      "command": "/ABSOLUTE/PATH/eng-rag/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/ABSOLUTE/PATH/eng-rag",
      "env": { "RAG_INDEX_DIR": "/ABSOLUTE/PATH/eng-rag/indexes/default" }
    }
  }
}
```

Restart Claude Desktop and ask "How do we deploy the payment service?". It will call `search_knowledge_base` on its own.

### MCP tools

| Tool | Purpose |
|---|---|
| `search_knowledge_base(query, top_k, source_types, after, before, service)` | hybrid search + rerank; returns chunks with dates, `answerability` and `guidance` |
| `get_topic_timeline(topic)` | statements about a topic ordered by date, to resolve contradictions |
| `get_chunk_context(chunk_id, window)` | neighbouring chunks of a hit |
| `get_document(doc_id)` | full document |
| `list_sources(source_type)` | catalogue with counts and date ranges |

## Using the real dataset instead of the synthetic one

The pipeline reads `data/raw/{pdf,markdown,runbooks,faq,transcripts,slack}/`. Put the provided documents there (or pass `--raw /path`) and rebuild the index. Things to check:

1. **Formats.** Run `python -c "from rag.extract import extract_corpus; ds=extract_corpus('data/raw'); print([(d.doc_id,d.date,len(d.sections)) for d in ds[:20]])"` and inspect a few docs of each type. Transcript turn format (`TURN_RE`) and the Slack export layout are the most likely to need small adjustments.
2. **Dates.** Count documents with `date_source == "unknown"`; add a date pattern in `parse_date` if needed.
3. **Questions.** Write ground truth for the real data in the same JSON format as `eval/questions.json` (see the docstring in `scripts/build_questions.py`), then re-run the experiments.

## Project layout

```
rag/            extraction, chunking, embeddings, index + retrieval, build CLI
mcp_server/     FastMCP server (stdio)
agent/          LLM agent + scripted protocol demo, traces/
eval/           questions.json, run_experiments.py, answer_eval.py
scripts/        facts.py (single source of truth), generate_dataset.py, build_questions.py
tests/          sanity tests
docs/           ARCHITECTURE, EXPERIMENT_REPORT, DECISION_LOG, DEFENSE_GUIDE, results/
data/raw/       generated corpus
```

## Note on the numbers in the report

The committed results were produced with the offline fallbacks (LSA embeddings, heuristic reranker) because the build environment could not download models. After installing `sentence-transformers`, run `python -m eval.run_experiments` again; `docs/results/tables.md` is regenerated automatically. Update the figures quoted in `docs/EXPERIMENT_REPORT.md` if they change.
