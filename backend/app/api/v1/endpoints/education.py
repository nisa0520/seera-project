"""Education endpoints (UC-02)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.core.database import get_db
from app.core.exceptions import EducationTopicNotFoundError
from app.services.education_service import EducationService
from app.services.conversation_service import ConversationService, STATE_EDUCATION
from app.services.aiml_interpreter import AIMLInterpreter

router = APIRouter(prefix="/education", tags=["education"])


@router.get("/topics")
def list_topics(session_id: Optional[int] = Query(default=None), db: DBSession = Depends(get_db)):
    education = EducationService(db)
    topics = education.list_topics()
    payload = [
        {"code": t.code, "title": t.title, "description": t.description}
        for t in topics
    ]

    if session_id:
        conv = ConversationService(db)
        try:
            session = conv.get_session(session_id)
            conv.log_message(
                session,
                "Tampilkan daftar topik edukasi.",
                "BUYER",
                education="LIST_TOPICS",
            )
            db.commit()
        except Exception:
            db.rollback()

    return {"topics": payload}


@router.get("/topics/{topic_code}")
def get_topic(
    topic_code: str,
    session_id: Optional[int] = Query(default=None),
    db: DBSession = Depends(get_db),
):
    education = EducationService(db)
    aiml = AIMLInterpreter(db)

    try:
        topic = education.get_topic_by_code(topic_code)
    except EducationTopicNotFoundError:
        response = aiml.respond("TOPIC_UNAVAILABLE", context={"topic_code": topic_code})
        if session_id:
            conv = ConversationService(db)
            try:
                session = conv.get_session(session_id)
                conv.log_message(session, f"Permintaan topik: {topic_code}", "BUYER")
                conv.log_message(
                    session,
                    response["message"],
                    "BOT",
                    aiml_category_id=response["aiml_category_id"],
                    education=topic_code,
                )
                db.commit()
            except Exception:
                db.rollback()
        raise EducationTopicNotFoundError(response["message"])

    content = education.latest_content(topic)
    quick_replies = [
        {"label": t.title, "value": t.code}
        for t in education.list_topics()
        if t.id != topic.id
    ]
    quick_replies.append({"label": "Cari rekomendasi", "value": "START_RECOMMENDATION"})

    if session_id:
        conv = ConversationService(db)
        try:
            session = conv.get_session(session_id)
            conv.log_message(session, f"Pilih topik edukasi: {topic.title}", "BUYER")
            previous_state = session.conversation_state
            if session.conversation_state != STATE_EDUCATION:
                session.previous_state = previous_state
                session.conversation_state = STATE_EDUCATION
            conv.log_message(
                session,
                content.content if content else topic.description or "",
                "BOT",
                education=topic.code,
                education_topic_id=topic.id,
            )
            db.commit()
        except Exception:
            db.rollback()

    return {
        "topic_code": topic.code,
        "title": topic.title,
        "content": content.content if content else (topic.description or ""),
        "source_note": content.source_note if content else None,
        "quick_replies": quick_replies,
    }
