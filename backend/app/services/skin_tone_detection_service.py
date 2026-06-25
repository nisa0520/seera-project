"""Estimasi skin tone dari warna kulit representatif (FR-IMG-06).

Rantai teori yang diimplementasikan:

  1. Chardon et al. (1991) — mendefinisikan Individual Typology Angle (ITA):
        ITA = arctan((L* − 50) / b*)  [derajat]
     dihitung pada ruang warna CIELAB (iluminan D65). ITA adalah ukuran
     kuantitatif pigmentasi melanin konstitusional berdasarkan kecerahan
     (L*) dan komponen kuning (b*).

  2. Del Bino & Bernerd (2013) — memvalidasi ITA pada 3.500 perempuan dari
     populasi Asia, Afrika, Eropa, dan Amerika Latin, dan menetapkan 6
     kategori dengan batas 55° / 41° / 28° / 10° / −30°.
     Nama kategori asli Del Bino: Very Light / Light / Intermediate /
     Tan / Brown / Dark.

  3. Nasr (2018) — menggunakan skala Fitzpatrick dalam konteks fashion
     dengan label: Very Fair / Fair / Medium Fair / Moderate Brown /
     Brown / Dark Brown.

Keputusan desain: keenam kategori ITA Del Bino dipadankan (aligned) dengan
nama Nasr karena keduanya merepresentasikan spektrum warna kulit yang sama
dari paling terang ke paling gelap. Pemadanan ini membuat output kompatibel
dengan FIS Layer 1 existing yang menggunakan label Nasr.

Catatan batasan: Del Bino menyatakan Fitzpatrick "ill-adapted to Asians";
ITA justru menjadi alternatif yang lebih terukur. Namun batas 28° (III/IV)
belum divalidasi spesifik untuk populasi Indonesia — zona ini paling sensitif
karena L* ≈ 50 membuat denominator ITA mendekati nol.
"""
import math

import cv2
import numpy as np

from app.services.input_validation_service import SKIN_TONE_MAP


# Batas ITA (derajat) dari Del Bino & Bernerd (2013), urut dari paling terang.
# Del Bino : Very Light | Light | Intermediate | Tan    | Brown | Dark
# Nasr     : Very Fair  | Fair  | Medium Fair  | Mod. Brown | Brown | Dark Brown
# Kode FIS : I          | II    | III          | IV     | V     | VI
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
