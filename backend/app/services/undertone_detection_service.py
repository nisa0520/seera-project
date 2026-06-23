"""Estimasi undertone dari warna kulit representatif (FR-IMG-07).

Menggunakan sudut hue CIELAB (hab = atan2(b*, a*)): kulit dengan undertone
warm condong ke kuning (sudut hue besar), cool condong ke merah muda/biru
(sudut hue kecil), dan di antaranya neutral. Output kompatibel dengan
kategori COOL/NEUTRAL/WARM pada FIS Layer 1 existing.
"""
import math

from app.services.input_validation_service import UNDERTONE_MAP
from app.services.skin_tone_detection_service import rgb_to_lab


# Sudut hue (derajat) batas kategori undertone untuk sampel kulit.
HUE_COOL_MAX = 47.0
HUE_WARM_MIN = 58.0


def compute_hue_angle(rgb: tuple[int, int, int]) -> float:
    _, a_star, b_star = rgb_to_lab(rgb)
    if abs(a_star) < 1e-6:
        a_star = 1e-6
    return math.degrees(math.atan2(b_star, a_star))


def classify_hue(hue_angle: float) -> str:
    if hue_angle <= HUE_COOL_MAX:
        return "COOL"
    if hue_angle >= HUE_WARM_MIN:
        return "WARM"
    return "NEUTRAL"


def _confidence_from_hue(hue_angle: float) -> float:
    """Tepat di batas → 0.5; makin jauh dari batas → mendekati 0.95."""
    nearest = min(abs(hue_angle - HUE_COOL_MAX), abs(hue_angle - HUE_WARM_MIN))
    half_band = 8.0
    confidence = 0.5 + min(nearest / half_band, 1.0) * 0.45
    return round(min(confidence, 0.95), 3)


def estimate_undertone(rgb: tuple[int, int, int]) -> dict:
    """Estimasi kategori undertone + confidence dari RGB kulit representatif."""
    hue_angle = compute_hue_angle(rgb)
    code = classify_hue(hue_angle)
    value, name = UNDERTONE_MAP[code]
    return {
        "code": code,
        "name": name,
        "value": value,
        "hue_angle": round(hue_angle, 2),
        "confidence": _confidence_from_hue(hue_angle),
    }
