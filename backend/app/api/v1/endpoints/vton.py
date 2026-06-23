"""Realistic Virtual Try-On endpoints (PRD Revisi IDM-VTON bagian 13).

Lapisan visualisasi setelah rekomendasi: eligibility → consent + foto upper-body
→ job asinkron IDM-VTON (default; CatVTON fallback) → polling status → hasil
side-by-side + feedback. Kegagalan di lapisan ini tidak pernah mengubah hasil
rekomendasi FIS/ROC (BR-VTO-11).
"""
import io
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session as DBSession

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.core.exceptions import SeeraError, InvalidConversationStateError
from app.models.product import Product
from app.models.recommendation_item import RecommendationItem
from app.models.vton_person_image import VtonPersonImage
from app.models.vton_job import VtonJob, JOB_QUEUED
from app.models.vton_feedback import VtonFeedback
from app.schemas.conversation import VtonJobRequest, VtonFeedbackRequest
from app.services.conversation_service import ConversationService
from app.services.recommendation_service import RecommendationService
from app.services.vton_eligibility_service import VTONEligibilityService
from app.services.background_service import BackgroundService
from app.services.garment_caption_service import build_garment_caption
from app.services import person_image_service
from app.services import temporary_image_storage as storage
from app.services import vton_job_service

router = APIRouter(tags=["vton"])


class VtonError(SeeraError):
    code = "VTON_ERROR"


class VtonNotFoundError(SeeraError):
    code = "VTON_NOT_FOUND"

    def __init__(self, message: str = "Data VTON tidak ditemukan."):
        super().__init__(message, status_code=404)


CONSENT_MESSAGE = (
    "Foto Anda hanya diproses untuk membuat preview realistic try-on pada sesi ini, "
    "tidak dipakai untuk mengenali identitas (face recognition), tidak dipakai untuk "
    "melatih model, dan dihapus otomatis setelah masa sesi berakhir."
)

DISCLAIMER = (
    "Hasil try-on adalah preview visual, bukan jaminan ukuran, fitting, "
    "atau kenyamanan pakaian."
)


# ---- API-VTO-01: eligibility ----

@router.get("/products/{product_id}/vton-eligibility")
def vton_eligibility(product_id: int, variant_id: int = None, db: DBSession = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise VtonNotFoundError("Produk tidak ditemukan.")
    result = VTONEligibilityService(db).check(product)
    if variant_id is not None:
        result["variant_id"] = variant_id
    return result


# ---- API-VTO-02: upload person image ----

@router.post("/conversations/{session_id}/vton/person-image")
async def upload_person_image(
    session_id: int,
    image_file: UploadFile = File(...),
    source_type: str = Form("UPLOAD"),
    consent_confirmed: bool = Form(False),
    db: DBSession = Depends(get_db),
):
    conv = ConversationService(db)
    session = conv.get_active_session(session_id)

    # FR-VTO-05: consent wajib sebelum pemrosesan foto
    if not consent_confirmed:
        raise VtonError(
            "Persetujuan pemrosesan foto diperlukan sebelum melanjutkan. " + CONSENT_MESSAGE
        )

    content = await image_file.read()
    result = person_image_service.validate_person_image(content, image_file.filename)

    source = source_type.strip().upper()
    source = source if source in {"CAMERA", "UPLOAD"} else "UPLOAD"

    if not result["ok"]:
        conv.log_message(session, f"[Foto upper-body ditolak: {result['status']}]", "BUYER")
        db.commit()
        return {
            "session_id": session.id,
            "person_image_id": None,
            "quality_status": result["status"],
            "face_detected": result["face_detected"],
            "body_detected": result["body_detected"],
            "message": result["message"],
        }

    token = storage.save(content, suffix=".png")
    mask_bytes = person_image_service.generate_clothing_mask(result["image"], result["face_bbox"])
    mask_token = storage.save(mask_bytes, suffix=".png") if mask_bytes else None

    person = VtonPersonImage(
        session_id=session.id,
        storage_token=token,
        image_source_type=source,
        image_width=result["width"],
        image_height=result["height"],
        quality_status=result["status"],
        face_detected=True,
        body_detected=True,
        mask_status=person_image_service.MASK_SUCCESS if mask_token else person_image_service.MASK_FAILED,
        mask_token=mask_token,
        consent_confirmed=True,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.VTON_IMAGE_TTL_MINUTES),
    )
    db.add(person)
    conv.log_message(session, "[Foto upper-body diterima untuk realistic try-on]", "BUYER")
    db.commit()

    return {
        "session_id": session.id,
        "person_image_id": person.id,
        "quality_status": person.quality_status,
        "face_detected": True,
        "body_detected": True,
        "mask_status": person.mask_status,
        "message": "Foto valid. Silakan pilih produk untuk memulai realistic try-on.",
    }


# ---- API-VTO-03: create job ----

@router.post("/conversations/{session_id}/vton/jobs")
def create_vton_job(session_id: int, payload: VtonJobRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    session = conv.get_active_session(session_id)

    person = db.get(VtonPersonImage, payload.person_image_id)
    if not person or person.session_id != session.id:
        raise VtonNotFoundError("Foto pengguna tidak ditemukan pada sesi ini.")
    if not person.consent_confirmed or not person.body_detected:
        raise VtonError("Foto pengguna belum valid untuk try-on. Silakan unggah ulang.")

    # BR-VTO-02: produk harus berasal dari hasil rekomendasi sesi ini
    rec_service = RecommendationService(db)
    recommendation = rec_service.get_latest_recommendation(session)
    item = (
        db.query(RecommendationItem)
        .filter(
            RecommendationItem.recommendation_id == recommendation.id,
            RecommendationItem.product_id == payload.product_id,
        )
        .first()
    )
    if not item:
        raise InvalidConversationStateError(
            "Produk tidak termasuk dalam hasil rekomendasi sesi ini."
        )

    # FR-VTO-15/17: tier gating sebelum inference.
    product = item.product
    eligibility = VTONEligibilityService(db).check(product)
    tier = eligibility["vton_asset_tier"]
    quality_mode = eligibility["tryon_quality_mode"]

    # BR-VTO-25: aset tidak didukung tidak boleh dikirim ke model.
    if not eligibility["vton_supported"]:
        raise VtonError(
            eligibility["reason_if_not_supported"]
            or "Virtual try-on belum tersedia untuk produk ini."
        )

    # FR-VTO-16: tier experimental/limited butuh konfirmasi pengguna eksplisit.
    if eligibility["requires_user_confirmation_for_experimental_mode"] and not payload.confirm_experimental:
        raise VtonError(
            eligibility["quality_warning_message"]
            or "Diperlukan konfirmasi untuk menjalankan preview eksperimental.",
        )

    background = None
    if payload.background_id is not None:
        background = BackgroundService(db).get_active(payload.background_id)

    # NFR-VTO-07: batasi jumlah job per sesi
    job_count = db.query(VtonJob).filter(VtonJob.session_id == session.id).count()
    if job_count >= settings.VTON_MAX_JOBS_PER_SESSION:
        raise VtonError(
            f"Batas {settings.VTON_MAX_JOBS_PER_SESSION} try-on per sesi tercapai. "
            "Silakan mulai sesi baru untuk mencoba lagi."
        )

    # BR-VTO-16: petakan ke varian warna yang tepat. Bila pengguna memilih
    # variant_id, validasi bahwa itu warna milik produk; jika tidak, pakai dominan.
    colors_sorted = sorted(product.product_colors, key=lambda c: c.color_rank)
    selected_pc = None
    if payload.variant_id is not None:
        selected_pc = next((pc for pc in colors_sorted if pc.color_id == payload.variant_id), None)
        if selected_pc is None:
            raise VtonError("Varian warna yang dipilih tidak tersedia pada produk ini.")
    if selected_pc is None:
        selected_pc = next((pc for pc in colors_sorted if pc.color_role == "DOMINANT"), None)
    if selected_pc is None and colors_sorted:
        selected_pc = colors_sorted[0]
    selected_color_name = (
        selected_pc.color.color_name if (selected_pc and selected_pc.color) else None
    )

    # Garment fidelity: caption (override aset bila ada) dicatat per job (BR-VTO-13/15).
    asset = product.vton_asset
    caption = (asset.garment_caption if asset and asset.garment_caption else None) or build_garment_caption(product)

    job = VtonJob(
        session_id=session.id,
        user_id=session.user_id,
        product_id=product.id,
        person_image_id=person.id,
        background_id=background.id if background else None,
        garment_vton_image_url=eligibility["garment_vton_image_url"],
        garment_vton_asset_id=asset.id if asset else None,
        selected_variant_id=selected_pc.color_id if selected_pc else None,
        garment_caption=caption,
        vton_asset_tier=tier,
        tryon_quality_mode=quality_mode,
        mask_token=person.mask_token,
        model_name=settings.VTON_MODEL_NAME,
        model_version=settings.VTON_MODEL_VERSION,
        inference_resolution=settings.VTON_INFERENCE_RESOLUTION,
        status=JOB_QUEUED,
    )
    db.add(job)
    db.flush()  # dapatkan job.id untuk logging

    # FR-VTO-09 / item PRD #7: log lengkap request try-on (ketelusuran aset).
    logger.info(
        "VTON request job=%s product=%s variant=%s color=%s tier=%s quality_mode=%s "
        "product_image=%s garment_vton_image=%s category=%s caption=%r provider=%s "
        "model=%s repo=%s space=%s mode=%s",
        job.id, product.id, job.selected_variant_id, selected_color_name, tier, quality_mode,
        product.image_url, job.garment_vton_image_url,
        asset.garment_category if asset else None, caption,
        settings.VTON_MODEL_PROVIDER, settings.VTON_MODEL_NAME, settings.VTON_MODEL_REPO,
        settings.VTON_SPACE_ID, settings.VTON_INFERENCE_MODE,
    )
    conv.log_message(
        session,
        f"Realistic try-on ({quality_mode}) dimulai untuk produk #{product.id} varian {selected_color_name}",
        "BUYER",
    )
    db.commit()

    vton_job_service.enqueue(job.id)

    return {
        "vton_job_id": job.id,
        "status": job.status,
        "product_id": product.id,
        "selected_variant_id": job.selected_variant_id,
        "selected_color": selected_color_name,
        "vton_asset_tier": tier,
        "tryon_quality_mode": quality_mode,
        "garment_caption": caption,
        "quality_warning_message": eligibility["quality_warning_message"],
        "estimated_message": "Sedang membuat realistic try-on preview. Proses ini dapat memakan waktu hingga beberapa menit.",
        "disclaimer": DISCLAIMER,
    }


# ---- API-VTO-04: job status ----

@router.get("/vton/jobs/{vton_job_id}")
def get_vton_job(vton_job_id: int, db: DBSession = Depends(get_db)):
    job = db.get(VtonJob, vton_job_id)
    if not job:
        raise VtonNotFoundError("VTON job tidak ditemukan.")

    vton_job_service.refresh_expiry(db, job)

    variant_color = None
    if job.selected_variant_id:
        from app.models.color import Color
        color = db.get(Color, job.selected_variant_id)
        variant_color = color.color_name if color else None

    tier = job.vton_asset_tier
    quality_mode = job.tryon_quality_mode
    experimental_label = None
    if quality_mode == "experimental":
        experimental_label = "Preview Eksperimental"
    elif quality_mode == "limited":
        experimental_label = "Kualitas Aset Terbatas"

    return {
        "vton_job_id": job.id,
        "status": job.status,
        "product_id": job.product_id,
        "product_name": job.product.name if job.product else None,
        "selected_variant_id": job.selected_variant_id,
        "selected_color": variant_color,
        # Side-by-side (BR-VTO-17/26): produk asli + garment image + hasil
        "product_image_url": job.product.image_url if job.product else None,
        "garment_vton_image_url": job.garment_vton_image_url,
        "garment_caption": job.garment_caption,
        "vton_asset_tier": tier,
        "tryon_quality_mode": quality_mode,
        "experimental_label": experimental_label,
        "model_provider": settings.VTON_MODEL_PROVIDER,
        "model_name": job.model_name,
        "model_version": job.model_version,
        "model_repo": settings.VTON_MODEL_REPO,
        "inference_parameters": job.inference_parameters,
        "background_id": job.background_id,
        "output_image_url": (
            f"/api/v1/vton/images/{job.output_token}" if job.output_token else None
        ),
        "error_message": job.error_message,
        "result_warning": (
            "Hasil virtual try-on adalah visualisasi AI dan dapat berbeda dari produk asli."
        ),
        "disclaimer": DISCLAIMER,
    }


# ---- API-VTO-05: feedback ----

@router.post("/vton/jobs/{vton_job_id}/feedback")
def submit_vton_feedback(
    vton_job_id: int, payload: VtonFeedbackRequest, db: DBSession = Depends(get_db)
):
    job = db.get(VtonJob, vton_job_id)
    if not job:
        raise VtonNotFoundError("VTON job tidak ditemukan.")
    if job.feedback:
        raise VtonError("Feedback untuk try-on ini sudah pernah dikirim.")

    feedback = VtonFeedback(
        vton_job_id=job.id,
        visual_quality_rating=payload.visual_quality_rating,
        proportion_rating=payload.proportion_rating,
        garment_similarity_rating=payload.garment_similarity_rating,
        satisfaction_rating=payload.satisfaction_rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    return {"feedback_id": feedback.id, "message": "Terima kasih atas umpan balik Anda!"}


# ---- Penyaji image sementara & aset garment ----

@router.get("/vton/images/{token}")
def get_vton_image(token: str):
    content = storage.load(token)
    if content is None:
        raise VtonNotFoundError("Image tidak ditemukan atau sudah kedaluwarsa.")
    return Response(content=content, media_type="image/png")


@router.get("/vton/garments/{filename}")
def get_vton_garment(filename: str):
    path = vton_job_service.garment_file_path(filename)
    if not path:
        raise VtonNotFoundError("Aset garment tidak ditemukan.")
    return FileResponse(path, media_type="image/png")
