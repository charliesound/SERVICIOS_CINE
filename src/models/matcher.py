from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class MatcherJobStatus:
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class MatcherJob(Base):
    __tablename__ = "matcher_jobs"
    __table_args__ = (
        Index("ix_matcher_jobs_org_project", "organization_id", "project_id"),
        Index("ix_matcher_jobs_status", "status"),
        Index("ix_matcher_jobs_input_hash", "input_hash"),
        UniqueConstraint(
            "project_id",
            "organization_id",
            "input_hash",
            "trigger_type",
            name="uq_matcher_jobs_project_org_input_hash_trigger",
        ),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), nullable=False, index=True)
    organization_id = Column(String(36), nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False)  # document_updated, funding_call_updated, manual
    trigger_ref_id = Column(String(36), nullable=True)  # e.g., document_id or funding_call_id
    input_hash = Column(String(64), nullable=False)  # sha256 of relevant inputs
    status = Column(String(20), nullable=False, default=MatcherJobStatus.PENDING)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    result_summary_json = Column(Text, nullable=True)  # JSON summary of outcome
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )