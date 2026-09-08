"""Deterministic reranker applying domain rules and version awareness."""

from typing import List, Dict, Any


class DeterministicReranker:
    def rerank(
        self,
        candidates: List[Dict[str, Any]],
        query: str,
        query_entities: List[str],
    ) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        reranked = []

        for item in candidates:
            score = item["hybrid_score"]
            meta = item.get("metadata", {})
            section = (meta.get("section") or "").lower()
            text = (meta.get("raw_text") or "").lower()

            # Heading match boost
            if section and any(word in section for word in query_lower.split() if len(word) > 3):
                score += 0.10

            # Entity coverage boost
            if query_entities and all(e.lower() in text for e in query_entities):
                score += 0.08

            # Superseded penalty
            if meta.get("superseded_by"):
                score -= 0.25

            # Inactive exclusion
            if meta.get("active") is False:
                continue

            item_copy = dict(item)
            item_copy["final_score"] = round(max(0.0, min(1.0, score)), 5)
            reranked.append(item_copy)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked
