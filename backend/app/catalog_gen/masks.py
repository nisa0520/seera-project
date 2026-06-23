"""Per-template **labeled region masks** — authored once, cached, never re-estimated.

For each template we derive, deterministically and offline:

* ``alpha``  — the subject silhouette (garment-on-person, background removed). Reused
  from the existing ``public/tryon/`` cutout when available, else background-keyed.
* ``labels`` — a labelled region map over the **garment fabric only** (skin/background
  excluded): ``0`` non-garment, ``1`` torso, ``2`` sleeves, ``3`` collar/cuffs/trim.
  The binary clothing mask is ``labels > 0``.

These are *static reference data*: computed once per template and cached to
``mask_cache/``; every generated variant of a template reuses the same cached masks.
They are never recomputed per generated image. Authoring is a pure function of the
template pixels + its inherited face anchor, so the cache is fully reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from skimage.color import rgb2lab, deltaE_ciede2000

from app.catalog_gen import paths
from app.catalog_gen.templates import Template

# Region label constants.
LBL_NONE = 0
LBL_TORSO = 1
LBL_SLEEVE = 2
LBL_TRIM = 3


@dataclass
class TemplateMask:
    labels: np.ndarray   # uint8 HxW in {0,1,2,3}
    alpha: np.ndarray    # uint8 HxW subject alpha
    size: Tuple[int, int]  # (W, H)

    @property
    def garment(self) -> np.ndarray:
        return self.labels > 0


# ----------------------------------------------------------------------------- #
# Subject + skin                                                                #
# ----------------------------------------------------------------------------- #
def _load_subject_alpha(template: Template, rgb: np.ndarray) -> np.ndarray:
    """Subject silhouette: prefer the existing transparent cutout's alpha."""
    cutout_path = template.source_cutout_path
    if cutout_path.is_file():
        cut = Image.open(cutout_path).convert("RGBA")
        alpha = np.array(cut)[:, :, 3]
        if alpha.shape != rgb.shape[:2]:
            alpha = cv2.resize(alpha, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST)
        return (alpha > 16).astype(np.uint8) * 255
    # Fallback: key out a near-uniform background sampled from the image corners.
    h, w = rgb.shape[:2]
    corners = np.concatenate([
        rgb[0:8, 0:8].reshape(-1, 3), rgb[0:8, w - 8:w].reshape(-1, 3),
        rgb[h - 8:h, 0:8].reshape(-1, 3), rgb[h - 8:h, w - 8:w].reshape(-1, 3),
    ]).astype(np.float64)
    bg = np.median(corners, axis=0)
    dist = np.linalg.norm(rgb.astype(np.float64) - bg, axis=2)
    subject = (dist > 40).astype(np.uint8)
    subject = cv2.morphologyEx(subject, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    subject = cv2.morphologyEx(subject, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return subject * 255


def _face_ellipse_mask(template: Template, shape: Tuple[int, int]) -> np.ndarray:
    """Carve out the model's face/neck using the inherited face anchor box."""
    h, w = shape
    a = template.anchor
    cx, cy, bw = a.get("cx", 0.5), a.get("cy", 0.0), a.get("w", 0.2)
    mask = np.zeros((h, w), np.uint8)
    center = (int(cx * w), int(cy * h))
    rx = max(4, int(0.62 * bw * w))
    ry = max(4, int(0.92 * bw * w))
    cv2.ellipse(mask, center, (rx, ry), 0, 0, 360, 255, -1)
    return mask > 0


def _skin_mask(rgb: np.ndarray) -> np.ndarray:
    """Colour-based skin candidate (YCrCb + HSV). Deterministic."""
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    cr = ycrcb[:, :, 1].astype(np.int16)
    cb = ycrcb[:, :, 2].astype(np.int16)
    skin_ycrcb = (cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    hh = hsv[:, :, 0].astype(np.int16)
    ss = hsv[:, :, 1].astype(np.int16)
    vv = hsv[:, :, 2].astype(np.int16)
    skin_hsv = ((hh <= 25) | (hh >= 172)) & (ss >= 25) & (ss <= 180) & (vv >= 60)
    return skin_ycrcb & skin_hsv


def _lab_image(rgb: np.ndarray) -> np.ndarray:
    return rgb2lab(rgb.astype(np.float64) / 255.0)


# ----------------------------------------------------------------------------- #
# Region labelling                                                              #
# ----------------------------------------------------------------------------- #
def _label_regions(garment: np.ndarray) -> np.ndarray:
    """Heuristic, deterministic torso/sleeve/trim labelling within the garment mask.

    The exact split need not be perfect: it only *biases* colour ordering. The
    proportional partition (recolor.py) enforces the actual area shares, and falls
    back to a coherent partition inside the garment mask where regions can't satisfy
    the target proportions. Front full-garment shots map cleanly here.
    """
    h, w = garment.shape
    labels = np.zeros((h, w), np.uint8)
    ys, xs = np.where(garment)
    if ys.size == 0:
        return labels
    y0, y1 = ys.min(), ys.max()
    gh = max(1, y1 - y0)

    # Collar / trim: top band of the garment (neckline, mandarin collar, placket top).
    trim_cut = y0 + int(0.10 * gh)
    # Sleeves live in the upper portion, at the lateral extremities of each row.
    sleeve_zone_bottom = y0 + int(0.58 * gh)
    sleeve_frac = 0.22

    labels[garment] = LBL_TORSO
    for y in range(y0, y1 + 1):
        row = np.where(garment[y])[0]
        if row.size == 0:
            continue
        if y <= trim_cut:
            labels[y, row] = LBL_TRIM
            continue
        if y <= sleeve_zone_bottom:
            span = row.max() - row.min() + 1
            edge = max(1, int(sleeve_frac * span))
            left = row[row < row.min() + edge]
            right = row[row > row.max() - edge]
            labels[y, left] = LBL_SLEEVE
            labels[y, right] = LBL_SLEEVE
    return labels


def _build_mask(template: Template) -> TemplateMask:
    img = Image.open(template.source_image_path).convert("RGB")
    rgb = np.array(img)
    h, w = rgb.shape[:2]

    subject = _load_subject_alpha(template, rgb) > 0

    # Exclude the face (anchor-based, fabric-colour-independent).
    face = _face_ellipse_mask(template, (h, w))
    garment = subject & ~face

    # Exclude clearly-skin pixels (hands/neck) — but only where they differ markedly
    # from the garment's own fabric tone, so beige/nude fabrics are not eaten.
    lab = _lab_image(rgb)
    if garment.any():
        fabric_ref = np.median(lab[garment].reshape(-1, 3), axis=0).reshape(1, 3)
        flat_lab = lab.reshape(-1, 3)
        de = deltaE_ciede2000(flat_lab, np.repeat(fabric_ref, flat_lab.shape[0], axis=0))
        de = de.reshape(h, w)
        skin = _skin_mask(rgb) & (de > 18.0)
        garment = garment & ~skin

    # Clean up: fill pinholes, drop specks, keep meaningful components.
    g = garment.astype(np.uint8)
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    g = cv2.morphologyEx(g, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    num, lab_cc, stats, _ = cv2.connectedComponentsWithStats(g, connectivity=8)
    total = int(g.sum())
    keep = np.zeros_like(g)
    if total > 0:
        for i in range(1, num):
            if stats[i, cv2.CC_STAT_AREA] >= max(64, 0.003 * total):
                keep[lab_cc == i] = 1
    garment = keep.astype(bool)
    if not garment.any():  # safety net: never produce an empty garment mask
        garment = subject & ~face

    labels = _label_regions(garment)
    return TemplateMask(labels=labels, alpha=(subject.astype(np.uint8) * 255), size=(w, h))


# ----------------------------------------------------------------------------- #
# Cache                                                                         #
# ----------------------------------------------------------------------------- #
def _labels_path(template: Template):
    return paths.MASK_CACHE_DIR / f"{template.mask_key}__labels.png"


def _alpha_path(template: Template):
    return paths.MASK_CACHE_DIR / f"{template.mask_key}__alpha.png"


def load_mask(template: Template, force: bool = False) -> TemplateMask:
    """Load cached masks for a template, authoring + caching them once if missing."""
    lp, ap = _labels_path(template), _alpha_path(template)
    if not force and lp.is_file() and ap.is_file():
        labels = np.array(Image.open(lp).convert("L"), dtype=np.uint8)
        alpha = np.array(Image.open(ap).convert("L"), dtype=np.uint8)
        return TemplateMask(labels=labels, alpha=alpha, size=(labels.shape[1], labels.shape[0]))

    mask = _build_mask(template)
    paths.MASK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask.labels, mode="L").save(lp, optimize=True)
    Image.fromarray(mask.alpha, mode="L").save(ap, optimize=True)
    return mask


def author_all(templates, force: bool = False) -> int:
    n = 0
    for t in templates:
        load_mask(t, force=force)
        n += 1
    return n
