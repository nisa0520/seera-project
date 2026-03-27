from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint, JSON, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(20), nullable=False)
    education: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    aiml_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("aiml_categories.id", ondelete="SET NULL"), nullable=True
    )
    education_topic_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("education_topics.id", ondelete="SET NULL"), nullable=True
    )
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("sender IN ('BUYER','BOT','SYSTEM')", name="ck_chat_log_sender"),
        Index("idx_chat_logs_session_created", "session_id", "created_at"),
    )

    session = relationship("Session", back_populates="chat_logs")
    aiml_category = relationship("AIMLCategory")
    education_topic = relationship("EducationTopic")
