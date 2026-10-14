# Experiment results (auto-generated)

Embedder: `st:BAAI/bge-small-en-v1.5` · Abstain threshold: 0.3 · 90 questions

### E1: Extraction strategy (chunking=fixed; retrieval=hybrid, then full pipeline)

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| naive/fixed/hybrid | 1.00 | 0.73 | 0.20 | 0.90 | 1.00 | 0.67 | 0.91 | 0.74 | 0.78 | 0.86 | 0.11 | 6.2 |
| aware/fixed/hybrid | 1.00 | 0.73 | 0.13 | 0.83 | 0.87 | 0.67 | 0.87 | 0.75 | 0.77 | 0.84 | 0.13 | 6.2 |
| naive/fixed/hybrid_rerank_temporal | 1.00 | 0.73 | 0.47 | 1.00 | 1.00 | 0.67 | 0.95 | 0.82 | 0.84 | 0.94 | 0.11 | 569.3 |
| aware/fixed/hybrid_rerank_temporal | 1.00 | 0.73 | 0.47 | 0.93 | 1.00 | 0.67 | 0.93 | 0.83 | 0.85 | 0.91 | 0.09 | 520.6 |

#### naive/fixed/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.92 | 0.93 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.71 | 0.73 | 0.73 | – | – | 0.33 |
| temporal | 15 | 0.93 | 0.51 | 0.62 | 0.87 | 0.20 | – | 0.00 |
| multi_doc | 15 | 0.90 | 0.82 | 0.84 | 0.83 | – | – | 0.00 |
| sparse | 15 | 1.00 | 0.72 | 0.79 | 0.87 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.67 | – |
| overall | 90 | 0.91 | 0.74 | 0.78 | 0.86 | 0.20 | 0.67 | 0.11 |

#### aware/fixed/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.97 | 0.97 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.70 | 0.71 | 0.73 | – | – | 0.33 |
| temporal | 15 | 0.93 | 0.45 | 0.58 | 0.87 | 0.13 | – | 0.00 |
| multi_doc | 15 | 0.83 | 0.93 | 0.84 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.87 | 0.71 | 0.75 | 0.80 | – | – | 0.20 |
| no_answer | 15 | – | – | – | – | – | 0.67 | – |
| overall | 90 | 0.87 | 0.75 | 0.77 | 0.84 | 0.13 | 0.67 | 0.13 |

#### naive/fixed/hybrid_rerank_temporal — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.86 | 0.89 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.62 | 0.65 | 0.73 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.70 | 0.78 | 1.00 | 0.47 | – | 0.00 |
| multi_doc | 15 | 1.00 | 0.93 | 0.91 | 0.97 | – | – | 0.00 |
| sparse | 15 | 1.00 | 1.00 | 1.00 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.67 | – |
| overall | 90 | 0.95 | 0.82 | 0.84 | 0.94 | 0.47 | 0.67 | 0.11 |

#### aware/fixed/hybrid_rerank_temporal — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.93 | 0.95 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.65 | 0.68 | 0.67 | – | – | 0.33 |
| temporal | 15 | 1.00 | 0.68 | 0.76 | 1.00 | 0.47 | – | 0.00 |
| multi_doc | 15 | 0.93 | 0.92 | 0.91 | 0.90 | – | – | 0.00 |
| sparse | 15 | 1.00 | 0.97 | 0.97 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.67 | – |
| overall | 90 | 0.93 | 0.83 | 0.85 | 0.91 | 0.47 | 0.67 | 0.09 |

### E2: Chunking strategy (extraction=aware, retrieval=hybrid)

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/fixed/hybrid | 1.00 | 0.73 | 0.13 | 0.83 | 0.87 | 0.67 | 0.87 | 0.75 | 0.77 | 0.84 | 0.13 | 6.7 |
| aware/structure/hybrid | 1.00 | 0.73 | 0.07 | 0.87 | 0.87 | 0.60 | 0.89 | 0.71 | 0.75 | 0.84 | 0.15 | 6.6 |
| aware/semantic/hybrid | 1.00 | 0.60 | 0.07 | 0.90 | 0.87 | 0.60 | 0.87 | 0.69 | 0.73 | 0.81 | 0.15 | 6.7 |
| aware/hierarchical/hybrid | 1.00 | 0.73 | 0.20 | 0.93 | 0.93 | 0.60 | 0.92 | 0.75 | 0.78 | 0.85 | 0.13 | 7.2 |

#### aware/fixed/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.97 | 0.97 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.70 | 0.71 | 0.73 | – | – | 0.33 |
| temporal | 15 | 0.93 | 0.45 | 0.58 | 0.87 | 0.13 | – | 0.00 |
| multi_doc | 15 | 0.83 | 0.93 | 0.84 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.87 | 0.71 | 0.75 | 0.80 | – | – | 0.20 |
| no_answer | 15 | – | – | – | – | – | 0.67 | – |
| overall | 90 | 0.87 | 0.75 | 0.77 | 0.84 | 0.13 | 0.67 | 0.13 |

#### aware/structure/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.93 | 0.94 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.67 | 0.68 | 0.73 | – | – | 0.47 |
| temporal | 15 | 1.00 | 0.43 | 0.56 | 0.80 | 0.07 | – | 0.00 |
| multi_doc | 15 | 0.87 | 0.87 | 0.82 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.87 | 0.67 | 0.73 | 0.87 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.89 | 0.71 | 0.75 | 0.84 | 0.07 | 0.60 | 0.15 |

#### aware/semantic/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.92 | 0.93 | 1.00 | – | – | 0.13 |
| semantic | 15 | 0.60 | 0.54 | 0.57 | 0.60 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.45 | 0.59 | 0.80 | 0.07 | – | 0.00 |
| multi_doc | 15 | 0.90 | 0.87 | 0.82 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.87 | 0.65 | 0.72 | 0.87 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.87 | 0.69 | 0.73 | 0.81 | 0.07 | 0.60 | 0.15 |

#### aware/hierarchical/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.97 | 0.97 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.63 | 0.66 | 0.73 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.53 | 0.65 | 0.80 | 0.20 | – | 0.00 |
| multi_doc | 15 | 0.93 | 0.89 | 0.87 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.93 | 0.71 | 0.77 | 0.93 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.92 | 0.75 | 0.78 | 0.85 | 0.20 | 0.60 | 0.13 |

### E3: Retrieval method (extraction=aware, chunking=structure)

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/structure/bm25 | 1.00 | 0.80 | 0.13 | 0.87 | 0.93 | 0.60 | 0.88 | 0.71 | 0.75 | 0.81 | 0.05 | 0.4 |
| aware/structure/dense | 0.93 | 0.67 | 0.00 | 0.80 | 0.73 | 0.60 | 0.81 | 0.64 | 0.67 | 0.74 | 0.21 | 6.3 |
| aware/structure/hybrid | 1.00 | 0.73 | 0.07 | 0.87 | 0.87 | 0.60 | 0.89 | 0.71 | 0.75 | 0.84 | 0.15 | 6.6 |
| aware/structure/hybrid_rerank | 1.00 | 0.80 | 0.47 | 1.00 | 1.00 | 0.60 | 0.96 | 0.83 | 0.86 | 0.95 | 0.13 | 408.1 |
| aware/structure/hybrid_rerank_temporal | 1.00 | 0.80 | 0.87 | 1.00 | 1.00 | 0.60 | 0.96 | 0.87 | 0.89 | 0.95 | 0.13 | 417.0 |

#### aware/structure/bm25 — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.80 | 0.86 | 0.93 | – | – | 0.07 |
| semantic | 15 | 0.80 | 0.72 | 0.74 | 0.80 | – | – | 0.20 |
| temporal | 15 | 0.80 | 0.44 | 0.55 | 0.73 | 0.13 | – | 0.00 |
| multi_doc | 15 | 0.87 | 0.85 | 0.80 | 0.63 | – | – | 0.00 |
| sparse | 15 | 0.93 | 0.76 | 0.80 | 0.93 | – | – | 0.00 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.88 | 0.71 | 0.75 | 0.81 | 0.13 | 0.60 | 0.05 |

#### aware/structure/dense — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 0.93 | 0.82 | 0.84 | 0.93 | – | – | 0.13 |
| semantic | 15 | 0.67 | 0.61 | 0.63 | 0.67 | – | – | 0.47 |
| temporal | 15 | 0.90 | 0.39 | 0.52 | 0.70 | 0.00 | – | 0.00 |
| multi_doc | 15 | 0.80 | 0.86 | 0.78 | 0.67 | – | – | 0.20 |
| sparse | 15 | 0.73 | 0.54 | 0.60 | 0.73 | – | – | 0.27 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.81 | 0.64 | 0.67 | 0.74 | 0.00 | 0.60 | 0.21 |

#### aware/structure/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.93 | 0.94 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.67 | 0.68 | 0.73 | – | – | 0.47 |
| temporal | 15 | 1.00 | 0.43 | 0.56 | 0.80 | 0.07 | – | 0.00 |
| multi_doc | 15 | 0.87 | 0.87 | 0.82 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.87 | 0.67 | 0.73 | 0.87 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.89 | 0.71 | 0.75 | 0.84 | 0.07 | 0.60 | 0.15 |

#### aware/structure/hybrid_rerank — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.92 | 0.94 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.80 | 0.68 | 0.70 | 0.80 | – | – | 0.47 |
| temporal | 15 | 1.00 | 0.66 | 0.74 | 1.00 | 0.47 | – | 0.00 |
| multi_doc | 15 | 1.00 | 0.90 | 0.91 | 0.97 | – | – | 0.07 |
| sparse | 15 | 1.00 | 1.00 | 1.00 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.96 | 0.83 | 0.86 | 0.95 | 0.47 | 0.60 | 0.13 |

#### aware/structure/hybrid_rerank_temporal — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.92 | 0.94 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.80 | 0.68 | 0.70 | 0.80 | – | – | 0.47 |
| temporal | 15 | 1.00 | 0.86 | 0.89 | 1.00 | 0.87 | – | 0.00 |
| multi_doc | 15 | 1.00 | 0.90 | 0.92 | 0.97 | – | – | 0.07 |
| sparse | 15 | 1.00 | 1.00 | 1.00 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.96 | 0.87 | 0.89 | 0.95 | 0.87 | 0.60 | 0.13 |

### E4: Retrieval method on hierarchical chunks (extraction=aware, chunking=hierarchical)

| Config | Direct Hit@5 | Semantic Hit@5 | Temporal CurFirst | Multi-doc Hit@5 | Sparse Hit@5 | No-answer Abstain | Overall Hit@5 | Overall MRR | Overall nDCG@10 | Overall Evid@5 | False abstain | p50 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aware/hierarchical/hybrid | 1.00 | 0.73 | 0.20 | 0.93 | 0.93 | 0.60 | 0.92 | 0.75 | 0.78 | 0.85 | 0.13 | 7.6 |
| aware/hierarchical/hybrid_rerank | 1.00 | 0.73 | 0.53 | 1.00 | 1.00 | 0.60 | 0.95 | 0.86 | 0.88 | 0.94 | 0.11 | 228.4 |
| aware/hierarchical/hybrid_rerank_temporal | 1.00 | 0.73 | 0.87 | 1.00 | 1.00 | 0.60 | 0.95 | 0.90 | 0.91 | 0.94 | 0.11 | 229.6 |

#### aware/hierarchical/hybrid — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 0.97 | 0.97 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.63 | 0.66 | 0.73 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.53 | 0.65 | 0.80 | 0.20 | – | 0.00 |
| multi_doc | 15 | 0.93 | 0.89 | 0.87 | 0.80 | – | – | 0.07 |
| sparse | 15 | 0.93 | 0.71 | 0.77 | 0.93 | – | – | 0.13 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.92 | 0.75 | 0.78 | 0.85 | 0.20 | 0.60 | 0.13 |

#### aware/hierarchical/hybrid_rerank — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 1.00 | 0.99 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.67 | 0.68 | 0.73 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.70 | 0.78 | 1.00 | 0.53 | – | 0.00 |
| multi_doc | 15 | 1.00 | 0.93 | 0.93 | 0.97 | – | – | 0.00 |
| sparse | 15 | 1.00 | 1.00 | 1.00 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.95 | 0.86 | 0.88 | 0.94 | 0.53 | 0.60 | 0.11 |

#### aware/hierarchical/hybrid_rerank_temporal — per category

| Category | n | Hit@5 | MRR | nDCG@10 | Evid@5 | CurFirst | Abstain | False abstain |
|---|---|---|---|---|---|---|---|---|
| direct | 15 | 1.00 | 1.00 | 0.99 | 1.00 | – | – | 0.07 |
| semantic | 15 | 0.73 | 0.67 | 0.68 | 0.73 | – | – | 0.40 |
| temporal | 15 | 1.00 | 0.86 | 0.89 | 1.00 | 0.87 | – | 0.00 |
| multi_doc | 15 | 1.00 | 0.97 | 0.96 | 0.97 | – | – | 0.00 |
| sparse | 15 | 1.00 | 1.00 | 1.00 | 1.00 | – | – | 0.07 |
| no_answer | 15 | – | – | – | – | – | 0.60 | – |
| overall | 90 | 0.95 | 0.90 | 0.91 | 0.94 | 0.87 | 0.60 | 0.11 |

### E5: Abstention threshold sweep (aware/structure/hybrid_rerank_temporal)

| Threshold | No-answer correctly abstained | Answerable wrongly abstained | Accuracy (all 90) |
|---|---|---|---|
| 0.10 | 0.40 | 0.01 | 0.89 |
| 0.20 | 0.53 | 0.08 | 0.86 |
| 0.25 | 0.60 | 0.09 | 0.86 |
| 0.30 (used) | 0.60 | 0.13 | 0.82 |
| 0.35 | 0.67 | 0.15 | 0.82 |
| 0.40 | 0.73 | 0.16 | 0.82 |
| 0.50 | 0.87 | 0.25 | 0.77 |
| 0.60 | 0.93 | 0.43 | 0.63 |
