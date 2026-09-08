"""BM25 lexical retriever implementation."""

from typing import List, Tuple, Dict, Any
from rank_bm25 import BM25Okapi
from app.nlp.normalizer import tokenize_for_search


class BM25Retriever:
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25: BM25Okapi | None = None
        self.chunk_ids: List[str] = []
        self.corpus_tokenized: List[List[str]] = []

    def fit(self, chunks: List[Dict[str, Any]]) -> None:
        """Fits BM25 index on chunk list containing 'id' and 'normalized_text'."""
        self.chunk_ids = [c["id"] for c in chunks]
        self.corpus_tokenized = [tokenize_for_search(c["normalized_text"]) for c in chunks]
        if self.corpus_tokenized:
            self.bm25 = BM25Okapi(self.corpus_tokenized, k1=self.k1, b=self.b)
        else:
            self.bm25 = None

    def search(self, query: str, top_k: int = 30) -> List[Tuple[str, float]]:
        """Returns list of (chunk_id, raw_bm25_score)."""
        if not self.bm25 or not self.chunk_ids:
            return []

        tokens = tokenize_for_search(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        results = [
            (self.chunk_ids[idx], float(scores[idx]))
            for idx in range(len(scores))
            if scores[idx] > 0
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
