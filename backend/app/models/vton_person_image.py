from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class VtonPersonImage(Base):
    """Foto upper-body pengguna untuk VTON — disimpan sementara per sesi (PRD CatVTON 12.1).

    File fisik berada di TemporaryImageStorage dengan masa berlaku; baris ini
    hanya menyimpan metadata + token file, bukan data biometrik permanen.
    """

    __tablename__ = "vton_person_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    storage_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    image_source_type: Mapped[str] = mapped_column(String(20), default="UPLOAD", nullable=False)
    image_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_status: Mapped[str] = mapped_column(String(50), nullable=False)
    face_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    body_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mask_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    mask_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    consent_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("image_source_type IN ('CAMERA','UPLOAD')", name="ck_vton_person_source"),
        Index("idx_vton_person_session", "session_id", "created_at"),
    )

    session: Mapped["Session"] = relationship("Session")
