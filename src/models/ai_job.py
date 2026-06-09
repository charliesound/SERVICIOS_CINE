from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from services.ai_job_status_service import AI_JOB_STATUSES


def _uuid_hex() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.utcnow()


def _enum_ck(column_name: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(repr(value) for value in values)
    return f"{column_name} IN ({quoted})"


class AIJob(Base):
    __tablename__ = "ai_jobs"
    __table_args__ = (
        CheckConstraint(
            _enum_ck("status", AI_JOB_STATUSES),
            name="ck_ai_jobs_status",
        ),
        CheckConstraint(
            "estimated_credits >= 0 AND reserved_credits >= 0 AND "
            "consumed_credits >= 0 AND released_credits >= 0",
            name="ck_ai_jobs_non_negative_credits",
        ),
        CheckConstraint(
            "attempt_number >= 1",
            name="ck_ai_jobs_attempt_number_positive",
        ),
        Index("ix_ai_jobs_organization_id_created_at", "organization_id", "created_at"),
        Index("ix_ai_jobs_organization_id_status", "organization_id", "status"),
        Index(
            "ix_ai_jobs_organization_id_project_id_created_at",
            "organization_id",
            "project_id",
            "created_at",
        ),
        Index(
            "ix_ai_jobs_organization_id_operation_type_created_at",
            "organization_id",
            "operation_type",
            "created_at",
        ),
        Index("ix_ai_jobs_parent_job_id", "parent_job_id"),
        Index("ix_ai_jobs_reservation_entry_id", "reservation_entry_id"),
        Index("ix_ai_jobs_consume_entry_id", "consume_entry_id"),
        Index("ix_ai_jobs_release_entry_id", "release_entry_id"),
        Index("ix_ai_jobs_provider_job_id", "provider_job_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    operation_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="created")
    estimated_credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consumed_credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    released_credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reservation_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    consume_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    release_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    provider_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provider_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    workflow_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    workflow_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    input_asset_ids: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    output_asset_ids: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_job_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    estimated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    credit_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reserved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    queued_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancel_requested_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    consume_pending_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    release_pending_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # SQLAlchemy Declarative reserves `metadata`, so the Python attribute uses
    # a safe alias while keeping the real column name contractual.
    job_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)


__all__ = [
    "AIJob",
]
