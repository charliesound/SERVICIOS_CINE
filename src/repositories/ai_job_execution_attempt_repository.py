from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import get_history, instance_state

from models.ai_job_execution_attempt import AIJobExecutionAttempt


class AIJobExecutionAttemptRepositoryError(Exception):
    """Base error for AIJobExecutionAttemptRepository operations."""


class AIJobExecutionAttemptNotFoundError(AIJobExecutionAttemptRepositoryError):
    """Raised when a tenant-scoped attempt lookup returns no row."""


class AIJobExecutionAttemptConflictError(AIJobExecutionAttemptRepositoryError):
    """Raised when a persisted attempt conflicts with a requested operation."""


class AIJobExecutionAttemptAlreadyInProgressError(AIJobExecutionAttemptConflictError):
    """Raised when an attempt replay finds an in-progress attempt."""


class AIJobExecutionAttemptFingerprintMismatchError(AIJobExecutionAttemptConflictError):
    """Raised when an attempt replay has a different fingerprint."""


class AIJobExecutionAttemptInvalidStateError(AIJobExecutionAttemptRepositoryError):
    """Raised when an attempt operation is invalid for the current state."""


class AIJobExecutionAttemptTenantMutationError(AIJobExecutionAttemptRepositoryError):
    """Raised when save() detects a silent organization_id reassignment."""


class AIJobExecutionAttemptRepository:
    """Async tenant-safe repository for AI job execution attempts.

    Contract: cid_ai_job_execution_attempt_model_repository_contract_v1.md
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
        self._validate_required_identity(attempt)
        self._session.add(attempt)
        await self._session.flush()
        return attempt

    async def get(
        self,
        organization_id: str,
        job_id: str,
        execution_attempt_id: str,
    ) -> Optional[AIJobExecutionAttempt]:
        stmt = self._select_by_key(organization_id, job_id, execution_attempt_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_for_update(
        self,
        organization_id: str,
        job_id: str,
        execution_attempt_id: str,
    ) -> Optional[AIJobExecutionAttempt]:
        stmt = self._select_by_key(
            organization_id,
            job_id,
            execution_attempt_id,
        ).with_for_update()
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
        self._validate_required_identity(attempt)
        await self._check_tenant_mutation(attempt)
        self._session.add(attempt)
        await self._session.flush()
        return attempt

    async def find_by_key(
        self,
        organization_id: str,
        job_id: str,
        execution_attempt_id: str,
    ) -> Optional[AIJobExecutionAttempt]:
        return await self.get(organization_id, job_id, execution_attempt_id)

    async def list_for_job(
        self,
        organization_id: str,
        job_id: str,
        *,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[AIJobExecutionAttempt], str | None]:
        safe_limit = min(max(int(limit or 50), 1), 100)
        stmt = (
            select(AIJobExecutionAttempt)
            .where(AIJobExecutionAttempt.organization_id == organization_id)
            .where(AIJobExecutionAttempt.job_id == job_id)
        )
        if cursor:
            stmt = stmt.where(AIJobExecutionAttempt.id < cursor)
        stmt = stmt.order_by(
            AIJobExecutionAttempt.created_at.desc(),
            AIJobExecutionAttempt.id.desc(),
        ).limit(safe_limit + 1)
        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        next_cursor = rows[safe_limit].id if len(rows) > safe_limit else None
        return rows[:safe_limit], next_cursor

    def _select_by_key(
        self,
        organization_id: str,
        job_id: str,
        execution_attempt_id: str,
    ):
        return (
            select(AIJobExecutionAttempt)
            .where(AIJobExecutionAttempt.organization_id == organization_id)
            .where(AIJobExecutionAttempt.job_id == job_id)
            .where(AIJobExecutionAttempt.execution_attempt_id == execution_attempt_id)
        )

    def _validate_required_identity(self, attempt: AIJobExecutionAttempt) -> None:
        for field_name in ("organization_id", "job_id", "execution_attempt_id"):
            value = getattr(attempt, field_name, None)
            if not isinstance(value, str) or not value.strip():
                raise AIJobExecutionAttemptRepositoryError(
                    "{0} must be a non-empty string".format(field_name)
                )

    async def _check_tenant_mutation(self, attempt: AIJobExecutionAttempt) -> None:
        try:
            state = instance_state(attempt)
            if state.persistent:
                history = get_history(attempt, "organization_id")
                if history.has_changes():
                    old_org = history.deleted[0] if history.deleted else None
                    if old_org is not None and old_org != attempt.organization_id:
                        raise AIJobExecutionAttemptTenantMutationError(
                            f"Cannot reassign execution attempt {attempt.id} "
                            f"from org {old_org} to org {attempt.organization_id}"
                        )
        except AIJobExecutionAttemptTenantMutationError:
            raise
        except Exception:
            pass

        if attempt.id is None:
            return

        stmt = select(AIJobExecutionAttempt.organization_id).where(
            AIJobExecutionAttempt.id == attempt.id
        )
        with self._session.no_autoflush:
            result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is not None and row != attempt.organization_id:
            raise AIJobExecutionAttemptTenantMutationError(
                f"Cannot reassign execution attempt {attempt.id} "
                f"from org {row} to org {attempt.organization_id}"
            )


__all__ = [
    "AIJobExecutionAttemptAlreadyInProgressError",
    "AIJobExecutionAttemptConflictError",
    "AIJobExecutionAttemptFingerprintMismatchError",
    "AIJobExecutionAttemptInvalidStateError",
    "AIJobExecutionAttemptNotFoundError",
    "AIJobExecutionAttemptRepository",
    "AIJobExecutionAttemptRepositoryError",
    "AIJobExecutionAttemptTenantMutationError",
]
