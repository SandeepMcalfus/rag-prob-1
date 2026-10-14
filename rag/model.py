"""Core data model + shared text utilities."""
import re
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Section:
    heading: str              # heading path, e.g. "Payment Service Runbook > Session issues"
    text: str
    meta: dict = field(default_factory=dict)   # e.g. {"time_range": "00:12:03-00:15:40", "speakers": [...]}


@dataclass
class Document:
    doc_id: str
    source_type: str          # pdf | markdown | runbook | faq | transcript | slack
    title: str
    path: str
    date: Optional[str]       # ISO yyyy-mm-dd or None
    date_source: str          # "explicit" (in document) | "inferred" (filename) | "unknown"
    sections: list

    def full_text(self):
        return "\n\n".join(s.text for s in self.sections)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    text: str                 # what gets embedded / BM25-indexed (includes contextual header)
    body: str                 # raw text shown to the agent
    heading: str
    title: str
    source_type: str
    date: Optional[str]
    date_source: str
    services: list
    parent_id: Optional[str] = None   # hierarchical strategy: child -> parent
    position: int = 0

    def to_dict(self):
        return asdict(self)


STOP = set("""a an the and or of to in on for with by is are was were be been it its this that these those at as from
into we our you your i do does did how what which who whom when where why can could should would will shall may might
there their them they he she his her not no yes if then than so such about any all some more most other only own same
too very just also up out over under again once here have has had having am me my us any each few both between through
during before after above below off nor s t don now""".split())

SERVICE_RE = re.compile(r"\b((?:[a-z]+-)+(?:service|pipeline|gateway))\b")
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._/:\-][a-z0-9]+)*")


def tokenize(text):
    """Lowercase tokens. Compound identifiers (payment-service, pay.3ds.enforce, /health/ready)
    are kept whole AND split into parts so both exact and partial matches work in BM25."""
    out = []
    for tok in TOKEN_RE.findall(text.lower()):
        if tok not in STOP:
            out.append(tok)
        if re.search(r"[._/:\-]", tok):
            out.extend(p for p in re.split(r"[._/:\-]+", tok) if p and p not in STOP)
    return out


def services_in(text):
    return sorted(set(SERVICE_RE.findall(text.lower())))


SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9#`\[(])")


def sentences(text):
    return [s.strip() for s in SENT_RE.split(text) if s.strip()]


def word_count(text):
    return len(text.split())
