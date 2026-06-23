from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint, Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


JOB_QUEUED = "QUEUED"
JOB_PROCESSING = "PROCESSING"
JOB_SUCCESS = "SUCCESS"
JOB_FAILED = "FAILED"
JOB_EXPIRED = "EXPIRED"


class VtonJob(Base):
    """Job asinkron realistic virtual try-on (PRD CatVTON 12.3, FR-VTO-09/10).

    model_name/model_version dicatat per job agar hasil pengujian dapat
    ditelusuri (BR-VTO-13). Kegagalan job tidak memengaruhi rekomendasi.
    """

    __tablename__ = "vton_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    person_image_id: Mapped[int] = mapped_column(
        ForeignKey("vton_person_images.id", ondelete="CASCADE"), nullable=False
    )
    background_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("background_presets.id", ondelete="SET NULL"), nullable=True
    )
    garment_vton_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mask_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model_name: Mapped[str] = mapped_column(String(50), default="IDM-VTON", nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inference_resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # Ketelusuran garment fidelity (PRD Revisi IDM-VTON FR-VTO-09, BR-VTO-13/16)
    garment_vton_asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_vton_assets.id", ondelete="SET NULL"), nullable=True
    )
    selected_variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("colors.id", ondelete="SET NULL"), nullable=True
    )
    garment_caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inference_parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Asset tier yang dipakai job ini (FR-VTO-15/16) — untuk label & ketelusuran.
    vton_asset_tier: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    tryon_quality_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=JOB_QUEUED, nullable=False)
    output_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED','PROCESSING','SUCCESS','FAILED','EXPIRED')",
            name="ck_vton_job_status",
        ),
        Index("idx_vton_jobs_session", "session_id", "created_at"),
        Index("idx_vton_jobs_status", "status", "created_at"),
    )

    session: Mapped["Session"] = relationship("Session")
    product: Mapped["Product"] = relationship("Product")
    person_image: Mapped["VtonPersonImage"] = relationship("VtonPersonImage")
    background: Mapped[Optional["BackgroundPreset"]] = relationship("BackgroundPreset")
    feedback: Mapped[Optional["VtonFeedback"]] = relationship(
        "VtonFeedback", back_populates="job", uselist=False, cascade="all,delete-orphan"
    )
