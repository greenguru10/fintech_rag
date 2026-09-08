"""System health and diagnostic endpoints for uptime monitoring."""

import time
from fastapi import APIRouter
from app.retrieval.index_manager import IndexManager

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/ping")
def ping():
    """Ultra-lightweight keep-alive heartbeat endpoint for uptime bots."""
    return {
        "status": "alive",
        "uptime_seconds": int(time.time() - START_TIME),
    }


@router.get("/health")
def health_check():
    """System health check and diagnostic status."""
    idx_mgr = IndexManager.get_instance()
    return {
        "status": "ok",
        "database": "ok",
        "bm25_index": "ready" if idx_mgr.is_ready else "empty",
        "tfidf_index": "ready" if idx_mgr.is_ready else "empty",
        "semantic_index": "disabled",
        "no_llm_mode": "enforced",
        "uptime_seconds": int(time.time() - START_TIME),
        "version": "1.0.0",
    }
