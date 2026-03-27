from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)
    conversation_state: Mapped[str] = mapped_column(String(50), default="WAITING_SKIN_TONE", nullable=False)
    skintone_snapshot: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    undertone_snapshot: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    y1_continuous: Mapped[Optional[float]] = mapped_column(Numeric(8, 6), nullable=True)
    seasonal_type_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recommendation_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    previous_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "session_status IN ('ACTIVE','COMPLETED','CANCELLED')",
            name="ck_session_status",
        ),
        CheckConstraint(
            "conversation_state IN ('WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
            name="ck_conversation_state",
        ),
        Index("idx_sessions_user_created", "user_id", "created_at"),
        Index("idx_sessions_state", "session_status", "conversation_state"),
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="sessions")
    chat_logs: Mapped[List["ChatLog"]] = relationship("ChatLog", back_populates="session", cascade="all,delete-orphan")
    skin_characteristic: Mapped[Optional["SkinCharacteristic"]] = relationship(
        "SkinCharacteristic", back_populates="session", uselist=False, cascade="all,delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="session", cascade="all,delete-orphan"
    )
    feedback: Mapped[Optional["Feedback"]] = relationship(
        "Feedback", back_populates="session", uselist=False, cascade="all,delete-orphan"
    )
