"""System health and diagnostic endpoint."""

from fastapi import APIRouter
from app.retrieval.index_manager import IndexManager

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    idx_mgr = IndexManager.get_instance()
    return {
        "status": "ok",
        "database": "ok",
        "bm25_index": "ready" if idx_mgr.is_ready else "empty",
        "tfidf_index": "ready" if idx_mgr.is_ready else "empty",
        "semantic_index": "disabled",
        "no_llm_mode": "enforced",
        "version": "1.0.0",
    }
