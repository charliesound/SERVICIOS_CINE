"""Add opportunity tracking, checklist, and notification tables

Revision ID: 1dda80b052e5
Revises: 20260422_000007
Create Date: 2026-04-22 22:57:58.371035
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dda80b052e5'
down_revision = '20260422_000007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create opportunity_trackings table
    op.create_table(
        'opportunity_trackings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), nullable=False, index=True),
        sa.Column('organization_id', sa.String(36), nullable=False, index=True),
        sa.Column('funding_call_id', sa.String(36), sa.ForeignKey('funding_calls.id'), nullable=False),
        sa.Column('project_funding_match_id', sa.String(36), sa.ForeignKey('project_funding_matches.id'), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='interested'),
        sa.Column('priority', sa.String(10), nullable=True),
        sa.Column('owner_user_id', sa.String(36), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_ot_project_id', 'opportunity_trackings', ['project_id'])
    op.create_index('ix_ot_org_project', 'opportunity_trackings', ['organization_id', 'project_id'])
    op.create_index('ix_ot_funding_call', 'opportunity_trackings', ['funding_call_id'])
    op.create_index('ix_ot_status', 'opportunity_trackings', ['status'])

    # Create requirement_checklist_items table
    op.create_table(
        'requirement_checklist_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tracking_id', sa.String(36), sa.ForeignKey('opportunity_trackings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False, index=True),
        sa.Column('label', sa.String(255), nullable=False),
        sa.Column('requirement_type', sa.String(50), nullable=True),
        sa.Column('is_fulfilled', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('auto_detected', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('linked_project_document_id', sa.String(36), nullable=True),
        sa.Column('evidence_excerpt', sa.Text, nullable=True),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_rci_tracking_id', 'requirement_checklist_items', ['tracking_id'])
    op.create_index('ix_rci_org_id', 'requirement_checklist_items', ['organization_id'])
    op.create_index('ix_rci_fulfilled', 'requirement_checklist_items', ['is_fulfilled'])

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False, index=True),
        sa.Column('project_id', sa.String(36), nullable=False, index=True),
        sa.Column('tracking_id', sa.String(36), sa.ForeignKey('opportunity_trackings.id', ondelete='SET NULL'), nullable=True),
        sa.Column('level', sa.String(10), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text, nullable=True),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_notif_org_id', 'notifications', ['organization_id'])
    op.create_index('ix_notif_project_id', 'notifications', ['project_id'])
    op.create_index('ix_notif_tracking_id', 'notifications', ['tracking_id'])
    op.create_index('ix_notif_level', 'notifications', ['level'])
    op.create_index('ix_notif_is_read', 'notifications', ['is_read'])


def downgrade() -> None:
    # Drop tables in reverse order to avoid foreign key constraints
    op.drop_table('notifications')
    op.drop_table('requirement_checklist_items')
    op.drop_table('opportunity_trackings')


def downgrade() -> None:
    pass
