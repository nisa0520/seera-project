"""Fuzzy membership functions per Bab IV.2.7.1 (Skripsi/TA).

Berisi fungsi keanggotaan dasar (triangular/trapezoidal, Persamaan 1-2) serta
fuzzifikasi non-singleton (Persamaan 3-4) untuk variabel kategorikal (Skin
Tone, Undertone) yang dipilih pengguna secara diskrit.
"""


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

# Urutan ketetanggaan Skin Tone di sepanjang universe [1, 6] (Tabel IV.12).
SKIN_TONE_ORDER = ["VERY_FAIR", "FAIR", "MEDIUM_FAIR", "MODERATE_BROWN", "BROWN", "DARK_BROWN"]

# Nilai crisp yang dipilih pengguna (tombol) selalu berupa titik tengah kategori.
SKIN_TONE_VALUE_TO_KEY = {
    1.0: "VERY_FAIR",
    2.0: "FAIR",
    3.0: "MEDIUM_FAIR",
    4.0: "MODERATE_BROWN",
    5.0: "BROWN",
    6.0: "DARK_BROWN",
}

UNDERTONE_SETS = {
    "COOL": ("trapezoidal", (0.0, 0.0, 0.5, 0.8)),
    "NEUTRAL": ("triangular", (0.6, 1.0, 1.4)),
    "WARM": ("trapezoidal", (1.2, 1.5, 2.0, 2.0)),
}

# Urutan ketetanggaan Undertone di sepanjang universe [0, 2] (Tabel IV.13).
UNDERTONE_ORDER = ["COOL", "NEUTRAL", "WARM"]

UNDERTONE_VALUE_TO_KEY = {
    0.0: "COOL",
    1.0: "NEUTRAL",
    2.0: "WARM",
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


def _ascending_segment(set_def: tuple) -> tuple[float, float]:
    """Titik (awal, akhir) sisi naik menuju core, sama untuk triangular/trapezoidal."""
    _kind, params = set_def
    a, b = params[0], params[1]
    return a, b


def _descending_segment(set_def: tuple) -> tuple[float, float]:
    """Titik (awal, akhir) sisi turun dari core, berbeda posisi antar bentuk."""
    kind, params = set_def
    if kind == "triangular":
        _a, b, c = params
        return b, c
    _a, b, c, d = params
    return c, d


def fire_neighbor(lower_set: tuple, upper_set: tuple) -> float:
    """Komposisi sup-min dua himpunan bertetangga (Persamaan 4).

    fire = (c1 - a2) / (w1 + w2), dengan c1 ujung sisi turun himpunan yang
    lebih rendah dan a2 awal sisi naik himpunan yang lebih tinggi. Diturunkan
    dari titik potong dua garis linear (lihat verifikasi Gambar IV.19).
    """
    b1, c1 = _descending_segment(lower_set)
    a2, b2 = _ascending_segment(upper_set)
    w1 = c1 - b1
    w2 = b2 - a2
    if c1 <= a2:
        return 0.0
    if w1 + w2 == 0:
        return 1.0
    return clamp((c1 - a2) / (w1 + w2), 0.0, 1.0)


def non_singleton_fire(input_key: str, sets_dict: dict, order: list[str]) -> dict:
    """Fuzzifikasi non-singleton (Mouzouris & Mendel, 1997; Persamaan 3-4).

    Memodelkan kategori terpilih pengguna sebagai himpunan fuzzy penuh
    (bukan titik crisp tunggal), lalu menghitung fire terhadap himpunan itu
    sendiri (=1, Core) serta kedua tetangga langsungnya pada sumbu universe.
    Himpunan yang bukan tetangga langsung tidak beririsan (fire=0), sesuai
    definisi parameter pada Tabel IV.12/IV.13.
    """
    idx = order.index(input_key)
    fires = {label: 0.0 for label in order}
    fires[input_key] = 1.0
    if idx > 0:
        lower_key = order[idx - 1]
        fires[lower_key] = fire_neighbor(sets_dict[lower_key], sets_dict[input_key])
    if idx < len(order) - 1:
        upper_key = order[idx + 1]
        fires[upper_key] = fire_neighbor(sets_dict[input_key], sets_dict[upper_key])
    return fires
