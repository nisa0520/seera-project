"""Reference-template registry.

Every generated image is a recolor of one existing template asset. Geometry,
framing, background, face anchors and VTON eligibility tier are **inherited** from
the template's existing seed entries (``FACE_ANCHORS`` + ``VTON_ASSET_SEED``),
imported read-only — recoloring changes colour only and can never upgrade a tier.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from app.catalog_gen import paths
from app.seed.seed_visual_assets import FACE_ANCHORS
from app.seed.seed_vton_assets import VTON_ASSET_SEED
from app.models.product_vton_asset import (
    TIER_READY,
    TIER_EXPERIMENTAL,
    TIER_LIMITED,
    TIER_NOT_SUPPORTED,
)


# Garment-type taxonomy derived from the template filename (FR-DATA-02): category
# and target_gender come from the template type, never randomly.
_GARMENT_RULES = (
    ("koko", "Koko", "Atasan", "MALE"),
    ("gamis", "Gamis", "Dress", "FEMALE"),
    ("abaya", "Abaya", "Dress", "FEMALE"),
    ("hijab", "Hijab", "Aksesoris", "FEMALE"),
)

# Prefer clean front full-garment (vton_ready) templates as primary recolor bases;
# recoloring cannot fix a bad angle/crop, so lesser tiers are sampled less often.
_TIER_WEIGHT = {
    TIER_READY: 1.0,
    TIER_EXPERIMENTAL: 0.4,
    TIER_LIMITED: 0.3,
    TIER_NOT_SUPPORTED: 0.15,
}


def _classify(image_url: str) -> tuple:
    stem = image_url.lstrip("/").lower()
    for key, garment, category, gender in _GARMENT_RULES:
        if stem.startswith(key):
            return key, garment, category, gender
    raise ValueError(f"Unknown garment type for template {image_url!r}")


@dataclass(frozen=True)
class Template:
    image_url: str          # e.g. "/koko-putih.png" (the template's catalog url)
    key: str                # garment type key: koko/gamis/abaya/hijab
    garment_word: str       # human label: Koko/Gamis/Abaya/Hijab
    category: str           # Atasan/Dress/Aksesoris
    target_gender: str      # MALE/FEMALE
    anchor: dict            # inherited FACE_ANCHORS entry
    tier: str               # inherited VTON tier (never upgraded downstream)
    garment_category: Optional[str]  # upper/dress/... (None for hijab)
    view_angle: str
    base_quality: float
    notes: str
    weight: float

    @property
    def source_image_path(self) -> Path:
        return paths.url_to_template_image(self.image_url)

    @property
    def source_cutout_path(self) -> Path:
        return paths.url_to_template_cutout(self.image_url)

    @property
    def mask_key(self) -> str:
        return self.image_url.lstrip("/").rsplit(".", 1)[0]


def build_templates() -> List[Template]:
    templates: List[Template] = []
    for image_url, spec in VTON_ASSET_SEED.items():
        # Skip generated variants that may have been additively merged into the seed
        # lookups — only the original hand-authored assets are recolor templates.
        if image_url.startswith("/generated/"):
            continue
        anchor = FACE_ANCHORS.get(image_url)
        if anchor is None:
            # A template without a face anchor cannot inherit try-on geometry; skip.
            continue
        key, garment, category, gender = _classify(image_url)
        tier = spec["tier"]
        templates.append(
            Template(
                image_url=image_url,
                key=key,
                garment_word=garment,
                category=category,
                target_gender=gender,
                anchor=dict(anchor),
                tier=tier,
                garment_category=spec.get("category"),
                view_angle=spec.get("view", "FRONT"),
                base_quality=float(spec.get("quality", 0.5)),
                notes=spec.get("notes", ""),
                weight=_TIER_WEIGHT.get(tier, 0.3),
            )
        )
    templates.sort(key=lambda t: t.image_url)  # stable order for determinism
    return templates


class TemplateRegistry:
    def __init__(self, limit_templates: Optional[Sequence[str]] = None):
        all_t = build_templates()
        if limit_templates:
            wanted = {x.strip().lower() for x in limit_templates if x.strip()}
            all_t = [t for t in all_t if t.key in wanted]
            if not all_t:
                raise ValueError(f"No templates match limit {sorted(wanted)!r}")
        self.templates = all_t
        self._by_url: Dict[str, Template] = {t.image_url: t for t in all_t}
        weights = np.array([t.weight for t in all_t], dtype=np.float64)
        self._probs = weights / weights.sum()

    def choose(self, rng: np.random.RandomState) -> Template:
        idx = int(rng.choice(len(self.templates), p=self._probs))
        return self.templates[idx]

    def by_url(self, image_url: str) -> Template:
        return self._by_url[image_url]
