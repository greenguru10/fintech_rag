"""Source, Category, and Feedback schemas."""

from typing import Optional, List
from pydantic import BaseModel, Field


class SourceSchema(BaseModel):
    id: str
    name: str
    authority_level: str
    authority_score: float
    source_type: str
    base_url: Optional[str] = None
    active: bool


class CategorySchema(BaseModel):
    id: int
    slug: str
    display_name: str
    description: Optional[str] = None
    active: bool


class FeedbackRequest(BaseModel):
    answer_id: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_type: Optional[str] = None  # incorrect, incomplete, helpful, inaccurate_calculation
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str
