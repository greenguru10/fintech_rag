"""Document management service."""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.source import Source, Category
from app.core.exceptions import DocumentNotFoundError


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def list_documents(
        self,
        status: str | None = None,
        category: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = (
            self.db.query(Document, Source.name.label("source_name"), Category.slug.label("category_slug"))
            .join(Source, Document.source_id == Source.id)
            .outerjoin(Category, Document.category_id == Category.id)
        )

        if status:
            query = query.filter(Document.status == status)
        if category:
            query = query.filter(Category.slug == category)

        total = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for doc, src_name, cat_slug in results:
            chunk_cnt = self.db.query(DocumentChunk).filter_by(document_id=doc.id).count()
            items.append({
                "id": str(doc.id),
                "title": doc.title,
                "status": doc.status,
                "source_name": src_name,
                "category": cat_slug,
                "document_type": doc.document_type,
                "last_updated": str(doc.last_updated) if doc.last_updated else None,
                "chunk_count": chunk_cnt,
                "created_at": doc.created_at,
            })

        return items, total

    def get_document(self, document_id: str) -> Dict[str, Any]:
        doc = self.db.query(Document).filter_by(id=document_id).first()
        if not doc:
            raise DocumentNotFoundError(document_id)

        source = self.db.query(Source).filter_by(id=doc.source_id).first()
        category = self.db.query(Category).filter_by(id=doc.category_id).first() if doc.category_id else None
        chunks = self.db.query(DocumentChunk).filter_by(document_id=doc.id).order_by(DocumentChunk.chunk_sequence).all()

        return {
            "id": str(doc.id),
            "title": doc.title,
            "source_id": str(doc.source_id),
            "source_name": source.name if source else "Unknown",
            "category": category.slug if category else None,
            "status": doc.status,
            "source_url": doc.source_url,
            "chunk_count": len(chunks),
            "extracted_text_preview": doc.extracted_text,
            "chunks": [
                {
                    "chunk_id": str(c.id),
                    "sequence": c.chunk_sequence,
                    "section": c.section,
                    "page_start": c.page_start,
                    "raw_text": c.raw_text,
                    "token_count": c.token_count,
                    "active": c.active,
                }
                for c in chunks
            ],
        }
