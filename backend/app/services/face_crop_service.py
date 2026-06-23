"""Pemrosesan crop kepala pengguna untuk virtual try-on.

Dari foto pengguna + bbox wajah, modul ini menghasilkan aset kepala siap
komposit:

1. Crop deterministik — wajah selalu menempati ``FACE_FRACTION`` lebar crop
   dengan pusat di ``FACE_CENTER_Y`` tinggi (portrait 1:1.25), sehingga skala
   kepala konsisten terhadap anchor foto produk.
2. Segmentasi kepala (GrabCut OpenCV) — background foto pengguna dibuang,
   siluet rambut asli dipertahankan, tepi alpha dihaluskan.
3. Pengukuran lebar kepala aktual (fraksi lebar crop) agar frontend dapat
   menyamakan lebar kepala pengguna dengan lebar kepala yang dianotasi
   per foto produk. (Warna kulit tidak diubah — penting untuk akurasi
   aplikasi personal color; penyesuaian kecerahan dilakukan frontend
   per produk.)

Hasil hanya dikirim dalam respons sesi (base64), tidak pernah disimpan
(NFR-IMG-02).
"""
import base64
import io

import cv2
import numpy as np
from PIL import Image

FACE_FRACTION = 0.70
FACE_CENTER_Y = 0.44
FACE_RATIO = 1.25
CROP_W = 256
CROP_H = 320

# Fallback bila segmentasi tidak meyakinkan.
DEFAULT_HEAD_WIDTH_FRACTION = 0.78


def _deterministic_crop(image_rgb: np.ndarray, face_bbox: tuple) -> np.ndarray:
    """Crop portrait 1:1.25 dengan framing wajah tetap; area di luar foto digandakan dari tepi."""
    x, y, w, h = face_bbox
    img_h, img_w = image_rgb.shape[:2]
    face_cx = x + w / 2.0
    face_cy = y + h / 2.0
    crop_w = w / FACE_FRACTION
    crop_h = crop_w * FACE_RATIO
    left = int(round(face_cx - crop_w / 2))
    top = int(round(face_cy - crop_h * FACE_CENTER_Y))
    right = int(round(left + crop_w))
    bottom = int(round(top + crop_h))

    pad_l = max(0, -left)
    pad_t = max(0, -top)
    pad_r = max(0, right - img_w)
    pad_b = max(0, bottom - img_h)
    if pad_l or pad_t or pad_r or pad_b:
        image_rgb = cv2.copyMakeBorder(
            image_rgb, pad_t, pad_b, pad_l, pad_r, cv2.BORDER_REPLICATE
        )
        left += pad_l
        right += pad_l
        top += pad_t
        bottom += pad_t

    crop = image_rgb[top:bottom, left:right]
    return cv2.resize(crop, (CROP_W, CROP_H), interpolation=cv2.INTER_AREA)


def _segment_head(crop_rgb: np.ndarray) -> np.ndarray:
    """Segmentasi kepala via GrabCut. Mengembalikan alpha 0-255 (atau None bila gagal)."""
    mask = np.full((CROP_H, CROP_W), cv2.GC_PR_BGD, dtype=np.uint8)
    # Tepi crop hampir pasti background foto pengguna
    border_x = int(CROP_W * 0.04)
    mask[:, :border_x] = cv2.GC_BGD
    mask[:, CROP_W - border_x:] = cv2.GC_BGD
    mask[: int(CROP_H * 0.03), :] = cv2.GC_BGD
    # Area wajah (framing deterministik) pasti foreground
    face_w = FACE_FRACTION * CROP_W
    fx1 = int(CROP_W / 2 - face_w * 0.32)
    fx2 = int(CROP_W / 2 + face_w * 0.32)
    fy1 = int(CROP_H * FACE_CENTER_Y - face_w * 0.30)
    fy2 = int(CROP_H * FACE_CENTER_Y + face_w * 0.38)
    mask[fy1:fy2, fx1:fx2] = cv2.GC_FGD

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(
            cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2BGR),
            mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK,
        )
    except cv2.error:
        return None

    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Ambil komponen terhubung terbesar (kepala), rapikan tepi
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(alpha, connectivity=8)
    if n_labels <= 1:
        return None
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    alpha = np.where(labels == largest, 255, 0).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)

    coverage = float((alpha > 128).mean())
    if coverage < 0.18 or coverage > 0.92:
        return None
    return alpha


def _fallback_oval_alpha() -> np.ndarray:
    """Mask oval feather bila segmentasi gagal — output tetap konsisten."""
    alpha = np.zeros((CROP_H, CROP_W), dtype=np.uint8)
    cv2.ellipse(
        alpha,
        (CROP_W // 2, int(CROP_H * 0.46)),
        (int(CROP_W * 0.44), int(CROP_H * 0.45)),
        0, 0, 360, 255, -1,
    )
    return cv2.GaussianBlur(alpha, (31, 31), 0)


def _measure_head_width_fraction(alpha: np.ndarray) -> float:
    """Lebar kepala (fraksi lebar crop) dari baris-baris di area kepala (di atas dagu)."""
    chin_row = int(CROP_H * (FACE_CENTER_Y + FACE_FRACTION / FACE_RATIO / 2))
    widths = []
    for row in range(int(CROP_H * 0.10), chin_row):
        cols = np.where(alpha[row] > 128)[0]
        if cols.size >= 2:
            widths.append(cols[-1] - cols[0])
    if not widths:
        return DEFAULT_HEAD_WIDTH_FRACTION
    width = float(np.percentile(widths, 90)) / CROP_W
    return float(np.clip(width, 0.50, 0.95))


def build_face_asset(image_rgb: np.ndarray, face_bbox: tuple) -> dict:
    """Bangun aset kepala transparan + metrik skala untuk try-on."""
    crop = _deterministic_crop(image_rgb, face_bbox)
    alpha = _segment_head(crop)
    segmented = alpha is not None
    if not segmented:
        alpha = _fallback_oval_alpha()

    head_width_fraction = (
        _measure_head_width_fraction(alpha) if segmented else DEFAULT_HEAD_WIDTH_FRACTION
    )

    rgba = np.dstack([crop, alpha])
    buf = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG", optimize=True)
    data_url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    return {
        "data_url": data_url,
        "head_width_fraction": round(head_width_fraction, 3),
        "segmented": segmented,
    }
