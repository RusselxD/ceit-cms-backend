"""add_public_page_views_table

Revision ID: 8b1e2d9f4a10
Revises: daa12da1198e
Create Date: 2026-03-03 11:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b1e2d9f4a10'
down_revision: Union[str, None] = 'daa12da1198e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "public_page_views",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day", "path"),
    )


def downgrade() -> None:
    op.drop_table("public_page_views")
