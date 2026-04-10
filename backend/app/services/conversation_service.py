"""Conversation orchestration: session lifecycle, chat logging, state transitions."""
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session
from app.models.skin_characteristic import SkinCharacteristic
from app.models.chat_log import ChatLog
from app.models.user import User
from app.core.exceptions import SessionNotFoundError, InvalidConversationStateError


SESSION_STATUS_ACTIVE = "ACTIVE"
SESSION_STATUS_COMPLETED = "COMPLETED"
SESSION_STATUS_CANCELLED = "CANCELLED"

STATE_WAITING_SKIN_TONE = "WAITING_SKIN_TONE"
STATE_WAITING_UNDERTONE = "WAITING_UNDERTONE"
STATE_WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
STATE_WAITING_CHANGE_SELECTION = "WAITING_CHANGE_SELECTION"
STATE_SHOWING_RECOMMENDATION = "SHOWING_RECOMMENDATION"
STATE_EDUCATION = "EDUCATION"


class ConversationService:
    def __init__(self, db: DBSession):
        self.db = db

    # ---- session ----
    def create_session(self, user_fingerprint: Optional[str] = None, buyer_id: Optional[int] = None) -> Session:
        user = None
        if buyer_id:
            user = self.db.get(User, buyer_id)
        elif user_fingerprint:
            user = self.db.query(User).filter(User.user_fingerprint == user_fingerprint).first()
            if not user:
                user = User(user_fingerprint=user_fingerprint)
                self.db.add(user)
                self.db.flush()

        session = Session(
            user_id=user.id if user else None,
            session_status=SESSION_STATUS_ACTIVE,
            conversation_state=STATE_WAITING_SKIN_TONE,
        )
        self.db.add(session)
        self.db.flush()
        return session

    def get_session(self, session_id: int) -> Session:
        session = self.db.get(Session, session_id)
        if not session:
            raise SessionNotFoundError()
        return session

    def get_active_session(self, session_id: int) -> Session:
        session = self.get_session(session_id)
        if session.session_status != SESSION_STATUS_ACTIVE:
            raise InvalidConversationStateError("Sesi tidak aktif.")
        return session

    def require_state(self, session: Session, *allowed_states: str) -> None:
        if session.conversation_state not in allowed_states:
            raise InvalidConversationStateError(
                f"Operasi tidak valid pada state '{session.conversation_state}'."
            )

    def set_state(self, session: Session, new_state: str, *, remember_previous: bool = False) -> None:
        if remember_previous:
            session.previous_state = session.conversation_state
        session.conversation_state = new_state
        self.db.flush()

    def restore_previous_state(self, session: Session) -> None:
        if session.previous_state:
            session.conversation_state = session.previous_state
            session.previous_state = None
            self.db.flush()

    def complete_session(self, session: Session) -> None:
        session.session_status = SESSION_STATUS_COMPLETED
        self.db.flush()

    # ---- skin characteristic ----
    def get_or_create_skin_characteristic(self, session: Session) -> SkinCharacteristic:
        if session.skin_characteristic:
            return session.skin_characteristic
        sc = SkinCharacteristic(session_id=session.id, user_id=session.user_id)
        self.db.add(sc)
        self.db.flush()
        session.skin_characteristic = sc
        return sc

    # ---- chat log ----
    def log_message(
        self,
        session: Session,
        message: str,
        sender: str,
        *,
        aiml_category_id: Optional[int] = None,
        education_topic_id: Optional[int] = None,
        education: Optional[str] = None,
        payload: Optional[dict] = None,
    ) -> ChatLog:
        log = ChatLog(
            session_id=session.id,
            message=message,
            sender=sender,
            aiml_category_id=aiml_category_id,
            education_topic_id=education_topic_id,
            education=education,
            payload=payload,
        )
        self.db.add(log)
        self.db.flush()
        return log
