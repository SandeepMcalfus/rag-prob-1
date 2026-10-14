"""Build an index:  python -m rag.build --extraction aware --chunking structure --out indexes/default"""
import argparse
import time

from .chunking import chunk_corpus
from .embeddings import Embedder
from .extract import extract_corpus
from .model import sentences
from .retrieval import Index


def build(raw="data/raw", extraction="aware", chunking="structure", embedder="auto", embedder_obj=None):
    t = time.time()
    docs = extract_corpus(raw, extraction)
    emb = embedder_obj or Embedder(embedder)
    if emb.backend == "lsa" and emb._vec is None:
        # fit the LSA space on sentences (also needed before semantic chunking)
        emb.fit([s for d in docs for sec in d.sections for s in sentences(sec.text)] +
                [sec.text for d in docs for sec in d.sections])
    chunks, parents = chunk_corpus(docs, chunking, emb)
    ix = Index(chunks, parents, emb, dict(extraction=extraction, chunking=chunking, embedder=emb.name,
                                          n_docs=len(docs), n_chunks=len(chunks)))
    ix.config["build_seconds"] = round(time.time() - t, 2)
    return ix


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--extraction", default="aware", choices=["naive", "aware"])
    ap.add_argument("--chunking", default="structure", choices=["fixed", "structure", "semantic", "hierarchical"])
    ap.add_argument("--embedder", default="auto", choices=["auto", "st", "lsa"])
    ap.add_argument("--out", default="indexes/default")
    a = ap.parse_args()
    ix = build(a.raw, a.extraction, a.chunking, a.embedder)
    ix.save(a.out)
    print(f"saved {a.out}: {ix.config}")
