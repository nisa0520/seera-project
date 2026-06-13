"""FIS Layer 2 - Color Suitability per PRD Section 17.9."""
from app.services.fuzzy_membership import memberships, CT_SETS, CB_SETS


# Singleton outputs per output category
SUITABILITY_SINGLETONS = {
    "VERY_SUITABLE": 0.90,
    "SUITABLE": 0.65,
    "LESS_SUITABLE": 0.35,
    "NOT_SUITABLE": 0.10,
}

# (seasonal_set, ct_set, cb_set, output_label, rule_id)
LAYER2_RULES = [
    ("SPRING", "WARM", "LIGHT", "VERY_SUITABLE", "L2-R1"),
    ("SPRING", "WARM", "MEDIUM", "SUITABLE", "L2-R2"),
    ("SPRING", "WARM", "DARK", "LESS_SUITABLE", "L2-R3"),
    ("SPRING", "NEUTRAL", "LIGHT", "SUITABLE", "L2-R4"),
    ("SPRING", "NEUTRAL", "MEDIUM", "SUITABLE", "L2-R5"),
    ("SPRING", "NEUTRAL", "DARK", "LESS_SUITABLE", "L2-R6"),
    ("SPRING", "COOL", "LIGHT", "LESS_SUITABLE", "L2-R7"),
    ("SPRING", "COOL", "MEDIUM", "LESS_SUITABLE", "L2-R8"),
    ("SPRING", "COOL", "DARK", "NOT_SUITABLE", "L2-R9"),
    ("SUMMER", "COOL", "LIGHT", "VERY_SUITABLE", "L2-R10"),
    ("SUMMER", "COOL", "MEDIUM", "SUITABLE", "L2-R11"),
    ("SUMMER", "COOL", "DARK", "LESS_SUITABLE", "L2-R12"),
    ("SUMMER", "NEUTRAL", "LIGHT", "SUITABLE", "L2-R13"),
    ("SUMMER", "NEUTRAL", "MEDIUM", "SUITABLE", "L2-R14"),
    ("SUMMER", "NEUTRAL", "DARK", "LESS_SUITABLE", "L2-R15"),
    ("SUMMER", "WARM", "LIGHT", "LESS_SUITABLE", "L2-R16"),
    ("SUMMER", "WARM", "MEDIUM", "LESS_SUITABLE", "L2-R17"),
    ("SUMMER", "WARM", "DARK", "NOT_SUITABLE", "L2-R18"),
    ("AUTUMN", "WARM", "DARK", "VERY_SUITABLE", "L2-R19"),
    ("AUTUMN", "WARM", "MEDIUM", "VERY_SUITABLE", "L2-R20"),
    ("AUTUMN", "WARM", "LIGHT", "SUITABLE", "L2-R21"),
    ("AUTUMN", "NEUTRAL", "DARK", "SUITABLE", "L2-R22"),
    ("AUTUMN", "NEUTRAL", "MEDIUM", "SUITABLE", "L2-R23"),
    ("AUTUMN", "NEUTRAL", "LIGHT", "LESS_SUITABLE", "L2-R24"),
    ("AUTUMN", "COOL", "DARK", "LESS_SUITABLE", "L2-R25"),
    ("AUTUMN", "COOL", "MEDIUM", "LESS_SUITABLE", "L2-R26"),
    ("AUTUMN", "COOL", "LIGHT", "NOT_SUITABLE", "L2-R27"),
    ("WINTER", "COOL", "DARK", "VERY_SUITABLE", "L2-R28"),
    ("WINTER", "COOL", "MEDIUM", "VERY_SUITABLE", "L2-R29"),
    ("WINTER", "COOL", "LIGHT", "SUITABLE", "L2-R30"),
    ("WINTER", "NEUTRAL", "DARK", "SUITABLE", "L2-R31"),
    ("WINTER", "NEUTRAL", "MEDIUM", "SUITABLE", "L2-R32"),
    ("WINTER", "NEUTRAL", "LIGHT", "LESS_SUITABLE", "L2-R33"),
    ("WINTER", "WARM", "DARK", "LESS_SUITABLE", "L2-R34"),
    ("WINTER", "WARM", "MEDIUM", "LESS_SUITABLE", "L2-R35"),
    ("WINTER", "WARM", "LIGHT", "NOT_SUITABLE", "L2-R36"),
]


def label_for_score(score: float) -> str:
    if score >= 0.80:
        return "VERY_SUITABLE"
    if score >= 0.55:
        return "SUITABLE"
    if score >= 0.30:
        return "LESS_SUITABLE"
    return "NOT_SUITABLE"


LABEL_INDONESIAN = {
    "VERY_SUITABLE": "Sangat sesuai",
    "SUITABLE": "Sesuai",
    "LESS_SUITABLE": "Kurang sesuai",
    "NOT_SUITABLE": "Tidak sesuai",
}


def compute_color_score(ct: float, cb: float, seasonal_membership: dict) -> dict:
    mu_ct = memberships(ct, CT_SETS)
    mu_cb = memberships(cb, CB_SETS)

    fired = []
    numerator = 0.0
    denominator = 0.0

    for seasonal_set, ct_set, cb_set, output_label, rule_id in LAYER2_RULES:
        mu_seasonal = seasonal_membership.get(seasonal_set, 0.0)
        mu_ct_val = mu_ct.get(ct_set, 0.0)
        mu_cb_val = mu_cb.get(cb_set, 0.0)

        alpha = min(mu_ct_val, mu_cb_val) * mu_seasonal
        if alpha > 0:
            singleton = SUITABILITY_SINGLETONS[output_label]
            numerator += alpha * singleton
            denominator += alpha
            fired.append({
                "rule_id": rule_id,
                "seasonal_set": seasonal_set,
                "ct_set": ct_set,
                "cb_set": cb_set,
                "output_label": output_label,
                "alpha": alpha,
                "singleton": singleton,
            })

    y2 = numerator / denominator if denominator > 0 else 0.0
    label = label_for_score(y2)

    return {
        "y2": y2,
        "label": label,
        "label_indonesian": LABEL_INDONESIAN[label],
        "ct_membership": mu_ct,
        "cb_membership": mu_cb,
        "fired_rules": fired,
    }
