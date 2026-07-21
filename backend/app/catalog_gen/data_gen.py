"""Colour-first product *data* generation (deterministic, schema-valid).

Colour metadata is the single source of truth and is generated first; the image is
produced from it later. Everything is driven by a stable per-product seed so the same
``external_catalog_id`` always yields the same record.

Role mapping note (schema-driven): the DB enforces ``color_rank BETWEEN 1 AND 3`` *and*
``UNIQUE(product_id, color_role)``, so a product may have at most three colours (rule
of three / 60-30-10, Subbab IV.2.7.5), mapped rank -> role as DOMINANT / SECONDARY /
ACCENT.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from app.catalog_gen.config import GenConfig, ID_PREFIX, ID_WIDTH
from app.catalog_gen.palette import Palette, PaletteColor
from app.catalog_gen.rng import Deterministic
from app.catalog_gen.templates import Template, TemplateRegistry

# Rank (1-based) -> role. Index 0 unused. Maks 3 warna (rule of three).
RANK_ROLE = {1: "DOMINANT", 2: "SECONDARY", 3: "ACCENT"}

# Category-aware price centres/bounds (IDR), rounded to the nearest 5,000.
_PRICE_BANDS = {
    "Atasan": (250000, 70000, 150000, 450000),
    "Dress": (300000, 90000, 180000, 550000),
    "Outerwear": (350000, 90000, 200000, 600000),
    "Bawahan": (200000, 60000, 120000, 400000),
    "Aksesoris": (120000, 45000, 45000, 250000),
}

# Dominant percentage range by colour count (keeps the remainder >= min_share each).
_DOMINANT_RANGE = {2: (62.0, 80.0), 3: (55.0, 72.0)}

_STYLE_WORDS = [
    "Classic", "Modern", "Premium", "Daily", "Elegan", "Minimalis", "Signature",
    "Heritage", "Luxe", "Casual", "Formal", "Earth Tone", "Urban", "Soft", "Bold",
]
_FINISH_WORDS = [
    "Series", "Edition", "Collection", "Look", "Style", "Touch", "Line", "Mode",
]


def external_id(index: int) -> str:
    return f"{ID_PREFIX}{index:0{ID_WIDTH}d}"


@dataclass
class ProductSpec:
    external_catalog_id: str
    template: Template
    colors: List[PaletteColor]      # rank order, index 0 == DOMINANT
    roles: List[str]
    percentages: List[float]
    name: str
    description: str
    price: int
    rating: float
    stock: int
    popularity: int
    is_active: bool

    @property
    def category(self) -> str:
        return self.template.category

    @property
    def target_gender(self) -> str:
        return self.template.target_gender

    def color_tuples(self):
        """(color_name, role, pct) tuples in the exact shape seed_products expects."""
        return [
            (c.name, role, pct)
            for c, role, pct in zip(self.colors, self.roles, self.percentages)
        ]


def _choose_k(rng: np.random.RandomState, cfg: GenConfig) -> int:
    return int(rng.choice([1, 2, 3], p=cfg.color_count_weights()))


def _make_percentages(rng: np.random.RandomState, k: int, min_share: float) -> List[float]:
    if k == 1:
        return [100.0]
    lo, hi = _DOMINANT_RANGE[k]
    dom = float(rng.uniform(lo, hi))
    rest = 100.0 - dom
    base = min_share * (k - 1)
    extra = max(0.0, rest - base)
    weights = np.sort(rng.uniform(0.5, 1.0, size=k - 1))[::-1]
    weights = weights / weights.sum()
    others = [base / (k - 1) + extra * float(w) for w in weights]
    others.sort(reverse=True)
    shares = [dom] + others

    # Round to 1 dp and absorb the residual into the dominant (keeps it the largest).
    shares = [round(s, 1) for s in shares]
    shares[0] = round(shares[0] + (100.0 - sum(shares)), 1)
    # Guard monotonic non-increasing after rounding.
    for i in range(1, len(shares)):
        if shares[i] > shares[i - 1]:
            shares[i] = shares[i - 1]
    shares[0] = round(shares[0] + (100.0 - sum(shares)), 1)
    return shares


def _make_price(rng: np.random.RandomState, category: str) -> int:
    center, spread, lo, hi = _PRICE_BANDS.get(category, _PRICE_BANDS["Atasan"])
    raw = rng.lognormal(mean=np.log(center), sigma=spread / center)
    val = int(round(raw / 5000.0)) * 5000
    return int(min(max(val, lo), hi))


def _make_rating(rng: np.random.RandomState) -> float:
    return round(float(np.clip(5.0 - rng.exponential(0.35), 3.8, 5.0)), 1)


def _make_name(rng: np.random.RandomState, garment: str, dom_color: str) -> str:
    style = _STYLE_WORDS[rng.randint(len(_STYLE_WORDS))]
    if rng.random() < 0.45:
        finish = _FINISH_WORDS[rng.randint(len(_FINISH_WORDS))]
        return f"{garment} {dom_color} {style} {finish}"
    return f"{garment} {dom_color} {style}"


def _make_description(spec_garment: str, image_url: str, colors: List[PaletteColor]) -> str:
    names = [c.name for c in colors]
    if len(names) == 1:
        color_phrase = f"warna {names[0]}"
    else:
        color_phrase = "kombinasi warna " + ", ".join(names[:-1]) + f" dan {names[-1]}"
    return (
        f"{spec_garment} dengan {color_phrase}. Variasi warna sintetis yang dihasilkan "
        f"dari template {image_url} dengan menjaga siluet, tekstur, dan latar aslinya."
    )


def generate_spec(
    index: int,
    cfg: GenConfig,
    palette: Palette,
    registry: TemplateRegistry,
) -> ProductSpec:
    ext_id = external_id(index)
    det = Deterministic(ext_id, salt=cfg.seed)

    template = registry.choose(det.numpy("template"))
    k = _choose_k(det.numpy("kcount"), cfg)
    colors = palette.select(det.numpy("colors"), k, cfg.min_pairwise_delta_e)
    k = len(colors)  # palette.select may clamp
    percentages = _make_percentages(det.numpy("percent"), k, cfg.min_color_share_pp)
    roles = [RANK_ROLE[i + 1] for i in range(k)]

    sc = det.numpy("scalars")
    price = _make_price(sc, template.category)
    rating = _make_rating(sc)
    stock = 0 if sc.random() < 0.08 else int(sc.randint(3, 40))
    popularity = int(sc.randint(20, 250))
    is_active = bool(sc.random() >= 0.03)

    name = _make_name(det.numpy("name"), template.garment_word, colors[0].name)
    description = _make_description(template.garment_word, template.image_url, colors)

    return ProductSpec(
        external_catalog_id=ext_id,
        template=template,
        colors=colors,
        roles=roles,
        percentages=percentages,
        name=name,
        description=description,
        price=price,
        rating=rating,
        stock=stock,
        popularity=popularity,
        is_active=is_active,
    )
