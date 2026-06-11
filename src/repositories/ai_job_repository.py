from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import get_history, instance_state

from models.ai_job import AIJob
from services.ai_job_status_service import (
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_RELEASE_PENDING,
)


class AIJobRepositoryError(Exception):
    """Base error for AIJobRepository operations."""


class AIJobTenantMutationError(AIJobRepositoryError):
    """Raised when save() detects a silent organization_id reassignment."""


class AIJobRepository:
    """Async tenant-safe repository for AIJob persistence.

    Contract: cid_ai_job_repository_async_contract_v1.md

    Rules:
    - every read filters by organization_id in the query itself;
    - there is no get(job_id) without organization_id;
    - save() rejects silent tenant reassignment;
    - the repository never calls session commit; it may call flush;
    - the repository shares AsyncSession with orchestration/gateway/ledger.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, job: AIJob) -> AIJob:
        self._session.add(job)
        await self._session.flush()
        return job

    async def get(self, organization_id: str, job_id: str) -> Optional[AIJob]:
        stmt = (
            select(AIJob)
            .where(AIJob.organization_id == organization_id)
            .where(AIJob.id == job_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_update(self, organization_id: str, job_id: str) -> Optional[AIJob]:
        stmt = (
            select(AIJob)
            .where(AIJob.organization_id == organization_id)
            .where(AIJob.id == job_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_organization(
        self,
        organization_id: str,
        *,
        status: str | None = None,
        project_id: str | None = None,
        operation_type: str | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[AIJob], str | None]:
        safe_limit = min(max(int(limit or 50), 1), 100)
        stmt = select(AIJob).where(AIJob.organization_id == organization_id)
        if status:
            stmt = stmt.where(AIJob.status == status)
        if project_id:
            stmt = stmt.where(AIJob.project_id == project_id)
        if operation_type:
            stmt = stmt.where(AIJob.operation_type == operation_type)
        if created_after:
            stmt = stmt.where(AIJob.created_at >= created_after)
        if created_before:
            stmt = stmt.where(AIJob.created_at <= created_before)
        if cursor:
            stmt = stmt.where(AIJob.id < cursor)
        stmt = stmt.order_by(AIJob.id.desc()).limit(safe_limit + 1)
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        next_cursor = rows[safe_limit].id if len(rows) > safe_limit else None
        return rows[:safe_limit], next_cursor

    async def list_cancelled_credit_release_candidates(
        self,
        organization_id: str,
        *,
        limit: int,
    ) -> list[AIJob]:
        safe_limit = min(max(int(limit or 1), 1), 100)
        stmt = (
            select(AIJob)
            .where(AIJob.organization_id == organization_id)
            .where(
                AIJob.status.in_(
                    (
                        AI_JOB_STATUS_CANCEL_REQUESTED,
                        AI_JOB_STATUS_CANCELLED,
                        AI_JOB_STATUS_RELEASE_PENDING,
                    )
                )
            )
            .where(AIJob.reservation_entry_id.is_not(None))
            .where(AIJob.consume_entry_id.is_(None))
            .where(AIJob.release_entry_id.is_(None))
            .where(AIJob.consumed_credits == 0)
            .where(AIJob.reserved_credits > 0)
            .order_by(AIJob.created_at.asc(), AIJob.id.asc())
            .limit(safe_limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, job: AIJob) -> AIJob:
        if job.organization_id is None:
            raise AIJobRepositoryError("organization_id must not be None")

        await self._check_tenant_mutation(job)

        self._session.add(job)
        await self._session.flush()
        return job

    async def _check_tenant_mutation(self, job: AIJob) -> None:
        try:
            state = instance_state(job)
            if state.persistent:
                history = get_history(job, "organization_id")
                if history.has_changes():
                    old_org = history.deleted[0] if history.deleted else None
                    if old_org is not None and old_org != job.organization_id:
                        raise AIJobTenantMutationError(
                            f"Cannot reassign job {job.id} from org {old_org} "
                            f"to org {job.organization_id}"
                        )
        except AIJobTenantMutationError:
            raise
        except Exception:
            pass

        if job.id is None:
            return

        stmt = select(AIJob.organization_id).where(AIJob.id == job.id)
        async with self._session.no_autoflush:
            result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is not None and row != job.organization_id:
            raise AIJobTenantMutationError(
                f"Cannot reassign job {job.id} from org {row} "
                f"to org {job.organization_id}"
            )

    async def find_by_idempotency_key(
        self, organization_id: str, idempotency_key: str
    ) -> Optional[AIJob]:
        stmt = (
            select(AIJob)
            .where(AIJob.organization_id == organization_id)
            .where(AIJob.idempotency_key == idempotency_key)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


__all__ = ["AIJobRepository", "AIJobRepositoryError", "AIJobTenantMutationError"]
