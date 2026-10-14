"""Chunking strategies (experiment E2).

  fixed        : sliding window over the whole document, ignores structure (baseline)
  structure    : one chunk per logical unit (PDF/markdown section, FAQ Q&A pair, Slack thread,
                 group of transcript turns); long units split on sentence boundaries, tiny ones merged
  semantic     : split where adjacent-sentence embedding similarity drops (topic shift)
  hierarchical : small "child" chunks are indexed for precise matching; the agent receives the
                 enclosing "parent" section for context (small-to-big retrieval)

Every chunk gets a contextual header (title | type | date > heading) prepended to the indexed
text. This puts document-level facts (which service? how old?) into chunks that would otherwise
lose them, e.g. a runbook paragraph that never names its own service.
"""
import numpy as np

from .model import Chunk, sentences, services_in, word_count


def _header(doc, heading):
    date = doc.date or "undated"
    return f"[{doc.title} | {doc.source_type} | {date}] {heading}".strip()


def _mk(doc, idx, body, heading, parent_id=None, suffix=""):
    header = _header(doc, heading)
    return Chunk(chunk_id=f"{doc.doc_id}#{suffix}{idx}", doc_id=doc.doc_id, text=f"{header}\n{body}", body=body,
                 heading=heading, title=doc.title, source_type=doc.source_type, date=doc.date,
                 date_source=doc.date_source, services=services_in(doc.title + " " + body),
                 parent_id=parent_id, position=idx)


def _split_sentences(text, max_words):
    """Greedy pack sentences into pieces of <= max_words."""
    out, cur = [], []
    for s in sentences(text) or [text]:
        if cur and word_count(" ".join(cur + [s])) > max_words:
            out.append(" ".join(cur))
            cur = []
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


# ------------------------------------------------------------------------------ fixed
def chunk_fixed(doc, size=200, overlap=40):
    # keep section headings inline: they carry the topic ("Emails or SMS not delivered")
    words = "\n".join(f"{sec.heading}\n{sec.text}" if sec.heading else sec.text for sec in doc.sections).split()
    chunks, step = [], size - overlap
    for i, start in enumerate(range(0, max(len(words) - overlap, 1), step)):
        chunks.append(_mk(doc, i, " ".join(words[start:start + size]), doc.title))
    return chunks


# ------------------------------------------------------------------------------ structure
def _structure_units(doc, max_words=220, min_words=30):
    units = []
    for s in doc.sections:
        pieces = _split_sentences(s.text, max_words) if word_count(s.text) > max_words else [s.text]
        units.extend((s.heading, p) for p in pieces)
    merged = []
    for h, t in units:   # merge tiny units into the previous one from the same document
        if merged and word_count(t) < min_words and word_count(merged[-1][1]) + word_count(t) <= max_words \
                and doc.source_type not in ("faq",):          # FAQ pairs stay atomic
            ph, pt = merged[-1]
            merged[-1] = (ph if ph == h else f"{ph} / {h.split(' > ')[-1]}", f"{pt}\n{t}")
        else:
            merged.append((h, t))
    return merged


def chunk_structure(doc, max_words=220):
    return [_mk(doc, i, t, h) for i, (h, t) in enumerate(_structure_units(doc, max_words))]


# ------------------------------------------------------------------------------ semantic
def chunk_semantic(doc, embedder, max_words=220, min_words=40, pct=25):
    sents = [s for sec in doc.sections for s in sentences(sec.text)]
    if len(sents) < 3:
        return [_mk(doc, 0, " ".join(sents), doc.title)]
    E = embedder.encode_docs(sents)
    sims = np.sum(E[1:] * E[:-1], axis=1)
    thr = np.percentile(sims, pct)
    chunks, cur = [], [sents[0]]
    for s, sim in zip(sents[1:], sims):
        n = word_count(" ".join(cur))
        if (sim < thr and n >= min_words) or n + word_count(s) > max_words:
            chunks.append(" ".join(cur))
            cur = []
        cur.append(s)
    chunks.append(" ".join(cur))
    return [_mk(doc, i, t, doc.title) for i, t in enumerate(chunks)]


# ------------------------------------------------------------------------------ hierarchical
def chunk_hierarchical(doc, parent_words=400, child_words=60):
    """Returns (children, parents). Children are indexed; parents are returned to the caller."""
    parents, children = [], []
    for pi, (h, t) in enumerate(_structure_units(doc, max_words=parent_words)):
        parent = _mk(doc, pi, t, h, suffix="p")
        parents.append(parent)
        for ci, piece in enumerate(_split_sentences(t, child_words)):
            children.append(_mk(doc, ci, piece, h, parent_id=parent.chunk_id, suffix=f"p{pi}c"))
    return children, parents


def chunk_corpus(docs, strategy, embedder=None):
    """Returns (indexed_chunks, parents_by_id)."""
    chunks, parents = [], {}
    for d in docs:
        if strategy == "fixed":
            chunks += chunk_fixed(d)
        elif strategy == "structure":
            chunks += chunk_structure(d)
        elif strategy == "semantic":
            chunks += chunk_semantic(d, embedder)
        elif strategy == "hierarchical":
            c, p = chunk_hierarchical(d)
            chunks += c
            parents.update({x.chunk_id: x for x in p})
        else:
            raise ValueError(strategy)
    return chunks, parents
