"""FIS Layer 1 - Klasifikasi Seasonal Color Type per Bab IV.2.7.3.

Skin Tone dan Undertone dipilih pengguna secara diskrit (tombol antarmuka),
sehingga difuzzifikasi non-singleton (Persamaan 3-4): kategori terpilih
direpresentasikan sebagai himpunan fuzzy penuh, bukan titik crisp tunggal,
agar tumpang-tindih terhadap kategori tetangga tetap terjaga.

Keluaran berupa vektor keanggotaan musim (Spring/Summer/Autumn/Winter) hasil
agregasi MAX antar-aturan sekonsekuen (Persamaan 6), TANPA defuzzifikasi -
karena struktur ketetanggaan keempat musim bersifat siklis (Gambar IV.18),
bukan linear, sehingga rata-rata terbobot pada satu sumbu numerik akan
menghasilkan keliru-klasifikasi (lihat Subbab IV.2.7.3 Poin 3).
"""
from app.services.fuzzy_membership import (
    SKIN_TONE_SETS,
    SKIN_TONE_ORDER,
    SKIN_TONE_VALUE_TO_KEY,
    UNDERTONE_SETS,
    UNDERTONE_ORDER,
    UNDERTONE_VALUE_TO_KEY,
    non_singleton_fire,
)


SEASONAL_NAMES = {
    "SPRING": "Spring",
    "SUMMER": "Summer",
    "AUTUMN": "Autumn",
    "WINTER": "Winter",
}

# (skin_tone_set, undertone_set, output_seasonal, rule_id) - Tabel IV.14.
LAYER1_RULES = [
    ("VERY_FAIR", "COOL", "SUMMER", "R1"),
    ("FAIR", "COOL", "SUMMER", "R2"),
    ("MEDIUM_FAIR", "COOL", "SUMMER", "R3"),
    ("MODERATE_BROWN", "COOL", "WINTER", "R4"),
    ("BROWN", "COOL", "WINTER", "R5"),
    ("DARK_BROWN", "COOL", "WINTER", "R6"),
    ("VERY_FAIR", "WARM", "SPRING", "R7"),
    ("FAIR", "WARM", "SPRING", "R8"),
    ("MEDIUM_FAIR", "WARM", "SPRING", "R9"),
    ("MODERATE_BROWN", "WARM", "AUTUMN", "R10"),
    ("BROWN", "WARM", "AUTUMN", "R11"),
    ("DARK_BROWN", "WARM", "AUTUMN", "R12"),
    ("VERY_FAIR", "NEUTRAL", "SUMMER", "R13"),
    ("FAIR", "NEUTRAL", "SUMMER", "R14"),
    ("MEDIUM_FAIR", "NEUTRAL", "SPRING", "R15"),
    ("MODERATE_BROWN", "NEUTRAL", "AUTUMN", "R16"),
    ("BROWN", "NEUTRAL", "AUTUMN", "R17"),
    ("DARK_BROWN", "NEUTRAL", "WINTER", "R18"),
]


def classify(skin_tone: float, undertone: float) -> dict:
    skin_key = SKIN_TONE_VALUE_TO_KEY[skin_tone]
    undertone_key = UNDERTONE_VALUE_TO_KEY[undertone]

    fire_skin = non_singleton_fire(skin_key, SKIN_TONE_SETS, SKIN_TONE_ORDER)
    fire_undertone = non_singleton_fire(undertone_key, UNDERTONE_SETS, UNDERTONE_ORDER)

    fired = []
    seasonal_membership = {"SPRING": 0.0, "SUMMER": 0.0, "AUTUMN": 0.0, "WINTER": 0.0}

    for skin_set, undertone_set, seasonal_out, rule_id in LAYER1_RULES:
        mu_a = fire_skin.get(skin_set, 0.0)
        mu_b = fire_undertone.get(undertone_set, 0.0)
        alpha = min(mu_a, mu_b)  # Persamaan 5
        if alpha <= 0:
            continue
        fired.append({
            "rule_id": rule_id,
            "skin_set": skin_set,
            "undertone_set": undertone_set,
            "output_seasonal": seasonal_out,
            "alpha": alpha,
        })
        if alpha > seasonal_membership[seasonal_out]:  # Persamaan 6 (MAX)
            seasonal_membership[seasonal_out] = alpha

    dominant = max(seasonal_membership.items(), key=lambda kv: kv[1])[0]
    score_seasonal = seasonal_membership[dominant]

    return {
        "seasonal_code": dominant,
        "seasonal_name": SEASONAL_NAMES[dominant],
        "score_seasonal": score_seasonal,
        "seasonal_membership": seasonal_membership,
        "skin_membership": fire_skin,
        "undertone_membership": fire_undertone,
        "fired_rules": fired,
    }
