"""Unified hybrid retriever orchestrator."""

from typing import List, Dict, Any, Tuple
from app.retrieval.index_manager import IndexManager
from app.retrieval.hybrid import HybridRanker
from app.retrieval.reranker import DeterministicReranker
from app.retrieval.evidence import EvidenceExtractor
from app.core.config import settings


class HybridRetriever:
    def __init__(self):
        self.index_manager = IndexManager.get_instance()
        if not self.index_manager.is_ready:
            self.index_manager.load_from_disk()
        self.hybrid_ranker = HybridRanker()
        self.reranker = DeterministicReranker()
        self.evidence_extractor = EvidenceExtractor()

    def retrieve(
        self,
        query: str,
        expanded_query: str | None = None,
        query_entities: List[str] | None = None,
        category_filter: str | None = None,
        top_k: int = 15,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Performs candidate retrieval, hybrid fusion, reranking, and evidence extraction.

        Returns: (ranked_chunks, selected_evidence)
        """
        if not self.index_manager.is_ready:
            return [], []

        search_query = expanded_query or query
        bm25_results = self.index_manager.bm25_retriever.search(search_query, top_k=settings.RETRIEVAL_TOP_K)
        tfidf_results = self.index_manager.tfidf_retriever.search(search_query, top_k=settings.RETRIEVAL_TOP_K)

        bm25_dict = dict(bm25_results)
        tfidf_dict = dict(tfidf_results)

        # Fuse scores
        fused = self.hybrid_ranker.fuse_scores(
            bm25_scores=bm25_dict,
            tfidf_scores=tfidf_dict,
            chunk_metadata=self.index_manager.chunk_metadata,
            category_filter=category_filter,
        )

        # Rerank candidates
        reranked = self.reranker.rerank(
            candidates=fused,
            query=query,
            query_entities=query_entities or [],
        )

        top_candidates = reranked[:top_k]

        # Extract evidence sentences
        evidence = self.evidence_extractor.extract_evidence(
            top_chunks=top_candidates,
            query=query,
            query_entities=query_entities or [],
            max_sentences=settings.FINAL_EVIDENCE_K,
            min_sentence_score=settings.MIN_SENTENCE_SCORE,
        )

        return top_candidates, evidence
