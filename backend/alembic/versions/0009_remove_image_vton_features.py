"""remove image-based skin analysis & virtual try-on (VTON) tables/states

Revision ID: 0009_remove_image_vton
Revises: 0008_fuzzy_roc
Create Date: 2026-07-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0009_remove_image_vton"
down_revision: Union[str, None] = "0008_fuzzy_roc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CORE_STATES = (
    "'WAITING_GENDER','WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION',"
    "'WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION'"
)
ALL_STATES = (
    f"{CORE_STATES},"
    "'WAITING_INPUT_METHOD','WAITING_IMAGE_CAPTURE','PROCESSING_IMAGE_ANALYSIS',"
    "'WAITING_IMAGE_RESULT_CONFIRMATION','SHOWING_VISUAL_RECOMMENDATION','WAITING_BACKGROUND_SELECTION'"
)


def upgrade() -> None:
    # Remap any lingering sessions still parked in a removed image/vton state
    # before tightening the CHECK constraint, so the ALTER doesn't fail on live rows.
    op.execute(
        "UPDATE sessions SET conversation_state = 'WAITING_SKIN_TONE' "
        "WHERE conversation_state IN ("
        "'WAITING_INPUT_METHOD','WAITING_IMAGE_CAPTURE','PROCESSING_IMAGE_ANALYSIS',"
        "'WAITING_IMAGE_RESULT_CONFIRMATION','WAITING_BACKGROUND_SELECTION')"
    )
    op.execute(
        "UPDATE sessions SET conversation_state = 'SHOWING_RECOMMENDATION' "
        "WHERE conversation_state = 'SHOWING_VISUAL_RECOMMENDATION'"
    )

    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            f"conversation_state IN ({CORE_STATES})",
        )

    # Drop children before parents to satisfy FK constraints.
    op.drop_table("vton_feedback")
    op.drop_table("vton_jobs")
    op.drop_table("vton_person_images")
    op.drop_table("product_vton_assets")
    op.drop_table("visual_match_sessions")
    op.drop_table("product_visual_assets")
    op.drop_table("background_presets")
    op.drop_table("image_analysis_sessions")


def downgrade() -> None:
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
        "product_visual_assets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_url", sa.String(500), nullable=False),
        sa.Column("asset_type", sa.String(30), nullable=False, server_default="IMAGE"),
        sa.Column("dominant_color_hex", sa.String(9), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("anchor_config", sa.JSON(), nullable=True),
        sa.CheckConstraint("asset_type IN ('IMAGE','SWATCH','TEMPLATE')", name="ck_visual_asset_type"),
    )
    op.create_index(
        "idx_visual_assets_product", "product_visual_assets", ["product_id", "is_active"]
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
        "product_vton_assets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("garment_vton_image_url", sa.String(500), nullable=True),
        sa.Column("garment_category", sa.String(30), nullable=True),
        sa.Column("view_angle", sa.String(30), nullable=True),
        sa.Column("background_status", sa.String(30), nullable=True),
        sa.Column("asset_quality_status", sa.String(30), nullable=True),
        sa.Column("vton_status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("model_compatibility", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("garment_caption", sa.Text(), nullable=True),
        sa.Column("vton_asset_tier", sa.String(30), nullable=False, server_default="vton_not_supported"),
        sa.Column("tryon_quality_mode", sa.String(20), nullable=True),
        sa.Column("vton_asset_quality_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("asset_validation_notes", sa.Text(), nullable=True),
        sa.CheckConstraint("vton_status IN ('READY','PENDING','NOT_SUPPORTED')", name="ck_vton_asset_status"),
        sa.CheckConstraint(
            "garment_category IS NULL OR garment_category IN ('upper','lower','dress','outer')",
            name="ck_vton_garment_category",
        ),
        sa.CheckConstraint(
            "vton_asset_tier IN ('vton_ready','vton_experimental','vton_limited','vton_not_supported')",
            name="ck_vton_asset_tier",
        ),
    )
    op.create_index("idx_vton_assets_product", "product_vton_assets", ["product_id", "vton_status"])

    op.create_table(
        "vton_person_images",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("storage_token", sa.String(64), nullable=False, unique=True),
        sa.Column("image_source_type", sa.String(20), nullable=False, server_default="UPLOAD"),
        sa.Column("image_width", sa.Integer(), nullable=True),
        sa.Column("image_height", sa.Integer(), nullable=True),
        sa.Column("quality_status", sa.String(50), nullable=False),
        sa.Column("face_detected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("body_detected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("mask_status", sa.String(30), nullable=True),
        sa.Column("mask_token", sa.String(64), nullable=True),
        sa.Column("consent_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("image_source_type IN ('CAMERA','UPLOAD')", name="ck_vton_person_source"),
    )
    op.create_index("idx_vton_person_session", "vton_person_images", ["session_id", "created_at"])

    op.create_table(
        "vton_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("person_image_id", sa.Integer(), sa.ForeignKey("vton_person_images.id", ondelete="CASCADE"), nullable=False),
        sa.Column("background_id", sa.Integer(), sa.ForeignKey("background_presets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("garment_vton_image_url", sa.String(500), nullable=False),
        sa.Column("mask_token", sa.String(64), nullable=True),
        sa.Column("model_name", sa.String(50), nullable=False, server_default="CatVTON"),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("inference_resolution", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="QUEUED"),
        sa.Column("output_token", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("garment_vton_asset_id", sa.Integer(), sa.ForeignKey("product_vton_assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("selected_variant_id", sa.Integer(), sa.ForeignKey("colors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("garment_caption", sa.Text(), nullable=True),
        sa.Column("inference_parameters", sa.JSON(), nullable=True),
        sa.Column("vton_asset_tier", sa.String(30), nullable=True),
        sa.Column("tryon_quality_mode", sa.String(20), nullable=True),
        sa.CheckConstraint(
            "status IN ('QUEUED','PROCESSING','SUCCESS','FAILED','EXPIRED')",
            name="ck_vton_job_status",
        ),
    )
    op.create_index("idx_vton_jobs_session", "vton_jobs", ["session_id", "created_at"])
    op.create_index("idx_vton_jobs_status", "vton_jobs", ["status", "created_at"])

    op.create_table(
        "vton_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vton_job_id", sa.Integer(), sa.ForeignKey("vton_jobs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("visual_quality_rating", sa.Integer(), nullable=True),
        sa.Column("proportion_rating", sa.Integer(), nullable=True),
        sa.Column("garment_similarity_rating", sa.Integer(), nullable=True),
        sa.Column("satisfaction_rating", sa.Integer(), nullable=True),
        sa.Column("comment", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("visual_quality_rating IS NULL OR (visual_quality_rating BETWEEN 1 AND 5)", name="ck_vton_fb_visual"),
        sa.CheckConstraint("proportion_rating IS NULL OR (proportion_rating BETWEEN 1 AND 5)", name="ck_vton_fb_proportion"),
        sa.CheckConstraint("garment_similarity_rating IS NULL OR (garment_similarity_rating BETWEEN 1 AND 5)", name="ck_vton_fb_similarity"),
        sa.CheckConstraint("satisfaction_rating IS NULL OR (satisfaction_rating BETWEEN 1 AND 5)", name="ck_vton_fb_satisfaction"),
    )

    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            f"conversation_state IN ({ALL_STATES})",
        )
