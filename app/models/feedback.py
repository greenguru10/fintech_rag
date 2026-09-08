"""Feedback and CalculationHistory models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.database.types import GUID, PortableJSON


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    answer_id: Mapped[str] = mapped_column(GUID, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    feedback_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    answer = relationship("AnswerModel", back_populates="feedback")


class CalculationHistoryModel(Base):
    __tablename__ = "calculation_history"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str | None] = mapped_column(GUID, ForeignKey("sessions.id"), nullable=True, index=True)
    calculation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    inputs_json: Mapped[dict] = mapped_column(PortableJSON(), default=dict)
    outputs_json: Mapped[dict] = mapped_column(PortableJSON(), default=dict)
    formula_version: Mapped[str] = mapped_column(String(30), nullable=False, default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    session = relationship("SessionModel", back_populates="calculations")
