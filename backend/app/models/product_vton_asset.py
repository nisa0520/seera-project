from datetime import datetime
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.core.database import Base


# Status governance legacy (BR-VTO-12) — dipertahankan untuk kompatibilitas.
VTON_STATUS_READY = "READY"
VTON_STATUS_PENDING = "PENDING"
VTON_STATUS_NOT_SUPPORTED = "NOT_SUPPORTED"

# VTON Asset Eligibility Tier (FR-VTO-15, BR-VTO-22) — sumber kebenaran kelayakan.
TIER_READY = "vton_ready"
TIER_EXPERIMENTAL = "vton_experimental"
TIER_LIMITED = "vton_limited"
TIER_NOT_SUPPORTED = "vton_not_supported"

# Mode kualitas try-on diturunkan dari tier (FR-VTO-16).
QUALITY_MODE_REALISTIC = "realistic"
QUALITY_MODE_EXPERIMENTAL = "experimental"
QUALITY_MODE_LIMITED = "limited"
QUALITY_MODE_BLOCKED = "blocked"

TIER_TO_QUALITY_MODE = {
    TIER_READY: QUALITY_MODE_REALISTIC,
    TIER_EXPERIMENTAL: QUALITY_MODE_EXPERIMENTAL,
    TIER_LIMITED: QUALITY_MODE_LIMITED,
    TIER_NOT_SUPPORTED: QUALITY_MODE_BLOCKED,
}


class ProductVtonAsset(Base):
    """Aset garment khusus VTON per produk (PRD AssetTier 12.2, BR-VTO-03/04/12/22).

    garment_vton_image_url adalah aset terstandar untuk model VTON — terpisah
    dari product_image katalog. Tier kelayakan (vton_asset_tier) menentukan
    apakah produk dapat menjalankan try-on realistis, experimental, limited,
    atau diblokir total.
    """

    __tablename__ = "product_vton_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    garment_vton_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    garment_category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    garment_caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    view_angle: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    background_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    asset_quality_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    vton_status: Mapped[str] = mapped_column(String(30), default=VTON_STATUS_PENDING, nullable=False)
    # ---- Asset Eligibility Tier (FR-VTO-15) ----
    vton_asset_tier: Mapped[str] = mapped_column(String(30), default=TIER_NOT_SUPPORTED, nullable=False)
    tryon_quality_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    vton_asset_quality_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    asset_validation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_compatibility: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "vton_status IN ('READY','PENDING','NOT_SUPPORTED')",
            name="ck_vton_asset_status",
        ),
        CheckConstraint(
            "vton_asset_tier IN ('vton_ready','vton_experimental','vton_limited','vton_not_supported')",
            name="ck_vton_asset_tier",
        ),
        CheckConstraint(
            "garment_category IS NULL OR garment_category IN ('upper','lower','dress','outer')",
            name="ck_vton_garment_category",
        ),
        Index("idx_vton_assets_product", "product_id", "vton_status"),
    )

    product: Mapped["Product"] = relationship("Product", back_populates="vton_asset")
