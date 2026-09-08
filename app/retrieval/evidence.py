"""Extractive sentence selection and evidence scoring."""

from typing import List, Dict, Any
from app.nlp.normalizer import split_sentences, tokenize_for_search


def token_jaccard(tokens1: List[str], tokens2: List[str]) -> float:
    set1, set2 = set(tokens1), set(tokens2)
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


class EvidenceExtractor:
    def extract_evidence(
        self,
        top_chunks: List[Dict[str, Any]],
        query: str,
        query_entities: List[str],
        max_sentences: int = 3,
        min_sentence_score: float = 0.35,
    ) -> List[Dict[str, Any]]:
        query_tokens = set(tokenize_for_search(query))
        selected_evidence: List[Dict[str, Any]] = []
        seen_token_sets: List[List[str]] = []

        for chunk in top_chunks:
            meta = chunk.get("metadata", {})
            raw_text = meta.get("raw_text", "")
            chunk_hybrid = chunk.get("final_score", chunk.get("hybrid_score", 0.5))
            auth_score = float(meta.get("authority_score", 0.8))
            section = (meta.get("section") or "").lower()

            sentences = split_sentences(raw_text)

            for s_idx, sentence in enumerate(sentences):
                s_tokens = tokenize_for_search(sentence)
                if len(s_tokens) < 4:
                    continue

                # Jaccard deduplication with already selected sentences
                if any(token_jaccard(s_tokens, prev) > 0.65 for prev in seen_token_sets):
                    continue

                # 1. Query overlap
                overlap = len(set(s_tokens) & query_tokens) / max(1, len(query_tokens))

                # 2. Entity coverage
                ent_cov = 0.0
                if query_entities:
                    s_lower = sentence.lower()
                    matched_ents = sum(1 for e in query_entities if e.lower() in s_lower)
                    ent_cov = matched_ents / len(query_entities)

                # 3. Section match
                sec_match = 1.0 if any(t in section for t in query_tokens) else 0.0

                sentence_score = (
                    0.45 * overlap
                    + 0.20 * ent_cov
                    + 0.15 * chunk_hybrid
                    + 0.10 * sec_match
                    + 0.10 * auth_score
                )

                if sentence_score >= min_sentence_score:
                    selected_evidence.append({
                        "chunk_id": chunk["chunk_id"],
                        "sentence_text": sentence,
                        "sentence_index": s_idx,
                        "sentence_score": round(sentence_score, 4),
                        "document_id": meta.get("document_id"),
                        "title": meta.get("title", "Financial Guide"),
                        "section": meta.get("section"),
                        "page_number": meta.get("page_start"),
                        "source_name": meta.get("source_name", "Authoritative Regulator"),
                        "source_url": meta.get("source_url"),
                        "authority_level": meta.get("authority_level", "A"),
                        "last_updated": meta.get("last_updated"),
                    })
                    seen_token_sets.append(s_tokens)

        # Sort evidence by sentence score
        selected_evidence.sort(key=lambda x: x["sentence_score"], reverse=True)

        # Graceful fallback: If no sentences exceeded min_sentence_score, pull top sentences from best chunks
        if not selected_evidence and top_chunks:
            for top_chunk in top_chunks[:2]:
                meta = top_chunk.get("metadata", {})
                raw_text = meta.get("raw_text", "")
                sentences = split_sentences(raw_text)
                for s_idx, sentence in enumerate(sentences[:2]):
                    if len(tokenize_for_search(sentence)) >= 4:
                        selected_evidence.append({
                            "chunk_id": top_chunk["chunk_id"],
                            "sentence_text": sentence,
                            "sentence_index": s_idx,
                            "sentence_score": 0.45,
                            "document_id": meta.get("document_id"),
                            "title": meta.get("title", "Financial Regulatory Guide"),
                            "section": meta.get("section"),
                            "page_number": meta.get("page_start"),
                            "source_name": meta.get("source_name", "Official Regulator"),
                            "source_url": meta.get("source_url"),
                            "authority_level": meta.get("authority_level", "A"),
                            "last_updated": meta.get("last_updated"),
                        })
                        if len(selected_evidence) >= max_sentences:
                            break
                if len(selected_evidence) >= max_sentences:
                    break

        return selected_evidence[:max_sentences]
