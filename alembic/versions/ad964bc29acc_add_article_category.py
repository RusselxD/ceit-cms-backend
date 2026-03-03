"""add_article_category

Revision ID: ad964bc29acc
Revises: 8b1e2d9f4a10
Create Date: 2026-03-03 11:01:07.816642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad964bc29acc'
down_revision: Union[str, None] = '8b1e2d9f4a10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    article_category_enum = sa.Enum(
        "ANNOUNCEMENTS",
        "ACHIEVEMENTS",
        "EVENTS",
        "PARTNERSHIPS",
        name="articlecategory",
    )
    article_category_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "articles",
        sa.Column(
            "category",
            article_category_enum,
            nullable=False,
            server_default="ANNOUNCEMENTS",
        ),
    )

    op.execute(sa.text("UPDATE articles SET category = 'ANNOUNCEMENTS' WHERE category IS NULL"))

    op.alter_column("articles", "category", server_default=None)


def downgrade() -> None:
    op.drop_column("articles", "category")
    article_category_enum = sa.Enum(
        "ANNOUNCEMENTS",
        "ACHIEVEMENTS",
        "EVENTS",
        "PARTNERSHIPS",
        name="articlecategory",
    )
    article_category_enum.drop(op.get_bind(), checkfirst=True)
