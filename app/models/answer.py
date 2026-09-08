"""Answer and Citation models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Numeric, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.database.types import GUID, PortableJSON


class AnswerModel(Base):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id: Mapped[str] = mapped_column(GUID, ForeignKey("queries.id"), unique=True, nullable=False)
    response_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    confidence_label: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence_support_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    contradiction_score: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    calculation_json: Mapped[dict | None] = mapped_column(PortableJSON(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    query = relationship("QueryModel", back_populates="answer")
    citations = relationship("CitationModel", back_populates="answer", cascade="all, delete-orphan")
    feedback = relationship("FeedbackModel", back_populates="answer", cascade="all, delete-orphan")


class CitationModel(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    answer_id: Mapped[str] = mapped_column(GUID, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(GUID, ForeignKey("document_chunks.id"), nullable=False, index=True)
    citation_order: Mapped[int] = mapped_column(Integer, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    sentence_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    answer = relationship("AnswerModel", back_populates="citations")
    chunk = relationship("DocumentChunk", back_populates="citations")
