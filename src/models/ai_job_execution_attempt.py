from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


ATTEMPT_STATUS_IN_PROGRESS = "in_progress"
ATTEMPT_STATUS_SUCCEEDED = "succeeded"
ATTEMPT_STATUS_FAILED = "failed"
ATTEMPT_STATUS_CANCELLED = "cancelled"
ATTEMPT_STATUS_CONFLICTED = "conflicted"

AI_JOB_EXECUTION_ATTEMPT_STATUSES = (
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_SUCCEEDED,
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_CANCELLED,
    ATTEMPT_STATUS_CONFLICTED,
)

ATTEMPT_MODE_SUCCESS = "success"
ATTEMPT_MODE_FAILURE = "failure"
ATTEMPT_MODE_CANCEL = "cancel"

AI_JOB_EXECUTION_ATTEMPT_MODES = (
    ATTEMPT_MODE_SUCCESS,
    ATTEMPT_MODE_FAILURE,
    ATTEMPT_MODE_CANCEL,
)


def _uuid_hex() -> str:
    return uuid.uuid4().hex


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _enum_ck(column_name: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(repr(value) for value in values)
    return f"{column_name} IN ({quoted})"


class AIJobExecutionAttempt(Base):
    __tablename__ = "ai_job_execution_attempts"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "job_id",
            "execution_attempt_id",
            name="uq_ai_job_execution_attempts_org_job_attempt",
        ),
        CheckConstraint(
            _enum_ck("mode", AI_JOB_EXECUTION_ATTEMPT_MODES),
            name="ck_ai_job_execution_attempts_mode",
        ),
        CheckConstraint(
            _enum_ck("status", AI_JOB_EXECUTION_ATTEMPT_STATUSES),
            name="ck_ai_job_execution_attempts_status",
        ),
        CheckConstraint(
            "consumed_credits IS NULL OR consumed_credits > 0",
            name="ck_ai_job_execution_attempts_consumed_credits_positive",
        ),
        CheckConstraint(
            "released_credits IS NULL OR released_credits > 0",
            name="ck_ai_job_execution_attempts_released_credits_positive",
        ),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="ck_ai_job_execution_attempts_finished_after_started",
        ),
        Index("ix_ai_job_execution_attempts_org_job", "organization_id", "job_id"),
        Index(
            "ix_ai_job_execution_attempts_org_job_created_at",
            "organization_id",
            "job_id",
            "created_at",
        ),
        Index(
            "ix_ai_job_execution_attempts_org_status_created_at",
            "organization_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_ai_job_execution_attempts_org_attempt",
            "organization_id",
            "execution_attempt_id",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("ai_jobs.id", name="fk_ai_job_execution_attempts_job_id_ai_jobs"),
        nullable=False,
    )
    execution_attempt_id: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ATTEMPT_STATUS_IN_PROGRESS,
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    fingerprint_version: Mapped[str] = mapped_column(String(10), nullable=False, default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )
    requested_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    result_status: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    consume_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    release_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    consumed_credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    released_credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message_safe: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)


__all__ = [
    "AIJobExecutionAttempt",
    "AI_JOB_EXECUTION_ATTEMPT_MODES",
    "AI_JOB_EXECUTION_ATTEMPT_STATUSES",
    "ATTEMPT_MODE_CANCEL",
    "ATTEMPT_MODE_FAILURE",
    "ATTEMPT_MODE_SUCCESS",
    "ATTEMPT_STATUS_CANCELLED",
    "ATTEMPT_STATUS_CONFLICTED",
    "ATTEMPT_STATUS_FAILED",
    "ATTEMPT_STATUS_IN_PROGRESS",
    "ATTEMPT_STATUS_SUCCEEDED",
]
