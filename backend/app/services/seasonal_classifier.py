"""FIS Layer 1 - Seasonal Color Type classification per PRD Section 17.5."""
from typing import Optional
from app.services.fuzzy_membership import memberships, SKIN_TONE_SETS, UNDERTONE_SETS, SEASONAL_SETS_Y1, evaluate_set


SEASONAL_SINGLETONS = {
    "SPRING": 0.5,
    "SUMMER": 1.5,
    "AUTUMN": 2.0,
    "WINTER": 2.5,
}

SEASONAL_NAMES = {
    "SPRING": "Spring",
    "SUMMER": "Summer",
    "AUTUMN": "Autumn",
    "WINTER": "Winter",
}

# (skin_tone_set, undertone_set, output_seasonal, weight, rule_id)
LAYER1_RULES = [
    ("VERY_FAIR", "COOL", "SUMMER", 1.0, "L1-R1"),
    ("FAIR", "COOL", "SUMMER", 1.0, "L1-R2"),
    ("MEDIUM_FAIR", "COOL", "SUMMER", 0.8, "L1-R3"),
    ("MODERATE_BROWN", "COOL", "WINTER", 1.0, "L1-R4"),
    ("BROWN", "COOL", "WINTER", 1.0, "L1-R5"),
    ("DARK_BROWN", "COOL", "WINTER", 1.0, "L1-R6"),
    ("VERY_FAIR", "WARM", "SPRING", 1.0, "L1-R7"),
    ("FAIR", "WARM", "SPRING", 1.0, "L1-R8"),
    ("MEDIUM_FAIR", "WARM", "SPRING", 0.8, "L1-R9"),
    ("MODERATE_BROWN", "WARM", "AUTUMN", 1.0, "L1-R10"),
    ("BROWN", "WARM", "AUTUMN", 1.0, "L1-R11"),
    ("DARK_BROWN", "WARM", "AUTUMN", 0.8, "L1-R12"),
    ("VERY_FAIR", "NEUTRAL", "SUMMER", 0.7, "L1-R13"),
    ("FAIR", "NEUTRAL", "SUMMER", 0.7, "L1-R14"),
    ("MEDIUM_FAIR", "NEUTRAL", "SPRING", 0.7, "L1-R15"),
    ("MODERATE_BROWN", "NEUTRAL", "AUTUMN", 0.7, "L1-R16"),
    ("BROWN", "NEUTRAL", "AUTUMN", 0.7, "L1-R17"),
    ("DARK_BROWN", "NEUTRAL", "WINTER", 0.7, "L1-R18"),
]


def classify(skin_tone: float, undertone: float) -> dict:
    mu_skin = memberships(skin_tone, SKIN_TONE_SETS)
    mu_under = memberships(undertone, UNDERTONE_SETS)

    fired = []
    numerator = 0.0
    denominator = 0.0

    for skin_set, under_set, seasonal_out, weight, rule_id in LAYER1_RULES:
        mu_a = mu_skin.get(skin_set, 0.0)
        mu_b = mu_under.get(under_set, 0.0)
        alpha = min(mu_a, mu_b) * weight
        if alpha > 0:
            singleton = SEASONAL_SINGLETONS[seasonal_out]
            numerator += alpha * singleton
            denominator += alpha
            fired.append({
                "rule_id": rule_id,
                "skin_set": skin_set,
                "undertone_set": under_set,
                "output_seasonal": seasonal_out,
                "alpha": alpha,
                "singleton": singleton,
                "weight": weight,
            })

    if denominator > 0:
        y1 = numerator / denominator
    else:
        y1 = 1.5  # fallback to Summer if no rules fire

    # Fuzzify Y1 into seasonal memberships
    seasonal_membership = {}
    for label, set_def in SEASONAL_SETS_Y1.items():
        seasonal_membership[label] = evaluate_set(y1, set_def)

    # Determine dominant seasonal
    if max(seasonal_membership.values()) == 0:
        # snap to the nearest singleton
        dominant = min(
            SEASONAL_SINGLETONS.items(),
            key=lambda kv: abs(kv[1] - y1),
        )[0]
        score_seasonal = 1.0
    else:
        dominant = max(seasonal_membership.items(), key=lambda kv: kv[1])[0]
        score_seasonal = seasonal_membership[dominant]

    return {
        "y1_continuous": y1,
        "seasonal_code": dominant,
        "seasonal_name": SEASONAL_NAMES[dominant],
        "score_seasonal": score_seasonal,
        "seasonal_membership": seasonal_membership,
        "skin_membership": mu_skin,
        "undertone_membership": mu_under,
        "fired_rules": fired,
    }
