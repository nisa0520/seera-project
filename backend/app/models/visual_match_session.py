from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class VisualMatchSession(Base):
    """Konfigurasi preview visual matching (produk + background) per sesi."""

    __tablename__ = "visual_match_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    recommendation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True
    )
    selected_product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    selected_background_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("background_presets.id", ondelete="SET NULL"), nullable=True
    )
    preview_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_visual_match_session", "session_id", "created_at"),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="visual_matches")
    selected_product: Mapped[Optional["Product"]] = relationship("Product")
    selected_background: Mapped[Optional["BackgroundPreset"]] = relationship("BackgroundPreset")
