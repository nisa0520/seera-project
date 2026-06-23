"""VTONEligibilityService: VTON Asset Eligibility Tier (FR-VTO-15/16/17).

Setiap produk/varian diklasifikasikan ke salah satu tier sebelum inference:

- vton_ready        : aset ideal (tampak depan, garment utuh, background bersih,
                      SKU/warna benar) — try-on realistis tanpa warning.
- vton_experimental : foto seadanya namun masih layak — jalan hanya setelah
                      konfirmasi pengguna; hasil dilabeli "Preview Eksperimental".
- vton_limited      : foto kurang ideal namun masih terbaca — jalan hanya bila
                      experimental mode diaktifkan; warning lebih kuat.
- vton_not_supported: aset hilang/rusak/terlalu ter-crop/blur/salah produk —
                      tidak boleh memanggil model VTON.

Produk tetap berasal dari katalog internal (BR-VTO-06) dan kelayakan ini tidak
memengaruhi hasil rekomendasi FIS/ROC (BR-VTO-11).
"""
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.product import Product
from app.models.product_vton_asset import (
    TIER_READY,
    TIER_EXPERIMENTAL,
    TIER_LIMITED,
    TIER_NOT_SUPPORTED,
    TIER_TO_QUALITY_MODE,
)


WARNING_EXPERIMENTAL = (
    "Foto produk ini belum memenuhi standar aset virtual try-on, sehingga hasil "
    "preview AI dapat berbeda dari produk asli."
)
WARNING_LIMITED = (
    "Kualitas aset produk ini terbatas. Hasil preview AI kemungkinan besar berbeda "
    "dari produk asli dan hanya bersifat eksperimental."
)
MESSAGE_READY = "Produk ini mendukung realistic virtual try-on."
REASON_NOT_SUPPORTED = (
    "Aset garment belum tersedia atau tidak layak untuk virtual try-on."
)


class VTONEligibilityService:
    def __init__(self, db: DBSession):
        self.db = db

    def _resolve_tier(self, product: Product) -> str:
        """Tentukan tier efektif dengan mempertimbangkan ketersediaan aset & stok."""
        asset = product.vton_asset
        if asset is None:
            return TIER_NOT_SUPPORTED

        tier = asset.vton_asset_tier or TIER_NOT_SUPPORTED

        # Tier apa pun selain not_supported wajib punya garment image valid.
        if tier != TIER_NOT_SUPPORTED and not asset.garment_vton_image_url:
            return TIER_NOT_SUPPORTED

        # Produk nonaktif / stok kosong tidak ditawarkan try-on (metrik 17.3).
        if product.stock <= 0 or not product.is_active:
            return TIER_NOT_SUPPORTED

        # Experimental/limited hanya boleh bila mode experimental diaktifkan.
        if tier in (TIER_EXPERIMENTAL, TIER_LIMITED) and not settings.VTON_ALLOW_EXPERIMENTAL_ASSET_MODE:
            return TIER_NOT_SUPPORTED

        return tier

    def check(self, product: Product) -> dict:
        """Response eligibility lengkap (API-VTO-01) sesuai PRD AssetTier bagian 6."""
        asset = product.vton_asset
        tier = self._resolve_tier(product)
        quality_mode = TIER_TO_QUALITY_MODE[tier]
        supported = tier != TIER_NOT_SUPPORTED

        warning = None
        requires_confirmation = False
        reason = None
        message = MESSAGE_READY

        if tier == TIER_EXPERIMENTAL:
            warning = WARNING_EXPERIMENTAL
            requires_confirmation = True
            message = WARNING_EXPERIMENTAL
        elif tier == TIER_LIMITED:
            warning = WARNING_LIMITED
            requires_confirmation = True
            message = WARNING_LIMITED
        elif tier == TIER_NOT_SUPPORTED:
            reason = REASON_NOT_SUPPORTED
            message = "Virtual try-on belum tersedia untuk produk ini."

        return {
            "product_id": product.id,
            # variant_id diisi pemanggil bila varian spesifik dipilih (BR-VTO-16)
            "variant_id": None,
            "vton_supported": supported,
            # Field legacy untuk kompatibilitas frontend lama:
            "vton_ready": tier == TIER_READY,
            "vton_status": asset.vton_status if asset else "NOT_SUPPORTED",
            "vton_asset_tier": tier,
            "tryon_quality_mode": quality_mode,
            "garment_category": asset.garment_category if asset else None,
            "garment_vton_image_url": (
                asset.garment_vton_image_url if (asset and supported) else None
            ),
            "vton_view_angle": asset.view_angle if asset else None,
            "vton_asset_quality_score": (
                float(asset.vton_asset_quality_score)
                if (asset and asset.vton_asset_quality_score is not None)
                else None
            ),
            "quality_warning_message": warning,
            "requires_user_confirmation_for_experimental_mode": requires_confirmation,
            "reason_if_not_supported": reason,
            "message": message,
        }

    def resolve_tier(self, product: Product) -> str:
        return self._resolve_tier(product)

    @staticmethod
    def status_for_item(product: Product) -> dict:
        """Ringkasan tier untuk kartu produk rekomendasi (UI 16.1)."""
        asset = product.vton_asset
        tier = asset.vton_asset_tier if asset else TIER_NOT_SUPPORTED
        has_asset = bool(asset and asset.garment_vton_image_url and product.stock > 0 and product.is_active)
        if not has_asset:
            tier = TIER_NOT_SUPPORTED
        return {
            "vton_ready": tier == TIER_READY,
            "vton_asset_tier": tier,
            "tryon_quality_mode": TIER_TO_QUALITY_MODE[tier],
            "vton_supported": tier != TIER_NOT_SUPPORTED,
        }
