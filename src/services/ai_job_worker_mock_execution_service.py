from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.ai_job_execution_attempt import (
    AIJobExecutionAttempt,
    ATTEMPT_STATUS_CANCELLED,
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_SUCCEEDED,
)
from repositories.ai_job_execution_attempt_repository import AIJobExecutionAttemptRepository
from services.ai_job_worker_mock_service import (
    AIJobWorkerMockCommand,
    AIJobWorkerMockResult,
    AIJobWorkerMockService,
)


FINGERPRINT_VERSION = "v1"
UNIQUE_ATTEMPT_CONSTRAINT = "uq_ai_job_execution_attempts_org_job_attempt"

TERMINAL_REPLAY_STATUSES = {
    ATTEMPT_STATUS_SUCCEEDED,
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_CANCELLED,
}


class AIJobWorkerMockExecutionError(Exception):
    """Base error for persisted mock worker execution idempotency."""


class AIJobWorkerMockExecutionConflictError(AIJobWorkerMockExecutionError):
    """Raised when a persisted execution attempt conflicts with a request."""


class AIJobWorkerMockExecutionInProgressError(AIJobWorkerMockExecutionConflictError):
    """Raised when a matching execution attempt is still in progress."""


class AIJobWorkerMockExecutionFingerprintMismatchError(
    AIJobWorkerMockExecutionConflictError
):
    """Raised when a retry reuses an attempt id with a different payload."""


class AIJobWorkerMockExecutionReplayError(AIJobWorkerMockExecutionError):
    """Raised when a replay path cannot reconstruct a safe result."""


class AIJobWorkerMockExecutionInvalidStateError(
    AIJobWorkerMockExecutionConflictError
):
    """Raised when a stored attempt has an unsupported status."""


@dataclass(frozen=True)
class AIJobWorkerMockExecutionResult:
    result: AIJobWorkerMockResult
    replay: bool
    attempt_status: str
    execution_attempt_id: str
    fingerprint_version: str = FINGERPRINT_VERSION


def compute_execution_attempt_fingerprint(command: AIJobWorkerMockCommand) -> str:
    payload: dict[str, Any] = {
        "mode": command.mode,
        "simulated_duration_ms": command.simulated_duration_ms,
        "mock_output_metadata": command.mock_output_metadata,
        "mock_error_code": command.mock_error_code,
        "mock_error_message": command.mock_error_message,
        "actual_credits": command.actual_credits,
        "release_credits": command.release_credits,
    }
    canonical_payload = {
        key: value for key, value in payload.items() if value is not None
    }
    canonical_json = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class AIJobWorkerMockExecutionService:
    """Idempotency wrapper around the backend-only mock worker."""

    def __init__(
        self,
        *,
        worker_service: AIJobWorkerMockService,
        attempt_repository_factory: Callable[
            [AsyncSession], AIJobExecutionAttemptRepository
        ] = AIJobExecutionAttemptRepository,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.worker_service = worker_service
        self.attempt_repository_factory = attempt_repository_factory
        self._now = now_fn or datetime.utcnow

    async def execute(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockExecutionResult:
        repository = self.attempt_repository_factory(session)
        fingerprint = compute_execution_attempt_fingerprint(command)
        attempt = self._build_attempt(command, fingerprint)

        try:
            await repository.create(attempt)
        except IntegrityError as exc:
            if not self._is_unique_attempt_integrity_error(exc):
                raise
            return await self._handle_existing_attempt(
                repository,
                command,
                fingerprint,
            )

        result = await self.worker_service.execute(session, command)
        self._apply_worker_result(attempt, command, result)
        await repository.save(attempt)
        return AIJobWorkerMockExecutionResult(
            result=result,
            replay=False,
            attempt_status=attempt.status,
            execution_attempt_id=command.execution_attempt_id,
        )

    def _build_attempt(
        self,
        command: AIJobWorkerMockCommand,
        fingerprint: str,
    ) -> AIJobExecutionAttempt:
        return AIJobExecutionAttempt(
            organization_id=command.organization_id,
            job_id=command.job_id,
            execution_attempt_id=command.execution_attempt_id,
            mode=str(command.mode),
            status=ATTEMPT_STATUS_IN_PROGRESS,
            fingerprint=fingerprint,
            fingerprint_version=FINGERPRINT_VERSION,
            requested_by=command.requested_by,
            started_at=self._now(),
        )

    async def _handle_existing_attempt(
        self,
        repository: AIJobExecutionAttemptRepository,
        command: AIJobWorkerMockCommand,
        fingerprint: str,
    ) -> AIJobWorkerMockExecutionResult:
        existing = await repository.get_for_update(
            command.organization_id,
            command.job_id,
            command.execution_attempt_id,
        )
        if existing is None:
            raise AIJobWorkerMockExecutionReplayError(
                "Execution attempt unique conflict could not be replayed"
            )
        if existing.fingerprint != fingerprint or existing.fingerprint_version != FINGERPRINT_VERSION:
            raise AIJobWorkerMockExecutionFingerprintMismatchError(
                "Execution attempt fingerprint mismatch"
            )
        if existing.status == ATTEMPT_STATUS_IN_PROGRESS:
            raise AIJobWorkerMockExecutionInProgressError(
                "Execution attempt is already in progress"
            )
        if existing.status in TERMINAL_REPLAY_STATUSES:
            result = self._reconstruct_worker_result_from_attempt(existing)
            return AIJobWorkerMockExecutionResult(
                result=result,
                replay=True,
                attempt_status=existing.status,
                execution_attempt_id=command.execution_attempt_id,
                fingerprint_version=existing.fingerprint_version,
            )
        raise AIJobWorkerMockExecutionInvalidStateError(
            "Execution attempt status cannot be replayed: {0}".format(existing.status)
        )

    def _apply_worker_result(
        self,
        attempt: AIJobExecutionAttempt,
        command: AIJobWorkerMockCommand,
        result: AIJobWorkerMockResult,
    ) -> None:
        if command.mode == "success":
            attempt.status = ATTEMPT_STATUS_SUCCEEDED
        elif command.mode == "failure":
            attempt.status = ATTEMPT_STATUS_FAILED
        elif command.mode == "cancel":
            attempt.status = ATTEMPT_STATUS_CANCELLED
        else:
            raise AIJobWorkerMockExecutionInvalidStateError(
                "Unsupported mock worker mode: {0}".format(command.mode)
            )
        attempt.result_status = result.status
        attempt.consume_entry_id = result.consume_entry_id
        attempt.release_entry_id = result.release_entry_id
        attempt.consumed_credits = result.consumed_credits
        attempt.released_credits = result.released_credits
        attempt.finished_at = self._now()

    def _reconstruct_worker_result_from_attempt(
        self,
        attempt: AIJobExecutionAttempt,
    ) -> AIJobWorkerMockResult:
        if attempt.status not in TERMINAL_REPLAY_STATUSES:
            raise AIJobWorkerMockExecutionInvalidStateError(
                "Execution attempt status cannot be replayed: {0}".format(attempt.status)
            )
        if not attempt.result_status:
            raise AIJobWorkerMockExecutionReplayError(
                "Execution attempt replay is missing result_status"
            )
        return AIJobWorkerMockResult(
            organization_id=attempt.organization_id,
            job_id=attempt.job_id,
            mode=attempt.mode,  # type: ignore[arg-type]
            status=attempt.result_status,
            consumed_credits=attempt.consumed_credits,
            released_credits=attempt.released_credits,
            consume_entry_id=attempt.consume_entry_id,
            release_entry_id=attempt.release_entry_id,
            output_metadata=None,
            error_metadata=None,
        )

    def _is_unique_attempt_integrity_error(self, error: IntegrityError) -> bool:
        original = getattr(error, "orig", None)
        pgcode = getattr(original, "pgcode", None) or getattr(original, "sqlstate", None)
        diag = getattr(original, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)
        message = str(error)
        if constraint_name == UNIQUE_ATTEMPT_CONSTRAINT:
            return True
        if pgcode == "23505" and UNIQUE_ATTEMPT_CONSTRAINT in message:
            return True
        return False


__all__ = [
    "AIJobWorkerMockExecutionConflictError",
    "AIJobWorkerMockExecutionError",
    "AIJobWorkerMockExecutionFingerprintMismatchError",
    "AIJobWorkerMockExecutionInProgressError",
    "AIJobWorkerMockExecutionInvalidStateError",
    "AIJobWorkerMockExecutionReplayError",
    "AIJobWorkerMockExecutionResult",
    "AIJobWorkerMockExecutionService",
    "compute_execution_attempt_fingerprint",
]
