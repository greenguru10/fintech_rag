"""Conversation state model and session context."""

from datetime import datetime, timezone
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ConversationState(BaseModel):
    session_id: str
    previous_intent: str | None = None
    previous_category: str | None = None
    previous_entities: List[str] = Field(default_factory=list)
    previous_document_ids: List[str] = Field(default_factory=list)
    previous_chunk_ids: List[str] = Field(default_factory=list)
    previous_answer_mode: str | None = None
    previous_calculation_type: str | None = None
    pending_clarification_field: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
