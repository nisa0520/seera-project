import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=4.5)
    popularity: Mapped[int] = mapped_column(Integer, default=0)
    stock: Mapped[int] = mapped_column(Integer, default=100, index=True)
    image_url: Mapped[str] = mapped_column(String(500), default="")
    thumbnail_url: Mapped[str] = mapped_column(String(500), default="")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped[Category | None] = relationship("Category", back_populates="products")
    product_colors: Mapped[list["ProductColor"]] = relationship("ProductColor", back_populates="product", cascade="all, delete-orphan")


class Color(Base):
    __tablename__ = "colors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), unique=True, nullable=False, index=True)
    r: Mapped[int] = mapped_column(Integer, nullable=False)
    g: Mapped[int] = mapped_column(Integer, nullable=False)
    b: Mapped[int] = mapped_column(Integer, nullable=False)
    h: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    s: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    v: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    ct: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    cb: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product_colors: Mapped[list["ProductColor"]] = relationship("ProductColor", back_populates="color")


class ProductColor(Base):
    __tablename__ = "product_colors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id"), nullable=False)
    dominance_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    product: Mapped[Product] = relationship("Product", back_populates="product_colors")
    color: Mapped[Color] = relationship("Color", back_populates="product_colors")

    __table_args__ = (
        UniqueConstraint('product_id', 'dominance_rank', name='uq_product_rank'),
        UniqueConstraint('product_id', 'color_id', name='uq_product_color'),
    )


class ChatSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    skin_tone: Mapped[int | None] = mapped_column(Integer, nullable=True)
    undertone: Mapped[str | None] = mapped_column(String(10), nullable=True)
    y1_continuous: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    seasonal_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    chat_logs: Mapped[list["ChatLog"]] = relationship("ChatLog", back_populates="session", cascade="all, delete-orphan")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="session", cascade="all, delete-orphan")


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(10), nullable=False)
    intent: Mapped[str | None] = mapped_column(String(40), nullable=True)
    content_type: Mapped[str] = mapped_column(String(20), default="text")
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="chat_logs")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    roc_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    color_scores: Mapped[list["RecommendationColorScore"]] = relationship("RecommendationColorScore", back_populates="recommendation", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('session_id', 'rank', name='uq_session_rank'),
        UniqueConstraint('session_id', 'product_id', name='uq_session_product'),
    )


class RecommendationColorScore(Base):
    __tablename__ = "recommendation_color_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(ForeignKey("recommendations.id"), nullable=False, index=True)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id"), nullable=False)
    dominance_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    y2_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    roc_weight: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)

    recommendation: Mapped[Recommendation] = relationship("Recommendation", back_populates="color_scores")

    __table_args__ = (
        UniqueConstraint('recommendation_id', 'color_id', name='uq_recommendation_color'),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False, unique=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="feedbacks")


class VisualAsset(Base):
    __tablename__ = "visual_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(500), default="")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
