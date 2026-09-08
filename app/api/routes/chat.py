"""Chat API route."""

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = ChatService(db)
    return service.process_chat(
        message=req.message,
        session_id=req.session_id,
        include_debug=req.include_debug,
        background_tasks=background_tasks,
    )

