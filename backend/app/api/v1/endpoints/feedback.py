"""Feedback endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.schemas.conversation import FeedbackRequest
from app.services.conversation_service import ConversationService
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/conversations", tags=["feedback"])


@router.post("/{session_id}/feedback")
def submit_feedback(session_id: int, payload: FeedbackRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    fb_service = FeedbackService(db)

    session = conv.get_session(session_id)
    fb = fb_service.submit(session, payload.rating, payload.comment, payload.is_skipped)

    conv.log_message(
        session,
        f"Feedback rating={payload.rating} skipped={payload.is_skipped}",
        "BUYER",
        payload={
            "rating": payload.rating,
            "comment": payload.comment,
            "is_skipped": payload.is_skipped,
        },
    )

    conv.log_message(session, "Terima kasih atas umpan balik Anda.", "BOT")
    conv.complete_session(session)

    db.commit()
    return {"message": "Terima kasih atas umpan balik Anda.", "feedback_id": fb.id}
