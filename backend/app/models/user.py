from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    user_fingerprint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    time_session: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="user")
