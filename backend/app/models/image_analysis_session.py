from datetime import datetime
from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class ImageAnalysisSession(Base):
    """Hasil analisis image per sesi (PRD 11.3). Hanya data turunan; foto asli tidak disimpan."""

    __tablename__ = "image_analysis_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    image_source_type: Mapped[str] = mapped_column(String(20), default="UPLOAD", nullable=False)
    face_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    face_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image_quality_status: Mapped[str] = mapped_column(String(50), nullable=False)
    skin_tone_detected: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    skin_tone_value: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    undertone_detected: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    undertone_value: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    skin_tone_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    undertone_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    sample_rgb: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sample_hsv: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    is_confirmed_by_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("image_source_type IN ('CAMERA','UPLOAD')", name="ck_image_source_type"),
        Index("idx_image_analysis_session", "session_id", "created_at"),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="image_analyses")
