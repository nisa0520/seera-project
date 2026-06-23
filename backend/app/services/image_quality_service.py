"""Validasi kualitas image sebelum analisis warna kulit (FR-IMG-02, FR-IMG-04).

Modul ini sengaja terpisah dari logika fuzzy/ROC (NFR-IMG-07): hanya menangani
dekoding file, validasi format/ukuran, pencahayaan, dan ketajaman.
"""
import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from app.core.config import settings


ALLOWED_FORMATS = {"JPEG", "PNG"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

QUALITY_OK = "OK"
QUALITY_INVALID_FILE = "INVALID_FILE"
QUALITY_FILE_TOO_LARGE = "FILE_TOO_LARGE"
QUALITY_UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
QUALITY_RESOLUTION_TOO_LOW = "RESOLUTION_TOO_LOW"
QUALITY_TOO_DARK = "TOO_DARK"
QUALITY_TOO_BRIGHT = "TOO_BRIGHT"
QUALITY_BLURRY = "BLURRY"
QUALITY_NO_FACE = "NO_FACE"
QUALITY_MULTIPLE_FACES = "MULTIPLE_FACES"
QUALITY_FACE_TOO_SMALL = "FACE_TOO_SMALL"
QUALITY_SKIN_AREA_OBSCURED = "SKIN_AREA_OBSCURED"

QUALITY_MESSAGES = {
    QUALITY_OK: "Foto valid dan siap dianalisis.",
    QUALITY_INVALID_FILE: "File tidak dapat dibaca sebagai gambar. Silakan unggah file JPG, JPEG, atau PNG yang valid.",
    QUALITY_FILE_TOO_LARGE: "Ukuran file terlalu besar (maksimal 5 MB). Silakan gunakan foto dengan ukuran lebih kecil.",
    QUALITY_UNSUPPORTED_FORMAT: "Format file tidak didukung. Gunakan format JPG, JPEG, atau PNG.",
    QUALITY_RESOLUTION_TOO_LOW: "Resolusi foto terlalu kecil. Gunakan foto dengan resolusi lebih tinggi agar wajah terlihat jelas.",
    QUALITY_TOO_DARK: "Pencahayaan terlalu gelap. Coba ambil foto di tempat dengan cahaya yang lebih terang.",
    QUALITY_TOO_BRIGHT: "Pencahayaan terlalu terang. Hindari cahaya langsung yang menyilaukan wajah.",
    QUALITY_BLURRY: "Foto terlihat buram. Pegang kamera dengan stabil lalu coba lagi.",
    QUALITY_NO_FACE: "Wajah tidak terdeteksi pada foto. Pastikan wajah berada di dalam area panduan.",
    QUALITY_MULTIPLE_FACES: "Terdeteksi lebih dari satu wajah. Pastikan hanya wajah Anda yang ada di dalam foto.",
    QUALITY_FACE_TOO_SMALL: "Wajah terlalu jauh dari kamera. Dekatkan wajah ke area panduan lalu coba lagi.",
    QUALITY_SKIN_AREA_OBSCURED: "Area kulit wajah kurang terlihat (mungkin tertutup masker, rambut, atau aksesoris). Coba ambil ulang foto.",
}


def quality_message(status: str) -> str:
    return QUALITY_MESSAGES.get(status, QUALITY_MESSAGES[QUALITY_INVALID_FILE])


def validate_file(content: bytes, filename: Optional[str] = None) -> dict:
    """Validasi tipe & ukuran file lalu dekode menjadi array RGB.

    Mengembalikan {"status": ..., "image": np.ndarray|None}.
    """
    if not content:
        return {"status": QUALITY_INVALID_FILE, "image": None}

    if len(content) > settings.IMAGE_MAX_UPLOAD_BYTES:
        return {"status": QUALITY_FILE_TOO_LARGE, "image": None}

    if filename:
        lowered = filename.lower()
        if "." in lowered and not any(lowered.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            return {"status": QUALITY_UNSUPPORTED_FORMAT, "image": None}

    try:
        with Image.open(io.BytesIO(content)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(content)) as img:
            if (img.format or "").upper() not in ALLOWED_FORMATS:
                return {"status": QUALITY_UNSUPPORTED_FORMAT, "image": None}
            rgb = np.array(img.convert("RGB"))
    except (UnidentifiedImageError, OSError, ValueError):
        return {"status": QUALITY_INVALID_FILE, "image": None}

    h, w = rgb.shape[:2]
    if min(h, w) < settings.IMAGE_MIN_DIMENSION:
        return {"status": QUALITY_RESOLUTION_TOO_LOW, "image": None}

    return {"status": QUALITY_OK, "image": rgb}


def check_brightness(image_rgb: np.ndarray) -> str:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    mean_brightness = float(gray.mean())
    if mean_brightness < settings.IMAGE_BRIGHTNESS_MIN:
        return QUALITY_TOO_DARK
    if mean_brightness > settings.IMAGE_BRIGHTNESS_MAX:
        return QUALITY_TOO_BRIGHT
    return QUALITY_OK


def _focus_measure(gray: np.ndarray) -> float:
    """Variance-of-Laplacian: makin tinggi makin tajam."""
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def check_blur(image_rgb: np.ndarray) -> str:
    """Deteksi foto buram via ketajaman tepi (variance-of-Laplacian).

    Variance global rentan positif palsu: foto tajam tapi wajahnya mulus dengan
    latar polos punya sedikit tekstur frekuensi tinggi, sehingga area datar
    menekan rata-rata variance di bawah ambang walau foto sebenarnya fokus.
    Karena subjek berada di tengah (di balik garis panduan), kita ambil nilai
    tertinggi antara frame penuh dan crop tengah. Efeknya selalu melonggarkan
    (nilai tak pernah lebih kecil dari sebelumnya): foto tajam lolos lewat salah
    satu ukuran, sedangkan foto benar-benar buram tetap mendekati nol di keduanya.
    """
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    variance = _focus_measure(gray)

    h, w = gray.shape[:2]
    ch, cw = int(h * 0.6), int(w * 0.6)
    if ch > 0 and cw > 0:
        y0, x0 = (h - ch) // 2, (w - cw) // 2
        variance = max(variance, _focus_measure(gray[y0:y0 + ch, x0:x0 + cw]))

    if variance < settings.IMAGE_BLUR_THRESHOLD:
        return QUALITY_BLURRY
    return QUALITY_OK
