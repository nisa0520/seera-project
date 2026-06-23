"""add anchor_config to product_visual_assets for photo-based virtual try-on

Revision ID: 0004_visual_asset_anchor
Revises: 0003_image_feature
Create Date: 2026-06-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_visual_asset_anchor"
down_revision: Union[str, None] = "0003_image_feature"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("product_visual_assets") as batch:
        batch.add_column(sa.Column("anchor_config", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("product_visual_assets") as batch:
        batch.drop_column("anchor_config")
