"""Index artifact manager and lifecycle coordinator."""

import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.source import Source, Category
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.tfidf import TfidfRetriever


class IndexManager:
    _instance = None

    def __init__(self):
        self.bm25_retriever = BM25Retriever(k1=settings.BM25_K1, b=settings.BM25_B)
        self.tfidf_retriever = TfidfRetriever()
        self.chunk_metadata: Dict[str, Dict[str, Any]] = {}
        self.is_ready = False
        self.corpus_hash = ""

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def rebuild_indexes(self, db: Session) -> Dict[str, Any]:
        """Loads active chunks from DB and rebuilds in-memory BM25 and TF-IDF indexes."""
        # Query active chunks with document and source metadata
        results = (
            db.query(DocumentChunk, Document, Source, Category)
            .join(Document, DocumentChunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .outerjoin(Category, Document.category_id == Category.id)
            .filter(DocumentChunk.active == True, Document.status == "active")
            .all()
        )

        chunks_data: List[Dict[str, Any]] = []
        meta_dict: Dict[str, Dict[str, Any]] = {}

        for chunk, doc, src, cat in results:
            chunks_data.append({
                "id": str(chunk.id),
                "normalized_text": chunk.normalized_text,
                "raw_text": chunk.raw_text,
            })
            meta_dict[str(chunk.id)] = {
                "chunk_id": str(chunk.id),
                "document_id": str(doc.id),
                "title": doc.title,
                "section": chunk.section,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "raw_text": chunk.raw_text,
                "source_name": src.name,
                "source_url": doc.source_url or src.base_url,
                "authority_level": src.authority_level,
                "authority_score": float(src.authority_score),
                "category": cat.slug if cat else None,
                "last_updated": str(doc.last_updated) if doc.last_updated else None,
                "superseded_by": str(doc.superseded_by) if doc.superseded_by else None,
                "active": chunk.active,
            }

        # Fit models
        self.bm25_retriever.fit(chunks_data)
        self.tfidf_retriever.fit(chunks_data)
        self.chunk_metadata = meta_dict

        # Calculate corpus hash
        hasher = hashlib.sha256()
        for c in chunks_data:
            hasher.update(c["normalized_text"].encode("utf-8"))
        self.corpus_hash = hasher.hexdigest()
        self.is_ready = bool(chunks_data)

        # Save artifacts to disk
        settings.INDEXES_DIR.mkdir(parents=True, exist_ok=True)
        artifact_path = settings.INDEXES_DIR / "retrieval_bundle.pkl"
        with open(artifact_path, "wb") as f:
            pickle.dump({
                "bm25": self.bm25_retriever,
                "tfidf": self.tfidf_retriever,
                "metadata": self.chunk_metadata,
                "corpus_hash": self.corpus_hash,
            }, f)

        return {
            "chunk_count": len(chunks_data),
            "corpus_hash": self.corpus_hash,
            "status": "ready" if self.is_ready else "empty",
        }

    def load_from_disk(self) -> bool:
        artifact_path = settings.INDEXES_DIR / "retrieval_bundle.pkl"
        if not artifact_path.exists():
            return False
        try:
            with open(artifact_path, "rb") as f:
                data = pickle.load(f)
            self.bm25_retriever = data["bm25"]
            self.tfidf_retriever = data["tfidf"]
            self.chunk_metadata = data["metadata"]
            self.corpus_hash = data.get("corpus_hash", "")
            self.is_ready = True
            return True
        except Exception:
            return False
