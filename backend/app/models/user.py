from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    user_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    time_session: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "gender IS NULL OR gender IN ('MALE','FEMALE','PREFER_NOT_TO_SAY')",
            name="ck_user_gender",
        ),
    )

    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")
