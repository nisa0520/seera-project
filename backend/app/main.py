import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .chatbot import build_chat_response, init_aiml_kernel, parse_multimodal_blocks
from .color_utils import compute_color_features
from .database import Base, SessionLocal, engine, get_db
from .fuzzy import infer_layer1
from .models import ChatLog, ChatSession, Feedback, Product, Color, ProductColor, Recommendation, RecommendationColorScore
from .recommendation import evaluate_product_colors, rank_with_saw
from .schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    ProductCreate,
    ProductResponse,
    RecommendRequest,
    RecommendResponse,
)
from .seed import seed_products

app = FastAPI(
    title="Seera Color Match — Chatbot Rekomendasi API",
    description="API untuk chatbot rekomendasi warna pakaian berdasarkan warna kulit menggunakan Fuzzy Logic, ROC, SAW, dan AIML Multimodal",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # Wildcard origin tidak boleh dipasangkan dengan credentials=True — browser memblokir fetch (mis. POST /recommend).
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_aiml_kernel()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "seera-color-match"}


# === Products ===

@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    response = []
    for product in products:
        colors = sorted(product.product_colors, key=lambda pc: pc.dominance_rank)
        response.append(
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "rating": product.rating,
                "popularity": product.popularity,
                "stock": product.stock,
                "image_url": product.image_url,
                "thumbnail_url": product.thumbnail_url,
                "colors": [
                    {
                        "hex_code": pc.color.hex_code,
                        "color_name": pc.color.color_name,
                        "dominance_rank": pc.dominance_rank,
                        "r": pc.color.r,
                        "g": pc.color.g,
                        "b": pc.color.b,
                        "h": pc.color.h,
                        "s": pc.color.s,
                        "v": pc.color.v,
                        "ct": pc.color.ct,
                        "cb": pc.color.cb,
                    }
                    for pc in colors
                ],
            }
        )
    return response


# === Chat (PRD Section 11.2) ===

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session = None
    if payload.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()

    if not session:
        session = ChatSession()
        db.add(session)
        db.flush()

    # Log user message (FR-SES-04)
    db.add(ChatLog(
        session_id=session.id,
        message=payload.message,
        sender="user",
        content_type="text",
    ))

    bot_message, skin_tone, undertone, seasonal_type, y1 = build_chat_response(
        payload.message,
        session.skin_tone,
        session.undertone,
    )

    if skin_tone is not None:
        session.skin_tone = skin_tone
    if undertone is not None:
        session.undertone = undertone
    if seasonal_type is not None:
        session.seasonal_type = seasonal_type
    if y1 is not None:
        session.y1_continuous = y1

    # Build multimodal blocks from bot_message
    blocks = parse_multimodal_blocks(bot_message)
    content_type = "multimodal" if len(blocks) > 1 or (len(blocks) == 1 and blocks[0]["type"] != "text") else "text"

    # Build quick replies based on state
    quick_replies = _build_quick_replies(session, seasonal_type)

    # Log bot response (FR-SES-04)
    db.add(ChatLog(
        session_id=session.id,
        message=bot_message,
        sender="bot",
        content_type=content_type,
        payload=json.dumps({"blocks": blocks, "quick_replies": [qr for qr in quick_replies]}, ensure_ascii=False),
    ))

    db.commit()

    return {
        "session_id": session.id,
        "bot_message": bot_message,
        "content_type": content_type,
        "blocks": blocks,
        "quick_replies": quick_replies,
        "skin_tone": session.skin_tone,
        "undertone": session.undertone,
        "seasonal_type": session.seasonal_type,
        "y1_continuous": session.y1_continuous,
    }


def _build_quick_replies(session: ChatSession, new_seasonal: str | None) -> list[dict]:
    """Generate context-aware quick replies per PRD FR-EDU-04, FR-NAV-01-05"""
    if new_seasonal or session.seasonal_type:
        return [
            {"label": "🎨 Lihat Rekomendasi", "value": "lihat rekomendasi"},
            {"label": "📚 Pelajari Lebih Lanjut", "value": "apa itu seasonal color type"},
            {"label": "🔄 Ulang Profiling", "value": "mulai profiling"},
        ]
    elif session.skin_tone is not None and session.undertone is None:
        return [
            {"label": "Hangat (Warm)", "value": "warm"},
            {"label": "Netral (Neutral)", "value": "neutral"},
            {"label": "Dingin (Cool)", "value": "cool"},
        ]
    else:
        return [
            {"label": "🎨 Cari Rekomendasi", "value": "Saya mau rekomendasi"},
            {"label": "📚 Teori Warna", "value": "apa itu skin tone"},
            {"label": "🏠 Menu Utama", "value": "menu utama"},
        ]

# === Visualizations (PRD Section 11.5) ===

@app.get("/visuals/{asset_key}")
def get_visual_asset(asset_key: str):
    """Serve metadata and url of visual assets"""
    # In a real app, these would come from the database `visual_assets` table.
    # We mock them here to fulfill the PRD requirements without requiring static files immediately.
    
    # Map visual types to some placeholder images or colors
    visuals_db = {
        "fitzpatrick_scale": {"type": "infographic", "url": "/about.png", "alt": "Skala Fitzpatrick (Testing Local Image)"},
        "undertone_comparison": {"type": "infographic", "url": "https://placehold.co/600x300/f5f5f5/333333?text=Perbandingan+Undertone", "alt": "Warm vs Cool vs Neutral"},
        "palette_spring": {"type": "palette", "url": "https://placehold.co/400x200/F4C2C2/333?text=Palet+Spring", "alt": "Palet Spring"},
        "palette_summer": {"type": "palette", "url": "https://placehold.co/400x200/B0C4DE/333?text=Palet+Summer", "alt": "Palet Summer"},
        "palette_autumn": {"type": "palette", "url": "https://placehold.co/400x200/D2B48C/333?text=Palet+Autumn", "alt": "Palet Autumn"},
        "palette_winter": {"type": "palette", "url": "https://placehold.co/400x200/E6E6FA/333?text=Palet+Winter", "alt": "Palet Winter"},
        "seasonal_overview": {"type": "infographic", "url": "https://placehold.co/600x400/f5f5f5/333?text=4+Musim+Warna", "alt": "4 Musim Warna"},
        "mascot_seera": {"type": "illustration", "url": "https://placehold.co/200x200/c9a86a/fff?text=Seera", "alt": "Maskot Seera"},
        "rgb_to_hsv_diagram": {"type": "infographic", "url": "https://placehold.co/500x300/f5f5f5/333?text=Tips+Fashion", "alt": "Tips Fashion Diagram"}
    }
    
    asset = visuals_db.get(asset_key)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset tidak ditemukan")
        
    return {
        "asset_key": asset_key,
        "type": asset["type"],
        "url": asset["url"],
        "alt": asset["alt"],
        "metadata": {}
    }


class ChartRequest(BaseModel):
    recommendation_id: str

@app.post("/charts/score-breakdown")
def generate_score_chart(payload: ChartRequest):
    """Generate SVG/PNG chart skor (PRD Section 11.5)"""
    # Mocking the chart generation. In a real app, use matplotlib/plotly to generate and return SVG
    return {
        "type": "chart",
        "format": "svg",
        "url": f"https://placehold.co/400x200/eef2ff/4f46e5?text=Score+Chart+{payload.recommendation_id}",
        "alt": "Bar chart skor breakdown",
        "data": {
            "C1": 0.8,
            "C2": 0.1,
            "C3": 0.05,
            "C4": 0.05
        }
    }


# === Recommendations (PRD Section 11.4) ===

@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    if session.skin_tone is None or session.undertone is None:
        raise HTTPException(status_code=400, detail="Profiling belum lengkap")

    skin = float(session.skin_tone)
    under_raw = session.undertone
    if isinstance(under_raw, (int, float)):
        under = float(under_raw)
    else:
        s = str(under_raw).strip().lower()
        _map = {"cool": 0.0, "neutral": 1.0, "warm": 2.0, "0": 0.0, "1": 1.0, "2": 2.0}
        under = _map.get(s)
        if under is None:
            try:
                under = float(s)
            except ValueError:
                under = 1.0

    l1_result = infer_layer1(skin, under)
    session.y1_continuous = l1_result.y1
    session.seasonal_type = l1_result.seasonal_type
    # session.price_pref_enabled = not payload.disable_price # We no longer save this to session here, just use in SAW

    products = db.query(Product).all()
    eval_items = []

    for product in products:
        colors = []
        for pc in sorted(product.product_colors, key=lambda x: x.dominance_rank):
            colors.append({
                "color_id": pc.color.id,
                "hex_code": pc.color.hex_code,
                "color_name": pc.color.color_name,
                "dominance_rank": pc.dominance_rank,
                "ct_value": float(pc.color.ct),
                "cb_value": float(pc.color.cb),
            })
            
        # evaluate_product_colors should now handle dominance_rank instead of color_order
        skor_produk, roc, details = evaluate_product_colors(l1_result.y1, colors)

        # Build color swatches for frontend display
        color_swatches = [
            {"hex_code": c["hex_code"], "color_name": c["color_name"]}
            for c in colors
        ]

        eval_items.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "thumbnail_url": product.thumbnail_url or product.image_url,
                "skor_produk": float(skor_produk), # C1 for SAW
                "price": float(product.price),
                "rating": float(product.rating),
                "popularity": product.popularity,
                "image_url": product.image_url,
                "color_details": details,
                "color_swatches": color_swatches,
                "roc_weights": {k: float(v) for k, v in roc.items()},
                "raw_colors": colors
            }
        )

    # rank_with_saw uses skor_produk, price, rating, popularity
    ranked, weights = rank_with_saw(eval_items, disable_price=payload.disable_price)

    # Clear old recommendations and save new ones
    db.query(Recommendation).filter(Recommendation.session_id == session.id).delete()
    db.flush()
    for idx, item in enumerate(ranked[:payload.top_n], start=1):
        rec = Recommendation(
            session_id=session.id,
            product_id=item["product_id"],
            roc_score=item["skor_produk"],
            final_score=item["saw_score"],
            rank=idx,
        )
        db.add(rec)
        db.flush()
        
        # Save detailed recommendation color scores
        for color_detail in item["color_details"]:
            db.add(RecommendationColorScore(
                recommendation_id=rec.id,
                color_id=color_detail["color_id"],
                dominance_rank=color_detail["dominance_rank"],
                y2_score=color_detail["suitability_score"],
                roc_weight=item["roc_weights"][color_detail["dominance_rank"]]
            ))

        # Rename saw_score to final_score for the response
        item["final_score"] = item.pop("saw_score")
        item["roc_score"] = item.pop("skor_produk")
        item["rank"] = idx

    db.commit()

    return {
        "session_id": session.id,
        "seasonal_type": l1_result.seasonal_type,
        "y1_continuous": l1_result.y1,
        "weights": weights,
        "recommendations": ranked[:payload.top_n],
    }


# === Feedback (PRD Section 11.6, FR-FB-01 to FR-FB-03) ===

@app.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    feedback = Feedback(
        session_id=session.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()

    return {"ok": True, "message": "Terima kasih atas feedback Anda!"}


# === Chat History (PRD Section 11.2) ===

@app.get("/chat/history/{session_id}")
def get_chat_history(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    logs = (
        db.query(ChatLog)
        .filter(ChatLog.session_id == session_id)
        .order_by(ChatLog.created_at.asc())
        .all()
    )

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": log.id,
                "sender": log.sender,
                "message": log.message,
                "content_type": log.content_type,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
    }
