"""initial — all tables

Revision ID: 0001
Revises:
Create Date: 2026-03-29 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── permissions ──
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_permissions_id", "permissions", ["id"])

    # ── roles ──
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_id", "roles", ["id"])

    # ── role_permissions ──
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # ── users ──
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # ── articles ──
    op.create_table(
        "articles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("image_path", sa.String(255), nullable=True),
        sa.Column("image_alt_text", sa.String(255), nullable=True),
        sa.Column("category", sa.Enum("ANNOUNCEMENTS", "ACHIEVEMENTS", "EVENTS", "PARTNERSHIPS", name="articlecategory"), nullable=False, server_default="ANNOUNCEMENTS"),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("DRAFT", "PENDING", "APPROVED", "ARCHIVED", name="articlestatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_articles_id", "articles", ["id"])

    # ── daily_page_views ──
    op.create_table(
        "daily_page_views",
        sa.Column("day", sa.Date(), primary_key=True),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
    )

    # ── public_page_views ──
    op.create_table(
        "public_page_views",
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("path", sa.String(255), nullable=False),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("day", "path"),
    )

    # ── newsletters ──
    op.create_table(
        "newsletters",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("volume", sa.String(50), nullable=False),
        sa.Column("issue", sa.String(50), nullable=False),
        sa.Column("month_year", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("highlights", sa.Text(), nullable=True),
        sa.Column("tags", sa.String(500), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cover_url", sa.String(500), nullable=True),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("flipbook_url", sa.String(500), nullable=True),
        sa.Column("is_latest", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
    )

    # ── site_content ──
    op.create_table(
        "site_content",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("page", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("content", JSONB, nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(now() AT TIME ZONE 'UTC')"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("site_content")
    op.drop_table("newsletters")
    op.drop_table("public_page_views")
    op.drop_table("daily_page_views")
    op.drop_index("ix_articles_id", table_name="articles")
    op.drop_table("articles")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_index("ix_roles_id", table_name="roles")
    op.drop_table("roles")
    op.drop_index("ix_permissions_id", table_name="permissions")
    op.drop_table("permissions")
    sa.Enum(name="articlestatus").drop(op.get_bind())
    sa.Enum(name="articlecategory").drop(op.get_bind())
