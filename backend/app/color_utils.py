def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    return int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    r_p = r / 255
    g_p = g / 255
    b_p = b / 255

    c_max = max(r_p, g_p, b_p)
    c_min = min(r_p, g_p, b_p)
    delta = c_max - c_min

    if delta == 0:
        h = 0
    elif c_max == r_p:
        h = (60 * ((g_p - b_p) / delta)) % 360
    elif c_max == g_p:
        h = 60 * (((b_p - r_p) / delta) + 2)
    else:
        h = 60 * (((r_p - g_p) / delta) + 4)

    s = 0 if c_max == 0 else delta / c_max
    v = c_max

    return round(h, 3), round(s, 4), round(v, 4)

# def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
#     """
#     Mengkonversi nilai warna dari ruang warna RGB ke HSV.

#     Langkah-langkah (Chernov et al., 2015):
#       1. Temukan M = max(R, G, B) dan m = min(R, G, B)
#       2. Tetapkan V = M
#       3. Hitung d = M − m
#       4. Jika d = 0 → kasus akromatik: S = 0, H = 0 (tidak terdefinisi)
#       5. Hitung S = d / M
#       6. Hitung H berdasarkan komponen mana yang menjadi M dan m:
#             H = (1/6) * { (G−B)/d,           jika M=R dan m=B
#                         { 1 + (R−B)/d,        jika M=G dan m=B
#                         { 2 + (B−R)/d,        jika M=G dan m=R
#                         { 3 + (G−R)/d,        jika M=B dan m=R
#                         { 4 + (R−G)/d,        jika M=B dan m=G
#                         { 5 + (B−G)/d,        jika M=R dan m=G

#     Parameters
#     ----------
#     r : int  — komponen merah  (0–255)
#     g : int  — komponen hijau  (0–255)
#     b : int  — komponen biru   (0–255)

#     Returns
#     -------
#     tuple[float, float, float]
#         (H, S, V) di mana:
#             H ∈ [0°, 360°)
#             S ∈ [0, 1]
#             V ∈ [0, 1]
#     """
#     # Normalisasi ke rentang [0, 1]
#     r_p = r / 255
#     g_p = g / 255
#     b_p = b / 255

#     # Langkah 1: Temukan M (maksimum) dan m (minimum)
#     M = max(r_p, g_p, b_p)
#     m = min(r_p, g_p, b_p)

#     # Langkah 2: V = M
#     v = M

#     # Langkah 3: d = M − m
#     d = M - m

#     # Langkah 4: Kasus akromatik (d = 0)
#     if d == 0:
#         s = 0.0
#         h = 0.0  # H tidak terdefinisi pada kasus akromatik
#         return round(h, 3), round(s, 4), round(v, 4)

#     # Langkah 5: S = d / M
#     s = d / M

#     # Langkah 6: Hitung H menggunakan rumus Chernov et al. (2015)
#     if M == r_p and m == b_p:
#         # Sektor 1: M=R, m=B → H = (1/6) * (G−B)/d
#         h = (1 / 6) * ((g_p - b_p) / d)
#     elif M == g_p and m == b_p:
#         # Sektor 2: M=G, m=B → H = (1/6) * (1 + (R−B)/d)
#         h = (1 / 6) * (1 + (r_p - b_p) / d)
#     elif M == g_p and m == r_p:
#         # Sektor 3: M=G, m=R → H = (1/6) * (2 + (B−R)/d)
#         h = (1 / 6) * (2 + (b_p - r_p) / d)
#     elif M == b_p and m == r_p:
#         # Sektor 4: M=B, m=R → H = (1/6) * (3 + (G−R)/d)
#         h = (1 / 6) * (3 + (g_p - r_p) / d)
#     elif M == b_p and m == g_p:
#         # Sektor 5: M=B, m=G → H = (1/6) * (4 + (R−G)/d)
#         h = (1 / 6) * (4 + (r_p - g_p) / d)
#     else:
#         # Sektor 6: M=R, m=G → H = (1/6) * (5 + (B−G)/d)
#         h = (1 / 6) * (5 + (b_p - g_p) / d)

#     # Konversi H dari [0, 1] ke derajat [0°, 360°)
#     h = h * 360

#     return round(h, 3), round(s, 4), round(v, 4)


def calculate_ct(h: float, s: float) -> float:
    if s == 0:
        return 1.0

    if 90 <= h <= 150 or 270 <= h <= 330:
        return 1.0

    if 90 <= h <= 270:
        ct = 0.8 * (1 - abs(h - 210) / 60)
        return round(max(0.0, min(0.8, ct)), 4)

    if 0 <= h < 90:
        ct = 1.2 + 0.8 * (1 - abs(h - 45) / 45)
        return round(max(1.2, min(2.0, ct)), 4)

    ct = 1.2 + 0.8 * (1 - abs(h - 345) / 15)
    return round(max(1.2, min(2.0, ct)), 4)


def compute_color_features(hex_code: str) -> dict:
    r, g, b = hex_to_rgb(hex_code)
    h, s, v = rgb_to_hsv(r, g, b)
    ct = calculate_ct(h, s)
    return {
        "h_value": h,
        "s_value": s,
        "v_value": v,
        "ct_value": ct,
        "cb_value": v,
    }
