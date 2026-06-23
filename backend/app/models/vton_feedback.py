from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class VtonFeedback(Base):
    """Feedback kualitas hasil realistic try-on (PRD CatVTON 12.4, FR-VTO-13)."""

    __tablename__ = "vton_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vton_job_id: Mapped[int] = mapped_column(
        ForeignKey("vton_jobs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    visual_quality_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    proportion_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    garment_similarity_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "visual_quality_rating IS NULL OR (visual_quality_rating BETWEEN 1 AND 5)",
            name="ck_vton_fb_visual",
        ),
        CheckConstraint(
            "proportion_rating IS NULL OR (proportion_rating BETWEEN 1 AND 5)",
            name="ck_vton_fb_proportion",
        ),
        CheckConstraint(
            "garment_similarity_rating IS NULL OR (garment_similarity_rating BETWEEN 1 AND 5)",
            name="ck_vton_fb_similarity",
        ),
        CheckConstraint(
            "satisfaction_rating IS NULL OR (satisfaction_rating BETWEEN 1 AND 5)",
            name="ck_vton_fb_satisfaction",
        ),
    )

    job: Mapped["VtonJob"] = relationship("VtonJob", back_populates="feedback")
