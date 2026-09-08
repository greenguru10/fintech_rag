"""TF-IDF vectorizer and cosine similarity retriever."""

from typing import List, Tuple, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.nlp.normalizer import tokenize_for_search


def custom_search_tokenizer(text: str) -> List[str]:
    return tokenize_for_search(text)


class TfidfRetriever:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            tokenizer=custom_search_tokenizer,
            token_pattern=None,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.98,
            sublinear_tf=True,
            lowercase=True,
        )
        self.matrix = None
        self.chunk_ids: List[str] = []

    def fit(self, chunks: List[Dict[str, Any]]) -> None:
        self.chunk_ids = [c["id"] for c in chunks]
        texts = [c["normalized_text"] for c in chunks]
        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)
        else:
            self.matrix = None

    def search(self, query: str, top_k: int = 30) -> List[Tuple[str, float]]:
        if self.matrix is None or not self.chunk_ids:
            return []

        tokens = tokenize_for_search(query)
        if not tokens:
            return []

        try:
            query_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vec, self.matrix).flatten()
            results = [
                (self.chunk_ids[idx], float(sims[idx]))
                for idx in range(len(sims))
                if sims[idx] > 0
            ]
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        except Exception:
            return []
