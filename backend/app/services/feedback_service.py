"""Feedback persistence."""
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.feedback import Feedback
from app.models.session import Session


class FeedbackService:
    def __init__(self, db: DBSession):
        self.db = db

    def submit(self, session: Session, rating: Optional[int], comment: Optional[str], is_skipped: bool) -> Feedback:
        existing = self.db.query(Feedback).filter(Feedback.session_id == session.id).first()
        if existing:
            existing.rating = rating
            existing.comment = comment
            existing.is_skipped = is_skipped
            self.db.flush()
            return existing
        fb = Feedback(
            session_id=session.id,
            rating=rating,
            comment=comment,
            is_skipped=is_skipped,
        )
        self.db.add(fb)
        self.db.flush()
        return fb
