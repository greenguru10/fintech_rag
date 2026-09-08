"""Query and RetrievalResult models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Numeric, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.database.types import GUID, PortableJSON


class QueryModel(Base):
    __tablename__ = "queries"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("sessions.id"), nullable=True, index=True)
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query: Mapped[str] = mapped_column(Text, nullable=False)
    expanded_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    intent: Mapped[str] = mapped_column(String(50), nullable=False)
    intent_confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=1.0)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    safety_flags: Mapped[list] = mapped_column(PortableJSON(), default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    session = relationship("SessionModel", back_populates="queries")
    retrieval_results = relationship("RetrievalResultModel", back_populates="query", cascade="all, delete-orphan")
    answer = relationship("AnswerModel", back_populates="query", uselist=False)


class RetrievalResultModel(Base):
    __tablename__ = "retrieval_results"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id: Mapped[str] = mapped_column(GUID, ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(GUID, ForeignKey("document_chunks.id"), nullable=False, index=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    bm25_score: Mapped[float | None] = mapped_column(Numeric(8, 6), nullable=True)
    tfidf_score: Mapped[float | None] = mapped_column(Numeric(8, 6), nullable=True)
    semantic_score: Mapped[float | None] = mapped_column(Numeric(8, 6), nullable=True)
    metadata_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False, default=0.0)
    hybrid_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    selected_as_evidence: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    query = relationship("QueryModel", back_populates="retrieval_results")
