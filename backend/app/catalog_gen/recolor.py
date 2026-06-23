"""Texture-preserving CIELAB recolor + region-aware proportional partition.

Recolor philosophy (FR-IMG-04): operate in CIELAB and keep the **relative shading**
(the L-channel texture: folds, shadows, highlights). The garment's luminance
distribution is *mean-shifted* onto the target colour's lightness and its chroma is
retargeted to the target a/b. This both (a) preserves fabric depth/structure and
(b) makes the rendered region's mean LAB equal the metadata colour — which is exactly
what the ΔE2000 QA gate verifies. For near-black/near-white/low-chroma targets this
degrades gracefully (chroma is small, so we simply re-centre luminance), satisfying the
edge-case rule. The background and any non-garment pixels are never converted, so they
stay byte-for-byte identical.

Partition philosophy (FR-IMG-05): every garment pixel is assigned a colour *rank* so
that the rendered area shares match the configured percentages. Pixels are ordered by
``(region_priority, vertical, horizontal)`` and sliced by cumulative percentage, which
(a) honours the targets exactly (down to pixel rounding), (b) is spatially coherent,
and (c) maps torso→DOMINANT, sleeves→SECONDARY, trim→ACCENT when region sizes allow —
otherwise it spills coherently inside the garment mask (the deterministic fallback).
"""
from __future__ import annotations

import warnings
from typing import List, Sequence, Tuple

import numpy as np
from skimage.color import rgb2lab, lab2rgb

from app.catalog_gen.masks import TemplateMask, LBL_TORSO, LBL_SLEEVE, LBL_TRIM

# Colour rank -> the region it prefers to occupy first (semantic mapping).
_REGION_PRIORITY = {LBL_TORSO: 0.0, LBL_SLEEVE: 1.0, LBL_TRIM: 2.0}


def partition(mask: TemplateMask, percentages: Sequence[float]) -> np.ndarray:
    """Return an int8 rank map: -1 = non-garment, 0..k-1 = colour rank (0 == DOMINANT)."""
    h, w = mask.labels.shape
    rankmap = np.full((h, w), -1, dtype=np.int8)
    ys, xs = np.where(mask.garment)
    n = ys.size
    k = len(percentages)
    if n == 0 or k == 0:
        return rankmap
    if k == 1:
        rankmap[ys, xs] = 0
        return rankmap

    y0, y1 = ys.min(), ys.max()
    x0, x1 = xs.min(), xs.max()
    gh = max(1, y1 - y0)
    gw = max(1, x1 - x0)

    region = mask.labels[ys, xs]
    prio = np.vectorize(lambda v: _REGION_PRIORITY.get(int(v), 1.0))(region).astype(np.float64)
    yy = (ys - y0) / gh
    xx = (xs - x0) / gw
    # Sort key stays within its region band: prio is integral, the spatial part < 1.
    key = prio + 0.90 * yy + 0.05 * xx
    order = np.argsort(key, kind="stable")

    # Cumulative pixel boundaries from the (normalised) percentages.
    pct = np.asarray(percentages, dtype=np.float64)
    pct = pct / pct.sum()
    bounds = np.floor(np.cumsum(pct) * n).astype(int)
    bounds[-1] = n

    ranks_sorted = np.empty(n, dtype=np.int8)
    start = 0
    for i in range(k):
        end = int(bounds[i])
        if i < k - 1 and end <= start:
            end = start + 1  # guarantee every colour gets at least one pixel
        ranks_sorted[start:end] = i
        start = end
    if start < n:
        ranks_sorted[start:] = k - 1

    rankmap[ys[order], xs[order]] = ranks_sorted
    return rankmap


def recolor_lab(
    rgb: np.ndarray,
    rankmap: np.ndarray,
    targets_lab: Sequence[Tuple[float, float, float]],
    texture_strength: float = 1.0,
) -> np.ndarray:
    """Recolor garment pixels per rank; return a full RGB image (uint8).

    Non-garment pixels are copied verbatim from ``rgb`` (no LAB round-trip), so the
    background and skin stay byte-for-byte identical. ``texture_strength`` scales how
    much of the original L-deviation is retained (1.0 = full texture; lower values
    tighten the region around the target colour and are used on QA retries).
    """
    out = rgb.copy()
    lab_full = rgb2lab(rgb.astype(np.float64) / 255.0)
    L = lab_full[:, :, 0]

    for i, (tL, ta, tb) in enumerate(targets_lab):
        sel = rankmap == i
        if not sel.any():
            continue
        Lr = L[sel]
        mu = float(Lr.mean())
        newL = np.clip(tL + (Lr - mu) * float(texture_strength), 0.0, 100.0)
        n = newL.shape[0]
        lab_pixels = np.empty((n, 1, 3), dtype=np.float64)
        lab_pixels[:, 0, 0] = newL
        lab_pixels[:, 0, 1] = ta
        lab_pixels[:, 0, 2] = tb
        with warnings.catch_warnings():
            # Out-of-gamut targets are clipped deterministically; the warning is benign.
            warnings.simplefilter("ignore", category=UserWarning)
            rgb_pixels = lab2rgb(lab_pixels)  # -> (n,1,3) in [0,1]
        out[sel] = np.clip(np.round(rgb_pixels[:, 0, :] * 255.0), 0, 255).astype(np.uint8)

    return out


def render_artifacts(
    rgb: np.ndarray,
    mask: TemplateMask,
    percentages: Sequence[float],
    targets_lab: Sequence[Tuple[float, float, float]],
    texture_strength: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Produce the three mutually-consistent artifacts from one recolored render.

    Returns ``(catalog_rgb, subject_rgba, rankmap)``:

    * ``catalog_rgb``  — full image, garment recolored, original background preserved.
    * ``subject_rgba`` — recolored RGB + subject alpha (transparent background). Used
      for BOTH the try-on cutout and the clean VTON garment cutout (pixel-identical).
    * ``rankmap``      — per-pixel colour rank, fed to the QA gate.
    """
    rankmap = partition(mask, percentages)
    catalog_rgb = recolor_lab(rgb, rankmap, targets_lab, texture_strength)
    alpha = mask.alpha
    if alpha.shape != catalog_rgb.shape[:2]:
        import cv2
        alpha = cv2.resize(alpha, (catalog_rgb.shape[1], catalog_rgb.shape[0]),
                           interpolation=cv2.INTER_NEAREST)
    subject_rgba = np.dstack([catalog_rgb, alpha]).astype(np.uint8)
    return catalog_rgb, subject_rgba, rankmap
