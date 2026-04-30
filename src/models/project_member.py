from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Index, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        Index("ix_project_member_project_id", "project_id"),
        Index("ix_project_member_user_id", "user_id"),
        Index("ix_project_member_project_user", "project_id", "user_id", unique=True),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    professional_role: Mapped[str] = mapped_column(
        String(30),
        default="viewer"
    )
    permissions_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    can_manage_permissions: Mapped[bool] = mapped_column(Boolean, default=False)
    can_manage_members: Mapped[bool] = mapped_column(Boolean, default=False)
    invited_by_user_id: Mapped[Optional[str]] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(
        String(20),
        default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


PROFESSIONAL_ROLES = [
    "owner",
    "producer",
    "executive_producer",
    "production_manager",
    "director",
    "editor",
    "sound",
    "dop",
    "script_supervisor",
    "viewer",
]

PROJECT_PERMISSIONS = [
    "project.view",
    "project.edit",
    "project.delete",
    "project.members.view",
    "project.members.invite",
    "project.members.edit",
    "project.members.remove",
    "project.permissions.manage",
    "project.permissions.delegate",
    "project.permissions.revoke_delegate",
    "script.view",
    "script.edit",
    "script.version.create",
    "script.version.activate",
    "storyboard.view",
    "storyboard.generate",
    "breakdown.view",
    "breakdown.edit",
    "budget.view",
    "budget.generate",
    "budget.edit",
    "funding.view",
    "funding.manage",
    "producer_pack.view",
    "producer_pack.generate",
    "distribution.view",
    "distribution.manage",
    "crm.view",
    "crm.manage",
    "media.scan",
    "media.view",
    "documents.ingest",
    "documents.approve",
    "reports.view",
    "reports.edit",
    "editorial.view",
    "editorial.reconcile",
    "editorial.score",
    "editorial.assembly",
    "davinci.export",
]

ROLE_DEFAULT_PERMISSIONS = {
    "owner": PROJECT_PERMISSIONS,
    "producer": [
        "project.view",
        "project.edit",
        "project.members.view",
        "project.members.invite",
        "project.members.edit",
        "project.members.remove",
        "project.permissions.manage",
        "project.permissions.delegate",
        "project.permissions.revoke_delegate",
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "breakdown.edit",
        "budget.view",
        "budget.generate",
        "budget.edit",
        "funding.view",
        "funding.manage",
        "producer_pack.view",
        "producer_pack.generate",
        "distribution.view",
        "distribution.manage",
        "crm.view",
        "crm.manage",
        "media.scan",
        "media.view",
        "documents.ingest",
        "documents.approve",
        "reports.view",
        "reports.edit",
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
        "davinci.export",
    ],
    "executive_producer": [
        "project.view",
        "project.edit",
        "project.members.view",
        "project.members.invite",
        "project.members.edit",
        "project.permissions.manage",
        "project.permissions.delegate",
        "script.view",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "budget.view",
        "budget.generate",
        "funding.view",
        "producer_pack.view",
        "producer_pack.generate",
        "distribution.view",
        "media.view",
        "reports.view",
        "editorial.view",
        "davinci.export",
    ],
    "production_manager": [
        "project.view",
        "project.members.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "breakdown.edit",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.scan",
        "media.view",
        "documents.ingest",
        "documents.approve",
        "reports.view",
        "reports.edit",
        "editorial.view",
    ],
    "director": [
        "project.view",
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "reports.view",
        "editorial.view",
    ],
    "editor": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "documents.ingest",
        "reports.view",
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
        "davinci.export",
    ],
    "sound": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "media.view",
        "reports.view",
        "editorial.view",
    ],
    "dop": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "media.view",
        "reports.view",
    ],
    "script_supervisor": [
        "project.view",
        "script.view",
        "script.edit",
        "storyboard.view",
        "breakdown.view",
        "media.view",
        "reports.view",
        "reports.edit",
    ],
    "viewer": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "reports.view",
        "editorial.view",
    ],
}
