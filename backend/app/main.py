from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .chatbot import build_chat_response, init_aiml_kernel
from .color_utils import compute_color_features
from .database import Base, SessionLocal, engine, get_db
from .fuzzy import infer_layer1
from .models import ChatSession, Product, ProductColor, Recommendation
from .recommendation import evaluate_product_colors, rank_with_saw
from .schemas import (
    ChatRequest,
    ChatResponse,
    ProductCreate,
    ProductResponse,
    RecommendRequest,
    RecommendResponse,
)
from .seed import seed_products

app = FastAPI(title="Seera Recommendation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    response = []
    for product in products:
        colors = sorted(product.colors, key=lambda c: c.color_order)
        response.append(
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "rating": product.rating,
                "sold_count": product.sold_count,
                "image_url": product.image_url,
                "colors": [
                    {
                        "hex_code": c.hex_code,
                        "color_order": c.color_order,
                        "h_value": c.h_value,
                        "s_value": c.s_value,
                        "v_value": c.v_value,
                        "ct_value": c.ct_value,
                        "cb_value": c.cb_value,
                    }
                    for c in colors
                ],
            }
        )
    return response


@app.post("/products", response_model=ProductResponse)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        rating=payload.rating,
        sold_count=payload.sold_count,
        image_url=payload.image_url,
    )
    db.add(product)
    db.flush()

    for color_payload in sorted(payload.colors, key=lambda x: x.color_order):
        features = compute_color_features(color_payload.hex_code)
        color = ProductColor(
            product_id=product.id,
            hex_code=color_payload.hex_code,
            color_order=color_payload.color_order,
            **features,
        )
        db.add(color)

    db.commit()
    db.refresh(product)

    colors = sorted(product.colors, key=lambda c: c.color_order)
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "rating": product.rating,
        "sold_count": product.sold_count,
        "image_url": product.image_url,
        "colors": [
            {
                "hex_code": c.hex_code,
                "color_order": c.color_order,
                "h_value": c.h_value,
                "s_value": c.s_value,
                "v_value": c.v_value,
                "ct_value": c.ct_value,
                "cb_value": c.cb_value,
            }
            for c in colors
        ],
    }


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    session = None
    if payload.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()

    if not session:
        session = ChatSession()
        db.add(session)
        db.flush()

    bot_message, skin_tone, undertone, seasonal_type, y1 = build_chat_response(
        payload.message,
        session.skin_tone_value,
        session.undertone_value,
    )

    if skin_tone is not None:
        session.skin_tone_value = skin_tone
    if undertone is not None:
        session.undertone_value = undertone
    if seasonal_type is not None:
        session.seasonal_type = seasonal_type
    if y1 is not None:
        session.y1_value = y1

    db.commit()

    return {
        "session_id": session.id,
        "bot_message": bot_message,
        "skin_tone_value": session.skin_tone_value,
        "undertone_value": session.undertone_value,
        "seasonal_type": session.seasonal_type,
        "y1_value": session.y1_value,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session tidak ditemukan")

    if session.skin_tone_value is None or session.undertone_value is None:
        raise HTTPException(status_code=400, detail="Profiling belum lengkap")

    l1_result = infer_layer1(session.skin_tone_value, session.undertone_value)
    session.y1_value = l1_result.y1
    session.seasonal_type = l1_result.seasonal_type
    session.price_pref_enabled = not payload.disable_price

    products = db.query(Product).all()
    eval_items = []

    for product in products:
        colors = [
            {
                "hex_code": c.hex_code,
                "color_order": c.color_order,
                "ct_value": c.ct_value,
                "cb_value": c.cb_value,
            }
            for c in product.colors
        ]
        skor_produk, roc, details = evaluate_product_colors(l1_result.y1, colors)
        eval_items.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "skor_produk": skor_produk,
                "price": product.price,
                "rating": product.rating,
                "sold_count": product.sold_count,
                "image_url": product.image_url,
                "color_details": details,
                "roc_weights": roc,
            }
        )

    ranked, weights = rank_with_saw(eval_items, disable_price=payload.disable_price)

    db.query(Recommendation).filter(Recommendation.session_id == session.id).delete()
    for idx, item in enumerate(ranked, start=1):
        db.add(
            Recommendation(
                session_id=session.id,
                product_id=item["product_id"],
                skor_produk=item["skor_produk"],
                saw_score=item["saw_score"],
                rank=idx,
            )
        )
        item["rank"] = idx

    db.commit()

    return {
        "session_id": session.id,
        "seasonal_type": l1_result.seasonal_type,
        "y1_value": l1_result.y1,
        "weights": weights,
        "recommendations": ranked,
    }
