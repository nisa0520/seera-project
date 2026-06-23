"""add realistic virtual try-on (CatVTON) tables: assets, person images, jobs, feedback

Revision ID: 0005_vton
Revises: 0004_visual_asset_anchor
Create Date: 2026-06-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_vton"
down_revision: Union[str, None] = "0004_visual_asset_anchor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
        sa.CheckConstraint("vton_status IN ('READY','PENDING','NOT_SUPPORTED')", name="ck_vton_asset_status"),
        sa.CheckConstraint(
            "garment_category IS NULL OR garment_category IN ('upper','lower','dress','outer')",
            name="ck_vton_garment_category",
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


def downgrade() -> None:
    op.drop_table("vton_feedback")
    op.drop_index("idx_vton_jobs_status", table_name="vton_jobs")
    op.drop_index("idx_vton_jobs_session", table_name="vton_jobs")
    op.drop_table("vton_jobs")
    op.drop_index("idx_vton_person_session", table_name="vton_person_images")
    op.drop_table("vton_person_images")
    op.drop_index("idx_vton_assets_product", table_name="product_vton_assets")
    op.drop_table("product_vton_assets")
