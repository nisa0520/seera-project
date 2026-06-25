"""Estimasi undertone dari warna kulit representatif (FR-IMG-07).

Dasar teori:
  Nasr (2018) mendefinisikan undertone berdasarkan pigmen dominan yang
  tampak pada warna kulit:
    - WARM  → kandungan kuning (karotenoid / eumelanin) dominan
    - COOL  → kandungan merah-muda / kebiruan (oksihemoglobin) dominan
    - NEUTRAL → keseimbangan antara keduanya

  Implementasi menggunakan sudut hue CIELAB (h_ab = atan2(b*, a*)):
    - b* tinggi relatif terhadap a*  → sudut hue besar → WARM
    - a* tinggi relatif terhadap b*  → sudut hue kecil → COOL
    - keseimbangan a* dan b*         → sudut hue tengah → NEUTRAL

  Ruang CIELAB dipilih karena perceptually uniform sehingga rasio b*/a*
  langsung merepresentasikan dominansi pigmen kuning vs merah-muda.

Keputusan desain:
  Batas HUE_COOL_MAX = 47° dan HUE_WARM_MIN = 58° adalah parameter
  kalibrasi sistem yang ditetapkan berdasarkan distribusi tipikal sudut hue
  kulit manusia (a* ≈ 10–20, b* ≈ 10–30) pada sampel wajah yang dipotret
  dalam kondisi pencahayaan standar. Batas ini bukan nilai dari literatur
  yang dapat dikutip secara langsung.
"""
import math

from app.services.input_validation_service import UNDERTONE_MAP
from app.services.skin_tone_detection_service import rgb_to_lab


# Batas sudut hue (derajat) antar kategori undertone — parameter kalibrasi desain.
# Kulit tipikal: a* ∈ [10, 20], b* ∈ [10, 30] → h_ab ∈ [26°, 72°]
HUE_COOL_MAX = 47.0   # ≤ 47° → COOL
HUE_WARM_MIN = 58.0   # ≥ 58° → WARM, antara keduanya → NEUTRAL


def compute_hue_angle(rgb: tuple[int, int, int]) -> float:
    _, a_star, b_star = rgb_to_lab(rgb)
    # atan2 menangani a_star = 0 secara native; tidak perlu guard pembagi.
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
