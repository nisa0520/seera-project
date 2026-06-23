"""Derive Visual + VTON asset inheritance data for a generated product.

Because a generated variant is a *recolor of a known template*, its geometry, framing,
background, anchors and try-on suitability are inherited from the template — recoloring
changes colour only. We never re-estimate geometry and never upgrade a tier.

The data here is consumed by the **unchanged** ``seed_visual_assets`` / ``seed_vton_assets``
through additive ``FACE_ANCHORS`` / ``VTON_ASSET_SEED`` entries keyed on the generated
``image_url``. Those seeds then derive ``dominant_color_hex`` (rank-1 colour), resolve
``asset_url`` / ``garment_vton_image_url`` via the existing ``_cutout_url`` / ``_garment_url``
helpers, and apply the existing tier→status/quality-mode mappings — all with no logic change.
"""
from __future__ import annotations

from app.catalog_gen.config import GenConfig
from app.catalog_gen.data_gen import ProductSpec
from app.models.product_vton_asset import TIER_NOT_SUPPORTED


def catalog_url(external_catalog_id: str) -> str:
    """The catalog ``image_url`` (served from ``public/generated/``)."""
    return f"/generated/{external_catalog_id}.png"


def visual_anchor_entry(spec: ProductSpec):
    """(image_url, anchor_config) inherited from the template's FACE_ANCHORS entry."""
    return catalog_url(spec.external_catalog_id), dict(spec.template.anchor)


def vton_seed_entry(spec: ProductSpec, cfg: GenConfig):
    """(image_url, vton_spec) inheriting the template's tier/category/view (never upgraded)."""
    t = spec.template
    # Quality score never exceeds the base; apply a small synthetic-recolor penalty.
    quality = round(max(0.0, t.base_quality - cfg.synthetic_quality_penalty), 3)
    note = (
        f"Sintetis (recolor dari {t.image_url}); tier & geometri diwarisi dari template "
        f"dan tidak di-upgrade."
    )
    if t.tier == TIER_NOT_SUPPORTED:
        note = f"Sintetis (recolor dari {t.image_url}); aksesoris kepala tetap NOT_SUPPORTED."
    return catalog_url(spec.external_catalog_id), {
        "tier": t.tier,
        "category": t.garment_category,
        "view": t.view_angle,
        "quality": quality,
        "notes": note,
    }


def supports_vton_garment(spec: ProductSpec) -> bool:
    """Whether a clean VTON garment cutout should be emitted (NOT_SUPPORTED gets none)."""
    return spec.template.tier != TIER_NOT_SUPPORTED
