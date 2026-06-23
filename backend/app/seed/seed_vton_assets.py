"""Seed aset garment VTON per produk dengan VTON Asset Eligibility Tier
(PRD AssetTier 12.2, FR-VTO-15, BR-VTO-12/22).

garment_vton_image adalah aset terstandar untuk model VTON (BR-VTO-04 —
bukan product_image katalog): background sudah dibersihkan (cutout transparan)
dan disajikan backend di /api/v1/vton/garments/{file}.

Tier kelayakan:
- vton_ready        : foto depan, garment utuh, background bersih -> realistic.
- vton_experimental : foto seadanya (mis. angle ringan) -> butuh konfirmasi.
- vton_limited      : foto kurang ideal (mis. close-up parsial) -> warning kuat.
- vton_not_supported: di luar cloth type / tanpa garment utuh -> diblokir.
"""
import os

from sqlalchemy.orm import Session as DBSession

from app.models.product import Product
from app.models.product_vton_asset import (
    ProductVtonAsset,
    TIER_READY,
    TIER_EXPERIMENTAL,
    TIER_LIMITED,
    TIER_NOT_SUPPORTED,
    TIER_TO_QUALITY_MODE,
    VTON_STATUS_READY,
    VTON_STATUS_PENDING,
    VTON_STATUS_NOT_SUPPORTED,
)


def _garment_url(image_url: str) -> str:
    return "/api/v1/vton/garments/" + image_url.lstrip("/").split("/")[-1]


# Status legacy diturunkan dari tier agar konsisten dengan constraint lama.
_TIER_TO_STATUS = {
    TIER_READY: VTON_STATUS_READY,
    TIER_EXPERIMENTAL: VTON_STATUS_PENDING,
    TIER_LIMITED: VTON_STATUS_PENDING,
    TIER_NOT_SUPPORTED: VTON_STATUS_NOT_SUPPORTED,
}


# Kunci = image_url produk katalog.
VTON_ASSET_SEED = {
    "/koko-putih.png":  {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.92, "notes": "Foto depan, garment utuh, background bersih."},
    "/koko-abu.png":    {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/koko-biru.png":   {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/koko-hijau.png":  {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/koko-coklat.png": {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/koko-bt.png":     {"tier": TIER_EXPERIMENTAL, "category": "upper", "view": "ANGLED",  "quality": 0.62, "notes": "Foto motif batik dengan angle sedikit miring."},
    "/koko-t.png":      {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.85, "notes": "Foto depan."},
    "/koko-w.png":      {"tier": TIER_READY,        "category": "upper", "view": "FRONT",   "quality": 0.85, "notes": "Foto depan, tekstur waffle."},
    # Foto detail close-up: garment tidak utuh -> limited (warning kuat)
    "/koko.png":        {"tier": TIER_LIMITED,      "category": "upper", "view": "PARTIAL", "quality": 0.40, "notes": "Foto close-up parsial; garment tidak utuh."},
    "/abaya-hitam.png": {"tier": TIER_EXPERIMENTAL, "category": "dress", "view": "FRONT",   "quality": 0.65, "notes": "Warna gelap, detail kurang kontras."},
    "/gamis-pink.png":  {"tier": TIER_READY,        "category": "dress", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    # Angle menyamping signifikan -> limited
    "/gamis-coklat.png": {"tier": TIER_LIMITED,     "category": "dress", "view": "ANGLED",  "quality": 0.45, "notes": "Angle menyamping signifikan."},
    "/gamis-p.png":     {"tier": TIER_READY,        "category": "dress", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/gamis.png":       {"tier": TIER_READY,        "category": "dress", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/abaya.png":       {"tier": TIER_EXPERIMENTAL, "category": "dress", "view": "FRONT",   "quality": 0.66, "notes": "Detail garment kurang tajam."},
    # Aksesoris kepala: di luar cloth type model (upper/lower/overall)
    "/hijab.png":       {"tier": TIER_NOT_SUPPORTED, "category": None,   "view": "FRONT",   "quality": 0.10, "notes": "Aksesoris kepala, di luar cloth type VTON."},
}


# --- Additive: inherit VTON specs for generated variants (optional, data-only) -
# Each generated entry inherits its template's tier/category/view (never upgraded),
# with a small synthetic-recolor quality penalty. Merged by data; the existing
# tier->status / quality-mode mappings in seed_vton_assets() are unchanged.
# Gated by SEED_INCLUDE_GENERATED (default on) — consistent with seed_catalog_dummy.
if os.getenv("SEED_INCLUDE_GENERATED", "1").strip().lower() not in ("0", "false", "no"):
    try:
        from app.seed.generated.generated_products import (
            GENERATED_VTON_ASSET_SEED as _GENERATED_VTON_ASSET_SEED,
        )
        VTON_ASSET_SEED = {**VTON_ASSET_SEED, **_GENERATED_VTON_ASSET_SEED}
    except ImportError:
        pass


def seed_vton_assets(db: DBSession) -> None:
    products = db.query(Product).filter(Product.image_url.isnot(None)).all()
    for product in products:
        spec = VTON_ASSET_SEED.get(product.image_url)
        if spec is None:
            continue
        tier = spec["tier"]
        existing = (
            db.query(ProductVtonAsset)
            .filter(ProductVtonAsset.product_id == product.id)
            .first()
        )
        # asset_quality_status = token pendek (varchar 30); notes lengkap di kolom Text.
        score = spec["quality"]
        quality_status = "GOOD" if score >= 0.8 else ("FAIR" if score >= 0.6 else "LOW")
        values = {
            "garment_vton_image_url": _garment_url(product.image_url) if tier != TIER_NOT_SUPPORTED else None,
            "garment_category": spec["category"],
            "view_angle": spec["view"],
            "background_status": "CLEAN",
            "asset_quality_status": quality_status,
            "vton_status": _TIER_TO_STATUS[tier],
            "vton_asset_tier": tier,
            "tryon_quality_mode": TIER_TO_QUALITY_MODE[tier],
            "vton_asset_quality_score": spec["quality"],
            "asset_validation_notes": spec["notes"],
            "model_compatibility": "idm-vton,catvton",
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
        else:
            db.add(ProductVtonAsset(product_id=product.id, **values))
    db.commit()
