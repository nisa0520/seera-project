"""add IDM-VTON garment-fidelity traceability columns to vton_jobs

Revision ID: 0006_vton_idm
Revises: 0005_vton
Create Date: 2026-06-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_vton_idm"
down_revision: Union[str, None] = "0005_vton"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("vton_jobs") as batch:
        batch.add_column(sa.Column("garment_vton_asset_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("selected_variant_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("garment_caption", sa.Text(), nullable=True))
        batch.add_column(sa.Column("inference_parameters", sa.JSON(), nullable=True))
        batch.create_foreign_key(
            "fk_vton_jobs_garment_asset",
            "product_vton_assets",
            ["garment_vton_asset_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_foreign_key(
            "fk_vton_jobs_variant",
            "colors",
            ["selected_variant_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("vton_jobs") as batch:
        batch.drop_constraint("fk_vton_jobs_variant", type_="foreignkey")
        batch.drop_constraint("fk_vton_jobs_garment_asset", type_="foreignkey")
        batch.drop_column("inference_parameters")
        batch.drop_column("garment_caption")
        batch.drop_column("selected_variant_id")
        batch.drop_column("garment_vton_asset_id")
