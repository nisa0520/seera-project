"""Integration test alur image input → rekomendasi → visual matching (PRD 19.2)."""
import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.database import SessionLocal
from app.seed.seed_aiml_categories import seed_aiml
from app.seed.seed_education import seed_education
from app.seed.seed_catalog_dummy import seed_catalog
from app.seed.seed_backgrounds import seed_backgrounds
from app.seed.seed_visual_assets import seed_visual_assets
from app.services import face_region_service


FACE_BBOX = (80, 80, 320, 320)


def _seed_all():
    db = SessionLocal()
    try:
        seed_aiml(db)
        seed_education(db)
        seed_catalog(db)
        seed_backgrounds(db)
        seed_visual_assets(db)
    finally:
        db.close()


def _skin_photo_bytes(rgb=(198, 144, 110), size: int = 480) -> bytes:
    rng = np.random.default_rng(7)
    base = np.full((size, size, 3), rgb, dtype=np.int16)
    jitter = rng.integers(-12, 13, size=(size, size, 3), dtype=np.int16)
    image = np.clip(base + jitter, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(image).save(buf, format="PNG")
    return buf.getvalue()


def _start_until_input_method(client) -> int:
    r = client.post("/api/v1/conversations/start", json={})
    assert r.status_code == 200
    session_id = r.json()["session_id"]
    r = client.post(f"/api/v1/conversations/{session_id}/gender", json={"gender": "FEMALE"})
    assert r.status_code == 200
    assert r.json()["conversation_state"] == "WAITING_INPUT_METHOD"
    assert any(qr["value"] == "INPUT_METHOD_IMAGE" for qr in r.json()["quick_replies"])
    return session_id


def _upload_image(client, session_id, content: bytes, filename="wajah.png", source_type="CAMERA"):
    return client.post(
        f"/api/v1/conversations/{session_id}/image-analysis",
        files={"image_file": (filename, content, "image/png")},
        data={"source_type": source_type},
    )


def test_image_flow_until_recommendation(monkeypatch):
    """Alur penuh: foto → deteksi → konfirmasi → pipeline existing → rekomendasi."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_BBOX])
    client = TestClient(app)

    session_id = _start_until_input_method(client)

    # Masuk image mode
    r = client.post(f"/api/v1/conversations/{session_id}/image-mode")
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "WAITING_IMAGE_CAPTURE"
    assert body["camera_instruction"]

    # Upload foto valid
    r = _upload_image(client, session_id, _skin_photo_bytes())
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "WAITING_IMAGE_RESULT_CONFIRMATION"
    assert body["image_quality_status"] == "OK"
    assert body["requires_confirmation"] is True
    assert body["skin_tone"]["code"] in {"I", "II", "III", "IV", "V", "VI"}
    assert body["undertone"]["code"] in {"COOL", "NEUTRAL", "WARM"}
    assert 0.0 <= body["skin_tone"]["confidence"] <= 1.0
    assert body["face_bbox"]["width"] == FACE_BBOX[2]
    # Aset kepala try-on hasil pemrosesan server (PNG transparan + lebar kepala)
    face_crop = body["face_crop"]
    assert face_crop["data_url"].startswith("data:image/png;base64,")
    assert 0.5 <= face_crop["head_width_fraction"] <= 0.95

    detected_skin = body["skin_tone"]["code"]
    detected_undertone = body["undertone"]["code"]

    # Konfirmasi hasil deteksi
    r = client.post(
        f"/api/v1/conversations/{session_id}/image-analysis/confirm",
        json={"is_confirmed": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "WAITING_CONFIRMATION"
    assert body["skin_tone_final"]["code"] == detected_skin
    assert body["undertone_final"]["code"] == detected_undertone
    assert body["summary"]["skin_tone"] == detected_skin

    # Jalankan rekomendasi lewat endpoint existing (API-IMG-04)
    r = client.post(f"/api/v1/conversations/{session_id}/confirm", json={"is_confirmed": True, "top_n": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "SHOWING_RECOMMENDATION"
    assert body["seasonal_result"]["seasonal_type"]
    assert len(body["recommendation"]["items"]) > 0
    # Produk stok kosong tidak boleh tampil (BR-IMG-07)
    assert all(
        item["product_name"] != "Abaya Hitam Premium (Out of Stock)"
        for item in body["recommendation"]["items"]
    )


def test_image_result_consistent_with_manual_input(monkeypatch):
    """Konsistensi algoritma: input image yang dipetakan = input manual bernilai sama (PRD 17.3)."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_BBOX])
    client = TestClient(app)

    # Jalur image
    session_image = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_image}/image-mode")
    r = _upload_image(client, session_image, _skin_photo_bytes())
    skin_code = r.json()["skin_tone"]["code"]
    undertone_code = r.json()["undertone"]["code"]
    client.post(
        f"/api/v1/conversations/{session_image}/image-analysis/confirm",
        json={"is_confirmed": True},
    )
    r = client.post(f"/api/v1/conversations/{session_image}/confirm", json={"is_confirmed": True, "top_n": 5})
    image_result = r.json()

    # Jalur manual dengan nilai yang sama
    session_manual = _start_until_input_method(client)
    r = client.post(
        f"/api/v1/conversations/{session_manual}/input-method", json={"method": "MANUAL"}
    )
    assert r.json()["conversation_state"] == "WAITING_SKIN_TONE"
    client.post(f"/api/v1/conversations/{session_manual}/skin-tone", json={"skin_tone": skin_code})
    client.post(f"/api/v1/conversations/{session_manual}/undertone", json={"undertone": undertone_code})
    r = client.post(f"/api/v1/conversations/{session_manual}/confirm", json={"is_confirmed": True, "top_n": 5})
    manual_result = r.json()

    assert image_result["seasonal_result"]["seasonal_type"] == manual_result["seasonal_result"]["seasonal_type"]
    image_ranking = [item["product_id"] for item in image_result["recommendation"]["items"]]
    manual_ranking = [item["product_id"] for item in manual_result["recommendation"]["items"]]
    assert image_ranking == manual_ranking


def test_image_correction_applied(monkeypatch):
    """Koreksi manual hasil deteksi (FR-IMG-08, UAT no. 4)."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_BBOX])
    client = TestClient(app)

    session_id = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_id}/image-mode")
    _upload_image(client, session_id, _skin_photo_bytes())

    r = client.post(
        f"/api/v1/conversations/{session_id}/image-analysis/confirm",
        json={"is_confirmed": True, "corrected_skin_tone": "V", "corrected_undertone": "COOL"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["skin_tone_final"]["code"] == "V"
    assert body["undertone_final"]["code"] == "COOL"
    assert body["summary"]["undertone"] == "COOL"


def test_image_failed_then_fallback_manual(monkeypatch):
    """Alur image gagal → fallback manual (FR-IMG-15, PRD 19.2 no. 2)."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [])
    client = TestClient(app)

    session_id = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_id}/image-mode")

    # File bukan gambar → ditolak, sesi tidak berhenti (NFR-IMG-04)
    r = _upload_image(client, session_id, b"ini bukan gambar", filename="x.png")
    assert r.status_code == 200
    body = r.json()
    assert body["image_quality_status"] == "INVALID_FILE"
    assert body["conversation_state"] == "WAITING_IMAGE_CAPTURE"
    assert body["requires_confirmation"] is False
    assert any(qr["value"] == "INPUT_METHOD_MANUAL" for qr in body["quick_replies"])

    # Foto valid tapi tidak ada wajah → NO_FACE
    r = _upload_image(client, session_id, _skin_photo_bytes())
    body = r.json()
    assert body["image_quality_status"] == "NO_FACE"
    assert body["conversation_state"] == "WAITING_IMAGE_CAPTURE"

    # Fallback ke manual lalu alur existing tetap jalan
    r = client.post(f"/api/v1/conversations/{session_id}/input-method", json={"method": "MANUAL"})
    assert r.json()["conversation_state"] == "WAITING_SKIN_TONE"
    r = client.post(f"/api/v1/conversations/{session_id}/skin-tone", json={"skin_tone": "III"})
    assert r.status_code == 200
    r = client.post(f"/api/v1/conversations/{session_id}/undertone", json={"undertone": "WARM"})
    assert r.status_code == 200
    r = client.post(f"/api/v1/conversations/{session_id}/confirm", json={"is_confirmed": True, "top_n": 5})
    assert r.status_code == 200
    assert r.json()["conversation_state"] == "SHOWING_RECOMMENDATION"


def test_multiple_faces_rejected(monkeypatch):
    """BR-IMG-04: lebih dari satu wajah dominan ditolak."""
    _seed_all()
    monkeypatch.setattr(
        face_region_service,
        "detect_faces",
        lambda img: [(40, 80, 200, 200), (250, 80, 200, 200)],
    )
    client = TestClient(app)

    session_id = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_id}/image-mode")
    r = _upload_image(client, session_id, _skin_photo_bytes())
    body = r.json()
    assert body["image_quality_status"] == "MULTIPLE_FACES"
    assert body["face_count"] == 2
    assert body["conversation_state"] == "WAITING_IMAGE_CAPTURE"


def test_retake_photo_resets_previous_result(monkeypatch):
    """FR-IMG-13: ambil ulang foto mengganti hasil deteksi lama."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_BBOX])
    client = TestClient(app)

    session_id = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_id}/image-mode")
    r1 = _upload_image(client, session_id, _skin_photo_bytes(rgb=(225, 190, 160)))
    first_id = r1.json()["analysis_id"]

    # Tidak dikonfirmasi → kembali capture
    r = client.post(
        f"/api/v1/conversations/{session_id}/image-analysis/confirm",
        json={"is_confirmed": False},
    )
    assert r.json()["conversation_state"] == "WAITING_IMAGE_CAPTURE"

    r2 = _upload_image(client, session_id, _skin_photo_bytes(rgb=(120, 80, 60)))
    second_id = r2.json()["analysis_id"]
    assert second_id != first_id

    # Konfirmasi memakai hasil terbaru
    r = client.post(
        f"/api/v1/conversations/{session_id}/image-analysis/confirm",
        json={"is_confirmed": True},
    )
    assert r.json()["skin_tone_final"]["code"] == r2.json()["skin_tone"]["code"]


def test_backgrounds_and_visual_match(monkeypatch):
    """FR-IMG-11/12: pemilihan produk & background untuk preview visual."""
    _seed_all()
    monkeypatch.setattr(face_region_service, "detect_faces", lambda img: [FACE_BBOX])
    client = TestClient(app)

    # Background presets tersedia (API-IMG-05)
    r = client.get("/api/v1/backgrounds")
    assert r.status_code == 200
    backgrounds = r.json()["backgrounds"]
    assert len(backgrounds) >= 3
    assert all("image_url" in bg for bg in backgrounds)

    # Sampai rekomendasi via image flow
    session_id = _start_until_input_method(client)
    client.post(f"/api/v1/conversations/{session_id}/image-mode")
    _upload_image(client, session_id, _skin_photo_bytes())
    client.post(
        f"/api/v1/conversations/{session_id}/image-analysis/confirm",
        json={"is_confirmed": True},
    )
    r = client.post(f"/api/v1/conversations/{session_id}/confirm", json={"is_confirmed": True, "top_n": 5})
    items = r.json()["recommendation"]["items"]
    rec_id = r.json()["recommendation"]["id"]

    # Pilih produk pertama + background pertama
    r = client.post(
        f"/api/v1/conversations/{session_id}/visual-match",
        json={
            "recommendation_id": rec_id,
            "product_id": items[0]["product_id"],
            "background_id": backgrounds[0]["background_id"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "SHOWING_VISUAL_RECOMMENDATION"
    assert body["selected_product"]["product_id"] == items[0]["product_id"]
    assert body["selected_background"]["background_id"] == backgrounds[0]["background_id"]
    assert body["preview_config"]["background_url"] == backgrounds[0]["image_url"]
    assert body["preview_config"]["mode"] == "VIRTUAL_TRY_ON"
    # Try-on berbasis cutout foto produk (PNG transparan) + anchor posisi kepala
    expected_cutout = "/tryon/" + body["selected_product"]["image_url"].lstrip("/")
    assert body["preview_config"]["product_photo_url"] == expected_cutout
    anchor = body["preview_config"]["face_anchor"]
    assert set(anchor) >= {"cx", "cy", "w"}, anchor
    assert 0.0 < anchor["w"] < 1.0
    assert body["preview_config"]["garment_type"] in {"GAMIS", "ABAYA", "KOKO", "HIJAB"}
    assert body["preview_config"]["skin_hex"].startswith("#")
    assert "dominant" in body["preview_config"]["color_roles"]

    # Ganti produk tanpa background (preview diperbarui)
    r = client.post(
        f"/api/v1/conversations/{session_id}/visual-match",
        json={"product_id": items[1]["product_id"]},
    )
    assert r.status_code == 200
    assert r.json()["selected_product"]["product_id"] == items[1]["product_id"]

    # Produk di luar rekomendasi ditolak (BR-IMG-06)
    r = client.post(
        f"/api/v1/conversations/{session_id}/visual-match",
        json={"product_id": 999999},
    )
    assert r.status_code == 400

    # Aksi pasca-rekomendasi tetap bisa dipakai dari mode visual
    r = client.get(f"/api/v1/conversations/{session_id}/colors-to-avoid")
    assert r.status_code == 200

    # Feedback tetap berjalan (FR-IMG-14)
    r = client.post(
        f"/api/v1/conversations/{session_id}/feedback",
        json={"rating": 5, "comment": "Fitur visual bagus", "is_skipped": False},
    )
    assert r.status_code == 200
