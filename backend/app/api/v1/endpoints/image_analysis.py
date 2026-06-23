"""Image-based skin tone & undertone detection endpoints (PRD Image-Based Chatbot).

Alur: pilih metode input -> capture/upload foto -> analisis -> konfirmasi hasil ->
masuk pipeline rekomendasi existing (FIS Layer 1/2 + ROC) -> visual matching.
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.exceptions import (
    InvalidInputMethodError,
    InvalidSkinToneError,
    InvalidUndertoneError,
    ImageAnalysisNotFoundError,
)
from app.schemas.conversation import (
    InputMethodRequest,
    ImageAnalysisConfirmRequest,
    VisualMatchRequest,
)
from app.services.conversation_service import (
    ConversationService,
    STATE_WAITING_SKIN_TONE,
    STATE_WAITING_CONFIRMATION,
    STATE_WAITING_INPUT_METHOD,
    STATE_WAITING_IMAGE_CAPTURE,
    STATE_PROCESSING_IMAGE_ANALYSIS,
    STATE_WAITING_IMAGE_RESULT_CONFIRMATION,
    STATE_SHOWING_RECOMMENDATION,
    STATE_SHOWING_VISUAL_RECOMMENDATION,
)
from app.services.aiml_interpreter import AIMLInterpreter
from app.services.image_analysis_service import ImageAnalysisService
from app.services.input_validation_service import (
    normalize_skin_tone,
    normalize_undertone,
    skin_tone_payload,
    undertone_payload,
)
from app.services.recommendation_service import RecommendationService
from app.services.visual_match_service import VisualMatchService

router = APIRouter(prefix="/conversations", tags=["image-analysis"])


CAMERA_INSTRUCTION = (
    "Posisikan wajah di dalam garis panduan, pastikan pencahayaan cukup, "
    "tanpa filter kamera, dan hindari makeup tebal agar hasil deteksi akurat."
)

INPUT_METHOD_IMAGE = "IMAGE"
INPUT_METHOD_MANUAL = "MANUAL"

_METHOD_ALIASES = {
    "IMAGE": INPUT_METHOD_IMAGE,
    "FOTO": INPUT_METHOD_IMAGE,
    "FOTO WAJAH": INPUT_METHOD_IMAGE,
    "KAMERA": INPUT_METHOD_IMAGE,
    "CAMERA": INPUT_METHOD_IMAGE,
    "INPUT_METHOD_IMAGE": INPUT_METHOD_IMAGE,
    "MANUAL": INPUT_METHOD_MANUAL,
    "TEKS": INPUT_METHOD_MANUAL,
    "TEXT": INPUT_METHOD_MANUAL,
    "INPUT_METHOD_MANUAL": INPUT_METHOD_MANUAL,
}


def normalize_input_method(raw: str) -> Optional[str]:
    cleaned = " ".join(str(raw).strip().upper().replace("-", " ").split())
    return _METHOD_ALIASES.get(cleaned)


def _enter_image_mode(session, conv: ConversationService, aiml: AIMLInterpreter, db: DBSession) -> dict:
    conv.set_state(session, STATE_WAITING_IMAGE_CAPTURE)
    response = aiml.respond("IMAGE_MODE_INSTRUCTIONS")
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "camera_instruction": CAMERA_INSTRUCTION,
        "quick_replies": response["quick_replies"],
    }


def _enter_manual_mode(session, conv: ConversationService, aiml: AIMLInterpreter, db: DBSession) -> dict:
    conv.set_state(session, STATE_WAITING_SKIN_TONE)
    response = aiml.respond("WELCOME_AND_SKINTONE_LIST")
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


@router.post("/{session_id}/input-method")
def choose_input_method(session_id: int, payload: InputMethodRequest, db: DBSession = Depends(get_db)):
    """FR-IMG-01: pengguna memilih metode input foto wajah atau manual."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(
        session,
        STATE_WAITING_INPUT_METHOD,
        STATE_WAITING_IMAGE_CAPTURE,
        STATE_WAITING_IMAGE_RESULT_CONFIRMATION,
        STATE_WAITING_SKIN_TONE,
    )

    method = normalize_input_method(payload.method)
    if method is None:
        response = aiml.respond("INPUT_METHOD_OPTIONS")
        conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
        db.commit()
        raise InvalidInputMethodError("Metode input tidak dikenal. Pilih foto wajah atau manual.")

    conv.log_message(session, "Gunakan foto wajah" if method == INPUT_METHOD_IMAGE else "Pilih manual", "BUYER")

    if method == INPUT_METHOD_IMAGE:
        return _enter_image_mode(session, conv, aiml, db)
    return _enter_manual_mode(session, conv, aiml, db)


@router.post("/{session_id}/image-mode")
def start_image_mode(session_id: int, db: DBSession = Depends(get_db)):
    """API-IMG-01: ubah state percakapan ke mode input image."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(
        session,
        STATE_WAITING_INPUT_METHOD,
        STATE_WAITING_IMAGE_CAPTURE,
        STATE_WAITING_IMAGE_RESULT_CONFIRMATION,
        STATE_WAITING_SKIN_TONE,
    )
    conv.log_message(session, "Gunakan foto wajah", "BUYER")
    return _enter_image_mode(session, conv, aiml, db)


@router.post("/{session_id}/image-analysis")
async def analyze_image(
    session_id: int,
    image_file: UploadFile = File(...),
    source_type: str = Form("UPLOAD"),
    db: DBSession = Depends(get_db),
):
    """API-IMG-02: terima image, validasi, deteksi skin tone & undertone."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(
        session,
        STATE_WAITING_IMAGE_CAPTURE,
        STATE_WAITING_IMAGE_RESULT_CONFIRMATION,
    )

    conv.set_state(session, STATE_PROCESSING_IMAGE_ANALYSIS)
    conv.log_message(
        session,
        f"[Image dikirim untuk analisis - {source_type.lower()}]",
        "BUYER",
    )

    content = await image_file.read()
    service = ImageAnalysisService(db)
    result = service.analyze_and_store(
        session,
        content,
        image_file.filename,
        source_type.strip().upper(),
    )

    if not result["ok"]:
        # FR-IMG-15: gagal diproses -> kembali ke mode capture + tawarkan fallback.
        conv.set_state(session, STATE_WAITING_IMAGE_CAPTURE)
        response = aiml.respond(
            "IMAGE_ANALYSIS_FAILED",
            context={"reason": result["quality_message"]},
        )
        conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
        db.commit()
        return {
            "session_id": session.id,
            "session_status": session.session_status,
            "conversation_state": session.conversation_state,
            "image_quality_status": result["quality_status"],
            "face_detected": result["face_detected"],
            "face_count": result["face_count"],
            "skin_tone": None,
            "undertone": None,
            "requires_confirmation": False,
            "message": response["message"],
            "quick_replies": response["quick_replies"],
        }

    skin = result["skin_tone"]
    undertone = result["undertone"]
    conv.set_state(session, STATE_WAITING_IMAGE_RESULT_CONFIRMATION)

    pattern = "IMAGE_ANALYSIS_LOW_CONFIDENCE" if result["low_confidence"] else "IMAGE_ANALYSIS_RESULT"
    response = aiml.respond(
        pattern,
        context={
            "skin_tone_name": skin["name"],
            "skin_tone_code": skin["code"],
            "undertone_name": undertone["name"],
            "skin_confidence_pct": str(round(skin["confidence"] * 100)),
            "undertone_confidence_pct": str(round(undertone["confidence"] * 100)),
        },
    )
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "analysis_id": result["analysis_id"],
        "image_quality_status": result["quality_status"],
        "face_detected": True,
        "face_count": result["face_count"],
        "face_bbox": result["face_bbox"],
        "image_size": result["image_size"],
        "skin_tone": {
            "code": skin["code"],
            "name": skin["name"],
            "value": skin["value"],
            "confidence": skin["confidence"],
        },
        "undertone": {
            "code": undertone["code"],
            "name": undertone["name"],
            "value": undertone["value"],
            "confidence": undertone["confidence"],
        },
        "sample_hex": result["sample_hex"],
        "low_confidence": result["low_confidence"],
        "face_crop": result.get("face_asset"),
        "requires_confirmation": True,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


@router.post("/{session_id}/image-analysis/confirm")
def confirm_image_analysis(
    session_id: int,
    payload: ImageAnalysisConfirmRequest,
    db: DBSession = Depends(get_db),
):
    """API-IMG-03: konfirmasi hasil deteksi atau terima koreksi manual (BR-IMG-02)."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_WAITING_IMAGE_RESULT_CONFIRMATION)

    service = ImageAnalysisService(db)
    analysis = service.get_latest_analysis(session)
    if not analysis or analysis.skin_tone_detected is None:
        raise ImageAnalysisNotFoundError()

    if not payload.is_confirmed:
        conv.log_message(session, "Ambil ulang foto", "BUYER")
        return _enter_image_mode(session, conv, aiml, db)

    skin_code = analysis.skin_tone_detected
    undertone_code = analysis.undertone_detected
    if payload.corrected_skin_tone:
        skin_code = normalize_skin_tone(payload.corrected_skin_tone)
        if skin_code is None:
            raise InvalidSkinToneError("Koreksi skin tone tidak valid. Pilih Tipe I sampai VI.")
    if payload.corrected_undertone:
        undertone_code = normalize_undertone(payload.corrected_undertone)
        if undertone_code is None:
            raise InvalidUndertoneError("Koreksi undertone tidak valid. Pilih Cool, Neutral, atau Warm.")

    conv.log_message(
        session,
        f"Konfirmasi hasil deteksi (skin tone {skin_code}, undertone {undertone_code})",
        "BUYER",
    )

    skin_data = skin_tone_payload(skin_code)
    undertone_data = undertone_payload(undertone_code)

    # Hasil deteksi diperlakukan sama seperti input manual (prinsip PRD 15.3).
    sc = conv.get_or_create_skin_characteristic(session)
    sc.skintone = skin_data["value"]
    sc.skintone_name = skin_data["name"]
    sc.undertone = undertone_data["value"]
    sc.undertone_name = undertone_data["name"]
    session.skintone_snapshot = skin_data["value"]
    session.undertone_snapshot = undertone_code

    service.mark_confirmed(analysis)
    conv.set_state(session, STATE_WAITING_CONFIRMATION)

    summary = _image_summary_payload(session)
    response = aiml.respond("SUMMARY_AND_CONFIRMATION", context=summary)
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "skin_tone_final": {"code": skin_code, "name": skin_data["name"], "value": skin_data["value"]},
        "undertone_final": {"code": undertone_code, "name": undertone_data["name"], "value": undertone_data["value"]},
        "message": response["message"],
        "quick_replies": response["quick_replies"],
        "summary": summary,
    }


@router.post("/{session_id}/visual-match")
def create_visual_match(session_id: int, payload: VisualMatchRequest, db: DBSession = Depends(get_db)):
    """API-IMG-06: simpan konfigurasi preview produk + background pilihan pengguna."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_SHOWING_RECOMMENDATION, STATE_SHOWING_VISUAL_RECOMMENDATION)

    rec_service = RecommendationService(db)
    recommendation = rec_service.get_latest_recommendation(session)

    vm_service = VisualMatchService(db)
    preview = vm_service.create_preview(
        session,
        recommendation,
        payload.product_id,
        payload.background_id,
    )

    conv.set_state(session, STATE_SHOWING_VISUAL_RECOMMENDATION)
    conv.log_message(
        session,
        f"Visual match: produk #{payload.product_id}, background #{payload.background_id}",
        "BUYER",
    )
    response = aiml.respond("VISUAL_MATCH_READY")
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "recommendation_id": recommendation.id,
        "selected_product": preview["selected_product"],
        "selected_background": preview["selected_background"],
        "preview_config": preview["preview_config"],
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


def _image_summary_payload(session) -> dict:
    from app.api.v1.endpoints.conversations import _summary_payload

    return _summary_payload(session)
