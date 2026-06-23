"""Closed-loop QA gate: prove the rendered image actually contains the metadata colours.

After rendering, garment pixels (inside the mask) are clustered with a deterministic
KMeans (k = number of metadata colours) in CIELAB; clusters are matched to the metadata
colours by ΔE2000 via an optimal assignment. The gate asserts:

  (a) every metadata colour is represented by a cluster,
  (b) the largest cluster maps to the DOMINANT colour,
  (c) each colour's rendered area share is within tolerance of its ``color_percentage``,
  (d) each matched ΔE2000 is below the threshold.

This module is **read-only** with respect to existing logic — it reuses the palette /
ΔE concepts but introduces no change to ``compute_color_features`` or any algorithm.
KMeans is implemented locally (no sklearn dependency) and fully seeded, so the verdict
is reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment
from skimage.color import rgb2lab, deltaE_ciede2000


@dataclass
class ColorCheck:
    name: str
    target_pct: float
    measured_pct: float
    delta_e: float


@dataclass
class QAResult:
    passed: bool
    reason: str = ""
    checks: List[ColorCheck] = field(default_factory=list)
    dominant_ok: bool = True

    def to_jsonable(self) -> dict:
        return {
            "passed": self.passed,
            "reason": self.reason,
            "dominant_ok": self.dominant_ok,
            "colors": [
                {
                    "name": c.name,
                    "target_pct": round(c.target_pct, 2),
                    "measured_pct": round(c.measured_pct, 2),
                    "delta_e": round(c.delta_e, 2),
                }
                for c in self.checks
            ],
        }


def _kmeans(X: np.ndarray, k: int, seed: int, iters: int = 60) -> Tuple[np.ndarray, np.ndarray]:
    """Deterministic KMeans (k-means++ init from a seeded RNG). Returns (labels, centers)."""
    rng = np.random.RandomState(seed)
    n = X.shape[0]
    k = min(k, n)
    centers = [X[rng.randint(n)]]
    for _ in range(1, k):
        c = np.array(centers)
        d2 = ((X[:, None, :] - c[None, :, :]) ** 2).sum(axis=2).min(axis=1)
        s = d2.sum()
        probs = (d2 / s) if s > 0 else np.full(n, 1.0 / n)
        centers.append(X[rng.choice(n, p=probs)])
    centers = np.array(centers, dtype=np.float64)
    for _ in range(iters):
        d2 = ((X[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = d2.argmin(axis=1)
        new = np.array([
            X[labels == j].mean(axis=0) if np.any(labels == j) else centers[j]
            for j in range(k)
        ])
        if np.allclose(new, centers):
            centers = new
            break
        centers = new
    return labels, centers


def _sample_lab(rgb: np.ndarray, garment: np.ndarray, cap: int) -> np.ndarray:
    ys, xs = np.where(garment)
    n = ys.size
    if n == 0:
        return np.empty((0, 3), dtype=np.float64)
    if n > cap:
        idx = np.linspace(0, n - 1, cap).astype(int)  # deterministic uniform subsample
        ys, xs = ys[idx], xs[idx]
    lab = rgb2lab(rgb.astype(np.float64) / 255.0)
    return lab[ys, xs].astype(np.float64)


def run_qa(
    rgb: np.ndarray,
    garment: np.ndarray,
    color_names: Sequence[str],
    targets_lab: Sequence[Tuple[float, float, float]],
    percentages: Sequence[float],
    *,
    seed: int,
    area_tolerance_pp: float,
    delta_e_threshold: float,
    sample_cap: int,
) -> QAResult:
    k = len(color_names)
    X = _sample_lab(rgb, garment, sample_cap)
    if X.shape[0] < k:
        return QAResult(passed=False, reason="too few garment pixels to verify")

    labels, centers = _kmeans(X, k, seed)
    counts = np.array([int(np.sum(labels == j)) for j in range(k)])
    total = max(1, int(counts.sum()))
    shares = counts / total * 100.0

    meta_lab = np.array(targets_lab, dtype=np.float64)
    # Cost matrix clusters(rows) x metadata-colours(cols) via ΔE2000.
    cost = np.zeros((k, k), dtype=np.float64)
    for ci in range(k):
        cl = np.repeat(centers[ci].reshape(1, 3), k, axis=0)
        cost[ci, :] = deltaE_ciede2000(cl, meta_lab)
    cluster_idx, meta_idx = linear_sum_assignment(cost)
    # meta colour -> assigned cluster
    meta_to_cluster = {int(m): int(c) for c, m in zip(cluster_idx, meta_idx)}

    checks: List[ColorCheck] = []
    max_de = 0.0
    worst_area = 0.0
    for m in range(k):
        cl = meta_to_cluster.get(m)
        de = float(cost[cl, m]) if cl is not None else 999.0
        measured = float(shares[cl]) if cl is not None else 0.0
        checks.append(ColorCheck(color_names[m], float(percentages[m]), measured, de))
        max_de = max(max_de, de)
        worst_area = max(worst_area, abs(measured - float(percentages[m])))

    largest_cluster = int(np.argmax(counts))
    dominant_meta_cluster = meta_to_cluster.get(0)
    dominant_ok = (dominant_meta_cluster == largest_cluster)

    passed = True
    reason = ""
    if len({c for c in meta_to_cluster.values()}) < k:
        passed, reason = False, "not all metadata colours represented"
    elif max_de > delta_e_threshold:
        passed, reason = False, f"max ΔE2000 {max_de:.1f} > {delta_e_threshold}"
    elif not dominant_ok:
        passed, reason = False, "largest cluster is not the DOMINANT colour"
    elif worst_area > area_tolerance_pp:
        passed, reason = False, f"area share off by {worst_area:.1f}pp > {area_tolerance_pp}"

    return QAResult(passed=passed, reason=reason, checks=checks, dominant_ok=dominant_ok)
