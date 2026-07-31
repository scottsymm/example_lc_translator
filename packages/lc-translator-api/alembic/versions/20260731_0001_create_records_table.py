"""create records table

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260731_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mt700_input", sa.Text(), nullable=True),
        sa.Column("generated_seed", sa.Integer(), nullable=True),
        sa.Column("generated_strict", sa.Boolean(), nullable=True),
        sa.Column("mx_xml", sa.Text(), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column("lc_model", sa.JSON(), nullable=True),
    )
    op.create_index("ix_records_created_at", "records", ["created_at"])
    op.create_index("ix_records_source_type", "records", ["source_type"])


def downgrade() -> None:
    op.drop_index("ix_records_source_type", table_name="records")
    op.drop_index("ix_records_created_at", table_name="records")
    op.drop_table("records")
