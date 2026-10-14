"""Protocol-level demo: a deterministic (non-LLM) agent that talks to the MCP server over stdio.

Proves the server works end-to-end through the real MCP protocol and produces readable traces,
without needing an API key. The LLM-driven agent (run_agent.py) uses the same tools but decides
its own calls.

    python -m agent.scripted_demo
"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = [
    "Does the payment service currently use Redis?",
    "How do we deploy the payment service?",
    "What happens if Redis goes down?",
    "How do I troubleshoot database connection failures?",
    "Which authentication mechanism does the order service use?",
    "What GPU instance type does the recommendation service use?",
]


def short(r, n=220):
    return r["text"].replace("\n", " ")[:n]


async def call(session, trace, name, args):
    res = await session.call_tool(name, args)
    data = json.loads(res.content[0].text)
    trace.append(f"**→ `{name}`** `{json.dumps(args)}`\n")
    return data


async def investigate(session, q):
    trace = [f"## Q: {q}\n", "_Agent receives only the question._\n"]
    s = await call(session, trace, "search_knowledge_base", {"query": q, "top_k": 6})
    a = s["answerability"]
    trace.append(f"answerability = {a['score']} ({a['level']}), temporal_intent = {s['temporal_intent']}\n")
    for r in s["results"][:4]:
        trace.append(f"- #{r['rank']} `{r['doc_id']}` ({r['source_type']}, {r['date']}): {short(r, 160)}")
    for g in s["guidance"]:
        trace.append(f"\n> guidance: {g}")
    trace.append("")
    if a["level"] == "low":
        q2 = " ".join(w for w in q.rstrip("?").split() if len(w) > 3)
        s2 = await call(session, trace, "search_knowledge_base", {"query": q2, "top_k": 10})
        trace.append(f"rephrased answerability = {s2['answerability']['score']}\n")
        if s2["answerability"]["level"] == "low":
            trace.append("**Decision:** evidence does not cover the question's key terms after rephrasing → "
                         "answer *not found in the knowledge base*.\n")
            return "\n".join(trace)
    if s["temporal_intent"]:
        tl = await call(session, trace, "get_topic_timeline", {"topic": q, "max_items": 6})
        for e in tl["timeline"]:
            trace.append(f"- {e['date']} · {e['source_type']} · `{e['doc_id']}`: {e['text'].replace(chr(10), ' ')[:180]}")
        dated = [e for e in tl["timeline"] if e["date"] != "unknown"]
        if dated:
            trace.append(f"\n**Decision:** latest dated evidence is `{dated[-1]['doc_id']}` ({dated[-1]['date']}); "
                         f"older/undated statements are reported as outdated.\n")
    else:
        top = s["results"][0]
        if top["source_type"] in ("slack", "transcript"):
            ctx = await call(session, trace, "get_chunk_context", {"chunk_id": top["chunk_id"], "window": 1})
            trace.append(f"expanded to {len(ctx['chunks'])} neighbouring chunks\n")
        trace.append(f"**Decision:** answer from `{top['doc_id']}` § {top['section']}: {short(top, 300)}\n")
    return "\n".join(trace)


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_server.server"], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            out = ["# Scripted MCP protocol demo\n",
                   "Tools discovered via `list_tools`: " + ", ".join(f"`{t.name}`" for t in tools.tools) + "\n"]
            for q in QUESTIONS:
                out.append(await investigate(session, q))
                out.append("---\n")
    path = ROOT / "agent" / "traces" / "scripted_demo.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(out))
    print(f"wrote {path}")


if __name__ == "__main__":
    asyncio.run(main())
