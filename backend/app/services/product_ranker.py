"""Agregasi Skor Produk multi-warna (Rank Order Centroid). Bab IV.2.7.5 / II.1.8."""
from typing import Optional

from app.services.color_match_service import label_for_score, LABEL_INDONESIAN


def roc_weights(n: int) -> list[float]:
    """Mode 1 - Rank Order Centroid (Persamaan 10, Barron & Barrett, 1996)."""
    if n < 1:
        return []
    return [(1 / n) * sum(1 / j for j in range(k, n + 1)) for k in range(1, n + 1)]


def percentage_weights(percentages: list[float]) -> list[float]:
    """Mode 2 - Persentase Langsung (Persamaan 11): w(k) = persentase_k / 100."""
    return [p / 100.0 for p in percentages]


def resolve_weights(n: int, percentages: Optional[list[Optional[float]]] = None) -> tuple[list[float], str]:
    """Pilih Mode 2 bila seluruh warna punya persentase pasti, selain itu Mode 1 (ROC)."""
    if percentages and len(percentages) == n and all(p is not None for p in percentages):
        return percentage_weights([float(p) for p in percentages]), "PERCENTAGE"
    return roc_weights(n), "ROC"


def aggregate_product_score(
    color_scores: list[float], percentages: Optional[list[Optional[float]]] = None
) -> dict:
    """Gabungkan Y2 tiap warna (urut color_rank, Warna ke-1 dulu) menjadi Skor Produk (Persamaan 12)."""
    n = len(color_scores)
    weights, weight_mode = resolve_weights(n, percentages)
    total = 0.0
    parts = []
    for w, y2 in zip(weights, color_scores):
        contribution = w * y2
        total += contribution
        parts.append({"weight": w, "y2": y2, "contribution": contribution})

    label = label_for_score(total)
    return {
        "total_roc_score": total,
        "weights": weights,
        "weight_mode": weight_mode,
        "parts": parts,
        "label": label,
        "label_indonesian": LABEL_INDONESIAN[label],
        "amount_color": n,
    }


SORT_CRITERIA = {
    "SCORE_DESC": lambda item: (
        -float(item["product_score"]),
        -(item["rating_snapshot"] or 0),
        float(item["price_snapshot"]),
        item["product_name"],
    ),
    "PRICE_ASC": lambda item: (
        float(item["price_snapshot"]),
        -float(item["product_score"]),
        -(item["rating_snapshot"] or 0),
        item["product_name"],
    ),
    "RATING_DESC": lambda item: (
        -(item["rating_snapshot"] or 0),
        -float(item["product_score"]),
        float(item["price_snapshot"]),
        item["product_name"],
    ),
    "POPULARITY_DESC": lambda item: (
        -(item.get("popularity", 0)),
        -float(item["product_score"]),
        -(item["rating_snapshot"] or 0),
        item["product_name"],
    ),
}


def sort_items(items: list[dict], criteria: str) -> list[dict]:
    key = SORT_CRITERIA.get(criteria, SORT_CRITERIA["SCORE_DESC"])
    return sorted(items, key=key)
