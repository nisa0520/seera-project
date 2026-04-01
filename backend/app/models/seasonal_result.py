from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class SeasonalResult(Base):
    __tablename__ = "seasonal_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    skin_characteristic_id: Mapped[int] = mapped_column(
        ForeignKey("skin_characteristics.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    seasonal_code: Mapped[str] = mapped_column(String(30), nullable=False)
    seasonal_name: Mapped[str] = mapped_column(String(50), nullable=False)
    y1_continuous: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    score_seasonal: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    seasonal_membership: Mapped[dict] = mapped_column(JSON, nullable=False)
    fired_rules: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("y1_continuous >= 0 AND y1_continuous <= 3", name="ck_y1_range"),
        CheckConstraint("score_seasonal >= 0 AND score_seasonal <= 1", name="ck_score_seasonal_range"),
    )

    skin_characteristic = relationship("SkinCharacteristic", back_populates="seasonal_results")
    color_match_scores: Mapped[List["ColorMatchScore"]] = relationship(
        "ColorMatchScore", back_populates="seasonal_result", cascade="all,delete-orphan"
    )
    product_match_filters: Mapped[List["ProductMatchFilter"]] = relationship(
        "ProductMatchFilter", back_populates="seasonal_result", cascade="all,delete-orphan"
    )
