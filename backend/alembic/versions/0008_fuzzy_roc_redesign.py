"""Align schema with revised Fuzzy Logic (Layer 1 non-singleton) & ROC design.

- seasonal_results: drop y1_continuous (skalar linear yang digantikan vektor
  musim non-singleton, lihat Bab IV.2.7.3 Poin 3-4).
- sessions: drop y1_continuous (turunan dari kolom di atas).
- product_colors: batasi color_rank ke 1..3 dan color_role ke
  DOMINANT/SECONDARY/ACCENT (hapus MOTIF) sesuai pembatasan n<=3 (rule of
  three, Subbab IV.2.7.5).
- product_match_filters: ganti 4 kolom role tetap (dominant_roc/
  secondary_roc/motif_roc/accent_roc) dengan bobot per-peringkat generik
  (color_weight_1..3) + weight_mode (ROC/PERCENTAGE, Mode 1/Mode 2).

Revision ID: 0008_fuzzy_roc
Revises: 0007_vton_tier
Create Date: 2026-07-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_fuzzy_roc"
down_revision: Union[str, None] = "0007_vton_tier"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- seasonal_results: buang artefak Y1 skalar (linear) ---
    with op.batch_alter_table("seasonal_results") as batch:
        batch.drop_constraint("ck_y1_range", type_="check")
        batch.drop_column("y1_continuous")

    # --- sessions: kolom turunan Y1 ---
    with op.batch_alter_table("sessions") as batch:
        batch.drop_column("y1_continuous")

    # --- product_colors: n<=3, hapus role MOTIF ---
    # Data lama hasil generator (maks 4 warna) dipangkas ke 3 warna teratas
    # per produk; seed ulang (run_seed.py) akan menormalkan ulang persentase.
    op.execute("DELETE FROM product_colors WHERE color_rank > 3")
    with op.batch_alter_table("product_colors") as batch:
        batch.drop_constraint("ck_product_color_role", type_="check")
        batch.drop_constraint("ck_product_color_rank", type_="check")
        batch.create_check_constraint(
            "ck_product_color_role", "color_role IN ('DOMINANT','SECONDARY','ACCENT')"
        )
        batch.create_check_constraint("ck_product_color_rank", "color_rank BETWEEN 1 AND 3")

    # --- product_match_filters: role tetap -> bobot per-peringkat generik ---
    with op.batch_alter_table("product_match_filters") as batch:
        batch.add_column(
            sa.Column("weight_mode", sa.String(20), nullable=False, server_default="ROC")
        )
        batch.add_column(sa.Column("color_weight_1", sa.Numeric(8, 6), nullable=True))
        batch.add_column(sa.Column("color_weight_2", sa.Numeric(8, 6), nullable=True))
        batch.add_column(sa.Column("color_weight_3", sa.Numeric(8, 6), nullable=True))
        batch.create_check_constraint(
            "ck_product_match_weight_mode", "weight_mode IN ('ROC','PERCENTAGE')"
        )

    op.execute(
        "UPDATE product_match_filters SET color_weight_1 = dominant_roc, "
        "color_weight_2 = secondary_roc, color_weight_3 = accent_roc"
    )

    with op.batch_alter_table("product_match_filters") as batch:
        batch.drop_column("dominant_roc")
        batch.drop_column("secondary_roc")
        batch.drop_column("motif_roc")
        batch.drop_column("accent_roc")


def downgrade() -> None:
    with op.batch_alter_table("product_match_filters") as batch:
        batch.add_column(sa.Column("dominant_roc", sa.Numeric(8, 6), nullable=True))
        batch.add_column(sa.Column("secondary_roc", sa.Numeric(8, 6), nullable=True))
        batch.add_column(sa.Column("motif_roc", sa.Numeric(8, 6), nullable=True))
        batch.add_column(sa.Column("accent_roc", sa.Numeric(8, 6), nullable=True))

    op.execute(
        "UPDATE product_match_filters SET dominant_roc = color_weight_1, "
        "secondary_roc = color_weight_2, accent_roc = color_weight_3"
    )

    with op.batch_alter_table("product_match_filters") as batch:
        batch.drop_constraint("ck_product_match_weight_mode", type_="check")
        batch.drop_column("color_weight_1")
        batch.drop_column("color_weight_2")
        batch.drop_column("color_weight_3")
        batch.drop_column("weight_mode")

    with op.batch_alter_table("product_colors") as batch:
        batch.drop_constraint("ck_product_color_rank", type_="check")
        batch.drop_constraint("ck_product_color_role", type_="check")
        batch.create_check_constraint("ck_product_color_rank", "color_rank BETWEEN 1 AND 4")
        batch.create_check_constraint(
            "ck_product_color_role", "color_role IN ('DOMINANT','SECONDARY','MOTIF','ACCENT')"
        )

    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("y1_continuous", sa.Numeric(8, 6), nullable=True))

    with op.batch_alter_table("seasonal_results") as batch:
        batch.add_column(sa.Column("y1_continuous", sa.Numeric(8, 6), nullable=True))
        batch.create_check_constraint("ck_y1_range", "y1_continuous >= 0 AND y1_continuous <= 3")
