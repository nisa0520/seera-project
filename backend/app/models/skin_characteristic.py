from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class SkinCharacteristic(Base):
    __tablename__ = "skin_characteristics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    skintone: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    undertone: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    skintone_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    undertone_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("skintone IS NULL OR (skintone >= 1 AND skintone <= 6)", name="ck_skintone_range"),
        CheckConstraint("undertone IS NULL OR (undertone >= 0 AND undertone <= 2)", name="ck_undertone_range"),
        UniqueConstraint("session_id", name="uq_skin_characteristic_session"),
    )

    session: Mapped["Session"] = relationship("Session", back_populates="skin_characteristic")
    seasonal_results = relationship("SeasonalResult", back_populates="skin_characteristic", cascade="all,delete-orphan")
