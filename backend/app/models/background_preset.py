from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.core.database import Base


class BackgroundPreset(Base):
    """Background preset untuk preview visual matching (BR-IMG-08)."""

    __tablename__ = "background_presets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    background_name: Mapped[str] = mapped_column(String(100), nullable=False)
    background_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
