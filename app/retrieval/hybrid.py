"""Hybrid score normalization and fusion."""

from typing import Dict, Any, List


def min_max_normalize(scores: Dict[str, float]) -> Dict[str, float]:
    """Applies min-max score normalization per query."""
    if not scores:
        return {}
    vals = list(scores.values())
    min_v = min(vals)
    max_v = max(vals)
    if max_v == min_v:
        return {k: 1.0 if max_v > 0 else 0.0 for k in scores}
    return {k: (v - min_v) / (max_v - min_v) for k, v in scores.items()}


class HybridRanker:
    def __init__(
        self,
        bm25_weight: float = 0.48,
        tfidf_weight: float = 0.27,
        metadata_weight: float = 0.10,
        authority_weight: float = 0.10,
        recency_weight: float = 0.05,
    ):
        self.bm25_weight = bm25_weight
        self.tfidf_weight = tfidf_weight
        self.metadata_weight = metadata_weight
        self.authority_weight = authority_weight
        self.recency_weight = recency_weight

    def fuse_scores(
        self,
        bm25_scores: Dict[str, float],
        tfidf_scores: Dict[str, float],
        chunk_metadata: Dict[str, Dict[str, Any]],
        category_filter: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Combines normalized BM25, TF-IDF, and metadata scores."""
        all_chunk_ids = set(bm25_scores.keys()) | set(tfidf_scores.keys())
        if not all_chunk_ids:
            return []

        bm25_norm = min_max_normalize(bm25_scores)
        tfidf_norm = min_max_normalize(tfidf_scores)

        results: List[Dict[str, Any]] = []

        for cid in all_chunk_ids:
            meta = chunk_metadata.get(cid, {})
            b_score = bm25_norm.get(cid, 0.0)
            t_score = tfidf_norm.get(cid, 0.0)

            # Authority score
            auth_score = float(meta.get("authority_score", 0.80))

            # Metadata category relevance
            chunk_cat = meta.get("category")
            cat_match = 1.0 if (category_filter and chunk_cat == category_filter) else (0.5 if not category_filter else 0.0)
            meta_score = 0.60 * cat_match + 0.40 * 1.0

            # Recency default
            recency_score = 1.0

            hybrid = (
                self.bm25_weight * b_score
                + self.tfidf_weight * t_score
                + self.metadata_weight * meta_score
                + self.authority_weight * auth_score
                + self.recency_weight * recency_score
            )

            results.append({
                "chunk_id": cid,
                "bm25_score": b_score,
                "tfidf_score": t_score,
                "metadata_score": meta_score,
                "authority_score": auth_score,
                "hybrid_score": round(hybrid, 5),
                "metadata": meta,
            })

        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return results
