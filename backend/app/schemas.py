from pydantic import BaseModel, Field

# === Product Schemas ===

class ProductColorCreate(BaseModel):
    hex_code: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    color_name: str = ""
    dominance_rank: int = Field(ge=1, le=5)


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    popularity: int = Field(ge=0)
    stock: int = Field(default=100, ge=0)
    image_url: str = ""
    thumbnail_url: str = ""
    category_id: int | None = None
    colors: list[ProductColorCreate] = Field(min_length=1, max_length=5)


class ProductColorResponse(BaseModel):
    hex_code: str
    color_name: str = ""
    dominance_rank: int
    r: int
    g: int
    b: int
    h: float
    s: float
    v: float
    ct: float
    cb: float


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    rating: float
    popularity: int
    stock: int
    image_url: str
    thumbnail_url: str = ""
    colors: list[ProductColorResponse]


# === Chat Schemas (PRD Section 11.2) ===

class ChatRequest(BaseModel):
    session_id: int | None = None
    message: str


class QuickReply(BaseModel):
    label: str
    value: str


class MultimodalBlock(BaseModel):
    type: str  # 'text', 'image', 'palette', 'product-card', 'chart'
    content: str | None = None
    url: str | None = None
    alt: str | None = None
    data: dict | None = None
    chart_type: str | None = None
    data_ref: str | None = None


class ChatResponse(BaseModel):
    session_id: int
    bot_message: str
    content_type: str = "text"  # 'text' or 'multimodal'
    blocks: list[MultimodalBlock] = []
    quick_replies: list[QuickReply] = []
    skin_tone: float | None = None
    undertone: str | None = None
    seasonal_type: str | None = None
    y1_continuous: float | None = None


# === Recommendation Schemas (PRD Section 11.4) ===

class RecommendRequest(BaseModel):
    session_id: int
    disable_price: bool = False
    top_n: int = Field(default=5, ge=3, le=10)


class ColorSwatchResponse(BaseModel):
    hex_code: str
    color_name: str = ""


class RecommendationItem(BaseModel):
    rank: int
    product_id: int
    product_name: str
    thumbnail_url: str = ""
    final_score: float
    roc_score: float = 0.0
    price: float
    rating: float
    popularity: int
    image_url: str
    color_details: list[dict]
    color_swatches: list[ColorSwatchResponse] = []


class RecommendResponse(BaseModel):
    session_id: int
    seasonal_type: str
    y1_continuous: float
    weights: dict
    recommendations: list[RecommendationItem]


# === Feedback Schemas (PRD Section 11.6) ===

class FeedbackRequest(BaseModel):
    session_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class FeedbackResponse(BaseModel):
    ok: bool
    message: str = ""
