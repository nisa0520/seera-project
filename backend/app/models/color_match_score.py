from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, JSON, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class ColorMatchScore(Base):
    __tablename__ = "color_match_scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    seasonal_result_id: Mapped[int] = mapped_column(
        ForeignKey("seasonal_results.id", ondelete="CASCADE"), nullable=False
    )
    product_color_id: Mapped[int] = mapped_column(ForeignKey("product_colors.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id", ondelete="RESTRICT"), nullable=False)
    match_color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)
    ct: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    cb: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    suitable_score_color: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    suitability_label: Mapped[str] = mapped_column(String(30), nullable=False)
    ct_membership: Mapped[dict] = mapped_column(JSON, nullable=False)
    cb_membership: Mapped[dict] = mapped_column(JSON, nullable=False)
    fired_rules: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "suitable_score_color >= 0 AND suitable_score_color <= 1", name="ck_color_match_score_range"
        ),
        Index("idx_color_match_seasonal", "seasonal_result_id"),
    )

    seasonal_result = relationship("SeasonalResult", back_populates="color_match_scores")
    product_color = relationship("ProductColor", back_populates="color_match_scores")
    color = relationship("Color")
