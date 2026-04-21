import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    sold_count: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    colors: Mapped[list["ProductColor"]] = relationship("ProductColor", back_populates="product", cascade="all, delete-orphan")


class ProductColor(Base):
    __tablename__ = "product_colors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)
    color_order: Mapped[int] = mapped_column(Integer, default=1)
    h_value: Mapped[float] = mapped_column(Float, default=0)
    s_value: Mapped[float] = mapped_column(Float, default=0)
    v_value: Mapped[float] = mapped_column(Float, default=0)
    ct_value: Mapped[float] = mapped_column(Float, default=1)
    cb_value: Mapped[float] = mapped_column(Float, default=0)

    product: Mapped[Product] = relationship("Product", back_populates="colors")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    skin_tone_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    undertone_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    seasonal_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    y1_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_pref_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    skor_produk: Mapped[float] = mapped_column(Float, nullable=False)
    saw_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
