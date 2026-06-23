"""Seed aset visual produk untuk virtual try-on berbasis foto produk asli.

asset_url menunjuk ke cutout PNG transparan hasil preprocessing
(scripts/generate_tryon_cutouts.py) di public/tryon/ — kanvas berukuran sama
dengan foto asli sehingga anchor tetap berlaku.

anchor_config dianotasi manual per foto produk: posisi pusat (cx, cy) dan lebar (w)
box wajah pengguna sebagai fraksi dimensi foto (wajah menempati ~70% lebar box).
cy negatif berarti kepala berada di atas tepi foto (foto model tanpa kepala —
kerah di tepi atas).
"""
import os

from sqlalchemy.orm import Session as DBSession

from app.models.product import Product
from app.models.product_visual_asset import ProductVisualAsset


# Kunci = image_url produk pada katalog.
# mode ABOVE: kepala pengguna (siluet alpha asli) ditempatkan di atas kerah —
#   skala disesuaikan lebar kepala terukur, dagu dikunci ke garis kerah.
# mode OVERLAY: wajah pengguna (mask oval) menggantikan wajah model di dalam
#   hijab/penutup kepala pada foto.
FACE_ANCHORS = {
    "/koko-putih.png":  {"cx": 0.47,  "cy": -0.145, "w": 0.28,  "mode": "ABOVE"},
    "/koko-abu.png":    {"cx": 0.55,  "cy": -0.045, "w": 0.25,  "mode": "ABOVE"},
    "/koko-biru.png":   {"cx": 0.42,  "cy": -0.135, "w": 0.30,  "mode": "ABOVE"},
    "/koko-hijau.png":  {"cx": 0.39,  "cy": -0.165, "w": 0.30,  "mode": "ABOVE"},
    "/koko-coklat.png": {"cx": 0.45,  "cy": -0.075, "w": 0.22,  "mode": "ABOVE"},
    "/koko-bt.png":     {"cx": 0.42,  "cy": -0.125, "w": 0.28,  "mode": "ABOVE"},
    "/koko-t.png":      {"cx": 0.50,  "cy": 0.11,   "w": 0.22,  "mode": "ABOVE"},
    "/koko-w.png":      {"cx": 0.56,  "cy": -0.055, "w": 0.24,  "mode": "ABOVE"},
    "/koko.png":        {"cx": 0.55,  "cy": -0.17,  "w": 0.42,  "mode": "ABOVE"},
    "/abaya-hitam.png": {"cx": 0.56,  "cy": -0.03,  "w": 0.22,  "mode": "OVERLAY"},
    "/gamis-pink.png":  {"cx": 0.475, "cy": 0.05,   "w": 0.145, "mode": "OVERLAY"},
    "/gamis-coklat.png": {"cx": 0.34, "cy": 0.08,   "w": 0.23,  "mode": "OVERLAY"},
    "/gamis-p.png":     {"cx": 0.50,  "cy": 0.07,   "w": 0.15,  "mode": "OVERLAY"},
    "/gamis.png":       {"cx": 0.47,  "cy": -0.055, "w": 0.20,  "mode": "ABOVE"},
    "/abaya.png":       {"cx": 0.41,  "cy": 0.01,   "w": 0.22,  "mode": "OVERLAY"},
    "/hijab.png":       {"cx": 0.33,  "cy": 0.375,  "w": 0.38,  "mode": "OVERLAY"},
}


# --- Additive: inherit anchors for generated variants (optional, data-only) ----
# Generated products are recolors of templates, so they inherit the template's anchor
# (canvas/geometry identical). Merged in by data; seed_visual_assets() is unchanged.
# Gated by SEED_INCLUDE_GENERATED (default on) — consistent with seed_catalog_dummy.
if os.getenv("SEED_INCLUDE_GENERATED", "1").strip().lower() not in ("0", "false", "no"):
    try:
        from app.seed.generated.generated_products import (
            GENERATED_FACE_ANCHORS as _GENERATED_FACE_ANCHORS,
        )
        FACE_ANCHORS = {**FACE_ANCHORS, **_GENERATED_FACE_ANCHORS}
    except ImportError:
        pass


def _cutout_url(image_url: str) -> str:
    return "/tryon/" + image_url.lstrip("/")


def seed_visual_assets(db: DBSession) -> None:
    products = db.query(Product).filter(Product.image_url.isnot(None)).all()
    for product in products:
        anchor = FACE_ANCHORS.get(product.image_url)
        if anchor is None:
            continue
        existing = (
            db.query(ProductVisualAsset)
            .filter(
                ProductVisualAsset.product_id == product.id,
                ProductVisualAsset.asset_type == "IMAGE",
            )
            .first()
        )
        dominant = None
        colors_sorted = sorted(product.product_colors, key=lambda pc: pc.color_rank)
        if colors_sorted:
            dominant = colors_sorted[0].color.hex_code

        if existing:
            existing.asset_url = _cutout_url(product.image_url)
            existing.anchor_config = anchor
            existing.dominant_color_hex = dominant
            existing.is_active = True
        else:
            db.add(
                ProductVisualAsset(
                    product_id=product.id,
                    asset_url=_cutout_url(product.image_url),
                    asset_type="IMAGE",
                    dominant_color_hex=dominant,
                    anchor_config=anchor,
                    is_active=True,
                )
            )
    db.commit()
