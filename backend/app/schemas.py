from pydantic import BaseModel, Field


class ProductColorCreate(BaseModel):
    hex_code: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    color_order: int = Field(ge=1, le=3)


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    sold_count: int = Field(ge=0)
    image_url: str = ""
    colors: list[ProductColorCreate] = Field(min_length=1, max_length=3)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    bot_message: str
    skin_tone_value: float | None = None
    undertone_value: float | None = None
    seasonal_type: str | None = None
    y1_value: float | None = None


class RecommendRequest(BaseModel):
    session_id: str
    disable_price: bool = False


class ProductColorResponse(BaseModel):
    hex_code: str
    color_order: int
    h_value: float
    s_value: float
    v_value: float
    ct_value: float
    cb_value: float


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    rating: float
    sold_count: int
    image_url: str
    colors: list[ProductColorResponse]


class RecommendationItem(BaseModel):
    rank: int
    product_id: str
    product_name: str
    saw_score: float
    skor_produk: float
    price: float
    rating: float
    sold_count: int
    image_url: str
    color_details: list[dict]


class RecommendResponse(BaseModel):
    session_id: str
    seasonal_type: str
    y1_value: float
    weights: dict
    recommendations: list[RecommendationItem]
