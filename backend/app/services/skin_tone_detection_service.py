"""Estimasi skin tone dari warna kulit representatif (FR-IMG-06).

Menggunakan Individual Typology Angle (ITA) pada ruang warna CIELAB —
ukuran standar dermatologi (Del Bino & Bernerd) — lalu dipetakan ke skala
Fitzpatrick I–VI yang dipakai FIS Layer 1 existing.
"""
import math

import cv2
import numpy as np

from app.services.input_validation_service import SKIN_TONE_MAP


# Batas ITA (derajat) per kategori, urut dari paling terang.
# > 55: Very Light, 41–55: Light, 28–41: Intermediate, 10–28: Tan,
# -30–10: Brown, <= -30: Dark.
ITA_BOUNDARIES = (55.0, 41.0, 28.0, 10.0, -30.0)
ITA_CODES = ("I", "II", "III", "IV", "V", "VI")


def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Konversi sRGB (0-255) ke CIELAB sebenarnya (L* 0-100)."""
    arr = np.array([[rgb]], dtype=np.float32) / 255.0
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2Lab)[0][0]
    return float(lab[0]), float(lab[1]), float(lab[2])


def compute_ita(rgb: tuple[int, int, int]) -> float:
    l_star, _, b_star = rgb_to_lab(rgb)
    if abs(b_star) < 1e-6:
        b_star = 1e-6
    return math.degrees(math.atan((l_star - 50.0) / b_star))


def classify_ita(ita: float) -> str:
    for boundary, code in zip(ITA_BOUNDARIES, ITA_CODES):
        if ita > boundary:
            return code
    return ITA_CODES[-1]


def _confidence_from_boundaries(ita: float) -> float:
    """Keyakinan berdasarkan jarak ITA ke batas kategori terdekat.

    Tepat di batas kategori → 0.5; di tengah kategori → mendekati 0.95.
    """
    distances = [abs(ita - boundary) for boundary in ITA_BOUNDARIES]
    nearest = min(distances)
    # Lebar setengah pita kategori tipikal ~7 derajat (28→41 → lebar 13).
    half_band = 7.0
    confidence = 0.5 + min(nearest / half_band, 1.0) * 0.45
    return round(min(confidence, 0.95), 3)


def estimate_skin_tone(rgb: tuple[int, int, int]) -> dict:
    """Estimasi kode Fitzpatrick + confidence dari RGB kulit representatif."""
    ita = compute_ita(rgb)
    code = classify_ita(ita)
    value, name = SKIN_TONE_MAP[code]
    return {
        "code": code,
        "name": name,
        "value": value,
        "ita": round(ita, 2),
        "confidence": _confidence_from_boundaries(ita),
    }
