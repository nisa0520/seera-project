from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz


def triangular(x: float, a: float, b: float, c: float) -> float:
    universe = np.linspace(min(a, b, c), max(a, b, c), 1001)
    mf = fuzz.trimf(universe, np.array([a, b, c]))
    return float(fuzz.interp_membership(universe, mf, x))


def trapezoidal(x: float, a: float, b: float, c: float, d: float) -> float:
    universe = np.linspace(min(a, b, c, d), max(a, b, c, d), 1001)
    mf = fuzz.trapmf(universe, np.array([a, b, c, d]))
    return float(fuzz.interp_membership(universe, mf, x))


SKIN_SETS = {
    "very_fair": ("trap", (1.0, 1.0, 1.3, 1.7)),
    "fair": ("tri", (1.3, 2.0, 2.7)),
    "medium_fair": ("tri", (2.3, 3.0, 3.7)),
    "moderate_brown": ("tri", (3.3, 4.0, 4.7)),
    "brown": ("tri", (4.3, 5.0, 5.7)),
    "dark_brown": ("trap", (5.3, 5.7, 6.0, 6.0)),
}

UNDERTONE_SETS = {
    "cool": ("trap", (0.0, 0.0, 0.5, 0.8)),
    "neutral": ("tri", (0.6, 1.0, 1.4)),
    "warm": ("trap", (1.2, 1.5, 2.0, 2.0)),
}

CT_SETS = UNDERTONE_SETS
CB_SETS = {
    "dark": ("trap", (0.0, 0.0, 0.20, 0.40)),
    "medium": ("tri", (0.30, 0.50, 0.70)),
    "light": ("trap", (0.60, 0.80, 1.0, 1.0)),
}

SEASONAL_Y1_SETS = {
    "spring": (0.0, 0.5, 1.0),
    "summer": (0.5, 1.5, 2.0),
    "autumn": (1.5, 2.0, 2.5),
    "winter": (2.0, 2.5, 3.0),
}

SEASON_SINGLETON = {
    "spring": 0.5,
    "summer": 1.5,
    "autumn": 2.0,
    "winter": 2.5,
}

SUIT_SINGLETON = {
    "not_suitable": 10,
    "less_suitable": 35,
    "suitable": 65,
    "very_suitable": 90,
}

L1_RULES = [
    ("very_fair", "cool", "summer", 10),
    ("fair", "cool", "summer", 10),
    ("medium_fair", "cool", "summer", 8),
    ("moderate_brown", "cool", "winter", 10),
    ("brown", "cool", "winter", 10),
    ("dark_brown", "cool", "winter", 10),
    ("very_fair", "warm", "spring", 10),
    ("fair", "warm", "spring", 10),
    ("medium_fair", "warm", "spring", 8),
    ("moderate_brown", "warm", "autumn", 10),
    ("brown", "warm", "autumn", 10),
    ("dark_brown", "warm", "autumn", 8),
    ("very_fair", "neutral", "summer", 7),
    ("fair", "neutral", "summer", 7),
    ("medium_fair", "neutral", "spring", 7),
    ("moderate_brown", "neutral", "autumn", 7),
    ("brown", "neutral", "autumn", 7),
    ("dark_brown", "neutral", "winter", 7),
]

L2_RULE_BASE = {
    "spring": {
        ("warm", "light"): "very_suitable",
        ("warm", "medium"): "suitable",
        ("warm", "dark"): "less_suitable",
        ("neutral", "light"): "suitable",
        ("neutral", "medium"): "suitable",
        ("neutral", "dark"): "less_suitable",
        ("cool", "light"): "less_suitable",
        ("cool", "medium"): "less_suitable",
        ("cool", "dark"): "not_suitable",
    },
    "summer": {
        ("cool", "light"): "very_suitable",
        ("cool", "medium"): "suitable",
        ("cool", "dark"): "less_suitable",
        ("neutral", "light"): "suitable",
        ("neutral", "medium"): "suitable",
        ("neutral", "dark"): "less_suitable",
        ("warm", "light"): "less_suitable",
        ("warm", "medium"): "less_suitable",
        ("warm", "dark"): "not_suitable",
    },
    "autumn": {
        ("warm", "dark"): "very_suitable",
        ("warm", "medium"): "very_suitable",
        ("warm", "light"): "suitable",
        ("neutral", "dark"): "suitable",
        ("neutral", "medium"): "suitable",
        ("neutral", "light"): "less_suitable",
        ("cool", "dark"): "less_suitable",
        ("cool", "medium"): "less_suitable",
        ("cool", "light"): "not_suitable",
    },
    "winter": {
        ("cool", "dark"): "very_suitable",
        ("cool", "medium"): "very_suitable",
        ("cool", "light"): "suitable",
        ("neutral", "dark"): "suitable",
        ("neutral", "medium"): "suitable",
        ("neutral", "light"): "less_suitable",
        ("warm", "dark"): "less_suitable",
        ("warm", "medium"): "less_suitable",
        ("warm", "light"): "not_suitable",
    },
}

UNIVERSES = {
    "skin": np.linspace(1, 6, 1001),
    "undertone": np.linspace(0, 2, 1001),
    "ct": np.linspace(0, 2, 1001),
    "cb": np.linspace(0, 1, 1001),
    "season": np.linspace(0, 3, 1001),
}


def _build_mf_map(universe: np.ndarray, set_config: dict[str, tuple[str, tuple[float, ...]]]) -> dict[str, np.ndarray]:
    mf_map: dict[str, np.ndarray] = {}
    for set_name, (shape, params) in set_config.items():
        if shape == "tri":
            mf_map[set_name] = fuzz.trimf(universe, np.array(params))
        else:
            mf_map[set_name] = fuzz.trapmf(universe, np.array(params))
    return mf_map


SKIN_MFS = _build_mf_map(UNIVERSES["skin"], SKIN_SETS)
UNDERTONE_MFS = _build_mf_map(UNIVERSES["undertone"], UNDERTONE_SETS)
CT_MFS = _build_mf_map(UNIVERSES["ct"], CT_SETS)
CB_MFS = _build_mf_map(UNIVERSES["cb"], CB_SETS)
SEASON_MFS = {
    season: fuzz.trimf(UNIVERSES["season"], np.array(params))
    for season, params in SEASONAL_Y1_SETS.items()
}


@dataclass
class Layer1Result:
    y1: float
    seasonal_type: str


def _membership(value: float, set_def: tuple[str, tuple[float, ...]]) -> float:
    shape, params = set_def
    if shape == "tri":
        return max(0.0, triangular(value, *params))
    return max(0.0, trapezoidal(value, *params))


def _membership_precomputed(universe: np.ndarray, mf_map: dict[str, np.ndarray], key: str, value: float) -> float:
    return float(fuzz.interp_membership(universe, mf_map[key], value))


def infer_layer1(skin_tone: float, undertone: float) -> Layer1Result:
    mu_skin = {
        key: _membership_precomputed(UNIVERSES["skin"], SKIN_MFS, key, skin_tone)
        for key in SKIN_SETS.keys()
    }
    mu_under = {
        key: _membership_precomputed(UNIVERSES["undertone"], UNDERTONE_MFS, key, undertone)
        for key in UNDERTONE_SETS.keys()
    }

    weighted_sum = 0.0
    alpha_sum = 0.0

    for skin_set, under_set, seasonal, weight in L1_RULES:
        alpha = min(mu_skin[skin_set], mu_under[under_set]) * weight
        if alpha > 0:
            weighted_sum += alpha * SEASON_SINGLETON[seasonal]
            alpha_sum += alpha

    y1 = weighted_sum / alpha_sum if alpha_sum else 1.5
    seasonal_membership = {
        season: float(fuzz.interp_membership(UNIVERSES["season"], SEASON_MFS[season], y1))
        for season in SEASONAL_Y1_SETS.keys()
    }
    seasonal_type = max(seasonal_membership, key=seasonal_membership.get)
    return Layer1Result(round(y1, 4), seasonal_type)


def infer_layer2(y1: float, ct: float, cb: float) -> float:
    mu_season = {
        season: float(fuzz.interp_membership(UNIVERSES["season"], SEASON_MFS[season], y1))
        for season in SEASONAL_Y1_SETS.keys()
    }
    mu_ct = {
        name: _membership_precomputed(UNIVERSES["ct"], CT_MFS, name, ct)
        for name in CT_SETS.keys()
    }
    mu_cb = {
        name: _membership_precomputed(UNIVERSES["cb"], CB_MFS, name, cb)
        for name in CB_SETS.keys()
    }

    weighted_sum = 0.0
    alpha_sum = 0.0

    for season, season_mu in mu_season.items():
        if season_mu <= 0:
            continue
        for (ct_set, cb_set), suit_label in L2_RULE_BASE[season].items():
            alpha = min(mu_ct[ct_set], mu_cb[cb_set]) * season_mu
            if alpha > 0:
                weighted_sum += alpha * SUIT_SINGLETON[suit_label]
                alpha_sum += alpha

    y2 = weighted_sum / alpha_sum if alpha_sum else 35
    return round(y2 / 100, 4)
