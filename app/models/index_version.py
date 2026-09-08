"""Index version tracking model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from app.database.types import GUID, PortableJSON


class IndexVersion(Base):
    __tablename__ = "index_versions"

    id: Mapped[str] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    index_type: Mapped[str] = mapped_column(String(30), nullable=False)  # bm25, tfidf, hybrid
    artifact_path: Mapped[str] = mapped_column(Text, nullable=False)
    corpus_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False)
    parameters_json: Mapped[dict] = mapped_column(PortableJSON(), default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
