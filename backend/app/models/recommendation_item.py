from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    product_match_filter_id: Mapped[int] = mapped_column(
        ForeignKey("product_match_filters.id", ondelete="CASCADE"), nullable=False
    )
    rank_number: Mapped[int] = mapped_column(Integer, nullable=False)
    product_score: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    product_rank_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    price_snapshot: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rating_snapshot: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    stock_snapshot: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("rank_number > 0", name="ck_recommendation_item_rank"),
        CheckConstraint("product_score >= 0 AND product_score <= 1", name="ck_recommendation_item_score"),
        UniqueConstraint("recommendation_id", "rank_number", name="uq_recommendation_item_rank"),
        UniqueConstraint("recommendation_id", "product_id", name="uq_recommendation_item_product"),
        Index("idx_recommendation_items_rank", "recommendation_id", "rank_number"),
    )

    recommendation = relationship("Recommendation", back_populates="items")
    product = relationship("Product")
    product_match_filter = relationship("ProductMatchFilter", back_populates="recommendation_items")
