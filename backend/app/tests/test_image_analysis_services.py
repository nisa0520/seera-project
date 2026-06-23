"""Unit test untuk service analisis image (PRD 19.1)."""
import io

import numpy as np
import pytest
from PIL import Image

from app.services import face_region_service
from app.services.image_quality_service import (
    QUALITY_OK,
    QUALITY_INVALID_FILE,
    QUALITY_FILE_TOO_LARGE,
    QUALITY_UNSUPPORTED_FORMAT,
    QUALITY_RESOLUTION_TOO_LOW,
    QUALITY_TOO_DARK,
    QUALITY_TOO_BRIGHT,
    QUALITY_NO_FACE,
    QUALITY_MULTIPLE_FACES,
    QUALITY_FACE_TOO_SMALL,
    validate_file,
    check_brightness,
)
from app.services.skin_tone_detection_service import (
    classify_ita,
    estimate_skin_tone,
)
from app.services.undertone_detection_service import (
    classify_hue,
    estimate_undertone,
)


SKIN_RGB_LIGHT = (236, 200, 172)
SKIN_RGB_MEDIUM = (198, 144, 110)
SKIN_RGB_DARK = (87, 56, 38)


def _png_bytes(array: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(array.astype(np.uint8)).save(buf, format="PNG")
    return buf.getvalue()


def _skin_image(size: int = 480, rgb=SKIN_RGB_MEDIUM, noise: int = 12) -> np.ndarray:
    rng = np.random.default_rng(42)
    base = np.full((size, size, 3), rgb, dtype=np.int16)
    jitter = rng.integers(-noise, noise + 1, size=(size, size, 3), dtype=np.int16)
    return np.clip(base + jitter, 0, 255).astype(np.uint8)


# ---- validasi format & ukuran (19.1 no. 1-2) ----

def test_validate_file_rejects_non_image():
    result = validate_file(b"bukan gambar sama sekali", "foto.jpg")
    assert result["status"] == QUALITY_INVALID_FILE


def test_validate_file_rejects_unsupported_extension():
    result = validate_file(b"GIF89a....", "foto.gif")
    assert result["status"] == QUALITY_UNSUPPORTED_FORMAT


def test_validate_file_rejects_oversized(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "IMAGE_MAX_UPLOAD_BYTES", 10)
    result = validate_file(b"x" * 11, "foto.jpg")
    assert result["status"] == QUALITY_FILE_TOO_LARGE


def test_validate_file_rejects_low_resolution():
    tiny = _png_bytes(np.full((50, 50, 3), 180))
    result = validate_file(tiny, "foto.png")
    assert result["status"] == QUALITY_RESOLUTION_TOO_LOW


def test_validate_file_accepts_valid_png():
    content = _png_bytes(_skin_image())
    result = validate_file(content, "foto.png")
    assert result["status"] == QUALITY_OK
    assert result["image"] is not None
    assert result["image"].shape == (480, 480, 3)


# ---- validasi pencahayaan (19.1 no. 4) ----

def test_brightness_too_dark():
    dark = np.full((300, 300, 3), 20, dtype=np.uint8)
    assert check_brightness(dark) == QUALITY_TOO_DARK


def test_brightness_too_bright():
    bright = np.full((300, 300, 3), 245, dtype=np.uint8)
    assert check_brightness(bright) == QUALITY_TOO_BRIGHT


def test_brightness_normal():
    assert check_brightness(_skin_image()) == QUALITY_OK


# ---- deteksi jumlah wajah (19.1 no. 3) ----

def test_no_face_detected(monkeypatch):
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [])
    result = face_region_service.evaluate_faces(_skin_image())
    assert result["status"] == QUALITY_NO_FACE
    assert result["face_count"] == 0


def test_multiple_dominant_faces_rejected(monkeypatch):
    monkeypatch.setattr(
        face_region_service,
        "detect_faces",
        lambda img: [(40, 40, 200, 200), (250, 40, 190, 190)],
    )
    result = face_region_service.evaluate_faces(_skin_image())
    assert result["status"] == QUALITY_MULTIPLE_FACES
    assert result["face_count"] == 2


def test_face_too_small_rejected(monkeypatch):
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [(200, 200, 40, 40)])
    result = face_region_service.evaluate_faces(_skin_image())
    assert result["status"] == QUALITY_FACE_TOO_SMALL


def test_single_valid_face_accepted(monkeypatch):
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [(80, 80, 320, 320)])
    result = face_region_service.evaluate_faces(_skin_image())
    assert result["status"] == QUALITY_OK
    assert result["face_bbox"] == (80, 80, 320, 320)


# ---- sampling area kulit (FR-IMG-05) ----

def test_sample_skin_color_close_to_actual():
    image = _skin_image(rgb=SKIN_RGB_MEDIUM, noise=6)
    result = face_region_service.sample_skin_color(image, (80, 80, 320, 320))
    assert result["status"] == QUALITY_OK
    sampled = result["rgb"]
    for channel, expected in zip(sampled, SKIN_RGB_MEDIUM):
        assert abs(channel - expected) <= 10


# ---- pemetaan skin tone ke skala FIS (19.1 no. 5) ----

def test_classify_ita_boundaries():
    assert classify_ita(60.0) == "I"
    assert classify_ita(48.0) == "II"
    assert classify_ita(35.0) == "III"
    assert classify_ita(20.0) == "IV"
    assert classify_ita(-10.0) == "V"
    assert classify_ita(-40.0) == "VI"


def test_estimate_skin_tone_light_vs_dark():
    light = estimate_skin_tone(SKIN_RGB_LIGHT)
    dark = estimate_skin_tone(SKIN_RGB_DARK)
    assert light["code"] in {"I", "II", "III"}
    assert dark["code"] in {"V", "VI"}
    assert light["value"] < dark["value"]
    assert 0.0 <= light["confidence"] <= 1.0
    assert 0.0 <= dark["confidence"] <= 1.0


def test_skin_tone_value_compatible_with_fis_scale():
    result = estimate_skin_tone(SKIN_RGB_MEDIUM)
    assert result["code"] in {"I", "II", "III", "IV", "V", "VI"}
    assert result["value"] in {1.0, 2.0, 3.0, 4.0, 5.0, 6.0}


# ---- pemetaan undertone ke kategori FIS (19.1 no. 6) ----

def test_classify_hue_categories():
    assert classify_hue(40.0) == "COOL"
    assert classify_hue(52.0) == "NEUTRAL"
    assert classify_hue(65.0) == "WARM"


def test_estimate_undertone_warm_vs_cool():
    # Kulit kekuningan (warm) vs kemerahmudaan (cool)
    warm = estimate_undertone((225, 190, 140))
    cool = estimate_undertone((230, 180, 180))
    assert warm["code"] == "WARM"
    assert cool["code"] == "COOL"
    assert warm["value"] in {0.0, 1.0, 2.0}
    assert cool["value"] in {0.0, 1.0, 2.0}


def test_undertone_output_compatible_with_fis():
    result = estimate_undertone(SKIN_RGB_MEDIUM)
    assert result["code"] in {"COOL", "NEUTRAL", "WARM"}
    assert 0.0 <= result["confidence"] <= 1.0


# ---- aset kepala untuk virtual try-on (segmentasi + skala) ----

def _portrait_photo() -> np.ndarray:
    """Foto pengguna sintetis: kepala warna kulit + rambut pada latar kontras."""
    img = np.full((480, 480, 3), (130, 142, 158), dtype=np.uint8)
    yy, xx = np.mgrid[0:480, 0:480]
    hair = (((xx - 240) / 115) ** 2 + ((yy - 170) / 105) ** 2) <= 1
    img[hair] = (56, 40, 30)
    face = (((xx - 240) / 88) ** 2 + ((yy - 245) / 112) ** 2) <= 1
    img[face] = (214, 168, 136)
    return img


def test_build_face_asset_returns_scaled_transparent_head():
    from app.services.face_crop_service import build_face_asset

    asset = build_face_asset(_portrait_photo(), (150, 145, 180, 180))
    assert asset["data_url"].startswith("data:image/png;base64,")
    assert 0.5 <= asset["head_width_fraction"] <= 0.95
    assert isinstance(asset["segmented"], bool)


def test_build_face_asset_fallback_on_flat_image():
    from app.services.face_crop_service import build_face_asset

    flat = np.full((480, 480, 3), 128, dtype=np.uint8)
    asset = build_face_asset(flat, (150, 145, 180, 180))
    # Segmentasi boleh gagal, tetapi aset tetap dihasilkan (mask oval fallback)
    assert asset["data_url"].startswith("data:image/png;base64,")
    assert 0.5 <= asset["head_width_fraction"] <= 0.95
