"""Document extraction.

Two strategies, compared in experiment E1:
  naive : dump all text, no structure, no dates (the "just read the file" baseline)
  aware : per-type parsers that remove noise, keep structure and recover dates
"""
import json
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import pymupdf

from .model import Document, Section, word_count

TYPE_BY_DIR = {"pdf": "pdf", "markdown": "markdown", "runbooks": "runbook", "faq": "faq",
               "transcripts": "transcript", "slack": "slack"}
ISO_RE = re.compile(r"\b(20\d\d-[01]\d-[0-3]\d)\b")


def doc_id_for(path: Path, source_type: str):
    if source_type == "slack":
        return f"slack_{path.parent.name}_{path.stem}"
    return path.stem


def discover(raw_dir):
    raw_dir = Path(raw_dir)
    for sub, stype in TYPE_BY_DIR.items():
        for p in sorted((raw_dir / sub).rglob("*")):
            if p.is_file() and p.name != "users.json":
                yield p, stype


def parse_date(text):
    """Accepts 2025-02-12, '12 Feb 2025', 'February 12, 2025'."""
    m = ISO_RE.search(text)
    if m:
        return m.group(1)
    for fmt, rx in [("%d %b %Y", r"\b(\d{1,2} [A-Z][a-z]{2} 20\d\d)\b"), ("%B %d, %Y", r"\b([A-Z][a-z]+ \d{1,2}, 20\d\d)\b")]:
        m = re.search(rx, text)
        if m:
            try:
                return datetime.strptime(m.group(1), fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
    return None


# =============================================================================== NAIVE
def extract_naive(path: Path, stype: str) -> Document:
    if stype == "pdf":
        text = "\n".join(page.get_text() for page in pymupdf.open(path))
    elif stype == "faq":
        text = re.sub(r"<[^>]+>", " ", path.read_text())
    elif stype == "slack":
        text = "\n".join(f"{m.get('user')}: {m.get('text', '')}" for m in json.loads(path.read_text()))
    else:
        text = path.read_text()
    return Document(doc_id_for(path, stype), stype, path.stem, str(path), None, "unknown", [Section("", text)])


# =============================================================================== AWARE: PDF
PAGE_NUM_RE = re.compile(r"^\s*(page\s*)?\d+(\s*(of|/)\s*\d+)?\s*$", re.I)
TOC_RE = re.compile(r"\.{5,}\s*\d+\s*$")


def _pdf_lines(doc):
    pages = []
    for page in doc:
        lines = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if spans:
                    lines.append(("".join(s["text"] for s in spans).strip(), max(s["size"] for s in spans)))
        pages.append(lines)
    return pages


def extract_pdf(path: Path) -> Document:
    pages = _pdf_lines(pymupdf.open(path))
    # 1. repeated header/footer lines: same text (digits normalised) on >= 50% of pages
    norm = lambda t: re.sub(r"\d+", "#", t.lower())
    # keyed on (text, font size): a header that repeats the title in 8pt must not delete the 18pt title
    counts = Counter(k for lines in pages for k in {(norm(t), round(sz)) for t, sz in lines})
    repeated = {k for k, c in counts.items() if len(pages) > 1 and c >= max(2, len(pages) / 2)}
    sizes = [sz for lines in pages for _, sz in lines]
    body = statistics.median(sizes) if sizes else 10
    title, date, sections, cur_head, buf = None, None, [], "Preamble", []

    def flush():
        txt = " ".join(buf)
        txt = re.sub(r"(\w)- (\w)", r"\1-\2", txt)     # rejoin words hyphen-wrapped across lines
        if txt.strip():
            sections.append(Section(cur_head, txt.strip()))

    for pi, lines in enumerate(pages):
        for text, size in lines:
            if (norm(text), round(size)) in repeated or PAGE_NUM_RE.match(text) or TOC_RE.search(text) \
                    or text.lower() == "table of contents":
                continue
            if pi == 0 and title is None and size >= body * 1.5:
                title = text
                continue
            if date is None and re.search(r"document date", text, re.I):
                date = parse_date(text)
                continue
            if size >= body * 1.15:          # heading by font size
                flush()
                buf = []
                cur_head = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
                continue
            buf.append(text)
    flush()
    sections = [s for s in sections if s.heading != "Preamble" or word_count(s.text) > 5]
    return Document(path.stem, "pdf", title or path.stem, str(path), date, "explicit" if date else "unknown", sections)


# =============================================================================== AWARE: Markdown / runbooks
def _front_matter(text):
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            text = text[end + 4:]
    return meta, text


def _clean_md(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def extract_markdown(path: Path, stype: str) -> Document:
    meta, text = _front_matter(path.read_text())
    title = meta.get("title")
    stack, sections, buf = [], [], []

    def flush():
        body = _clean_md("\n".join(buf))
        if body:
            sections.append(Section(" > ".join(stack) or (title or path.stem), body))

    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush()
            buf = []
            level, head = len(m.group(1)), m.group(2).strip()
            if level == 1 and not title:
                title = head
            stack = stack[:level - 1] + [head]
            continue
        buf.append(line)
    flush()
    date = None
    for k in ("last_updated", "date", "updated"):
        if meta.get(k):
            date = parse_date(meta[k])
            break
    return Document(path.stem, stype, title or path.stem, str(path), date, "explicit" if date else "unknown", sections)


# =============================================================================== AWARE: FAQ HTML
class _FaqParser(HTMLParser):
    SKIP = {"script", "style", "footer", "nav"}

    def __init__(self):
        super().__init__()
        self.title, self.date, self.qas, self.skip, self.cur, self.tag = None, None, [], 0, None, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name") in ("last-updated", "date"):
            self.date = parse_date(a.get("content", ""))
        if self.skip or tag in self.SKIP or a.get("class") == "nav":
            self.skip += 1                     # depth inside a boilerplate element
        self.tag = tag

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1

    def handle_data(self, data):
        data = data.strip()
        if not data or self.skip:
            return
        if self.tag == "title" and not self.title:
            self.title = data
        elif self.tag == "h3":
            self.qas.append([data, ""])
        elif self.tag == "p" and self.qas:
            self.qas[-1][1] += " " + data


def extract_faq(path: Path) -> Document:
    p = _FaqParser()
    p.feed(path.read_text())
    secs = [Section(f"{p.title} > Q: {q}", f"Q: {q}\nA: {a.strip()}") for q, a in p.qas]
    return Document(path.stem, "faq", p.title or path.stem, str(path), p.date, "explicit" if p.date else "unknown", secs)


# =============================================================================== AWARE: transcripts
TURN_RE = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\s+([^:]+):\s*(.*)$")
DISFLUENCY = re.compile(r"\b(um+|uh+|erm|you know|i mean)\b,?\s*|\[crosstalk\]\s*", re.I)
SMALL_TALK = re.compile(r"^(okay|ok|yeah|right|sorry|thanks|makes sense|nothing from my side|can everyone hear me|"
                        r"let's take that offline|let me check|i'll share my screen|can you put that in the notes)", re.I)


def extract_transcript(path: Path, turns_per_section=8) -> Document:
    lines = path.read_text().splitlines()
    head = "\n".join(lines[:5])
    title = (re.search(r"^Meeting:\s*(.+)$", head, re.M) or [None, path.stem])[1]
    date = parse_date(head)
    turns = []
    for line in lines:
        m = TURN_RE.match(line)
        if not m:
            continue
        ts, spk, txt = m.groups()
        txt = DISFLUENCY.sub("", txt).strip()
        txt = txt[:1].upper() + txt[1:]
        # drop pure small talk; keep anything with substance
        if word_count(txt) < 4 or (SMALL_TALK.match(txt) and word_count(txt) < 9):
            continue
        turns.append((ts, spk.strip(), txt))
    secs = []
    for i in range(0, len(turns), turns_per_section):
        grp = turns[i:i + turns_per_section]
        body = "\n".join(f"{spk}: {txt}" for _, spk, txt in grp)
        secs.append(Section(f"{title} [{grp[0][0]}-{grp[-1][0]}]", body,
                            {"time_range": f"{grp[0][0]}-{grp[-1][0]}", "speakers": sorted({g[1] for g in grp})}))
    return Document(path.stem, "transcript", f"{title} ({date or 'undated'})", str(path), date,
                    "explicit" if date else "unknown", secs)


# =============================================================================== AWARE: Slack
_USERS = {}
LOW_SIGNAL = re.compile(r"^(\+1|ack|done|thanks!?|lgtm.*|ok merged|taking a look|:[a-z_+-]+:)$", re.I)


def _users(raw_root):
    if not _USERS:
        f = raw_root / "slack" / "users.json"
        if f.exists():
            _USERS.update({u["id"]: u["real_name"] for u in json.loads(f.read_text())})
    return _USERS


def extract_slack(path: Path) -> Document:
    users = _users(path.parent.parent.parent)
    channel = path.parent.name
    msgs = json.loads(path.read_text())
    threads, order = {}, []
    for m in msgs:
        key = m.get("thread_ts") or m["ts"]
        if key not in threads:
            threads[key] = []
            order.append(key)
        threads[key].append(m)

    def render(m):
        t = re.sub(r"<@(U\d+)>", lambda x: "@" + users.get(x.group(1), x.group(1)), m.get("text", ""))
        t = re.sub(r":[a-z0-9_+-]+:", "", t).strip()
        return t

    secs = []
    for key in order:
        thread = threads[key]
        parent = render(thread[0])
        replies = [(users.get(m["user"], m["user"]), render(m)) for m in thread[1:]]
        replies = [(u, t) for u, t in replies if t and not LOW_SIGNAL.match(t)]
        if not replies and (LOW_SIGNAL.match(parent) or word_count(parent) < 4):
            continue                                    # context-free noise
        when = datetime.fromtimestamp(float(key), tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        # Every thread section repeats its parent message so replies like "yeah that's the one" keep context.
        body = f"{users.get(thread[0]['user'], '?')}: {parent}" + "".join(f"\n  ↳ {u}: {t}" for u, t in replies)
        secs.append(Section(f"#{channel} thread {when} UTC", body, {"thread_ts": key}))
    date = parse_date(path.stem)
    return Document(f"slack_{channel}_{path.stem}", "slack", f"#{channel} {path.stem}", str(path), date,
                    "explicit" if date else "unknown", secs)


# =============================================================================== entry points
def extract_aware(path: Path, stype: str) -> Document:
    if stype == "pdf":
        d = extract_pdf(path)
    elif stype in ("markdown", "runbook"):
        d = extract_markdown(path, stype)
    elif stype == "faq":
        d = extract_faq(path)
    elif stype == "transcript":
        d = extract_transcript(path)
    else:
        d = extract_slack(path)
    if d.date is None:                               # last resort: date in the filename
        fd = parse_date(path.stem)
        if fd:
            d.date, d.date_source = fd, "inferred"
    return d


def extract_corpus(raw_dir, strategy="aware"):
    fn = extract_aware if strategy == "aware" else extract_naive
    return [fn(p, t) for p, t in discover(raw_dir)]
