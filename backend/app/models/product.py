from datetime import datetime
from sqlalchemy import String, Numeric, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_catalog_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    popularity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    target_gender: Mapped[str] = mapped_column(String(30), default="UNISEX", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_product_price_nonneg"),
        CheckConstraint("rating IS NULL OR (rating >= 0 AND rating <= 5)", name="ck_product_rating_range"),
        CheckConstraint("popularity >= 0", name="ck_product_popularity_nonneg"),
        CheckConstraint("stock >= 0", name="ck_product_stock_nonneg"),
        CheckConstraint("target_gender IN ('MALE','FEMALE','UNISEX')", name="ck_product_target_gender"),
        Index("idx_products_available", "is_active", "stock", "rating", "price"),
        Index("idx_products_target_gender", "target_gender", "is_active", "stock"),
    )

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    product_colors: Mapped[List["ProductColor"]] = relationship(
        "ProductColor", back_populates="product", cascade="all,delete-orphan"
    )
