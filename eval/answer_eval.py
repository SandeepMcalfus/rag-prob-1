"""End-to-end answer evaluation (optional, needs GROQ_API_KEY or ANTHROPIC_API_KEY).

Runs the MCP agent on every question and grades the final answer against ground truth with an
LLM judge. Complements the retrieval metrics in run_experiments.py, which measure whether the
right evidence was retrieved; this measures whether the agent turned it into a correct answer.

    python -m eval.answer_eval --limit 30     # quick sample
    python -m eval.answer_eval                # all 90 (writes docs/results/answer_eval.json)
"""
import argparse
import asyncio
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent.llm import LLM
from agent.run_agent import SYSTEM, ask

ROOT = Path(__file__).resolve().parent.parent
JUDGE = """You grade answers from an engineering assistant.
Question: {q}
Ground truth: {gt}
Assistant answer: {a}

Grade:
- "correct": states the ground-truth facts (wording may differ). For current-state questions it must give the
  CURRENT value, not an outdated one. For "Not in the knowledge base" ground truth, correct means the assistant
  clearly says it could not find the answer.
- "partial": some required facts present, others missing; or correct but also asserts an outdated value as current.
- "incorrect": wrong, outdated, or hallucinated (including answering a question whose ground truth is "not in KB").
Reply with JSON only: {{"grade": "correct|partial|incorrect", "reason": "<one sentence>"}}"""


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    qs = json.loads((ROOT / "eval" / "questions.json").read_text())
    if a.limit:  # stratified sample
        by = defaultdict(list)
        for q in qs:
            by[q["category"]].append(q)
        qs = [q for c in by.values() for q in c[: max(1, a.limit // len(by))]]
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"], cwd=str(ROOT))
    rows = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            llm = LLM(SYSTEM, listed.tools)
            for q in qs:
                ans, _, calls = await ask(session, llm, q["question"])
                txt = llm.complete(JUDGE.format(q=q["question"], gt=q["answer"], a=ans))
                txt = txt.strip().strip("`").removeprefix("json").strip()
                txt = txt[txt.find("{"):txt.rfind("}") + 1] if "{" in txt else txt
                try:
                    g = json.loads(txt)
                except json.JSONDecodeError:
                    g = {"grade": "incorrect", "reason": "unparseable judge output: " + txt[:80]}
                rows.append({**{k: q[k] for k in ("id", "category", "question")}, "answer": ans, "tool_calls": calls, **g})
                print(f"{q['id']:8s} {g['grade']:9s} calls={calls} {q['question'][:60]}")
    score = {"correct": 1, "partial": 0.5, "incorrect": 0}
    summary = {c: {"n": len(rs), "accuracy": round(statistics.mean(score[r["grade"]] for r in rs), 3),
                   "avg_tool_calls": round(statistics.mean(r["tool_calls"] for r in rs), 1)}
               for c in sorted({r["category"] for r in rows}) for rs in [[r for r in rows if r["category"] == c]]}
    summary["overall"] = {"n": len(rows), "accuracy": round(statistics.mean(score[r["grade"]] for r in rows), 3)}
    out = ROOT / "docs" / "results" / "answer_eval.json"
    out.write_text(json.dumps({"model": llm.name, "summary": summary, "rows": rows}, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
