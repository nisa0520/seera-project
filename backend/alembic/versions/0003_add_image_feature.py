"""add image-based skin analysis & visual matching tables + image conversation states

Revision ID: 0003_image_feature
Revises: 0002_gender_preferences
Create Date: 2026-06-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_image_feature"
down_revision: Union[str, None] = "0002_gender_preferences"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_STATES = (
    "'WAITING_GENDER','WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION',"
    "'WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION'"
)
IMAGE_STATES = (
    "'WAITING_INPUT_METHOD','WAITING_IMAGE_CAPTURE','PROCESSING_IMAGE_ANALYSIS',"
    "'WAITING_IMAGE_RESULT_CONFIRMATION','SHOWING_VISUAL_RECOMMENDATION','WAITING_BACKGROUND_SELECTION'"
)


def upgrade() -> None:
    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            f"conversation_state IN ({LEGACY_STATES},{IMAGE_STATES})",
        )

    op.create_table(
        "image_analysis_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_source_type", sa.String(20), nullable=False, server_default="UPLOAD"),
        sa.Column("face_detected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("face_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("image_quality_status", sa.String(50), nullable=False),
        sa.Column("skin_tone_detected", sa.String(10), nullable=True),
        sa.Column("skin_tone_value", sa.Numeric(4, 2), nullable=True),
        sa.Column("undertone_detected", sa.String(20), nullable=True),
        sa.Column("undertone_value", sa.Numeric(4, 2), nullable=True),
        sa.Column("skin_tone_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("undertone_confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("sample_rgb", sa.String(30), nullable=True),
        sa.Column("sample_hsv", sa.String(30), nullable=True),
        sa.Column("is_confirmed_by_user", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("image_source_type IN ('CAMERA','UPLOAD')", name="ck_image_source_type"),
    )
    op.create_index(
        "idx_image_analysis_session", "image_analysis_sessions", ["session_id", "created_at"]
    )

    op.create_table(
        "background_presets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("background_name", sa.String(100), nullable=False),
        sa.Column("background_category", sa.String(50), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "visual_match_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), sa.ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("selected_product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("selected_background_id", sa.Integer(), sa.ForeignKey("background_presets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("preview_config", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_visual_match_session", "visual_match_sessions", ["session_id", "created_at"]
    )

    op.create_table(
        "product_visual_assets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_url", sa.String(500), nullable=False),
        sa.Column("asset_type", sa.String(30), nullable=False, server_default="IMAGE"),
        sa.Column("dominant_color_hex", sa.String(9), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("asset_type IN ('IMAGE','SWATCH','TEMPLATE')", name="ck_visual_asset_type"),
    )
    op.create_index(
        "idx_visual_assets_product", "product_visual_assets", ["product_id", "is_active"]
    )


def downgrade() -> None:
    op.drop_index("idx_visual_assets_product", table_name="product_visual_assets")
    op.drop_table("product_visual_assets")
    op.drop_index("idx_visual_match_session", table_name="visual_match_sessions")
    op.drop_table("visual_match_sessions")
    op.drop_table("background_presets")
    op.drop_index("idx_image_analysis_session", table_name="image_analysis_sessions")
    op.drop_table("image_analysis_sessions")

    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            f"conversation_state IN ({LEGACY_STATES})",
        )
