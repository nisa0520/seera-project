from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class ProductMatchFilter(Base):
    __tablename__ = "product_match_filters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    seasonal_result_id: Mapped[int] = mapped_column(
        ForeignKey("seasonal_results.id", ondelete="CASCADE"), nullable=False
    )
    recommendation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=True
    )
    match_product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_color: Mapped[float] = mapped_column(Numeric(4, 0), nullable=False)
    dominant_roc: Mapped[Optional[float]] = mapped_column(Numeric(8, 6), nullable=True)
    secondary_roc: Mapped[Optional[float]] = mapped_column(Numeric(8, 6), nullable=True)
    motif_roc: Mapped[Optional[float]] = mapped_column(Numeric(8, 6), nullable=True)
    accent_roc: Mapped[Optional[float]] = mapped_column(Numeric(8, 6), nullable=True)
    total_roc_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    suitability_label: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("total_roc_score >= 0 AND total_roc_score <= 1", name="ck_product_match_total_score"),
        Index("idx_product_match_recommendation", "recommendation_id", "total_roc_score"),
    )

    product = relationship("Product")
    seasonal_result = relationship("SeasonalResult", back_populates="product_match_filters")
    recommendation = relationship("Recommendation", back_populates="product_match_filters")
    recommendation_items: Mapped[List["RecommendationItem"]] = relationship(
        "RecommendationItem", back_populates="product_match_filter", cascade="all,delete-orphan"
    )
