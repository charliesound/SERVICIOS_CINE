"""add organization_id to delivery and review

Revision ID: 20260418_000002
Revises: 20260418_000001
Create Date: 2026-04-18 19:16:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260418_000002"
down_revision = "20260418_000001"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # 1. Deliverables
    if not _column_exists("deliverables", "organization_id"):
        op.add_column(
            "deliverables",
            sa.Column("organization_id", sa.String(length=36), nullable=True)
        )
        op.create_index(
            "ix_deliverables_organization_id",
            "deliverables",
            ["organization_id"],
            unique=False
        )

    # 2. Reviews
    if not _column_exists("reviews", "organization_id"):
        op.add_column(
            "reviews",
            sa.Column("organization_id", sa.String(length=36), nullable=True)
        )
        op.create_index(
            "ix_reviews_organization_id",
            "reviews",
            ["organization_id"],
            unique=False
        )

    # 3. Approval Decisions
    if not _column_exists("approval_decisions", "organization_id"):
        op.add_column(
            "approval_decisions",
            sa.Column("organization_id", sa.String(length=36), nullable=True)
        )
        op.create_index(
            "ix_approval_decisions_organization_id",
            "approval_decisions",
            ["organization_id"],
            unique=False
        )

    # 4. Review Comments
    if not _column_exists("review_comments", "organization_id"):
        op.add_column(
            "review_comments",
            sa.Column("organization_id", sa.String(length=36), nullable=True)
        )
        op.create_index(
            "ix_review_comments_organization_id",
            "review_comments",
            ["organization_id"],
            unique=False
        )


def downgrade() -> None:
    # 1. Deliverables
    op.drop_index("ix_deliverables_organization_id", table_name="deliverables")
    op.drop_column("deliverables", "organization_id")

    # 2. Reviews
    op.drop_index("ix_reviews_organization_id", table_name="reviews")
    op.drop_column("reviews", "organization_id")

    # 3. Approval Decisions
    op.drop_index("ix_approval_decisions_organization_id", table_name="approval_decisions")
    op.drop_column("approval_decisions", "organization_id")

    # 4. Review Comments
    op.drop_index("ix_review_comments_organization_id", table_name="review_comments")
    op.drop_column("review_comments", "organization_id")
