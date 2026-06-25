"""Deteksi wajah dan sampling area kulit (FR-IMG-04, FR-IMG-05).

Deteksi wajah:
  Menggunakan Haar Cascade frontal face (Viola & Jones 2001; Lienhart &
  Maydt 2002) via OpenCV. Wajah dideteksi pada grayscale yang telah
  dinormalisasi histogram (equalizeHist) agar lebih robust terhadap
  variasi pencahayaan.

Sampling area kulit:
  4 patch geometris relatif terhadap bounding box wajah (dahi, pipi kiri,
  pipi kanan, dagu) dipilih agar menghindari area mata, alis, bibir, dan
  tepi rambut. Setiap patch difilter dengan skin mask YCrCb sebelum
  digabungkan.

Skin mask YCrCb:
  Chai & Ngan (1999) menetapkan rentang Cr 133–173 dan Cb 77–127 pada
  ruang YCrCb sebagai area warna kulit yang konsisten lintas etnis.
  YCrCb dipilih karena memisahkan luminansi (Y) dari krominansi (Cr, Cb)
  sehingga mask kulit lebih stabil terhadap perubahan kecerahan cahaya
  dibandingkan threshold langsung pada RGB.

Warna representatif:
  Median RGB dari seluruh piksel kulit yang lolos mask — median digunakan
  untuk ketahanan terhadap specular highlight dan piksel rambut liar yang
  menyusup ke patch.
"""
from typing import Optional

import cv2
import numpy as np

from app.core.config import settings
from app.services.image_quality_service import (
    QUALITY_OK,
    QUALITY_NO_FACE,
    QUALITY_MULTIPLE_FACES,
    QUALITY_FACE_TOO_SMALL,
    QUALITY_SKIN_AREA_OBSCURED,
)


_FACE_CASCADE: Optional[cv2.CascadeClassifier] = None

# Patch sampling relatif terhadap kotak wajah (x, y, w, h dalam fraksi 0..1).
# Dipilih agar tidak menyentuh mata, alis, bibir, dan tepi rambut.
SAMPLE_PATCHES = (
    ("forehead", 0.30, 0.13, 0.40, 0.12),
    ("left_cheek", 0.16, 0.45, 0.20, 0.18),
    ("right_cheek", 0.64, 0.45, 0.20, 0.18),
    ("chin", 0.40, 0.78, 0.20, 0.12),
)

# Rentang skin mask YCrCb dari Chai & Ngan (1999): Cr 133–173, Cb 77–127.
SKIN_CR_RANGE = (133, 173)
SKIN_CB_RANGE = (77, 127)

# Wajah lain dianggap "dominan" bila luasnya >= 40% wajah terbesar (BR-IMG-04).
DOMINANT_FACE_AREA_RATIO = 0.4


def _cascade() -> cv2.CascadeClassifier:
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        _FACE_CASCADE = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
    return _FACE_CASCADE


def detect_faces(image_rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Deteksi kotak wajah (x, y, w, h). Dapat dimock pada unit test."""
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = _cascade().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    return [tuple(int(v) for v in face) for face in faces]


def evaluate_faces(image_rgb: np.ndarray) -> dict:
    """Validasi jumlah & ukuran wajah. Mengembalikan status + bbox wajah utama."""
    faces = detect_faces(image_rgb)
    if not faces:
        return {"status": QUALITY_NO_FACE, "face_count": 0, "face_bbox": None}

    largest_area = max(w * h for (_, _, w, h) in faces)
    dominant = [f for f in faces if (f[2] * f[3]) >= DOMINANT_FACE_AREA_RATIO * largest_area]
    primary = max(dominant, key=lambda f: f[2] * f[3])

    if len(dominant) > 1:
        return {"status": QUALITY_MULTIPLE_FACES, "face_count": len(dominant), "face_bbox": primary}

    img_width = image_rgb.shape[1]
    if primary[2] < settings.IMAGE_MIN_FACE_RATIO * img_width:
        return {"status": QUALITY_FACE_TOO_SMALL, "face_count": 1, "face_bbox": primary}

    return {"status": QUALITY_OK, "face_count": 1, "face_bbox": primary}


def _skin_mask(patch_rgb: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(patch_rgb, cv2.COLOR_RGB2YCrCb)
    cr = ycrcb[:, :, 1]
    cb = ycrcb[:, :, 2]
    return (
        (cr >= SKIN_CR_RANGE[0]) & (cr <= SKIN_CR_RANGE[1])
        & (cb >= SKIN_CB_RANGE[0]) & (cb <= SKIN_CB_RANGE[1])
    )


def sample_skin_color(image_rgb: np.ndarray, face_bbox: tuple[int, int, int, int]) -> dict:
    """Ambil warna kulit representatif (median RGB) dari patch wajah yang relevan."""
    x, y, w, h = face_bbox
    img_h, img_w = image_rgb.shape[:2]

    skin_pixels = []
    for _, fx, fy, fw, fh in SAMPLE_PATCHES:
        px1 = max(0, int(x + fx * w))
        py1 = max(0, int(y + fy * h))
        px2 = min(img_w, int(x + (fx + fw) * w))
        py2 = min(img_h, int(y + (fy + fh) * h))
        if px2 <= px1 or py2 <= py1:
            continue
        patch = image_rgb[py1:py2, px1:px2]
        mask = _skin_mask(patch)
        if mask.any():
            skin_pixels.append(patch[mask])

    if not skin_pixels:
        return {"status": QUALITY_SKIN_AREA_OBSCURED, "rgb": None, "pixel_count": 0}

    all_pixels = np.concatenate(skin_pixels, axis=0)
    if all_pixels.shape[0] < settings.IMAGE_MIN_SKIN_PIXELS:
        return {"status": QUALITY_SKIN_AREA_OBSCURED, "rgb": None, "pixel_count": int(all_pixels.shape[0])}

    median_rgb = tuple(int(v) for v in np.median(all_pixels, axis=0))
    return {"status": QUALITY_OK, "rgb": median_rgb, "pixel_count": int(all_pixels.shape[0])}
