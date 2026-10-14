"""LLM agent demo: an LLM answers engineering questions using ONLY the MCP server's tools.

    export GROQ_API_KEY=gsk_...            # free key: console.groq.com/keys
    # or: export ANTHROPIC_API_KEY=sk-ant-...
    python -m agent.run_agent --demo        # 5 showcase questions -> agent/traces/llm_*.md
    python -m agent.run_agent "How do we deploy the payment service?"

Provider/model: see agent/llm.py (LLM_PROVIDER, GROQ_MODEL, ANTHROPIC_MODEL).
The agent receives only the question. It discovers the tools via MCP list_tools and decides on its
own what to search for, how many results, whether to check the timeline, and when to stop.
"""
import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent.llm import LLM

ROOT = Path(__file__).resolve().parent.parent
MAX_STEPS = 10

SYSTEM = """You are an engineering assistant for a company whose internal knowledge you do not know.
Everything you state must come from the knowledge-base tools; never answer from general knowledge.
- Search first. Refine and search again if results are weak or the question has several parts.
- Sources can be outdated or contradict each other. For questions about the current state, compare
  dates, prefer the newest explicit statement, and mention outdated sources with their dates.
- If the tools do not contain the answer after reasonable attempts, say clearly that the knowledge
  base does not contain it. Do not guess.
- Cite sources as (doc_id, date). Keep the final answer concise."""

DEMO = [
    "How do we deploy the payment service?",
    "Does the payment service currently use Redis?",
    "What happens if Redis goes down?",
    "How do I troubleshoot database connection failures?",
    "Which authentication mechanism does the order service use, and how are tokens signed today?",
]


def _summarise(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return ""
    if "results" in data:
        return f"  answerability={data['answerability']}, top docs: " + \
               ", ".join(f"{r['doc_id']} ({r['date']})" for r in data["results"][:5])
    if "timeline" in data:
        return "  timeline: " + " → ".join(f"{e['date']} {e['doc_id']}" for e in data["timeline"])
    return ""


async def ask(session, llm, question):
    llm.start(question)
    trace, calls, t0 = [f"## {question}\n"], 0, time.time()
    for _ in range(MAX_STEPS):
        try:
            text, tool_calls = llm.step()
        except Exception as e:          # e.g. Groq 'tool_use_failed' on a malformed call: retry once
            trace.append(f"_provider error, retrying: {type(e).__name__}: {str(e)[:160]}_\n")
            try:
                text, tool_calls = llm.step()
            except Exception as e2:
                trace.append(f"### Failed\n\n{type(e2).__name__}: {str(e2)[:300]}\n")
                return "(provider error)", "\n".join(trace), calls
        if not tool_calls:
            trace.append(f"### Final answer\n\n{text}\n")
            trace.append(f"_{calls} tool calls, {time.time() - t0:.1f}s_\n")
            return text, "\n".join(trace), calls
        if text.strip():
            trace.append(f"_reasoning:_ {text.strip()}\n")
        results = []
        for c in tool_calls:
            calls += 1
            try:
                res = await session.call_tool(c.name, c.args)
                out = res.content[0].text if res.content else "{}"
            except Exception as e:
                out = json.dumps({"error": f"{type(e).__name__}: {e}"})
            trace.append(f"**Step {calls} → `{c.name}`** `{json.dumps(c.args)}`")
            s = _summarise(out)
            if s:
                trace.append(s)
            trace.append("")
            results.append((c, out))
        llm.add_tool_results(results)
    return "(step limit reached)", "\n".join(trace), calls


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            llm = LLM(SYSTEM, (await session.list_tools()).tools)
            print(f"Using {llm.name}", file=sys.stderr)
            qs = DEMO if a.demo or not a.question else [a.question]
            out_dir = ROOT / "agent" / "traces"
            out_dir.mkdir(exist_ok=True)
            for q in qs:
                _, trace, _ = await ask(session, llm, q)
                print(trace)
                slug = re.sub(r"[^a-z0-9]+", "_", q.lower())[:60].strip("_")
                (out_dir / f"llm_{slug}.md").write_text(f"Model: {llm.name}\n\n{trace}")


if __name__ == "__main__":
    asyncio.run(main())
