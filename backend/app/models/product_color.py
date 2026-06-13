from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class ProductColor(Base):
    __tablename__ = "product_colors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id", ondelete="RESTRICT"), nullable=False)
    color_role: Mapped[str] = mapped_column(String(30), nullable=False)
    color_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    color_percentage: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("color_role IN ('DOMINANT','SECONDARY','MOTIF','ACCENT')", name="ck_product_color_role"),
        CheckConstraint("color_rank BETWEEN 1 AND 4", name="ck_product_color_rank"),
        CheckConstraint(
            "color_percentage IS NULL OR (color_percentage >= 0 AND color_percentage <= 100)",
            name="ck_product_color_percentage",
        ),
        UniqueConstraint("product_id", "color_rank", name="uq_product_color_rank"),
        UniqueConstraint("product_id", "color_role", name="uq_product_color_role"),
        Index("idx_product_colors_product_rank", "product_id", "color_rank"),
    )

    product = relationship("Product", back_populates="product_colors")
    color = relationship("Color", back_populates="product_colors")
    color_match_scores: Mapped[List["ColorMatchScore"]] = relationship(
        "ColorMatchScore", back_populates="product_color", cascade="all,delete-orphan"
    )
