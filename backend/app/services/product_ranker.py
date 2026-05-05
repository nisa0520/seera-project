"""Product ranking using ROC for multi-color products. PRD Section 17.10."""
from app.services.color_match_service import label_for_score, LABEL_INDONESIAN


def roc_weights(n: int) -> list[float]:
    if n < 1:
        return []
    return [(1 / n) * sum(1 / j for j in range(k, n + 1)) for k in range(1, n + 1)]


def aggregate_product_score(color_scores: list[float]) -> dict:
    """Given Y2 scores ordered by color_rank (dominant first), compute ROC weighted total."""
    n = len(color_scores)
    weights = roc_weights(n)
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
