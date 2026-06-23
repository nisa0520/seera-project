"""Palette loading + harmony-aware colour selection.

Colours are drawn **exclusively** from the existing ``COLORS_SEED`` palette so that
``seed_colors()`` / ``compute_color_features`` are exercised identically (no new
colour logic is introduced). ``compute_color_features`` is imported read-only and
its output (h, s, v, ct, cb) is reused verbatim for harmony grouping; CIELAB values
are computed independently here purely for recolor/QA maths (never fed back into any
existing algorithm).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from skimage.color import rgb2lab, deltaE_ciede2000

# Read-only imports from existing modules.
from app.seed.seed_catalog_dummy import COLORS_SEED
from app.services.color_feature_service import compute_color_features, hex_to_rgb


@dataclass(frozen=True)
class PaletteColor:
    name: str
    hex: str
    rgb: tuple  # (r, g, b) ints
    lab: tuple  # (L, a, b) floats
    h: float
    s: float
    v: float
    ct: float
    cb: float

    @property
    def is_neutral(self) -> bool:
        # Low chroma -> neutral (acts as a flexible pairing partner).
        return self.s < 0.20

    @property
    def temp_family(self) -> str:
        if self.is_neutral:
            return "neutral"
        if self.ct >= 1.2:
            return "warm"
        if self.ct <= 0.8:
            return "cool"
        return "neutral"


def _lab_of(rgb: tuple) -> tuple:
    arr = np.array(rgb, dtype=np.float64).reshape(1, 1, 3) / 255.0
    lab = rgb2lab(arr)[0, 0]
    return (float(lab[0]), float(lab[1]), float(lab[2]))


def delta_e(a: PaletteColor, b: PaletteColor) -> float:
    la = np.array(a.lab, dtype=np.float64).reshape(1, 3)
    lb = np.array(b.lab, dtype=np.float64).reshape(1, 3)
    return float(deltaE_ciede2000(la, lb)[0])


class Palette:
    def __init__(self, entries: Sequence[dict] = COLORS_SEED):
        self.colors: List[PaletteColor] = []
        for e in entries:
            rgb = hex_to_rgb(e["hex"])
            feats = compute_color_features(e["hex"])
            self.colors.append(
                PaletteColor(
                    name=e["name"],
                    hex=e["hex"],
                    rgb=rgb,
                    lab=_lab_of(rgb),
                    h=feats["h"], s=feats["s"], v=feats["v"],
                    ct=feats["ct"], cb=feats["cb"],
                )
            )
        self._by_name = {c.name: c for c in self.colors}

    def by_name(self, name: str) -> PaletteColor:
        return self._by_name[name]

    def select(
        self,
        rng: np.random.RandomState,
        k: int,
        min_pairwise_delta_e: float,
    ) -> List[PaletteColor]:
        """Deterministically pick *k* distinct, harmonious, distinguishable colours.

        Returns them in rank order (index 0 == DOMINANT). Harmony biases toward the
        dominant's temperature family or neutral+accent pairings; every pair is kept
        above ``min_pairwise_delta_e`` so the QA gate can separate them.
        """
        k = max(1, min(int(k), 4, len(self.colors)))
        pool = list(self.colors)

        # Dominant: prefer a colour with enough chroma to read as a distinct tone,
        # but neutrals are still allowed (many real products are white/black dominant).
        dom_weights = np.array([0.5 + min(c.s, 0.8) for c in pool], dtype=np.float64)
        dom_weights /= dom_weights.sum()
        dom_idx = int(rng.choice(len(pool), p=dom_weights))
        chosen = [pool[dom_idx]]

        while len(chosen) < k:
            weights = []
            for c in pool:
                if c in chosen:
                    weights.append(0.0)
                    continue
                if any(delta_e(c, s) < min_pairwise_delta_e for s in chosen):
                    weights.append(0.0)
                    continue
                w = 1.0
                dom = chosen[0]
                if c.temp_family == dom.temp_family:
                    w *= 2.0
                elif c.is_neutral or dom.is_neutral:
                    w *= 1.6  # neutral + accent pairing
                else:
                    w *= 0.5  # clashing temperatures: allowed but discouraged
                weights.append(w)
            wsum = sum(weights)
            if wsum <= 0:
                # No colour satisfies the min-ΔE constraint; take the farthest one so
                # the set stays as distinguishable as possible (deterministic).
                remaining = [c for c in pool if c not in chosen]
                best = max(
                    remaining,
                    key=lambda c: (min(delta_e(c, s) for s in chosen), c.name),
                )
                chosen.append(best)
                continue
            p = np.array(weights, dtype=np.float64) / wsum
            chosen.append(pool[int(rng.choice(len(pool), p=p))])

        return chosen
