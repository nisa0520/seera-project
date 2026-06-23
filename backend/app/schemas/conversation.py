from pydantic import BaseModel, Field
from typing import Optional, Any


class StartConversationRequest(BaseModel):
    buyer_id: Optional[int] = None
    user_fingerprint: Optional[str] = None


class GenderRequest(BaseModel):
    gender: str = Field(..., min_length=1, max_length=30)


class SkinToneRequest(BaseModel):
    skin_tone: str = Field(..., min_length=1, max_length=20)


class UndertoneRequest(BaseModel):
    undertone: str = Field(..., min_length=1, max_length=20)


class ConfirmRequest(BaseModel):
    is_confirmed: bool
    change_target: Optional[str] = None
    top_n: int = Field(default=5, ge=1, le=20)
    include_debug: bool = False


class FilterRequest(BaseModel):
    criteria: str = Field(..., min_length=1)


class FeedbackRequest(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)
    is_skipped: bool = False


class FreeTextRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class InputMethodRequest(BaseModel):
    method: str = Field(..., min_length=1, max_length=20)


class ImageAnalysisConfirmRequest(BaseModel):
    is_confirmed: bool
    corrected_skin_tone: Optional[str] = Field(default=None, max_length=20)
    corrected_undertone: Optional[str] = Field(default=None, max_length=20)


class VisualMatchRequest(BaseModel):
    recommendation_id: Optional[int] = None
    product_id: int
    background_id: Optional[int] = None


class VtonJobRequest(BaseModel):
    product_id: int
    person_image_id: int
    background_id: Optional[int] = None
    # Varian warna spesifik yang dipilih pengguna (BR-VTO-16). Bila None,
    # sistem memakai warna dominan produk.
    variant_id: Optional[int] = None
    # Konfirmasi eksplisit untuk tier experimental/limited (FR-VTO-16).
    confirm_experimental: bool = False


class VtonFeedbackRequest(BaseModel):
    visual_quality_rating: Optional[int] = Field(default=None, ge=1, le=5)
    proportion_rating: Optional[int] = Field(default=None, ge=1, le=5)
    garment_similarity_rating: Optional[int] = Field(default=None, ge=1, le=5)
    satisfaction_rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)


class ConversationSummary(BaseModel):
    gender: Optional[str] = None
    gender_name: Optional[str] = None
    skin_tone: Optional[str] = None
    skin_tone_name: Optional[str] = None
    undertone: Optional[str] = None
    undertone_name: Optional[str] = None


class ConversationStateResponse(BaseModel):
    session_id: int
    session_status: str
    conversation_state: str
    message: str
    quick_replies: Optional[list[dict[str, Any]]] = None
    summary: Optional[ConversationSummary] = None
    extra: Optional[dict[str, Any]] = None
