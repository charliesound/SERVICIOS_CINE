"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-12
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "budget_estimates",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("budget_level", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("total_min", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_estimated", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_max", sa.Float, nullable=False, server_default="0"),
        sa.Column("contingency_percent", sa.Float, nullable=False, server_default="10"),
        sa.Column("assumptions_json", sa.JSON, nullable=True),
        sa.Column("role_summaries_json", sa.JSON, nullable=True),
        sa.Column("created_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_table(
        "budget_line_items",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("budget_estimate_id", sa.String(64), nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False, server_default="1"),
        sa.Column("unit_cost_min", sa.Float, nullable=False, server_default="0"),
        sa.Column("unit_cost_estimated", sa.Float, nullable=False, server_default="0"),
        sa.Column("unit_cost_max", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_min", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_estimated", sa.Float, nullable=False, server_default="0"),
        sa.Column("total_max", sa.Float, nullable=False, server_default="0"),
        sa.Column("source", sa.String(50), nullable=False, server_default="default_rule"),
        sa.Column("confidence", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("notes", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("budget_line_items")
    op.drop_table("budget_estimates")
