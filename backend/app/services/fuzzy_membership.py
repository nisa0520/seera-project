"""Fuzzy membership functions per PRD Section 17.2."""


def triangular(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c:
        return 0.0
    if a < x <= b:
        if b == a:
            return 1.0
        return (x - a) / (b - a)
    if b < x < c:
        if c == b:
            return 1.0
        return (c - x) / (c - b)
    return 0.0


def trapezoidal(x: float, a: float, b: float, c: float, d: float) -> float:
    if a == b and x <= c:
        return 1.0 if x >= a else 0.0
    if c == d and x >= b:
        return 1.0 if x <= d else 0.0
    if x <= a or x >= d:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a)
    if b <= x <= c:
        return 1.0
    if c < x < d:
        return (d - x) / (d - c)
    return 0.0


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


SKIN_TONE_SETS = {
    "VERY_FAIR": ("trapezoidal", (1.0, 1.0, 1.3, 1.7)),
    "FAIR": ("triangular", (1.3, 2.0, 2.7)),
    "MEDIUM_FAIR": ("triangular", (2.3, 3.0, 3.7)),
    "MODERATE_BROWN": ("triangular", (3.3, 4.0, 4.7)),
    "BROWN": ("triangular", (4.3, 5.0, 5.7)),
    "DARK_BROWN": ("trapezoidal", (5.3, 5.7, 6.0, 6.0)),
}

UNDERTONE_SETS = {
    "COOL": ("trapezoidal", (0.0, 0.0, 0.5, 0.8)),
    "NEUTRAL": ("triangular", (0.6, 1.0, 1.4)),
    "WARM": ("trapezoidal", (1.2, 1.5, 2.0, 2.0)),
}

SEASONAL_SETS_Y1 = {
    "SPRING": ("triangular", (0.0, 0.5, 1.0)),
    "SUMMER": ("triangular", (0.5, 1.5, 2.0)),
    "AUTUMN": ("triangular", (1.5, 2.0, 2.5)),
    "WINTER": ("triangular", (2.0, 2.5, 3.0)),
}

CT_SETS = {
    "COOL": ("trapezoidal", (0.0, 0.0, 0.5, 0.8)),
    "NEUTRAL": ("triangular", (0.6, 1.0, 1.4)),
    "WARM": ("trapezoidal", (1.2, 1.5, 2.0, 2.0)),
}

CB_SETS = {
    "DARK": ("trapezoidal", (0.0, 0.0, 0.20, 0.40)),
    "MEDIUM": ("triangular", (0.30, 0.50, 0.70)),
    "LIGHT": ("trapezoidal", (0.60, 0.80, 1.0, 1.0)),
}


def evaluate_set(x: float, set_def: tuple) -> float:
    kind, params = set_def
    if kind == "triangular":
        return triangular(x, *params)
    if kind == "trapezoidal":
        return trapezoidal(x, *params)
    raise ValueError(f"Unknown set kind: {kind}")


def memberships(x: float, sets_dict: dict) -> dict:
    return {label: evaluate_set(x, set_def) for label, set_def in sets_dict.items()}
