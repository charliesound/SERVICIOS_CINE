from __future__ import annotations

import uuid
import hashlib
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime, Index, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ScriptVersion(Base):
    __tablename__ = "script_versions"
    __table_args__ = (
        Index("ix_script_version_project_id", "project_id"),
        Index("ix_script_version_org_project", "organization_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    source_filename: Mapped[Optional[str]] = mapped_column(String(255))
    script_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64))
    word_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    scene_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_by: Mapped[Optional[str]] = mapped_column(String(36))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    @staticmethod
    def calculate_hash(script_text: str) -> str:
        if not script_text:
            return ""
        return hashlib.sha256(script_text.encode('utf-8')).hexdigest()[:64]


class ScriptChangeReport(Base):
    __tablename__ = "script_change_reports"
    __table_args__ = (
        Index("ix_change_report_project_id", "project_id"),
        Index("ix_change_report_org", "organization_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    from_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    to_version_id: Mapped[str] = mapped_column(String(36))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    added_scenes_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    removed_scenes_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    modified_scenes_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    added_characters_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    removed_characters_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    modified_locations_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    production_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    budget_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    storyboard_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    funding_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    dossier_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    distribution_impact_json: Mapped[Optional[str]] = mapped_column(JSON, default=dict)
    recommended_actions_json: Mapped[Optional[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class ProjectModuleStatus(Base):
    __tablename__ = "project_module_status"
    __table_args__ = (
        Index("ix_module_status_project_id", "project_id"),
        Index("ix_module_status_project_module", "project_id", "module_name"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: uuid.uuid4().hex
    )
    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default="unchanged"
    )
    source_script_version_id: Mapped[Optional[str]] = mapped_column(String(36))
    affected_by_change_report_id: Mapped[Optional[str]] = mapped_column(String(36))
    summary: Mapped[Optional[str]] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )