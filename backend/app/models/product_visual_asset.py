from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, CheckConstraint, Index, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


class ProductVisualAsset(Base):
    """Aset visual produk untuk kebutuhan virtual try-on (PRD 11.3).

    anchor_config menyimpan anotasi posisi kepala pada foto produk:
    {"cx": .., "cy": .., "w": ..} sebagai fraksi lebar/tinggi foto
    (cy negatif berarti kepala berada di atas tepi foto, untuk foto model tanpa kepala).
    """

    __tablename__ = "product_visual_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    asset_url: Mapped[str] = mapped_column(String(500), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(30), default="IMAGE", nullable=False)
    dominant_color_hex: Mapped[Optional[str]] = mapped_column(String(9), nullable=True)
    anchor_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("asset_type IN ('IMAGE','SWATCH','TEMPLATE')", name="ck_visual_asset_type"),
        Index("idx_visual_assets_product", "product_id", "is_active"),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="visual_assets")
