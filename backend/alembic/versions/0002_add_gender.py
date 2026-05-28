"""add gender to sessions and skin_characteristics

Revision ID: 0002_add_gender
Revises: 0001_initial
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_gender"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    ...

def downgrade() -> None:
    ...