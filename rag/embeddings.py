"""Dense embedding backends.

  st:<model>  sentence-transformers model (default BAAI/bge-small-en-v1.5). Used whenever available.
  lsa         TF-IDF + truncated SVD (latent semantic analysis). Fully offline fallback so the
              whole pipeline runs with zero model downloads. Weaker on paraphrase, but a genuine
              dense, low-dimensional vector space.

`auto` picks st if the library and model load, otherwise lsa.
"""
import sys

import numpy as np

BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class Embedder:
    def __init__(self, backend="auto", model="BAAI/bge-small-en-v1.5", dim=256):
        self.backend, self.model_name, self.dim = backend, model, dim
        self._st = None
        self._vec = self._svd = None
        if backend in ("auto", "st"):
            try:
                from sentence_transformers import SentenceTransformer
                self._st = SentenceTransformer(model)
                self.backend = "st"
            except Exception as e:  # no library / no network for the model download
                if backend == "st":
                    raise
                print(f"[embeddings] sentence-transformers unavailable ({type(e).__name__}); using LSA fallback", file=sys.stderr)
                self.backend = "lsa"

    @property
    def name(self):
        return f"st:{self.model_name}" if self.backend == "st" else f"lsa-{self.dim}"

    def fit(self, texts):
        if self.backend != "lsa":
            return self
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=1, stop_words="english",
                                    token_pattern=r"(?u)\b[\w][\w.\-/]*\w\b|\b\w\b")
        X = self._vec.fit_transform(texts)
        k = min(self.dim, X.shape[1] - 1, X.shape[0] - 1)
        self._svd = TruncatedSVD(n_components=k, random_state=0).fit(X)
        return self

    def _norm(self, M):
        M = np.asarray(M, dtype=np.float32)
        return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)

    def encode_docs(self, texts, batch_size=64):
        if self.backend == "st":
            return self._norm(self._st.encode(texts, batch_size=batch_size, show_progress_bar=False))
        return self._norm(self._svd.transform(self._vec.transform(texts)))

    def encode_query(self, q):
        if self.backend == "st":
            prefix = BGE_QUERY_PREFIX if "bge" in self.model_name.lower() else ""
            return self._norm(self._st.encode([prefix + q]))[0]
        return self._norm(self._svd.transform(self._vec.transform([q])))[0]

    # pickling: drop the torch model, keep the name; reload lazily
    def __getstate__(self):
        s = self.__dict__.copy()
        s["_st"] = None
        return s

    def __setstate__(self, s):
        self.__dict__.update(s)
        if self.backend == "st":
            from sentence_transformers import SentenceTransformer
            self._st = SentenceTransformer(self.model_name)
