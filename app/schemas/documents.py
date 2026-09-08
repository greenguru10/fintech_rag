"""Document and Admin API schemas."""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel


class DocumentItemSchema(BaseModel):
    id: str
    title: str
    status: str
    source_name: str
    category: Optional[str] = None
    document_type: str
    last_updated: Optional[str] = None
    chunk_count: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: List[DocumentItemSchema]
    total: int
    page: int
    page_size: int


class DocumentDetailResponse(BaseModel):
    id: str
    title: str
    source_id: str
    source_name: str
    category: Optional[str] = None
    status: str
    source_url: Optional[str] = None
    chunk_count: int
    extracted_text_preview: Optional[str] = None
    chunks: List[Dict[str, Any]]
