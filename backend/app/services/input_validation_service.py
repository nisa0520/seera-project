"""Input normalization & validation for skin tone & undertone."""

SKIN_TONE_MAP = {
    "I": (1.0, "Very Fair"),
    "II": (2.0, "Fair"),
    "III": (3.0, "Medium Fair"),
    "IV": (4.0, "Moderate Brown"),
    "V": (5.0, "Brown"),
    "VI": (6.0, "Dark Brown"),
}

UNDERTONE_MAP = {
    "COOL": (0.0, "Cool"),
    "NEUTRAL": (1.0, "Neutral"),
    "WARM": (2.0, "Warm"),
}

SKIN_TONE_ALIASES = {
    "1": "I", "2": "II", "3": "III", "4": "IV", "5": "V", "6": "VI",
    "VERY FAIR": "I",
    "FAIR": "II",
    "MEDIUM FAIR": "III",
    "MEDIUM": "III",
    "MODERATE BROWN": "IV",
    "MODERATE": "IV",
    "BROWN": "V",
    "DARK BROWN": "VI",
    "DARK": "VI",
}

UNDERTONE_ALIASES = {
    "DINGIN": "COOL",
    "BIRU": "COOL",
    "UNGU": "COOL",
    "NETRAL": "NEUTRAL",
    "CAMPURAN": "NEUTRAL",
    "HANGAT": "WARM",
    "HIJAU": "WARM",
    "KUNING": "WARM",
}


def normalize_skin_tone(raw: str) -> str | None:
    if raw is None:
        return None
    cleaned = str(raw).strip().upper()
    if cleaned in SKIN_TONE_MAP:
        return cleaned
    if cleaned in SKIN_TONE_ALIASES:
        return SKIN_TONE_ALIASES[cleaned]
    return None


def normalize_undertone(raw: str) -> str | None:
    if raw is None:
        return None
    cleaned = str(raw).strip().upper()
    if cleaned in UNDERTONE_MAP:
        return cleaned
    if cleaned in UNDERTONE_ALIASES:
        return UNDERTONE_ALIASES[cleaned]
    return None


def skin_tone_payload(code: str) -> dict:
    value, name = SKIN_TONE_MAP[code]
    return {"code": code, "value": value, "name": name}


def undertone_payload(code: str) -> dict:
    value, name = UNDERTONE_MAP[code]
    return {"code": code, "value": value, "name": name}
