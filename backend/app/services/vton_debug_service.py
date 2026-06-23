"""Debug artifacts VTON (PRD AssetTier bagian 12).

Saat VTON_ENABLE_DEBUG_ARTIFACTS=true, simpan bukti gambar yang benar-benar
dikirim ke model + metadata, ke backend/storage/vton_debug/{job_id}/:

- person_input.png
- garment_input.png
- mask_input.png (bila ada)
- vton_output.png
- request_metadata.json
- model_response_metadata.json

Folder ini bersifat internal/evaluasi — tidak pernah diekspos publik di produksi
(NFR-VTO-02/03). Kegagalan menulis artefak tidak boleh menggagalkan job.
"""
import json
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


def _backend_root() -> Path:
    # app/services/vton_debug_service.py -> parents[2] = backend/
    return Path(__file__).resolve().parents[2]


def enabled() -> bool:
    return bool(settings.VTON_ENABLE_DEBUG_ARTIFACTS)


def job_dir(job_id: int) -> Path:
    base = Path(settings.VTON_DEBUG_DIR)
    if not base.is_absolute():
        base = _backend_root() / base
    path = base / str(job_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _copy(src_path: Optional[str], dest: Path) -> None:
    if not src_path:
        return
    try:
        data = Path(src_path).read_bytes()
        dest.write_bytes(data)
    except OSError:
        pass


def save_inputs(
    job_id: int,
    *,
    person_path: Optional[str],
    garment_path: Optional[str],
    mask_path: Optional[str],
    request_metadata: dict,
) -> None:
    if not enabled():
        return
    try:
        d = job_dir(job_id)
        _copy(person_path, d / "person_input.png")
        _copy(garment_path, d / "garment_input.png")
        if mask_path:
            _copy(mask_path, d / "mask_input.png")
        (d / "request_metadata.json").write_text(
            json.dumps(request_metadata, indent=2, default=str), encoding="utf-8"
        )
    except Exception:  # noqa: BLE001 - artefak debug tidak boleh menggagalkan job
        logger.warning("Gagal menyimpan artefak input VTON job %s", job_id, exc_info=True)


def save_output(job_id: int, *, output_bytes: Optional[bytes], response_metadata: dict) -> None:
    if not enabled():
        return
    try:
        d = job_dir(job_id)
        if output_bytes:
            (d / "vton_output.png").write_bytes(output_bytes)
        (d / "model_response_metadata.json").write_text(
            json.dumps(response_metadata, indent=2, default=str), encoding="utf-8"
        )
    except Exception:  # noqa: BLE001
        logger.warning("Gagal menyimpan artefak output VTON job %s", job_id, exc_info=True)
