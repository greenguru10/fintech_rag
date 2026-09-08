"""Feedback submission endpoint."""

import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.feedback import FeedbackModel
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(tags=["Feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    fb = FeedbackModel(
        id=str(uuid.uuid4()),
        answer_id=req.answer_id,
        rating=req.rating,
        feedback_type=req.feedback_type,
        comment=req.comment,
    )
    db.add(fb)
    db.commit()
    return FeedbackResponse(feedback_id=fb.id, status="recorded")
