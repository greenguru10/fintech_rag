"""Feedback API schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    answer_id: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_type: Optional[str] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str
