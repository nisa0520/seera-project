"""Test realistic virtual try-on / CatVTON layer (PRD CatVTON bagian 18)."""
import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.seed.seed_aiml_categories import seed_aiml
from app.seed.seed_education import seed_education
from app.seed.seed_catalog_dummy import seed_catalog
from app.seed.seed_backgrounds import seed_backgrounds
from app.seed.seed_visual_assets import seed_visual_assets
from app.seed.seed_vton_assets import seed_vton_assets
from app.services import face_region_service


# Wajah kecil di bagian atas frame -> foto upper-body valid
UPPER_BODY_FACE = (190, 60, 100, 100)
# Wajah besar memenuhi frame -> foto "hanya wajah"
FACE_ONLY_FACE = (90, 100, 300, 300)


def _seed_all():
    db = SessionLocal()
    try:
        seed_aiml(db)
        seed_education(db)
        seed_catalog(db)
        seed_backgrounds(db)
        seed_visual_assets(db)
        seed_vton_assets(db)
    finally:
        db.close()


def _photo_bytes(size=(480, 640)) -> bytes:
    rng = np.random.default_rng(11)
    base = np.full((size[1], size[0], 3), (170, 150, 135), dtype=np.int16)
    jitter = rng.integers(-12, 13, base.shape, dtype=np.int16)
    arr = np.clip(base + jitter, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


def _recommendation_session(client) -> tuple:
    r = client.post("/api/v1/conversations/start", json={})
    sid = r.json()["session_id"]
    client.post(f"/api/v1/conversations/{sid}/gender", json={"gender": "MALE"})
    client.post(f"/api/v1/conversations/{sid}/input-method", json={"method": "MANUAL"})
    client.post(f"/api/v1/conversations/{sid}/skin-tone", json={"skin_tone": "III"})
    client.post(f"/api/v1/conversations/{sid}/undertone", json={"undertone": "WARM"})
    r = client.post(f"/api/v1/conversations/{sid}/confirm", json={"is_confirmed": True, "top_n": 8})
    return sid, r.json()["recommendation"]["items"]


def _upload_person(client, sid, consent=True, source="CAMERA"):
    return client.post(
        f"/api/v1/conversations/{sid}/vton/person-image",
        files={"image_file": ("badan.png", _photo_bytes(), "image/png")},
        data={"source_type": source, "consent_confirmed": str(consent).lower()},
    )


@pytest.fixture(autouse=True)
def _vton_test_mode(monkeypatch, tmp_path):
    """Mode mock + sinkron agar job deterministik tanpa GPU (18.1 no. 5-6)."""
    monkeypatch.setattr(settings, "VTON_INFERENCE_MODE", "mock")
    monkeypatch.setattr(settings, "VTON_SYNC_MODE", True)
    monkeypatch.setattr(settings, "VTON_TEMP_DIR", str(tmp_path / "vton_tmp"))


# ---- Eligibility (FR-VTO-02, BR-VTO-03/05) ----

def test_eligibility_ready_and_not_supported():
    _seed_all()
    client = TestClient(app)
    db = SessionLocal()
    try:
        from app.models.product import Product
        koko = db.query(Product).filter(Product.name == "Koko Putih Classic").first()
        hijab = db.query(Product).filter(Product.name == "Hijab Lavender Soft").first()
        detail = db.query(Product).filter(Product.name == "Koko Navy Seera").first()
    finally:
        db.close()

    r = client.get(f"/api/v1/products/{koko.id}/vton-eligibility")
    body = r.json()
    assert body["vton_ready"] is True
    assert body["vton_status"] == "READY"
    assert body["garment_category"] == "upper"

    r = client.get(f"/api/v1/products/{hijab.id}/vton-eligibility")
    assert r.json()["vton_ready"] is False
    assert r.json()["vton_status"] == "NOT_SUPPORTED"

    r = client.get(f"/api/v1/products/{detail.id}/vton-eligibility")
    assert r.json()["vton_ready"] is False
    assert r.json()["vton_status"] == "PENDING"


def test_recommendation_items_include_vton_status():
    """Kartu produk membawa status & tier try-on (PRD 16.1, FR-VTO-15)."""
    _seed_all()
    client = TestClient(app)
    _, items = _recommendation_session(client)
    assert all(
        "vton_ready" in item and "vton_asset_tier" in item and "tryon_quality_mode" in item
        for item in items
    )
    assert any(item["vton_ready"] for item in items)
    valid_tiers = {"vton_ready", "vton_experimental", "vton_limited", "vton_not_supported"}
    assert all(item["vton_asset_tier"] in valid_tiers for item in items)


# ---- Person image: consent & validasi (FR-VTO-03/04/05) ----

def test_person_image_requires_consent(monkeypatch):
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, _ = _recommendation_session(client)

    r = _upload_person(client, sid, consent=False)
    assert r.status_code == 400
    assert "Persetujuan" in r.json()["detail"]["message"]


def test_person_image_rejects_face_only_photo(monkeypatch):
    """BR-VTO-01: foto yang hanya berisi wajah ditolak."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_ONLY_FACE])
    client = TestClient(app)
    sid, _ = _recommendation_session(client)

    r = _upload_person(client, sid)
    body = r.json()
    assert body["person_image_id"] is None
    assert body["quality_status"] == "FACE_ONLY"


def test_person_image_accepts_upper_body(monkeypatch):
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, _ = _recommendation_session(client)

    r = _upload_person(client, sid)
    body = r.json()
    assert body["person_image_id"] is not None
    assert body["quality_status"] == "OK"
    assert body["face_detected"] and body["body_detected"]
    assert body["mask_status"] == "SUCCESS"


# ---- Job lifecycle (FR-VTO-09/10, BR-VTO-02, BR-VTO-13) ----

def test_full_vton_job_flow(monkeypatch):
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(item for item in items if item["vton_ready"])

    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    assert r.status_code == 200
    job_id = r.json()["vton_job_id"]

    r = client.get(f"/api/v1/vton/jobs/{job_id}")
    body = r.json()
    assert body["status"] == "SUCCESS"
    assert body["output_image_url"]
    assert body["model_name"] == "MockVTON"  # mode mock pada test
    assert body["disclaimer"]

    # Output image dapat diambil
    r = client.get(body["output_image_url"])
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    Image.open(io.BytesIO(r.content)).verify()

    # Feedback try-on (FR-VTO-13)
    r = client.post(
        f"/api/v1/vton/jobs/{job_id}/feedback",
        json={
            "visual_quality_rating": 4,
            "proportion_rating": 4,
            "garment_similarity_rating": 5,
            "satisfaction_rating": 4,
            "comment": "Cukup realistis",
        },
    )
    assert r.status_code == 200
    assert r.json()["feedback_id"]

    # Feedback kedua ditolak
    r = client.post(f"/api/v1/vton/jobs/{job_id}/feedback", json={"satisfaction_rating": 5})
    assert r.status_code == 400


def test_job_rejected_for_non_recommended_product(monkeypatch):
    """BR-VTO-02: produk di luar hasil rekomendasi tidak dapat di-try-on."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, _ = _recommendation_session(client)
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": 999999, "person_image_id": person_id},
    )
    assert r.status_code == 400


def test_job_rejected_for_pending_asset(monkeypatch):
    """BR-VTO-03/05: produk tanpa aset READY tidak boleh diproses model."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    pending = next((item for item in items if not item["vton_ready"]), None)
    if pending is None:
        pytest.skip("Tidak ada produk non-ready pada rekomendasi ini")
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": pending["product_id"], "person_image_id": person_id},
    )
    assert r.status_code == 400


def test_failed_inference_does_not_break_recommendation(monkeypatch):
    """FR-VTO-14/BR-VTO-11: job gagal -> rekomendasi tetap utuh."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    # Paksa adapter gagal
    from app.services import vton_job_service
    from app.services.vton_model_adapter import VTONModelAdapter, VTONInferenceError

    class FailingAdapter(VTONModelAdapter):
        name = "MockVTON"

        def infer(self, *a, **k):
            raise VTONInferenceError("Simulasi inference gagal")

    monkeypatch.setattr("app.services.vton_job_service.get_adapter", lambda: FailingAdapter())

    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(item for item in items if item["vton_ready"])
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    job_id = r.json()["vton_job_id"]

    r = client.get(f"/api/v1/vton/jobs/{job_id}")
    assert r.json()["status"] == "FAILED"
    assert "gagal" in r.json()["error_message"].lower()

    # Rekomendasi tetap dapat diakses & tidak berubah (filter masih jalan)
    r = client.post(
        f"/api/v1/conversations/{sid}/recommendations/filter",
        json={"criteria": "PRICE_ASC"},
    )
    assert r.status_code == 200
    assert len(r.json()["items"]) > 0


def test_job_limit_per_session(monkeypatch):
    """NFR-VTO-07: batas try-on per sesi."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    monkeypatch.setattr(settings, "VTON_MAX_JOBS_PER_SESSION", 2)
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(item for item in items if item["vton_ready"])
    person_id = _upload_person(client, sid).json()["person_image_id"]

    for _ in range(2):
        r = client.post(
            f"/api/v1/conversations/{sid}/vton/jobs",
            json={"product_id": ready["product_id"], "person_image_id": person_id},
        )
        assert r.status_code == 200

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    assert r.status_code == 400
    assert "Batas" in r.json()["detail"]["message"]


def test_garment_asset_served():
    _seed_all()
    client = TestClient(app)
    r = client.get("/api/v1/vton/garments/koko-putih.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"

    r = client.get("/api/v1/vton/garments/../../etc/passwd")
    assert r.status_code in (404, 400)


# ---- IDM-VTON garment fidelity (PRD Revisi IDM-VTON) ----

def test_garment_caption_from_metadata():
    """FR-VTO-09 / 15.4: caption garment dibangun dari metadata produk."""
    _seed_all()
    from app.services.garment_caption_service import build_garment_caption
    from app.models.product import Product

    db = SessionLocal()
    try:
        koko = db.query(Product).filter(Product.name == "Koko Putih Classic").first()
        gamis = db.query(Product).filter(Product.name.like("Gamis%")).first()
        cap_koko = build_garment_caption(koko)
        cap_gamis = build_garment_caption(gamis)
    finally:
        db.close()

    assert "koko" in cap_koko.lower()
    assert "collar" in cap_koko.lower()
    # Warna dominan tersisip
    assert any(w in cap_koko.lower() for w in ("white", "putih", "ivory", "off"))
    assert "gamis" in cap_gamis.lower() or "dress" in cap_gamis.lower()


def test_job_records_idm_traceability(monkeypatch):
    """BR-VTO-13/16: job mencatat model default IDM-VTON, caption, varian, parameter."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(item for item in items if item["vton_ready"])
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    assert r.json()["garment_caption"]
    job_id = r.json()["vton_job_id"]

    db = SessionLocal()
    try:
        from app.models.vton_job import VtonJob
        job = db.get(VtonJob, job_id)
        assert job.garment_caption
        assert job.garment_vton_asset_id is not None
        assert job.selected_variant_id is not None
        assert job.inference_parameters  # diisi adapter saat diproses
    finally:
        db.close()

    # Status job membawa gambar produk asli untuk side-by-side (BR-VTO-17)
    r = client.get(f"/api/v1/vton/jobs/{job_id}")
    body = r.json()
    assert body["product_image_url"]
    assert body["output_image_url"]
    assert body["model_name"] == "MockVTON"  # mode mock pada test


def test_default_model_is_idm_vton():
    """PRD Revisi: model default = IDM-VTON, fallback = CatVTON."""
    from app.core.config import settings as live_settings
    assert live_settings.VTON_MODEL_DEFAULT == "idm-vton"
    assert live_settings.VTON_FALLBACK_MODEL == "catvton"


def test_fallback_chain_uses_catvton_when_idm_fails(monkeypatch, tmp_path):
    """BR-VTO-14: IDM-VTON gagal → fallback CatVTON otomatis menghasilkan output."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    # Mode "space" agar get_fallback_adapter aktif, tetapi adapter di-stub.
    monkeypatch.setattr(settings, "VTON_INFERENCE_MODE", "space")

    from app.services.vton_model_adapter import VTONModelAdapter, VTONInferenceError

    class FailingIDM(VTONModelAdapter):
        name = "IDM-VTON"
        def infer(self, *a, **k):
            raise VTONInferenceError("kuota GPU IDM-VTON habis")

    class WorkingCat(VTONModelAdapter):
        name = "CatVTON"
        def infer(self, *a, **k):
            from PIL import Image
            import io
            buf = io.BytesIO()
            Image.new("RGB", (64, 80), (200, 180, 160)).save(buf, format="PNG")
            return buf.getvalue()

    monkeypatch.setattr("app.services.vton_job_service.get_adapter", lambda: FailingIDM())
    monkeypatch.setattr("app.services.vton_job_service.get_fallback_adapter", lambda: WorkingCat())

    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(item for item in items if item["vton_ready"])
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    job_id = r.json()["vton_job_id"]

    r = client.get(f"/api/v1/vton/jobs/{job_id}")
    body = r.json()
    assert body["status"] == "SUCCESS"
    assert body["model_name"] == "CatVTON"  # fallback yang berhasil
    assert body["output_image_url"]


# ════════════════════════════════════════════════════════════════════════
#  VTON Asset Eligibility Tier (PRD AssetTier: FR-VTO-15/16/17, BR-VTO-22..26)
# ════════════════════════════════════════════════════════════════════════

def _product_by_name(name: str):
    db = SessionLocal()
    try:
        from app.models.product import Product
        return db.query(Product).filter(Product.name == name).first()
    finally:
        db.close()


def test_eligibility_tier_ready_response_shape():
    """vton_ready: realistic mode, tanpa warning/konfirmasi (PRD bagian 6)."""
    _seed_all()
    client = TestClient(app)
    koko = _product_by_name("Koko Putih Classic")
    body = client.get(f"/api/v1/products/{koko.id}/vton-eligibility").json()
    assert body["vton_supported"] is True
    assert body["vton_asset_tier"] == "vton_ready"
    assert body["tryon_quality_mode"] == "realistic"
    assert body["garment_vton_image_url"]
    assert body["quality_warning_message"] is None
    assert body["requires_user_confirmation_for_experimental_mode"] is False
    assert body["reason_if_not_supported"] is None


def test_eligibility_tier_experimental_requires_confirmation():
    """vton_experimental: warning + butuh konfirmasi (FR-VTO-16)."""
    _seed_all()
    client = TestClient(app)
    # abaya.png di-seed sebagai experimental
    prod = _product_by_name("Abaya Neutral Seera")
    body = client.get(f"/api/v1/products/{prod.id}/vton-eligibility").json()
    assert body["vton_supported"] is True
    assert body["vton_asset_tier"] == "vton_experimental"
    assert body["tryon_quality_mode"] == "experimental"
    assert body["requires_user_confirmation_for_experimental_mode"] is True
    assert body["quality_warning_message"]


def test_eligibility_tier_limited_has_stronger_warning():
    """vton_limited: warning lebih kuat (FR-VTO-15)."""
    _seed_all()
    client = TestClient(app)
    # koko.png (Koko Navy Seera) di-seed sebagai limited
    prod = _product_by_name("Koko Navy Seera")
    body = client.get(f"/api/v1/products/{prod.id}/vton-eligibility").json()
    assert body["vton_asset_tier"] == "vton_limited"
    assert body["tryon_quality_mode"] == "limited"
    assert body["requires_user_confirmation_for_experimental_mode"] is True
    assert body["quality_warning_message"]


def test_eligibility_tier_not_supported_blocks():
    """vton_not_supported: blocked + reason (FR-VTO-17/BR-VTO-25)."""
    _seed_all()
    client = TestClient(app)
    hijab = _product_by_name("Hijab Lavender Soft")
    body = client.get(f"/api/v1/products/{hijab.id}/vton-eligibility").json()
    assert body["vton_supported"] is False
    assert body["vton_asset_tier"] == "vton_not_supported"
    assert body["tryon_quality_mode"] == "blocked"
    assert body["reason_if_not_supported"]


def _run_until_recommendation(client):
    sid = client.post("/api/v1/conversations/start", json={}).json()["session_id"]
    client.post(f"/api/v1/conversations/{sid}/gender", json={"gender": "FEMALE"})
    client.post(f"/api/v1/conversations/{sid}/input-method", json={"method": "MANUAL"})
    client.post(f"/api/v1/conversations/{sid}/skin-tone", json={"skin_tone": "II"})
    client.post(f"/api/v1/conversations/{sid}/undertone", json={"undertone": "COOL"})
    r = client.post(f"/api/v1/conversations/{sid}/confirm", json={"is_confirmed": True, "top_n": 20})
    return sid, r.json()["recommendation"]["items"]


def test_experimental_job_blocked_without_confirmation(monkeypatch):
    """FR-VTO-16: tier experimental tanpa confirm_experimental ditolak."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _run_until_recommendation(client)
    exp = next((i for i in items if i["vton_asset_tier"] in ("vton_experimental", "vton_limited")), None)
    if exp is None:
        import pytest
        pytest.skip("Tidak ada produk experimental/limited pada rekomendasi ini")
    person_id = _upload_person(client, sid).json()["person_image_id"]

    # Tanpa konfirmasi → ditolak
    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": exp["product_id"], "person_image_id": person_id},
    )
    assert r.status_code == 400

    # Dengan konfirmasi → berjalan, job berlabel experimental/limited
    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": exp["product_id"], "person_image_id": person_id, "confirm_experimental": True},
    )
    assert r.status_code == 200
    assert r.json()["tryon_quality_mode"] in ("experimental", "limited")
    job_id = r.json()["vton_job_id"]
    body = client.get(f"/api/v1/vton/jobs/{job_id}").json()
    assert body["status"] == "SUCCESS"
    assert body["experimental_label"] in ("Preview Eksperimental", "Kualitas Aset Terbatas")


def test_not_supported_job_blocked_before_inference(monkeypatch):
    """BR-VTO-25: produk not_supported tidak memanggil model."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _run_until_recommendation(client)
    hijab = _product_by_name("Hijab Lavender Soft")
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": hijab.id, "person_image_id": person_id, "confirm_experimental": True},
    )
    # Bisa 400 (diblokir tier) atau ditolak karena bukan bagian rekomendasi —
    # yang penting tidak menghasilkan job sukses.
    assert r.status_code == 400


def test_ready_job_side_by_side_and_debug_artifacts(monkeypatch, tmp_path):
    """BR-VTO-17/26 side-by-side + PRD #12 debug artifacts untuk vton_ready."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    monkeypatch.setattr(settings, "VTON_ENABLE_DEBUG_ARTIFACTS", True)
    monkeypatch.setattr(settings, "VTON_DEBUG_DIR", str(tmp_path / "vton_debug"))
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(i for i in items if i["vton_asset_tier"] == "vton_ready")
    person_id = _upload_person(client, sid).json()["person_image_id"]

    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    job_id = r.json()["vton_job_id"]
    body = client.get(f"/api/v1/vton/jobs/{job_id}").json()
    assert body["status"] == "SUCCESS"
    # Side-by-side: produk asli + garment image + hasil
    assert body["product_image_url"]
    assert body["garment_vton_image_url"]
    assert body["output_image_url"]
    assert body["vton_asset_tier"] == "vton_ready"
    assert body["model_provider"] == "yisol"
    assert body["result_warning"]

    # Debug artifacts tersimpan (bukti gambar yang dikirim ke model)
    from pathlib import Path
    job_dir = Path(tmp_path) / "vton_debug" / str(job_id)
    assert (job_dir / "person_input.png").exists()
    assert (job_dir / "garment_input.png").exists()
    assert (job_dir / "vton_output.png").exists()
    assert (job_dir / "request_metadata.json").exists()
    assert (job_dir / "model_response_metadata.json").exists()


def test_selected_variant_maps_to_garment(monkeypatch):
    """BR-VTO-16: variant_id valid dipakai; invalid ditolak."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [UPPER_BODY_FACE])
    client = TestClient(app)
    sid, items = _recommendation_session(client)
    ready = next(i for i in items if i["vton_asset_tier"] == "vton_ready")
    valid_variant = ready["colors"][0]["color_id"] if ready.get("colors") and "color_id" in ready["colors"][0] else None
    person_id = _upload_person(client, sid).json()["person_image_id"]

    # Variant tidak valid → ditolak
    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id, "variant_id": 999999},
    )
    assert r.status_code == 400

    # Tanpa variant → pakai dominan, sukses + selected_variant tercatat
    r = client.post(
        f"/api/v1/conversations/{sid}/vton/jobs",
        json={"product_id": ready["product_id"], "person_image_id": person_id},
    )
    assert r.status_code == 200
    assert r.json()["selected_variant_id"] is not None
    assert r.json()["selected_color"]


def test_detailed_garment_caption():
    """FR-VTO-09/15.5: caption detail dari metadata (bukan generik)."""
    _seed_all()
    from app.services.garment_caption_service import build_garment_caption
    from app.models.product import Product
    db = SessionLocal()
    try:
        koko = db.query(Product).filter(Product.name == "Koko Batik Taupe").first()
        caption = build_garment_caption(koko)
    finally:
        db.close()
    assert "koko" in caption.lower()
    assert "collar" in caption.lower()
    assert "batik" in caption.lower()  # pola terdeteksi dari nama
    assert caption.lower() not in ("shirt", "a shirt", "clothing item")
