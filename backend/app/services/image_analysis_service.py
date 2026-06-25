"""Orkestrasi analisis image: validasi, deteksi wajah, estimasi skin tone & undertone.

Pipeline 7 langkah berurutan:
  1. validate_file     — format (JPEG/PNG), ukuran (≤5 MB), resolusi (≥200 px)
  2. check_brightness  — rata-rata grayscale 50–215 (hindari terlalu gelap/terang)
  3. check_blur        — variance-of-Laplacian ≥ 45 (foto harus cukup tajam)
  4. evaluate_faces    — Haar Cascade; tepat 1 wajah dominan, ukuran cukup besar
  5. sample_skin_color — 4-patch + YCrCb mask → median RGB kulit representatif
  6. estimate_skin_tone — ITA (Chardon 1991 / Del Bino 2013) → kode I–VI (Nasr 2018)
  7. estimate_undertone — sudut hue CIELAB (Nasr 2018) → COOL/NEUTRAL/WARM

Output skin_tone_value dan undertone_value identik format-nya dengan input manual,
sehingga FIS Layer 1/2 dan ROC tidak perlu mengetahui asal inputnya (PRD 15.3).
Foto asli tidak pernah disimpan (NFR-IMG-02); hanya data turunan yang dipersistensikan.
"""
import colorsys
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.models.session import Session
from app.models.image_analysis_session import ImageAnalysisSession
from app.services import face_region_service
from app.services.image_quality_service import (
    QUALITY_OK,
    validate_file,
    check_brightness,
    check_blur,
    quality_message,
)
from app.services.skin_tone_detection_service import estimate_skin_tone
from app.services.undertone_detection_service import estimate_undertone
from app.services.face_crop_service import build_face_asset


def _rgb_to_hsv_string(rgb: tuple[int, int, int]) -> str:
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    return f"{round(h * 360)},{round(s * 100)},{round(v * 100)}"


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


class ImageAnalysisService:
    def __init__(self, db: DBSession):
        self.db = db

    def analyze_and_store(
        self,
        session: Session,
        content: bytes,
        filename: Optional[str],
        source_type: str,
    ) -> dict:
        """Jalankan pipeline analisis lalu simpan data turunan (bukan foto) ke DB."""
        source_type = source_type if source_type in {"CAMERA", "UPLOAD"} else "UPLOAD"
        result = self._analyze(content, filename)

        record = ImageAnalysisSession(
            session_id=session.id,
            image_source_type=source_type,
            face_detected=result["face_detected"],
            face_count=result["face_count"],
            image_quality_status=result["quality_status"],
        )
        if result["ok"]:
            skin = result["skin_tone"]
            undertone = result["undertone"]
            record.skin_tone_detected = skin["code"]
            record.skin_tone_value = skin["value"]
            record.undertone_detected = undertone["code"]
            record.undertone_value = undertone["value"]
            record.skin_tone_confidence = skin["confidence"]
            record.undertone_confidence = undertone["confidence"]
            record.sample_rgb = ",".join(str(v) for v in result["sample_rgb_tuple"])
            record.sample_hsv = result["sample_hsv"]

        self.db.add(record)
        self.db.flush()

        result["analysis_id"] = record.id
        return result

    def _analyze(self, content: bytes, filename: Optional[str]) -> dict:
        failure_base = {
            "ok": False,
            "face_detected": False,
            "face_count": 0,
            "face_bbox": None,
            "image_size": None,
            "skin_tone": None,
            "undertone": None,
            "sample_rgb_tuple": None,
            "sample_hex": None,
            "sample_hsv": None,
            "low_confidence": False,
        }

        decoded = validate_file(content, filename)
        if decoded["status"] != QUALITY_OK:
            return {
                **failure_base,
                "quality_status": decoded["status"],
                "quality_message": quality_message(decoded["status"]),
            }

        image = decoded["image"]
        img_h, img_w = image.shape[:2]
        failure_base["image_size"] = {"width": img_w, "height": img_h}

        brightness_status = check_brightness(image)
        if brightness_status != QUALITY_OK:
            return {
                **failure_base,
                "quality_status": brightness_status,
                "quality_message": quality_message(brightness_status),
            }

        blur_status = check_blur(image)
        if blur_status != QUALITY_OK:
            return {
                **failure_base,
                "quality_status": blur_status,
                "quality_message": quality_message(blur_status),
            }

        faces = face_region_service.evaluate_faces(image)
        face_bbox = faces["face_bbox"]
        bbox_payload = None
        if face_bbox is not None:
            x, y, w, h = face_bbox
            bbox_payload = {"x": x, "y": y, "width": w, "height": h}
        if faces["status"] != QUALITY_OK:
            return {
                **failure_base,
                "face_detected": faces["face_count"] > 0,
                "face_count": faces["face_count"],
                "face_bbox": bbox_payload,
                "quality_status": faces["status"],
                "quality_message": quality_message(faces["status"]),
            }

        sample = face_region_service.sample_skin_color(image, face_bbox)
        if sample["status"] != QUALITY_OK:
            return {
                **failure_base,
                "face_detected": True,
                "face_count": faces["face_count"],
                "face_bbox": bbox_payload,
                "quality_status": sample["status"],
                "quality_message": quality_message(sample["status"]),
            }

        rgb = sample["rgb"]
        skin_tone = estimate_skin_tone(rgb)
        undertone = estimate_undertone(rgb)
        low_confidence = (
            skin_tone["confidence"] < settings.IMAGE_CONFIDENCE_THRESHOLD
            or undertone["confidence"] < settings.IMAGE_CONFIDENCE_THRESHOLD
        )

        # Aset kepala transparan untuk try-on; hanya hidup di respons sesi
        try:
            face_asset = build_face_asset(image, face_bbox)
        except Exception:
            face_asset = None

        return {
            "face_asset": face_asset,
            "ok": True,
            "quality_status": QUALITY_OK,
            "quality_message": quality_message(QUALITY_OK),
            "face_detected": True,
            "face_count": faces["face_count"],
            "face_bbox": bbox_payload,
            "image_size": {"width": img_w, "height": img_h},
            "skin_tone": skin_tone,
            "undertone": undertone,
            "sample_rgb_tuple": rgb,
            "sample_hex": _rgb_to_hex(rgb),
            "sample_hsv": _rgb_to_hsv_string(rgb),
            "low_confidence": low_confidence,
        }

    def get_latest_analysis(self, session: Session) -> Optional[ImageAnalysisSession]:
        return (
            self.db.query(ImageAnalysisSession)
            .filter(ImageAnalysisSession.session_id == session.id)
            .order_by(ImageAnalysisSession.id.desc())
            .first()
        )

    def mark_confirmed(self, analysis: ImageAnalysisSession) -> None:
        analysis.is_confirmed_by_user = True
        self.db.flush()
