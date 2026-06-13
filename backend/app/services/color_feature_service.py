"""Color feature conversion: hex -> RGB -> HSV -> CT, CB.

Implements PRD Section 17.7.
"""
from app.services.fuzzy_membership import clamp


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    cleaned = hex_code.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError("Hex color harus 6 digit")
    return int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    rp, gp, bp = r / 255.0, g / 255.0, b / 255.0
    cmax = max(rp, gp, bp)
    cmin = min(rp, gp, bp)
    delta = cmax - cmin

    if delta == 0:
        h = 0.0
    elif cmax == rp:
        h = 60.0 * (((gp - bp) / delta) % 6)
    elif cmax == gp:
        h = 60.0 * (((bp - rp) / delta) + 2)
    else:
        h = 60.0 * (((rp - gp) / delta) + 4)

    if h < 0:
        h += 360.0

    s = 0.0 if cmax == 0 else delta / cmax
    v = cmax
    return h, s, v


def hue_to_color_temperature(h: float, s: float) -> float:
    if s == 0:
        return 1.0

    h = h % 360.0

    if 0 <= h <= 90:
        return clamp(1.2 + 0.8 * (1 - abs(h - 45) / 45), 1.2, 2.0)
    if 90 < h < 150:
        return 1.0
    if 150 <= h <= 270:
        return clamp(0.8 * (1 - abs(h - 210) / 60), 0.0, 0.8)
    if 270 < h < 330:
        return 1.0
    if 330 <= h <= 360:
        return clamp(1.2 + 0.8 * (1 - abs(h - 345) / 15), 1.2, 2.0)

    return 1.0


def hsv_to_color_brightness(v: float) -> float:
    return clamp(v, 0.0, 1.0)


def compute_color_features(hex_code: str) -> dict:
    r, g, b = hex_to_rgb(hex_code)
    h, s, v = rgb_to_hsv(r, g, b)
    ct = hue_to_color_temperature(h, s)
    cb = hsv_to_color_brightness(v)
    return {
        "r": r,
        "g": g,
        "b": b,
        "h": h,
        "s": s,
        "v": v,
        "ct": ct,
        "cb": cb,
    }
