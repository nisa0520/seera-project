"""PersonImageValidationService + MaskGenerationService (FR-VTO-03/04/06/07).

Memvalidasi foto upper-body/full-body pengguna untuk realistic try-on dan
membuat mask area pakaian yang akan diganti. Realistic try-on tidak boleh
berjalan hanya dari foto wajah (BR-VTO-01).
"""
import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.services import face_region_service
from app.services.image_quality_service import (
    QUALITY_OK,
    QUALITY_NO_FACE,
    QUALITY_MULTIPLE_FACES,
    validate_file,
    check_brightness,
    check_blur,
    quality_message,
)

# Status khusus person image VTON
QUALITY_FACE_ONLY = "FACE_ONLY"
QUALITY_BODY_NOT_VISIBLE = "BODY_NOT_VISIBLE"

VTON_QUALITY_MESSAGES = {
    QUALITY_FACE_ONLY: (
        "Foto hanya memperlihatkan wajah. Mundurlah dari kamera agar wajah, bahu, "
        "dan pakaian bagian atas terlihat jelas."
    ),
    QUALITY_BODY_NOT_VISIBLE: (
        "Area tubuh/pakaian tidak terlihat cukup. Pastikan bahu hingga pinggang "
        "masuk ke dalam foto dan tubuh tidak terpotong."
    ),
}


def person_quality_message(status: str) -> str:
    return VTON_QUALITY_MESSAGES.get(status, quality_message(status))


MASK_SUCCESS = "SUCCESS"
MASK_FAILED = "FAILED"


def validate_person_image(content: bytes, filename: Optional[str]) -> dict:
    """Validasi foto upper-body. Mengembalikan status + metadata + image RGB."""
    failure = {
        "ok": False,
        "image": None,
        "width": None,
        "height": None,
        "face_detected": False,
        "body_detected": False,
        "face_bbox": None,
    }

    decoded = validate_file(content, filename)
    if decoded["status"] != QUALITY_OK:
        return {**failure, "status": decoded["status"], "message": person_quality_message(decoded["status"])}

    image = decoded["image"]
    img_h, img_w = image.shape[:2]
    base = {**failure, "image": image, "width": img_w, "height": img_h}

    for check in (check_brightness, check_blur):
        status = check(image)
        if status != QUALITY_OK:
            return {**base, "status": status, "message": person_quality_message(status)}

    faces = face_region_service.detect_faces(image)
    if not faces:
        return {**base, "status": QUALITY_NO_FACE, "message": person_quality_message(QUALITY_NO_FACE)}

    largest_area = max(w * h for (_, _, w, h) in faces)
    dominant = [f for f in faces if (f[2] * f[3]) >= 0.4 * largest_area]
    if len(dominant) > 1:
        return {
            **base,
            "face_detected": True,
            "status": QUALITY_MULTIPLE_FACES,
            "message": person_quality_message(QUALITY_MULTIPLE_FACES),
        }

    face = max(dominant, key=lambda f: f[2] * f[3])
    fx, fy, fw, fh = face

    # BR-VTO-01: tolak foto yang hanya berisi wajah
    if fh / img_h > settings.VTON_MAX_FACE_HEIGHT_RATIO:
        return {
            **base,
            "face_detected": True,
            "face_bbox": face,
            "status": QUALITY_FACE_ONLY,
            "message": person_quality_message(QUALITY_FACE_ONLY),
        }

    # Area di bawah dagu harus cukup untuk torso/pakaian yang akan diganti
    below_face = img_h - (fy + fh)
    face_center_frac = (fy + fh / 2) / img_h
    if below_face < settings.VTON_MIN_BELOW_FACE_RATIO * fh or face_center_frac > 0.55:
        return {
            **base,
            "face_detected": True,
            "face_bbox": face,
            "status": QUALITY_BODY_NOT_VISIBLE,
            "message": person_quality_message(QUALITY_BODY_NOT_VISIBLE),
        }

    return {
        **base,
        "ok": True,
        "face_detected": True,
        "body_detected": True,
        "face_bbox": face,
        "status": QUALITY_OK,
        "message": "Foto valid untuk realistic try-on.",
    }


def generate_clothing_mask(image_rgb: np.ndarray, face_bbox: tuple) -> Optional[bytes]:
    """Mask area pakaian upper-body (putih = diganti), wajah/rambut dipertahankan.

    Heuristik geometris dari bbox wajah: bahu mulai sedikit di bawah dagu,
    melebar ke torso hingga area pinggang/tepi bawah foto (FR-VTO-07).
    """
    try:
        img_h, img_w = image_rgb.shape[:2]
        fx, fy, fw, fh = face_bbox
        cx = fx + fw / 2

        neck_y = min(img_h - 1, int(fy + fh * 1.05))
        shoulder_y = min(img_h - 1, int(fy + fh * 1.35))
        waist_y = min(img_h - 1, int(fy + fh * 4.2))

        neck_half = fw * 0.42
        shoulder_half = fw * 1.45
        waist_half = fw * 1.55

        def x(v: float) -> int:
            return int(np.clip(v, 0, img_w - 1))

        points = np.array([
            [x(cx - neck_half), neck_y],
            [x(cx + neck_half), neck_y],
            [x(cx + shoulder_half), shoulder_y],
            [x(cx + waist_half), waist_y],
            [x(cx - waist_half), waist_y],
            [x(cx - shoulder_half), shoulder_y],
        ], dtype=np.int32)

        mask = np.zeros((img_h, img_w), dtype=np.uint8)
        cv2.fillPoly(mask, [points], 255)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        if not mask.any():
            return None
        buf = io.BytesIO()
        Image.fromarray(mask).save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None
