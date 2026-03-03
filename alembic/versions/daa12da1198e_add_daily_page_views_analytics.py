"""add_daily_page_views_analytics

Revision ID: daa12da1198e
Revises: c8ab6cf878a8
Create Date: 2026-03-03 10:46:38.897088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daa12da1198e'
down_revision: Union[str, None] = 'c8ab6cf878a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_page_views",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day"),
    )


def downgrade() -> None:
    op.drop_table("daily_page_views")
