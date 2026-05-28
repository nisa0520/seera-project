"""fix ck_conversation_state constraint

Revision ID: 0003_fix_constraint
Revises: 0002_add_gender
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0003_fix_constraint"
down_revision: Union[str, None] = "0002_add_gender"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_constraint("ck_conversation_state", "sessions", type_="check")
    op.create_check_constraint(
        "ck_conversation_state",
        "sessions",
        "conversation_state IN ('WAITING_GENDER','WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
    )

def downgrade() -> None:
    op.drop_constraint("ck_conversation_state", "sessions", type_="check")
    op.create_check_constraint(
        "ck_conversation_state",
        "sessions",
        "conversation_state IN ('WAITING_SKIN_TONE','WAITING_UNDERTONE','WAITING_CONFIRMATION','WAITING_CHANGE_SELECTION','SHOWING_RECOMMENDATION','EDUCATION')",
    )