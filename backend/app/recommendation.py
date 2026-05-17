from .fuzzy import infer_layer2


def roc_weights(n: int) -> list[float]:
    return [sum(1 / j for j in range(k, n + 1)) / n for k in range(1, n + 1)]


def aggregate_product_score(color_scores: list[float]) -> tuple[float, list[float]]:
    n = len(color_scores)
    if n == 0:
        return 0.0, []
    if n == 1:
        return color_scores[0], [1.0]
    weights = roc_weights(n)
    score = sum(w * s for w, s in zip(weights, color_scores))
    return round(score, 4), [round(w, 4) for w in weights]


def rank_with_saw(items: list[dict], disable_price: bool = False) -> tuple[list[dict], dict]:
    if not items:
        return [], {}

    if disable_price:
        base_weights = {"c1": 0.70, "c3": 0.10, "c4": 0.05}
        total = sum(base_weights.values())
        weights = {k: v / total for k, v in base_weights.items()}
    else:
        weights = {"c1": 0.70, "c2": 0.15, "c3": 0.10, "c4": 0.05}

    max_c1 = float(max(item["skor_produk"] for item in items)) if items else 0.0
    min_c2 = float(min(item["price"] for item in items)) if items else 0.0
    max_c3 = float(max(item["rating"] for item in items)) if items else 0.0
    max_c4 = float(max(item["popularity"] for item in items)) if items else 0.0

    for item in items:
        price = float(item["price"])
        r1 = float(item["skor_produk"]) / max_c1 if max_c1 else 0.0
        r3 = float(item["rating"]) / max_c3 if max_c3 else 0.0
        r4 = float(item["popularity"]) / max_c4 if max_c4 else 0.0

        if disable_price:
            saw_score = (weights["c1"] * r1) + (weights["c3"] * r3) + (weights["c4"] * r4)
        else:
            r2 = min_c2 / price if price else 0.0
            saw_score = (weights["c1"] * r1) + (weights["c2"] * r2) + (weights["c3"] * r3) + (weights["c4"] * r4)

        item["saw_score"] = round(float(saw_score), 4)

    items.sort(key=lambda x: x["saw_score"], reverse=True)
    return items, {k: round(v, 4) for k, v in weights.items()}


def evaluate_product_colors(y1: float, colors: list[dict]) -> tuple[float, list[float], list[dict]]:
    ordered_colors = sorted(colors, key=lambda c: c["dominance_rank"])
    per_color_scores = [infer_layer2(y1=y1, ct=c["ct_value"], cb=c["cb_value"]) for c in ordered_colors]
    skor_produk, roc = aggregate_product_score(per_color_scores)

    detail = []
    # Create 1-based indexing for roc so we can lookup by dominance rank
    roc_map = {idx: val for idx, val in enumerate(roc, start=1)}

    for color, score in zip(ordered_colors, per_color_scores):
        detail.append({
            "color_id": color["color_id"],
            "hex_code": color["hex_code"],
            "dominance_rank": color["dominance_rank"],
            "ct": color["ct_value"],
            "cb": color["cb_value"],
            "suitability_score": score,
        })

    return skor_produk, roc_map, detail
