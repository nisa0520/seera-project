"""add VTON asset eligibility tier columns to product_vton_assets

Revision ID: 0007_vton_tier
Revises: 0006_vton_idm
Create Date: 2026-06-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_vton_tier"
down_revision: Union[str, None] = "0006_vton_idm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("product_vton_assets") as batch:
        batch.add_column(sa.Column("garment_caption", sa.Text(), nullable=True))
        batch.add_column(
            sa.Column(
                "vton_asset_tier",
                sa.String(30),
                nullable=False,
                server_default="vton_not_supported",
            )
        )
        batch.add_column(sa.Column("tryon_quality_mode", sa.String(20), nullable=True))
        batch.add_column(sa.Column("vton_asset_quality_score", sa.Numeric(4, 3), nullable=True))
        batch.add_column(sa.Column("asset_validation_notes", sa.Text(), nullable=True))
        batch.create_check_constraint(
            "ck_vton_asset_tier",
            "vton_asset_tier IN ('vton_ready','vton_experimental','vton_limited','vton_not_supported')",
        )

    with op.batch_alter_table("vton_jobs") as batch:
        batch.add_column(sa.Column("vton_asset_tier", sa.String(30), nullable=True))
        batch.add_column(sa.Column("tryon_quality_mode", sa.String(20), nullable=True))

    # Migrasi data: petakan vton_status legacy -> tier baru.
    op.execute(
        "UPDATE product_vton_assets SET vton_asset_tier='vton_ready', "
        "tryon_quality_mode='realistic' WHERE vton_status='READY'"
    )
    op.execute(
        "UPDATE product_vton_assets SET vton_asset_tier='vton_experimental', "
        "tryon_quality_mode='experimental' WHERE vton_status='PENDING'"
    )
    op.execute(
        "UPDATE product_vton_assets SET vton_asset_tier='vton_not_supported', "
        "tryon_quality_mode='blocked' WHERE vton_status='NOT_SUPPORTED'"
    )


def downgrade() -> None:
    with op.batch_alter_table("vton_jobs") as batch:
        batch.drop_column("tryon_quality_mode")
        batch.drop_column("vton_asset_tier")

    with op.batch_alter_table("product_vton_assets") as batch:
        batch.drop_constraint("ck_vton_asset_tier", type_="check")
        batch.drop_column("asset_validation_notes")
        batch.drop_column("vton_asset_quality_score")
        batch.drop_column("tryon_quality_mode")
        batch.drop_column("vton_asset_tier")
        batch.drop_column("garment_caption")
