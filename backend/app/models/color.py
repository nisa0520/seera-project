from datetime import datetime
from sqlalchemy import String, Numeric, Integer, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.core.database import Base


class Color(Base):
    __tablename__ = "colors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    r: Mapped[int] = mapped_column(Integer, nullable=False)
    g: Mapped[int] = mapped_column(Integer, nullable=False)
    b: Mapped[int] = mapped_column(Integer, nullable=False)
    h: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    s: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    v: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    ct: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    cb: Mapped[float] = mapped_column(Numeric(8, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("r BETWEEN 0 AND 255", name="ck_color_r_range"),
        CheckConstraint("g BETWEEN 0 AND 255", name="ck_color_g_range"),
        CheckConstraint("b BETWEEN 0 AND 255", name="ck_color_b_range"),
        CheckConstraint("h >= 0 AND h <= 360", name="ck_color_h_range"),
        CheckConstraint("s >= 0 AND s <= 1", name="ck_color_s_range"),
        CheckConstraint("v >= 0 AND v <= 1", name="ck_color_v_range"),
        CheckConstraint("ct >= 0 AND ct <= 2", name="ck_color_ct_range"),
        CheckConstraint("cb >= 0 AND cb <= 1", name="ck_color_cb_range"),
    )

    product_colors: Mapped[List["ProductColor"]] = relationship("ProductColor", back_populates="color")
