"""Input normalization & validation for gender, skin tone & undertone."""
from typing import Optional

GENDER_MAP = {
    "MALE": "Pria",
    "FEMALE": "Wanita",
    "PREFER_NOT_TO_SAY": "Semua koleksi",
}

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

GENDER_ALIASES = {
    "M": "MALE",
    "MALE": "MALE",
    "PRIA": "MALE",
    "LAKI LAKI": "MALE",
    "COWOK": "MALE",
    "F": "FEMALE",
    "FEMALE": "FEMALE",
    "WANITA": "FEMALE",
    "PEREMPUAN": "FEMALE",
    "CEWEK": "FEMALE",
    "PREFER NOT TO SAY": "PREFER_NOT_TO_SAY",
    "SKIP": "PREFER_NOT_TO_SAY",
    "LEWATI": "PREFER_NOT_TO_SAY",
    "RAHASIA": "PREFER_NOT_TO_SAY",
    "SEMUA": "PREFER_NOT_TO_SAY",
    "SEMUA KOLEKSI": "PREFER_NOT_TO_SAY",
    "BEBAS": "PREFER_NOT_TO_SAY",
    "TIDAK MENYEBUTKAN": "PREFER_NOT_TO_SAY",
    "TIDAK INGIN MENYEBUTKAN": "PREFER_NOT_TO_SAY",
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


def _clean(raw: str) -> str:
    return " ".join(str(raw).strip().upper().replace("-", " ").replace("_", " ").split())


def normalize_gender(raw: str) -> Optional[str]:
    if raw is None:
        return None
    cleaned = _clean(raw)
    if cleaned in GENDER_MAP:
        return cleaned
    if cleaned in GENDER_ALIASES:
        return GENDER_ALIASES[cleaned]
    return None


def normalize_skin_tone(raw: str) -> Optional[str]:
    if raw is None:
        return None
    cleaned = _clean(raw)
    if cleaned in SKIN_TONE_MAP:
        return cleaned
    if cleaned in SKIN_TONE_ALIASES:
        return SKIN_TONE_ALIASES[cleaned]
    return None


def normalize_undertone(raw: str) -> Optional[str]:
    if raw is None:
        return None
    cleaned = _clean(raw)
    if cleaned in UNDERTONE_MAP:
        return cleaned
    if cleaned in UNDERTONE_ALIASES:
        return UNDERTONE_ALIASES[cleaned]
    return None


def gender_payload(code: str) -> dict:
    return {"code": code, "name": GENDER_MAP[code]}


def skin_tone_payload(code: str) -> dict:
    value, name = SKIN_TONE_MAP[code]
    return {"code": code, "value": value, "name": name}


def undertone_payload(code: str) -> dict:
    value, name = UNDERTONE_MAP[code]
    return {"code": code, "value": value, "name": name}
