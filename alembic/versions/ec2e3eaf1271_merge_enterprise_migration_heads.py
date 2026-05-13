"""merge enterprise migration heads

Revision ID: ec2e3eaf1271
Revises: 0079ce20dc99, 1dda80b052e5, 6ba14a0d02b6
Create Date: 2026-05-12 21:42:02.024341
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa



revision = 'ec2e3eaf1271'
down_revision = ('0079ce20dc99', '1dda80b052e5', '6ba14a0d02b6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
