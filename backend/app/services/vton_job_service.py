"""VTON job queue & lifecycle (FR-VTO-09/10, NFR-VTO-04/07).

Job berjalan asinkron pada worker thread in-process agar chatbot tidak terblokir;
status dicatat di tabel vton_jobs (QUEUED → PROCESSING → SUCCESS/FAILED/EXPIRED).
Kegagalan job tidak pernah mengubah hasil rekomendasi (BR-VTO-11).
"""
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from app.models.vton_job import (
    VtonJob,
    JOB_QUEUED,
    JOB_PROCESSING,
    JOB_SUCCESS,
    JOB_FAILED,
    JOB_EXPIRED,
)
from app.services import temporary_image_storage as storage
from app.services import vton_debug_service as vton_debug
from app.services.vton_model_adapter import (
    get_adapter,
    get_fallback_adapter,
    VTONInferenceError,
)


GARMENT_DIR = Path(__file__).resolve().parents[2] / "static" / "vton_garments"

_job_queue: "queue.Queue[int]" = queue.Queue()
_worker_started = threading.Lock()
_worker_thread: Optional[threading.Thread] = None


def garment_file_path(garment_url: str) -> Optional[str]:
    """Resolusi URL aset garment ke file lokal backend (cegah path traversal)."""
    filename = garment_url.rstrip("/").split("/")[-1]
    safe = "".join(c for c in filename if c.isalnum() or c in "._-")
    path = GARMENT_DIR / safe
    return str(path) if path.is_file() else None


def cloth_type_for(garment_category: Optional[str]) -> str:
    return {
        "upper": "upper",
        "outer": "upper",
        "lower": "lower",
        "dress": "overall",
    }.get((garment_category or "upper").lower(), "upper")


def enqueue(job_id: int) -> None:
    """Antrikan job; pada VTON_SYNC_MODE (test) langsung diproses inline."""
    if settings.VTON_SYNC_MODE:
        _process_job(job_id)
        return
    _ensure_worker()
    _job_queue.put(job_id)


def _ensure_worker() -> None:
    global _worker_thread
    with _worker_started:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_thread = threading.Thread(target=_worker_loop, daemon=True, name="vton-worker")
            _worker_thread.start()


def _worker_loop() -> None:
    while True:
        job_id = _job_queue.get()
        try:
            _process_job(job_id)
        except Exception:  # noqa: BLE001 - worker tidak boleh mati
            logger.exception("VTON worker error pada job %s", job_id)
        finally:
            _job_queue.task_done()


def _process_job(job_id: int) -> None:
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        job = db.get(VtonJob, job_id)
        if not job or job.status not in (JOB_QUEUED, JOB_PROCESSING):
            return

        job.status = JOB_PROCESSING
        db.commit()

        person_path = storage.path(job.person_image.storage_token)
        garment_path = garment_file_path(job.garment_vton_image_url)
        mask_path = storage.path(job.mask_token) if job.mask_token else None

        if not person_path:
            _fail(db, job, "Foto pengguna sudah kedaluwarsa. Silakan unggah ulang foto.")
            return
        if not garment_path:
            _fail(db, job, "Aset garment produk tidak ditemukan atau tidak valid.")
            return

        cloth_type = cloth_type_for(
            job.product.vton_asset.garment_category if job.product.vton_asset else None
        )

        # Simpan artefak input (bukti gambar yang dikirim ke model) — PRD #12.
        vton_debug.save_inputs(
            job.id,
            person_path=person_path,
            garment_path=garment_path,
            mask_path=mask_path,
            request_metadata={
                "job_id": job.id,
                "product_id": job.product_id,
                "selected_variant_id": job.selected_variant_id,
                "garment_vton_image_url": job.garment_vton_image_url,
                "garment_caption": job.garment_caption,
                "garment_category": (
                    job.product.vton_asset.garment_category if job.product.vton_asset else None
                ),
                "cloth_type": cloth_type,
                "vton_asset_tier": job.vton_asset_tier,
                "tryon_quality_mode": job.tryon_quality_mode,
                "model_provider": settings.VTON_MODEL_PROVIDER,
                "model_name": settings.VTON_MODEL_NAME,
                "model_repo": settings.VTON_MODEL_REPO,
                "space_id": settings.VTON_SPACE_ID,
                "inference_mode": settings.VTON_INFERENCE_MODE,
            },
        )

        # Model default IDM-VTON (garment fidelity); CatVTON sebagai fallback
        # otomatis bila resource IDM-VTON gagal/timeout (BR-VTO-14).
        primary = get_adapter()
        fallback = get_fallback_adapter()
        candidates = [primary] + ([fallback] if fallback else [])

        output_bytes = None
        last_error = "Inference gagal."
        used_adapter = None
        for index, adapter in enumerate(candidates):
            job.model_name = adapter.name
            job.model_version = adapter.version
            job.inference_resolution = settings.VTON_INFERENCE_RESOLUTION
            job.inference_parameters = adapter.inference_parameters()
            db.commit()
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(
                        adapter.infer,
                        person_path,
                        garment_path,
                        cloth_type,
                        mask_path,
                        job.garment_caption,
                    )
                    output_bytes = future.result(timeout=settings.VTON_TIMEOUT_SECONDS)
                used_adapter = adapter
                break
            except FutureTimeout:
                last_error = "Proses inference melebihi batas waktu."
            except VTONInferenceError as exc:
                last_error = str(exc)
            # Coba fallback berikutnya bila tersedia
            if index < len(candidates) - 1:
                logger.warning(
                    "VTON model %s gagal (%s); mencoba fallback.", adapter.name, last_error
                )

        if output_bytes is None:
            vton_debug.save_output(
                job.id,
                output_bytes=None,
                response_metadata={"status": "FAILED", "error": last_error},
            )
            _fail(db, job, last_error)
            return

        job.output_token = storage.save(output_bytes, suffix=".png")
        job.status = JOB_SUCCESS
        job.completed_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(minutes=settings.VTON_IMAGE_TTL_MINUTES)
        db.commit()

        vton_debug.save_output(
            job.id,
            output_bytes=output_bytes,
            response_metadata={
                "status": "SUCCESS",
                "model_name": job.model_name,
                "model_version": job.model_version,
                "is_fallback": bool(used_adapter and used_adapter is not primary),
                "inference_parameters": job.inference_parameters,
                "output_bytes_size": len(output_bytes),
            },
        )
    finally:
        db.close()


def _fail(db, job: VtonJob, message: str) -> None:
    job.status = JOB_FAILED
    job.error_message = message
    job.completed_at = datetime.utcnow()
    db.commit()


def refresh_expiry(db, job: VtonJob) -> None:
    """Tandai EXPIRED bila masa berlaku output habis (status dapat dilacak)."""
    if (
        job.status == JOB_SUCCESS
        and job.expires_at is not None
        and datetime.utcnow() > job.expires_at
    ):
        job.status = JOB_EXPIRED
        if job.output_token:
            storage.delete(job.output_token)
            job.output_token = None
        db.commit()
