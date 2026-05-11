"""Education topic & content service - internal knowledge base only."""
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.models.education import EducationTopic, EducationContent
from app.core.exceptions import EducationTopicNotFoundError


class EducationService:
    def __init__(self, db: DBSession):
        self.db = db

    def list_topics(self) -> list[EducationTopic]:
        return (
            self.db.query(EducationTopic)
            .filter(EducationTopic.is_active.is_(True))
            .order_by(EducationTopic.display_order.asc(), EducationTopic.id.asc())
            .all()
        )

    def get_topic_by_code(self, code: str) -> EducationTopic:
        topic = (
            self.db.query(EducationTopic)
            .filter(EducationTopic.code == code.upper(), EducationTopic.is_active.is_(True))
            .first()
        )
        if not topic:
            raise EducationTopicNotFoundError()
        return topic

    def latest_content(self, topic: EducationTopic) -> Optional[EducationContent]:
        return (
            self.db.query(EducationContent)
            .filter(EducationContent.topic_id == topic.id, EducationContent.is_active.is_(True))
            .order_by(EducationContent.version.desc(), EducationContent.id.desc())
            .first()
        )
