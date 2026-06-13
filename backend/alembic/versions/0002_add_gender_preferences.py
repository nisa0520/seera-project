"""add gender preferences for sessions, users, and products

Revision ID: 0002_gender_preferences
Revises: 0001_initial
Create Date: 2026-06-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_gender_preferences"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("gender", sa.String(30), nullable=True))
        batch.create_check_constraint(
            "ck_user_gender",
            "gender IS NULL OR gender IN ('MALE','FEMALE','PREFER_NOT_TO_SAY')",
        )

    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("gender_snapshot", sa.String(30), nullable=True))
        batch.alter_column(
            "conversation_state",
            existing_type=sa.String(50),
            server_default="WAITING_GENDER",
        )
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            "conversation_state IN ('WAITING_GENDER','WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
        )
        batch.create_check_constraint(
            "ck_session_gender_snapshot",
            "gender_snapshot IS NULL OR gender_snapshot IN ('MALE','FEMALE','PREFER_NOT_TO_SAY')",
        )

    with op.batch_alter_table("products") as batch:
        batch.add_column(
            sa.Column(
                "target_gender",
                sa.String(30),
                nullable=False,
                server_default="UNISEX",
            )
        )
        batch.create_check_constraint(
            "ck_product_target_gender",
            "target_gender IN ('MALE','FEMALE','UNISEX')",
        )

    op.create_index(
        "idx_products_target_gender",
        "products",
        ["target_gender", "is_active", "stock"],
    )


def downgrade() -> None:
    op.drop_index("idx_products_target_gender", table_name="products")

    with op.batch_alter_table("products") as batch:
        batch.drop_constraint("ck_product_target_gender", type_="check")
        batch.drop_column("target_gender")

    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("ck_session_gender_snapshot", type_="check")
        batch.drop_constraint("ck_conversation_state", type_="check")
        batch.create_check_constraint(
            "ck_conversation_state",
            "conversation_state IN ('WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
        )
        batch.alter_column(
            "conversation_state",
            existing_type=sa.String(50),
            server_default="WAITING_SKIN_TONE",
        )
        batch.drop_column("gender_snapshot")

    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("ck_user_gender", type_="check")
        batch.drop_column("gender")
