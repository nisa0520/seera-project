"""initial schema - all 16 tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(150), nullable=True),
        sa.Column("user_fingerprint", sa.String(255), nullable=True),
        sa.Column("time_session", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_fingerprint", "users", ["user_fingerprint"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("conversation_state", sa.String(50), nullable=False, server_default="WAITING_SKIN_TONE"),
        sa.Column("skintone_snapshot", sa.Numeric(4, 2), nullable=True),
        sa.Column("undertone_snapshot", sa.String(20), nullable=True),
        sa.Column("y1_continuous", sa.Numeric(8, 6), nullable=True),
        sa.Column("seasonal_type_name", sa.String(50), nullable=True),
        sa.Column("recommendation_id", sa.Integer, nullable=True),
        sa.Column("previous_state", sa.String(50), nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "session_status IN ('ACTIVE','COMPLETED','CANCELLED')", name="ck_session_status"
        ),
        sa.CheckConstraint(
            "conversation_state IN ('WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
            name="ck_conversation_state",
        ),
    )
    op.create_index("idx_sessions_user_created", "sessions", ["user_id", "created_at"])
    op.create_index("idx_sessions_state", "sessions", ["session_status", "conversation_state"])

    op.create_table(
        "skin_characteristics",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("skintone", sa.Numeric(4, 2), nullable=True),
        sa.Column("undertone", sa.Numeric(4, 2), nullable=True),
        sa.Column("name", sa.String(150), nullable=True),
        sa.Column("skintone_name", sa.String(50), nullable=True),
        sa.Column("undertone_name", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("skintone IS NULL OR (skintone >= 1 AND skintone <= 6)", name="ck_skintone_range"),
        sa.CheckConstraint(
            "undertone IS NULL OR (undertone >= 0 AND undertone <= 2)", name="ck_undertone_range"
        ),
        sa.UniqueConstraint("session_id", name="uq_skin_characteristic_session"),
    )

    op.create_table(
        "seasonal_results",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "skin_characteristic_id",
            sa.Integer,
            sa.ForeignKey("skin_characteristics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("seasonal_code", sa.String(30), nullable=False),
        sa.Column("seasonal_name", sa.String(50), nullable=False),
        sa.Column("y1_continuous", sa.Numeric(8, 6), nullable=False),
        sa.Column("score_seasonal", sa.Numeric(8, 6), nullable=False),
        sa.Column("seasonal_membership", sa.JSON, nullable=False),
        sa.Column("fired_rules", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("y1_continuous >= 0 AND y1_continuous <= 3", name="ck_y1_range"),
        sa.CheckConstraint("score_seasonal >= 0 AND score_seasonal <= 1", name="ck_score_seasonal_range"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("external_catalog_id", sa.String(100), nullable=True, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("popularity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("stock", sa.Integer, nullable=False, server_default="0"),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("price >= 0", name="ck_product_price_nonneg"),
        sa.CheckConstraint("rating IS NULL OR (rating >= 0 AND rating <= 5)", name="ck_product_rating_range"),
        sa.CheckConstraint("popularity >= 0", name="ck_product_popularity_nonneg"),
        sa.CheckConstraint("stock >= 0", name="ck_product_stock_nonneg"),
    )
    op.create_index("idx_products_available", "products", ["is_active", "stock", "rating", "price"])

    op.create_table(
        "colors",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("color_name", sa.String(100), nullable=False),
        sa.Column("hex_code", sa.String(7), nullable=False, unique=True),
        sa.Column("r", sa.Integer, nullable=False),
        sa.Column("g", sa.Integer, nullable=False),
        sa.Column("b", sa.Integer, nullable=False),
        sa.Column("h", sa.Numeric(8, 4), nullable=False),
        sa.Column("s", sa.Numeric(8, 6), nullable=False),
        sa.Column("v", sa.Numeric(8, 6), nullable=False),
        sa.Column("ct", sa.Numeric(8, 6), nullable=False),
        sa.Column("cb", sa.Numeric(8, 6), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("r BETWEEN 0 AND 255", name="ck_color_r_range"),
        sa.CheckConstraint("g BETWEEN 0 AND 255", name="ck_color_g_range"),
        sa.CheckConstraint("b BETWEEN 0 AND 255", name="ck_color_b_range"),
        sa.CheckConstraint("h >= 0 AND h <= 360", name="ck_color_h_range"),
        sa.CheckConstraint("s >= 0 AND s <= 1", name="ck_color_s_range"),
        sa.CheckConstraint("v >= 0 AND v <= 1", name="ck_color_v_range"),
        sa.CheckConstraint("ct >= 0 AND ct <= 2", name="ck_color_ct_range"),
        sa.CheckConstraint("cb >= 0 AND cb <= 1", name="ck_color_cb_range"),
    )

    op.create_table(
        "product_colors",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("color_id", sa.Integer, sa.ForeignKey("colors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("color_role", sa.String(30), nullable=False),
        sa.Column("color_rank", sa.Integer, nullable=False),
        sa.Column("color_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "color_role IN ('DOMINANT','SECONDARY','MOTIF','ACCENT')", name="ck_product_color_role"
        ),
        sa.CheckConstraint("color_rank BETWEEN 1 AND 4", name="ck_product_color_rank"),
        sa.CheckConstraint(
            "color_percentage IS NULL OR (color_percentage >= 0 AND color_percentage <= 100)",
            name="ck_product_color_percentage",
        ),
        sa.UniqueConstraint("product_id", "color_rank", name="uq_product_color_rank"),
        sa.UniqueConstraint("product_id", "color_role", name="uq_product_color_role"),
    )
    op.create_index("idx_product_colors_product_rank", "product_colors", ["product_id", "color_rank"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("top_n", sa.Integer, nullable=False, server_default="5"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("top_n > 0 AND top_n <= 20", name="ck_recommendation_top_n"),
    )

    op.create_table(
        "product_match_filters",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "seasonal_result_id",
            sa.Integer,
            sa.ForeignKey("seasonal_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "recommendation_id",
            sa.Integer,
            sa.ForeignKey("recommendations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("match_product_name", sa.String(255), nullable=False),
        sa.Column("amount_color", sa.Numeric(4, 0), nullable=False),
        sa.Column("dominant_roc", sa.Numeric(8, 6), nullable=True),
        sa.Column("secondary_roc", sa.Numeric(8, 6), nullable=True),
        sa.Column("motif_roc", sa.Numeric(8, 6), nullable=True),
        sa.Column("accent_roc", sa.Numeric(8, 6), nullable=True),
        sa.Column("total_roc_score", sa.Numeric(8, 6), nullable=False),
        sa.Column("suitability_label", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("total_roc_score >= 0 AND total_roc_score <= 1", name="ck_product_match_total_score"),
    )
    op.create_index(
        "idx_product_match_recommendation",
        "product_match_filters",
        ["recommendation_id", "total_roc_score"],
    )

    op.create_table(
        "recommendation_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "recommendation_id",
            sa.Integer,
            sa.ForeignKey("recommendations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column(
            "product_match_filter_id",
            sa.Integer,
            sa.ForeignKey("product_match_filters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rank_number", sa.Integer, nullable=False),
        sa.Column("product_score", sa.Numeric(8, 6), nullable=False),
        sa.Column("product_rank_label", sa.String(50), nullable=True),
        sa.Column("price_snapshot", sa.Numeric(12, 2), nullable=False),
        sa.Column("rating_snapshot", sa.Numeric(3, 2), nullable=True),
        sa.Column("stock_snapshot", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("rank_number > 0", name="ck_recommendation_item_rank"),
        sa.CheckConstraint("product_score >= 0 AND product_score <= 1", name="ck_recommendation_item_score"),
        sa.UniqueConstraint("recommendation_id", "rank_number", name="uq_recommendation_item_rank"),
        sa.UniqueConstraint("recommendation_id", "product_id", name="uq_recommendation_item_product"),
    )
    op.create_index(
        "idx_recommendation_items_rank", "recommendation_items", ["recommendation_id", "rank_number"]
    )

    op.create_table(
        "color_match_scores",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "seasonal_result_id",
            sa.Integer,
            sa.ForeignKey("seasonal_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_color_id",
            sa.Integer,
            sa.ForeignKey("product_colors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("color_id", sa.Integer, sa.ForeignKey("colors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("match_color_name", sa.String(100), nullable=False),
        sa.Column("hex_code", sa.String(7), nullable=False),
        sa.Column("ct", sa.Numeric(8, 6), nullable=False),
        sa.Column("cb", sa.Numeric(8, 6), nullable=False),
        sa.Column("suitable_score_color", sa.Numeric(8, 6), nullable=False),
        sa.Column("suitability_label", sa.String(30), nullable=False),
        sa.Column("ct_membership", sa.JSON, nullable=False),
        sa.Column("cb_membership", sa.JSON, nullable=False),
        sa.Column("fired_rules", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "suitable_score_color >= 0 AND suitable_score_color <= 1",
            name="ck_color_match_score_range",
        ),
    )
    op.create_index("idx_color_match_seasonal", "color_match_scores", ["seasonal_result_id"])

    op.create_table(
        "aiml_categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pattern", sa.String(150), nullable=False),
        sa.Column("topic", sa.String(150), nullable=True),
        sa.Column("that_pattern", sa.String(150), nullable=True),
        sa.Column("template", sa.Text, nullable=False),
        sa.Column("quick_replies", sa.JSON, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_aiml_lookup", "aiml_categories", ["pattern", "topic", "that_pattern", "is_active"]
    )

    op.create_table(
        "education_topics",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "education_contents",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "topic_id",
            sa.Integer,
            sa.ForeignKey("education_topics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("source_note", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "chat_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("sender", sa.String(20), nullable=False),
        sa.Column("education", sa.String(100), nullable=True),
        sa.Column(
            "aiml_category_id",
            sa.Integer,
            sa.ForeignKey("aiml_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "education_topic_id",
            sa.Integer,
            sa.ForeignKey("education_topics.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("sender IN ('BUYER','BOT','SYSTEM')", name="ck_chat_log_sender"),
    )
    op.create_index("idx_chat_logs_session_created", "chat_logs", ["session_id", "created_at"])

    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("is_skipped", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("rating IS NULL OR (rating BETWEEN 1 AND 5)", name="ck_feedback_rating"),
        sa.UniqueConstraint("session_id", name="uq_feedback_session"),
    )


def downgrade() -> None:
    op.drop_table("feedbacks")
    op.drop_index("idx_chat_logs_session_created", table_name="chat_logs")
    op.drop_table("chat_logs")
    op.drop_table("education_contents")
    op.drop_table("education_topics")
    op.drop_index("idx_aiml_lookup", table_name="aiml_categories")
    op.drop_table("aiml_categories")
    op.drop_index("idx_color_match_seasonal", table_name="color_match_scores")
    op.drop_table("color_match_scores")
    op.drop_index("idx_recommendation_items_rank", table_name="recommendation_items")
    op.drop_table("recommendation_items")
    op.drop_index("idx_product_match_recommendation", table_name="product_match_filters")
    op.drop_table("product_match_filters")
    op.drop_table("recommendations")
    op.drop_index("idx_product_colors_product_rank", table_name="product_colors")
    op.drop_table("product_colors")
    op.drop_table("colors")
    op.drop_index("idx_products_available", table_name="products")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("seasonal_results")
    op.drop_table("skin_characteristics")
    op.drop_index("idx_sessions_state", table_name="sessions")
    op.drop_index("idx_sessions_user_created", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_users_fingerprint", table_name="users")
    op.drop_table("users")
