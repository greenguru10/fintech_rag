"""Chat request and response schemas."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000)
    session_id: Optional[str] = None
    include_debug: bool = False


class SourceCitationSchema(BaseModel):
    citation_id: int
    chunk_id: Optional[str] = None
    title: str
    source_name: str
    authority_level: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    url: Optional[str] = None
    last_updated: Optional[str] = None
    excerpt: str


class ConfidenceSchema(BaseModel):
    score: float
    label: str
    factors: Dict[str, float]


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    intent: str
    category: Optional[str] = None
    response_mode: str
    confidence: ConfidenceSchema
    sources: List[SourceCitationSchema]
    calculation: Optional[Dict[str, Any]] = None
    follow_up: Optional[str] = None
    safety_notice: str = "Educational information only. Not personal financial or investment advice."
