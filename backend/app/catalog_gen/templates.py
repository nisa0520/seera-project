"""Reference-template registry.

Every generated image is a recolor of one existing template asset. Geometry,
framing, background and face anchors are **inherited** from the template's
hand-authored spec below, read-only — recoloring changes colour only.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

from app.catalog_gen import paths


# Garment-type taxonomy derived from the template filename (FR-DATA-02): category
# and target_gender come from the template type, never randomly.
_GARMENT_RULES = (
    ("koko", "Koko", "Atasan", "MALE"),
    ("gamis", "Gamis", "Dress", "FEMALE"),
    ("abaya", "Abaya", "Dress", "FEMALE"),
    ("hijab", "Hijab", "Aksesoris", "FEMALE"),
)

# Hand-authored per-template specs: face anchor box (cx, cy, w as fraction of the
# photo's dimensions) for masking, plus category/view/quality metadata used to
# weight which templates get recolored most often (prefer clean front full-garment
# shots; quality doubles as the sampling weight since higher-quality templates
# make better recolor bases).
_TEMPLATE_SPECS = {
    "/koko-putih.png":  {"cx": 0.47,  "cy": -0.145, "w": 0.28,  "category": "upper", "view": "FRONT",   "quality": 0.92, "notes": "Foto depan, garment utuh, background bersih."},
    "/koko-abu.png":    {"cx": 0.55,  "cy": -0.045, "w": 0.25,  "category": "upper", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/koko-biru.png":   {"cx": 0.42,  "cy": -0.135, "w": 0.30,  "category": "upper", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/koko-hijau.png":  {"cx": 0.39,  "cy": -0.165, "w": 0.30,  "category": "upper", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/koko-coklat.png": {"cx": 0.45,  "cy": -0.075, "w": 0.22,  "category": "upper", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/koko-bt.png":     {"cx": 0.42,  "cy": -0.125, "w": 0.28,  "category": "upper", "view": "ANGLED",  "quality": 0.62, "notes": "Foto motif batik dengan angle sedikit miring."},
    "/koko-t.png":      {"cx": 0.50,  "cy": 0.11,   "w": 0.22,  "category": "upper", "view": "FRONT",   "quality": 0.85, "notes": "Foto depan."},
    "/koko-w.png":      {"cx": 0.56,  "cy": -0.055, "w": 0.24,  "category": "upper", "view": "FRONT",   "quality": 0.85, "notes": "Foto depan, tekstur waffle."},
    # Foto detail close-up: garment tidak utuh -> kualitas rendah.
    "/koko.png":        {"cx": 0.55,  "cy": -0.17,  "w": 0.42,  "category": "upper", "view": "PARTIAL", "quality": 0.40, "notes": "Foto close-up parsial; garment tidak utuh."},
    "/abaya-hitam.png": {"cx": 0.56,  "cy": -0.03,  "w": 0.22,  "category": "dress", "view": "FRONT",   "quality": 0.65, "notes": "Warna gelap, detail kurang kontras."},
    "/gamis-pink.png":  {"cx": 0.475, "cy": 0.05,   "w": 0.145, "category": "dress", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    # Angle menyamping signifikan -> kualitas rendah.
    "/gamis-coklat.png": {"cx": 0.34, "cy": 0.08,   "w": 0.23,  "category": "dress", "view": "ANGLED",  "quality": 0.45, "notes": "Angle menyamping signifikan."},
    "/gamis-p.png":     {"cx": 0.50,  "cy": 0.07,   "w": 0.15,  "category": "dress", "view": "FRONT",   "quality": 0.90, "notes": "Foto depan, garment utuh."},
    "/gamis.png":       {"cx": 0.47,  "cy": -0.055, "w": 0.20,  "category": "dress", "view": "FRONT",   "quality": 0.88, "notes": "Foto depan, garment utuh."},
    "/abaya.png":       {"cx": 0.41,  "cy": 0.01,   "w": 0.22,  "category": "dress", "view": "FRONT",   "quality": 0.66, "notes": "Detail garment kurang tajam."},
    # Aksesoris kepala.
    "/hijab.png":       {"cx": 0.33,  "cy": 0.375,  "w": 0.38,  "category": None,    "view": "FRONT",   "quality": 0.10, "notes": "Aksesoris kepala."},
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
    anchor: dict            # inherited face-box anchor {cx, cy, w}
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
    for image_url, spec in _TEMPLATE_SPECS.items():
        key, garment, category, gender = _classify(image_url)
        quality = float(spec.get("quality", 0.5))
        templates.append(
            Template(
                image_url=image_url,
                key=key,
                garment_word=garment,
                category=category,
                target_gender=gender,
                anchor={"cx": spec["cx"], "cy": spec["cy"], "w": spec["w"]},
                garment_category=spec.get("category"),
                view_angle=spec.get("view", "FRONT"),
                base_quality=quality,
                notes=spec.get("notes", ""),
                weight=quality,
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
