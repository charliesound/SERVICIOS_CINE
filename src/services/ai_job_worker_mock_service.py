from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_job_async_orchestration_service import (
    AIJobAsyncConsumeRequest,
    AIJobAsyncExecutionTransitionRequest,
    AIJobAsyncOrchestrationService,
    AIJobAsyncReleaseRequest,
)

AIJobWorkerMockMode = Literal["success", "failure", "cancel"]

MAX_SIMULATED_DURATION_MS = 60_000


class AIJobWorkerMockError(Exception):
    """Base error for backend-only AI job mock worker execution."""


class AIJobWorkerMockInvalidModeError(AIJobWorkerMockError):
    """Raised when the mock command mode is not supported."""


class AIJobWorkerMockSettlementError(AIJobWorkerMockError):
    """Raised when the mock worker cannot safely settle reserved credits."""


@dataclass(frozen=True)
class AIJobWorkerMockCommand:
    organization_id: str
    job_id: str
    requested_by: str
    execution_attempt_id: str
    mode: AIJobWorkerMockMode
    simulated_duration_ms: int | None = None
    mock_output_metadata: dict[str, Any] | None = None
    mock_error_code: str | None = None
    mock_error_message: str | None = None
    actual_credits: int | None = None
    release_credits: int | None = None


@dataclass(frozen=True)
class AIJobWorkerMockResult:
    organization_id: str
    job_id: str
    mode: AIJobWorkerMockMode
    status: str
    consumed_credits: int | None = None
    released_credits: int | None = None
    consume_entry_id: str | None = None
    release_entry_id: str | None = None
    output_metadata: dict[str, Any] | None = None
    error_metadata: dict[str, Any] | None = None


class AIJobWorkerMockService:
    """Backend-only mock executor for AI Jobs.

    This service deliberately does not own transaction commits or persistent
    attempt replay storage. Full execution_attempt_id replay persistence remains
    a future phase; V1 passes the attempt id as the settlement caller key.
    """

    def __init__(self, orchestration_service: AIJobAsyncOrchestrationService) -> None:
        self.orchestration_service = orchestration_service

    async def execute(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockResult:
        normalized = self._validate_command(command)
        if normalized.mode == "success":
            return await self._execute_success(session, normalized)
        if normalized.mode == "failure":
            return await self._execute_failure(session, normalized)
        if normalized.mode == "cancel":
            return await self._execute_cancel(session, normalized)
        raise AIJobWorkerMockInvalidModeError("mode must be success, failure, or cancel")

    async def _execute_success(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockResult:
        initial_job = self._require_loaded_job(
            await self.orchestration_service.get_ai_job(
                session,
                command.organization_id,
                command.job_id,
            ),
        )
        actual_credits = self._resolve_credits(
            command.actual_credits,
            getattr(initial_job, "reserved_credits", None),
            "actual_credits",
        )
        await self.orchestration_service.enqueue_ai_job(
            session,
            self._transition_request(command),
        )
        await self.orchestration_service.start_ai_job(
            session,
            self._transition_request(command),
        )
        await self.orchestration_service.succeed_ai_job(
            session,
            self._transition_request(
                command,
                output_metadata=command.mock_output_metadata or {},
            ),
        )
        await self.orchestration_service.mark_consume_pending(
            session,
            self._transition_request(command),
        )
        settlement = await self.orchestration_service.consume_ai_job_credits(
            session,
            AIJobAsyncConsumeRequest(
                organization_id=command.organization_id,
                job_id=command.job_id,
                actual_credits=actual_credits,
                caller_key=command.execution_attempt_id,
            ),
        )
        job = settlement.job
        return AIJobWorkerMockResult(
            organization_id=command.organization_id,
            job_id=command.job_id,
            mode=command.mode,
            status=str(getattr(job, "status", "")),
            consumed_credits=getattr(job, "consumed_credits", None),
            consume_entry_id=getattr(job, "consume_entry_id", None),
            output_metadata=command.mock_output_metadata or {},
        )

    async def _execute_failure(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockResult:
        initial_job = self._require_loaded_job(
            await self.orchestration_service.get_ai_job(
                session,
                command.organization_id,
                command.job_id,
            ),
        )
        release_credits = self._resolve_credits(
            command.release_credits,
            getattr(initial_job, "reserved_credits", None),
            "release_credits",
        )
        error_metadata = self._build_error_metadata(command)
        await self.orchestration_service.enqueue_ai_job(
            session,
            self._transition_request(command),
        )
        await self.orchestration_service.start_ai_job(
            session,
            self._transition_request(command),
        )
        await self.orchestration_service.fail_ai_job(
            session,
            self._transition_request(command, error_metadata=error_metadata),
        )
        await self.orchestration_service.mark_release_pending(
            session,
            self._transition_request(command),
        )
        settlement = await self.orchestration_service.release_ai_job_credits(
            session,
            AIJobAsyncReleaseRequest(
                organization_id=command.organization_id,
                job_id=command.job_id,
                release_credits=release_credits,
                caller_key=command.execution_attempt_id,
            ),
        )
        job = settlement.job
        return AIJobWorkerMockResult(
            organization_id=command.organization_id,
            job_id=command.job_id,
            mode=command.mode,
            status=str(getattr(job, "status", "")),
            released_credits=getattr(job, "released_credits", None),
            release_entry_id=getattr(job, "release_entry_id", None),
            error_metadata=error_metadata,
        )

    async def _execute_cancel(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockResult:
        initial_job = self._require_loaded_job(
            await self.orchestration_service.get_ai_job(
                session,
                command.organization_id,
                command.job_id,
            ),
        )
        if getattr(initial_job, "status", None) != "cancel_requested":
            raise AIJobWorkerMockError(
                "cancel mode requires an existing cancel_requested job in V1"
            )
        release_credits = self._resolve_credits(
            command.release_credits,
            getattr(initial_job, "reserved_credits", None),
            "release_credits",
        )
        error_metadata = self._build_error_metadata(command)
        await self.orchestration_service.cancel_ai_job(
            session,
            self._transition_request(command, error_metadata=error_metadata),
        )
        await self.orchestration_service.mark_release_pending(
            session,
            self._transition_request(command),
        )
        settlement = await self.orchestration_service.release_ai_job_credits(
            session,
            AIJobAsyncReleaseRequest(
                organization_id=command.organization_id,
                job_id=command.job_id,
                release_credits=release_credits,
                caller_key=command.execution_attempt_id,
            ),
        )
        job = settlement.job
        return AIJobWorkerMockResult(
            organization_id=command.organization_id,
            job_id=command.job_id,
            mode=command.mode,
            status=str(getattr(job, "status", "")),
            released_credits=getattr(job, "released_credits", None),
            release_entry_id=getattr(job, "release_entry_id", None),
            error_metadata=error_metadata,
        )


    def _require_loaded_job(self, job: Any) -> Any:
        if job is None:
            raise AIJobWorkerMockError("AI job not found for mock worker execution")
        return job

    def _transition_request(
        self,
        command: AIJobWorkerMockCommand,
        *,
        output_metadata: dict[str, Any] | None = None,
        error_metadata: dict[str, Any] | None = None,
    ) -> AIJobAsyncExecutionTransitionRequest:
        return AIJobAsyncExecutionTransitionRequest(
            organization_id=command.organization_id,
            job_id=command.job_id,
            execution_attempt_id=command.execution_attempt_id,
            requested_by=command.requested_by,
            output_metadata=output_metadata,
            error_metadata=error_metadata,
        )

    def _validate_command(self, command: AIJobWorkerMockCommand) -> AIJobWorkerMockCommand:
        organization_id = self._require_text(command.organization_id, "organization_id")
        job_id = self._require_text(command.job_id, "job_id")
        requested_by = self._require_text(command.requested_by, "requested_by")
        execution_attempt_id = self._require_text(
            command.execution_attempt_id,
            "execution_attempt_id",
        )
        mode = self._require_text(str(command.mode), "mode")
        if mode not in {"success", "failure", "cancel"}:
            raise AIJobWorkerMockInvalidModeError("mode must be success, failure, or cancel")
        self._validate_simulated_duration(command.simulated_duration_ms)
        self._validate_optional_command_credits(command.actual_credits, "actual_credits")
        self._validate_optional_command_credits(command.release_credits, "release_credits")
        self._validate_metadata(command.mock_output_metadata, "mock_output_metadata")
        error_metadata = self._build_error_metadata(command)
        self._validate_metadata(error_metadata, "mock_error_metadata")
        return AIJobWorkerMockCommand(
            organization_id=organization_id,
            job_id=job_id,
            requested_by=requested_by,
            execution_attempt_id=execution_attempt_id,
            mode=mode,  # type: ignore[arg-type]
            simulated_duration_ms=command.simulated_duration_ms,
            mock_output_metadata=command.mock_output_metadata,
            mock_error_code=self._normalize_optional_text(command.mock_error_code),
            mock_error_message=self._normalize_optional_text(command.mock_error_message),
            actual_credits=command.actual_credits,
            release_credits=command.release_credits,
        )

    def _build_error_metadata(self, command: AIJobWorkerMockCommand) -> dict[str, Any]:
        metadata: dict[str, Any] = {}
        code = self._normalize_optional_text(command.mock_error_code)
        message = self._normalize_optional_text(command.mock_error_message)
        if code is not None:
            metadata["code"] = code
        if message is not None:
            metadata["message"] = message
        return metadata

    def _resolve_credits(
        self,
        explicit_value: int | None,
        reserved_credits: int | None,
        field_name: str,
    ) -> int:
        if explicit_value is not None:
            return self._validate_optional_credits(explicit_value, field_name)
        if reserved_credits is None:
            raise AIJobWorkerMockSettlementError(
                "reserved_credits must be available for mock settlement"
            )
        return self._validate_optional_credits(reserved_credits, "reserved_credits")

    def _validate_optional_command_credits(
        self,
        value: int | None,
        field_name: str,
    ) -> None:
        if value is None:
            return
        self._validate_optional_credits(value, field_name)

    def _validate_optional_credits(self, value: int | None, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            if value is None:
                raise AIJobWorkerMockSettlementError(
                    "{0} must be a positive integer".format(field_name)
                )
            raise AIJobWorkerMockSettlementError(
                "{0} must be a positive integer".format(field_name)
            )
        if value <= 0:
            raise AIJobWorkerMockSettlementError(
                "{0} must be a positive integer".format(field_name)
            )
        return value

    def _validate_simulated_duration(self, value: int | None) -> None:
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise AIJobWorkerMockError("simulated_duration_ms must be an integer")
        if value < 0:
            raise AIJobWorkerMockError("simulated_duration_ms must be non-negative")
        if value > MAX_SIMULATED_DURATION_MS:
            raise AIJobWorkerMockError("simulated_duration_ms exceeds maximum")

    def _validate_metadata(self, value: dict[str, Any] | None, field_name: str) -> None:
        if value is None:
            return
        if not isinstance(value, dict):
            raise AIJobWorkerMockError("{0} must be a JSON object".format(field_name))
        try:
            json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise AIJobWorkerMockError(
                "{0} must be JSON-safe".format(field_name)
            ) from exc

    def _require_text(self, value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise AIJobWorkerMockError("{0} must be a non-empty string".format(field_name))
        normalized = value.strip()
        if not normalized:
            raise AIJobWorkerMockError("{0} must be a non-empty string".format(field_name))
        return normalized

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = self._require_text(value, "optional text field")
        return normalized or None


__all__ = [
    "AIJobWorkerMockCommand",
    "AIJobWorkerMockError",
    "AIJobWorkerMockInvalidModeError",
    "AIJobWorkerMockMode",
    "AIJobWorkerMockResult",
    "AIJobWorkerMockService",
    "AIJobWorkerMockSettlementError",
]
