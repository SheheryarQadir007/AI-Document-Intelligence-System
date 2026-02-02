
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import numpy as np

@dataclass
class SearchResult:
    filename: str
    score: float
    snippet: str

class Retriever:
    """
    Local retrieval with two backends:
    1) SentenceTransformers + cosine similarity (preferred if model is present locally)
    2) TF-IDF cosine similarity fallback (fully offline, no model downloads)
    """

    def __init__(self, backend: str = "auto", model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.backend = backend
        self.model_name = model_name
        self._st_model = None
        self._tfidf = None
        self._tfidf_matrix = None
        self._docs = None
        self._emb = None

    def _try_load_sentence_transformer(self) -> bool:
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(self.model_name)
            return True
        except Exception:
            self._st_model = None
            return False

    def fit(self, filenames: List[str], texts: List[str]) -> str:
        self._docs = list(zip(filenames, texts))

        if self.backend in ("auto", "sentence-transformers"):
            ok = self._try_load_sentence_transformer()
            if ok:
                emb = self._st_model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                self._emb = np.asarray(emb, dtype=np.float32)
                self.backend = "sentence-transformers"
                return self.backend

        # Fallback to TF-IDF (always offline)
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
        self._tfidf_matrix = self._tfidf.fit_transform(texts)
        self.backend = "tfidf"
        return self.backend

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self._docs:
            return []
        query = query.strip()
        if not query:
            return []

        if self.backend == "sentence-transformers":
            q = self._st_model.encode([query], normalize_embeddings=True, show_progress_bar=False)
            q = np.asarray(q, dtype=np.float32)[0]
            scores = (self._emb @ q).tolist()
        else:
            from sklearn.metrics.pairwise import cosine_similarity
            qv = self._tfidf.transform([query])
            scores = cosine_similarity(self._tfidf_matrix, qv).ravel().tolist()

        idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results: List[SearchResult] = []
        for i in idxs:
            fn, txt = self._docs[i]
            snippet = (txt[:200] + "...") if len(txt) > 200 else txt
            results.append(SearchResult(filename=fn, score=float(scores[i]), snippet=snippet))
        return results
