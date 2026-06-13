import os
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.seed.seed_aiml_categories import seed_aiml
from app.seed.seed_education import seed_education
from app.seed.seed_catalog_dummy import seed_catalog


def _seed_all():
    db = SessionLocal()
    try:
        seed_aiml(db)
        seed_education(db)
        seed_catalog(db)
    finally:
        db.close()


def test_full_flow():
    _seed_all()
    client = TestClient(app)

    # Start
    r = client.post("/api/v1/conversations/start", json={})
    assert r.status_code == 200
    data = r.json()
    session_id = data["session_id"]
    assert data["conversation_state"] == "WAITING_SKIN_TONE"
    assert data["quick_replies"]

    # Invalid skin tone
    r = client.post(f"/api/v1/conversations/{session_id}/skin-tone", json={"skin_tone": "X"})
    assert r.status_code == 400
    body = r.json()
    assert body["detail"]["code"] == "INVALID_SKIN_TONE"

    # Valid skin tone
    r = client.post(f"/api/v1/conversations/{session_id}/skin-tone", json={"skin_tone": "II"})
    assert r.status_code == 200
    assert r.json()["conversation_state"] == "WAITING_UNDERTONE"

    # Invalid undertone
    r = client.post(f"/api/v1/conversations/{session_id}/undertone", json={"undertone": "Z"})
    assert r.status_code == 400

    # Valid undertone
    r = client.post(f"/api/v1/conversations/{session_id}/undertone", json={"undertone": "COOL"})
    assert r.status_code == 200
    assert r.json()["conversation_state"] == "WAITING_CONFIRMATION"

    # Confirm
    r = client.post(f"/api/v1/conversations/{session_id}/confirm", json={"is_confirmed": True, "top_n": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["conversation_state"] == "SHOWING_RECOMMENDATION"
    assert body["seasonal_result"]["seasonal_type"] == "SUMMER"
    items = body["recommendation"]["items"]
    assert len(items) > 0
    # Out-of-stock product (SK-008) must not appear
    assert all(item["product_name"] != "Dress Burgundy Silk (Out of Stock)" for item in items)
    # Tie-break ordering: score desc
    scores = [item["product_score"] for item in items]
    assert scores == sorted(scores, reverse=True)

    # Filter
    r = client.post(
        f"/api/v1/conversations/{session_id}/recommendations/filter",
        json={"criteria": "PRICE_ASC"},
    )
    assert r.status_code == 200
    items_filtered = r.json()["items"]
    prices = [item["price"] for item in items_filtered]
    assert prices == sorted(prices)

    # Colors to avoid
    r = client.get(f"/api/v1/conversations/{session_id}/colors-to-avoid")
    assert r.status_code == 200

    # Feedback
    r = client.post(
        f"/api/v1/conversations/{session_id}/feedback",
        json={"rating": 5, "comment": "Bagus", "is_skipped": False},
    )
    assert r.status_code == 200


def test_education_flow():
    _seed_all()
    client = TestClient(app)

    r = client.get("/api/v1/education/topics")
    assert r.status_code == 200
    topics = r.json()["topics"]
    assert any(t["code"] == "UNDERTONE" for t in topics)

    r = client.get("/api/v1/education/topics/UNDERTONE")
    assert r.status_code == 200
    assert "undertone" in r.json()["content"].lower()

    r = client.get("/api/v1/education/topics/NOT_EXIST")
    assert r.status_code == 404
