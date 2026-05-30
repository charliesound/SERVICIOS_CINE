"""merge heads

Revision ID: c0e56e33e9ee
Revises: 20260519_000001, 20260521_000001
Create Date: 2026-05-30 16:37:32.875644
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa



revision = 'c0e56e33e9ee'
down_revision = ('20260519_000001', '20260521_000001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
