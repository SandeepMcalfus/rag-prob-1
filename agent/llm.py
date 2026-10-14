"""Provider-agnostic chat-with-tools client.

Supported providers (pick with LLM_PROVIDER, or auto-detected from which key is set):
  groq       GROQ_API_KEY       model: GROQ_MODEL       (default llama-3.3-70b-versatile)
  anthropic  ANTHROPIC_API_KEY  model: ANTHROPIC_MODEL  (default claude-sonnet-5-5)

Any other OpenAI-compatible endpoint also works with LLM_PROVIDER=openai_compat plus
OPENAI_BASE_URL, OPENAI_API_KEY and OPENAI_MODEL.
"""
import json
import os

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_TOOL_RESULT_CHARS = int(os.environ.get("MAX_TOOL_RESULT_CHARS", "6000"))  # keeps free-tier token limits happy


def detect_provider():
    p = os.environ.get("LLM_PROVIDER")
    if p:
        return p
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    raise SystemExit("No LLM key found. Set GROQ_API_KEY (free at console.groq.com/keys) or ANTHROPIC_API_KEY.")


class ToolCall:
    def __init__(self, id, name, args):
        self.id, self.name, self.args = id, name, args


class LLM:
    """Keeps the conversation in the provider's own format and exposes one loop-friendly API:
         step() -> (text, [ToolCall])      empty tool list = final answer
         add_tool_results([(call, text)])
         complete(prompt) -> str           one-shot, used by the LLM judge"""

    def __init__(self, system, tools):
        self.provider = detect_provider()
        self.system = system
        if self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic()
            self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
            self.tools = [{"name": t.name, "description": t.description, "input_schema": t.inputSchema} for t in tools]
        else:
            from openai import OpenAI
            if self.provider == "groq":
                self.client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url=GROQ_BASE_URL, max_retries=5)
                self.model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
            else:
                self.client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], max_retries=5)
                self.model = os.environ["OPENAI_MODEL"]
            self.tools = [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                            "parameters": t.inputSchema}} for t in tools]
        self.messages = []

    @property
    def name(self):
        return f"{self.provider}:{self.model}"

    def start(self, question):
        self.messages = [{"role": "user", "content": question}]
        if self.provider != "anthropic":
            self.messages.insert(0, {"role": "system", "content": self.system})

    def step(self):
        if self.provider == "anthropic":
            r = self.client.messages.create(model=self.model, max_tokens=2000, system=self.system,
                                            tools=self.tools, messages=self.messages)
            self.messages.append({"role": "assistant", "content": r.content})
            text = "".join(b.text for b in r.content if b.type == "text")
            calls = [ToolCall(b.id, b.name, b.input) for b in r.content if b.type == "tool_use"]
            return text, (calls if r.stop_reason == "tool_use" else [])
        r = self.client.chat.completions.create(model=self.model, messages=self.messages, tools=self.tools,
                                                tool_choice="auto", temperature=0, max_tokens=2000)
        m = r.choices[0].message
        calls = []
        for tc in m.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(tc.id, tc.function.name, {k: v for k, v in args.items() if v is not None}))
        msg = {"role": "assistant", "content": m.content or ""}
        if m.tool_calls:
            msg["tool_calls"] = [{"id": tc.id, "type": "function",
                                  "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                 for tc in m.tool_calls]
        self.messages.append(msg)
        return m.content or "", calls

    def add_tool_results(self, results):
        if self.provider == "anthropic":
            self.messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": c.id, "content": t} for c, t in results]})
        else:
            for c, t in results:
                self.messages.append({"role": "tool", "tool_call_id": c.id, "content": t[:MAX_TOOL_RESULT_CHARS]})

    def complete(self, prompt, max_tokens=300):
        if self.provider == "anthropic":
            r = self.client.messages.create(model=self.model, max_tokens=max_tokens,
                                            messages=[{"role": "user", "content": prompt}])
            return r.content[0].text
        r = self.client.chat.completions.create(model=self.model, temperature=0, max_tokens=max_tokens,
                                                messages=[{"role": "user", "content": prompt}])
        return r.choices[0].message.content or ""
