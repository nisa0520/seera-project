from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    top_n: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("top_n > 0 AND top_n <= 20", name="ck_recommendation_top_n"),
    )

    session = relationship("Session", back_populates="recommendations")
    items: Mapped[List["RecommendationItem"]] = relationship(
        "RecommendationItem", back_populates="recommendation", cascade="all,delete-orphan"
    )
    product_match_filters: Mapped[List["ProductMatchFilter"]] = relationship(
        "ProductMatchFilter", back_populates="recommendation", cascade="all,delete-orphan"
    )
