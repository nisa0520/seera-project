from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, JSON, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.core.database import Base


class AIMLCategory(Base):
    __tablename__ = "aiml_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pattern: Mapped[str] = mapped_column(String(150), nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    that_pattern: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    quick_replies: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_aiml_lookup", "pattern", "topic", "that_pattern", "is_active"),
    )
