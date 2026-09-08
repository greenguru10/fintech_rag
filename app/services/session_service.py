"""Session and message history service."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.session import SessionModel, MessageModel


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        messages = (
            self.db.query(MessageModel)
            .filter_by(session_id=session_id)
            .order_by(MessageModel.created_at)
            .all()
        )
        return [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "metadata": m.message_metadata,
                "created_at": str(m.created_at),
            }
            for m in messages
        ]
