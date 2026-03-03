"""add_article_like_count

Revision ID: 979e890cd7e0
Revises: ad964bc29acc
Create Date: 2026-03-03 11:12:07.122275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '979e890cd7e0'
down_revision: Union[str, None] = 'ad964bc29acc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("articles", "like_count", server_default=None)


def downgrade() -> None:
    op.drop_column("articles", "like_count")
