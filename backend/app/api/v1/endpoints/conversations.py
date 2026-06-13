"""Conversation endpoints - core chatbot flow (UC-01)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.exceptions import (
    InvalidSkinToneError,
    InvalidUndertoneError,
    InvalidConversationStateError,
)
from app.schemas.conversation import (
    StartConversationRequest,
    SkinToneRequest,
    UndertoneRequest,
    ConfirmRequest,
    FilterRequest,
    FreeTextRequest,
)
from app.services.conversation_service import (
    ConversationService,
    STATE_WAITING_SKIN_TONE,
    STATE_WAITING_UNDERTONE,
    STATE_WAITING_CONFIRMATION,
    STATE_WAITING_CHANGE_SELECTION,
    STATE_SHOWING_RECOMMENDATION,
)
from app.services.aiml_interpreter import AIMLInterpreter
from app.services.input_validation_service import (
    normalize_skin_tone,
    normalize_undertone,
    skin_tone_payload,
    undertone_payload,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/start")
def start_conversation(payload: StartConversationRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.create_session(
        user_fingerprint=payload.user_fingerprint, buyer_id=payload.buyer_id
    )
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


@router.post("/{session_id}/skin-tone")
def set_skin_tone(session_id: int, payload: SkinToneRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    # Allow re-entry from waiting_change_selection too
    conv.require_state(session, STATE_WAITING_SKIN_TONE, STATE_WAITING_CHANGE_SELECTION)

    conv.log_message(session, payload.skin_tone, "BUYER")

    code = normalize_skin_tone(payload.skin_tone)
    if code is None:
        response = aiml.respond("INVALID_SKINTONE")
        conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
        db.commit()
        raise InvalidSkinToneError(response["message"])

    payload_data = skin_tone_payload(code)
    sc = conv.get_or_create_skin_characteristic(session)
    sc.skintone = payload_data["value"]
    sc.skintone_name = payload_data["name"]
    session.skintone_snapshot = payload_data["value"]
    conv.set_state(session, STATE_WAITING_UNDERTONE)

    response = aiml.respond(
        "UNDERTONE_LIST",
        context={"skin_tone_name": payload_data["name"], "skin_tone_code": code},
    )
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
        "skin_tone": {"code": code, "name": payload_data["name"], "value": payload_data["value"]},
    }


@router.post("/{session_id}/undertone")
def set_undertone(session_id: int, payload: UndertoneRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_WAITING_UNDERTONE, STATE_WAITING_CHANGE_SELECTION)
    if not session.skin_characteristic or session.skin_characteristic.skintone is None:
        raise InvalidConversationStateError("Skin tone belum diisi.")

    conv.log_message(session, payload.undertone, "BUYER")

    code = normalize_undertone(payload.undertone)
    if code is None:
        response = aiml.respond("INVALID_UNDERTONE")
        conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])
        db.commit()
        raise InvalidUndertoneError(response["message"])

    payload_data = undertone_payload(code)
    sc = session.skin_characteristic
    sc.undertone = payload_data["value"]
    sc.undertone_name = payload_data["name"]
    session.undertone_snapshot = code
    conv.set_state(session, STATE_WAITING_CONFIRMATION)

    response = aiml.respond(
        "SUMMARY_AND_CONFIRMATION",
        context={
            "skin_tone_name": sc.skintone_name,
            "undertone_name": payload_data["name"],
        },
    )
    conv.log_message(session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"])

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
        "summary": {
            "skin_tone": _skin_code_from_value(float(sc.skintone)),
            "skin_tone_name": sc.skintone_name,
            "undertone": code,
            "undertone_name": payload_data["name"],
        },
    }


@router.post("/{session_id}/confirm")
def confirm(session_id: int, payload: ConfirmRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_WAITING_CONFIRMATION)

    if not payload.is_confirmed:
        target = (payload.change_target or "").upper()
        if target == "SKIN_TONE":
            conv.set_state(session, STATE_WAITING_SKIN_TONE)
            response = aiml.respond("WELCOME_AND_SKINTONE_LIST")
        elif target == "UNDERTONE":
            conv.set_state(session, STATE_WAITING_UNDERTONE)
            response = aiml.respond(
                "UNDERTONE_LIST",
                context={
                    "skin_tone_name": session.skin_characteristic.skintone_name or "",
                },
            )
        else:
            conv.set_state(session, STATE_WAITING_CHANGE_SELECTION)
            response = aiml.respond("CHANGE_SELECTION_OPTIONS")

        conv.log_message(
            session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"]
        )
        db.commit()
        return {
            "session_id": session.id,
            "session_status": session.session_status,
            "conversation_state": session.conversation_state,
            "message": response["message"],
            "quick_replies": response["quick_replies"],
        }

    sc = session.skin_characteristic
    rec_service = RecommendationService(db)
    seasonal_result = rec_service.classify_seasonal(
        session, float(sc.skintone), float(sc.undertone)
    )
    rec_data = rec_service.generate_recommendation(session, seasonal_result, top_n=payload.top_n)
    items = rec_data["items"]

    conv.set_state(session, STATE_SHOWING_RECOMMENDATION)

    response = aiml.respond(
        "PRODUCT_RECOMMENDATIONS",
        context={
            "skin_tone_name": sc.skintone_name,
            "undertone_name": sc.undertone_name,
            "seasonal_name": seasonal_result.seasonal_name,
            "top_n": str(payload.top_n),
        },
    )
    conv.log_message(
        session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"]
    )

    debug = None
    if payload.include_debug:
        debug = {
            "skin_membership": seasonal_result.fired_rules,
            "y1_continuous": float(seasonal_result.y1_continuous),
            "seasonal_membership": seasonal_result.seasonal_membership,
        }

    db.commit()
    return {
        "session_id": session.id,
        "session_status": session.session_status,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
        "seasonal_result": {
            "y1_continuous": float(seasonal_result.y1_continuous),
            "seasonal_type": seasonal_result.seasonal_code,
            "seasonal_name": seasonal_result.seasonal_name,
            "score_seasonal": float(seasonal_result.score_seasonal),
            "membership": seasonal_result.seasonal_membership,
        },
        "recommendation": {
            "id": rec_data["recommendation"].id,
            "top_n": payload.top_n,
            "items": _serialize_items_for_response(items),
        },
        "debug": debug,
    }


@router.post("/{session_id}/recommendations/filter")
def filter_recommendations(session_id: int, payload: FilterRequest, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_SHOWING_RECOMMENDATION)
    conv.log_message(session, f"Filter: {payload.criteria}", "BUYER")

    rec_service = RecommendationService(db)
    rec = rec_service.get_latest_recommendation(session)
    criteria = payload.criteria.upper()
    if criteria not in {"SCORE_DESC", "PRICE_ASC", "RATING_DESC", "POPULARITY_DESC"}:
        raise InvalidConversationStateError("Kriteria filter tidak dikenal.")

    new_items = rec_service.reorder_items(rec, criteria)

    # Update rank_number in DB. To avoid violating unique(rec_id, rank_number)
    # mid-update, shift all current ranks above the active range, then assign final ranks.
    rank_by_product = {item["product_id"]: item["rank"] for item in new_items}
    offset = 1000 + rec.id * 100
    for db_item in rec.items:
        db_item.rank_number = offset + db_item.id
    db.flush()
    for db_item in rec.items:
        new_rank = rank_by_product.get(db_item.product_id)
        if new_rank is not None:
            db_item.rank_number = new_rank
    db.flush()

    response = aiml.respond(
        "FILTERED_RECOMMENDATIONS", context={"criteria": payload.criteria}
    )
    conv.log_message(
        session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"]
    )
    db.commit()
    return {
        "session_id": session.id,
        "recommendation_id": rec.id,
        "criteria": criteria,
        "items": new_items,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


@router.get("/{session_id}/colors-to-avoid")
def colors_to_avoid(session_id: int, db: DBSession = Depends(get_db)):
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.require_state(session, STATE_SHOWING_RECOMMENDATION)
    conv.log_message(session, "Tampilkan warna yang sebaiknya dihindari", "BUYER")

    rec_service = RecommendationService(db)
    rec = rec_service.get_latest_recommendation(session)
    colors = rec_service.colors_to_avoid(rec)
    response = aiml.respond("COLORS_TO_AVOID")
    conv.log_message(
        session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"]
    )
    db.commit()
    return {
        "session_id": session.id,
        "colors_to_avoid": colors,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


@router.post("/{session_id}/free-text")
def free_text(session_id: int, payload: FreeTextRequest, db: DBSession = Depends(get_db)):
    """Free-text fallback: tries to interpret keyword and respond, else NOT_UNDERSTOOD."""
    conv = ConversationService(db)
    aiml = AIMLInterpreter(db)

    session = conv.get_active_session(session_id)
    conv.log_message(session, payload.message, "BUYER")

    text = payload.message.strip().lower()

    # Try interpret as skin tone first if waiting
    if session.conversation_state in (STATE_WAITING_SKIN_TONE, STATE_WAITING_CHANGE_SELECTION):
        code = normalize_skin_tone(payload.message)
        if code:
            db.commit()
            return set_skin_tone(session_id, SkinToneRequest(skin_tone=code), db)

    if session.conversation_state in (STATE_WAITING_UNDERTONE, STATE_WAITING_CHANGE_SELECTION):
        code = normalize_undertone(payload.message)
        if code:
            db.commit()
            return set_undertone(session_id, UndertoneRequest(undertone=code), db)

    # Confirmation: yes/no
    if session.conversation_state == STATE_WAITING_CONFIRMATION:
        if any(word in text for word in ["ya", "iya", "ok", "oke", "sesuai", "lanjut", "confirm", "setuju"]):
            db.commit()
            return confirm(session_id, ConfirmRequest(is_confirmed=True), db)
        if any(word in text for word in ["tidak", "ubah", "ganti", "batal", "no"]):
            db.commit()
            return confirm(session_id, ConfirmRequest(is_confirmed=False), db)

    response = aiml.respond("NOT_UNDERSTOOD")
    conv.log_message(
        session, response["message"], "BOT", aiml_category_id=response["aiml_category_id"]
    )
    db.commit()
    return {
        "session_id": session.id,
        "conversation_state": session.conversation_state,
        "message": response["message"],
        "quick_replies": response["quick_replies"],
    }


def _serialize_items_for_response(items: list[dict]) -> list[dict]:
    out = []
    for item in items:
        out.append({
            "rank": item.get("rank"),
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "price": item["price_snapshot"],
            "rating": item["rating_snapshot"],
            "stock": item["stock_snapshot"],
            "popularity": item.get("popularity", 0),
            "image_url": item.get("image_url"),
            "product_score": item["product_score"],
            "label": item["label"],
            "label_indonesian": item["label_indonesian"],
            "colors": item["colors"],
        })
    return out


_SKIN_VALUE_TO_CODE = {1.0: "I", 2.0: "II", 3.0: "III", 4.0: "IV", 5.0: "V", 6.0: "VI"}


def _skin_code_from_value(value: float) -> str:
    return _SKIN_VALUE_TO_CODE.get(value, "")
