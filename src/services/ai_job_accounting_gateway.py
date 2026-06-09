from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.ai_job_costing_service import AIJobCostingService
from services.credit_gate_service import CreditAvailabilityCheckResult, CreditGateService
from services.credit_ledger_service import (
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditReservationResult,
)

__all__ = [
    "AIJobAccountingGatewayError",
    "AIJobAccountingGateway",
]


class AIJobAccountingGatewayError(Exception):
    """Base error for AI job accounting gateway operations."""


class AIJobAccountingGateway:
    """Async adapter between AI jobs and the credit layer."""

    def __init__(
        self,
        costing_service: AIJobCostingService,
        credit_gate_service: CreditGateService | None = None,
    ) -> None:
        self.costing_service = costing_service
        self.credit_gate_service = credit_gate_service

    def _require_text(self, value: str | None, field_name: str) -> str:
        if not isinstance(value, str):
            raise AIJobAccountingGatewayError(f"{field_name} must be a non-empty string")
        normalized = value.strip()
        if not normalized:
            raise AIJobAccountingGatewayError(f"{field_name} must be a non-empty string")
        return normalized

    def _require_positive_credits(self, value: int | None, field_name: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise AIJobAccountingGatewayError(f"{field_name} must be a positive integer")
        if value <= 0:
            raise AIJobAccountingGatewayError(f"{field_name} must be a positive integer")
        return value

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AIJobAccountingGatewayError("optional metadata fields must be strings")
        normalized = value.strip()
        return normalized or None

    def _normalize_asset_ids(self, asset_ids: Iterable[str] | None) -> list[str]:
        if asset_ids is None:
            return []
        if isinstance(asset_ids, str):
            raise AIJobAccountingGatewayError("asset_ids must be a list or tuple of strings")
        normalized: list[str] = []
        for asset_id in asset_ids:
            if not isinstance(asset_id, str):
                raise AIJobAccountingGatewayError("asset_ids entries must be strings")
            cleaned = asset_id.strip()
            if cleaned:
                normalized.append(cleaned)
        return normalized

    def build_idempotency_key(
        self,
        *,
        action: str,
        organization_id: str,
        job_id: str,
        caller_key: str | None = None,
    ) -> str:
        normalized_action = self._require_text(action, "action").lower()
        if normalized_action not in {"reserve", "consume", "release"}:
            raise AIJobAccountingGatewayError("action must be reserve, consume, or release")
        normalized_organization_id = self._require_text(organization_id, "organization_id")
        normalized_job_id = self._require_text(job_id, "job_id")
        base_key = f"ai_job:{normalized_organization_id}:{normalized_job_id}:{normalized_action}"
        if caller_key is None:
            return base_key
        normalized_caller_key = self._require_text(caller_key, "caller_key")
        return f"{base_key}:{normalized_caller_key}"

    async def estimate_credit_cost(
        self,
        session: AsyncSession,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> object:
        _ = session
        return self.costing_service.estimate_ai_job_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    async def check_credit_availability(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditAvailabilityCheckResult:
        if self.credit_gate_service is not None:
            return await self.credit_gate_service.check_credit_availability(
                session,
                organization_id=organization_id,
                operation_type=operation_type,
                estimated_credits=estimated_credits,
            )
        return await self.costing_service.check_ai_job_credit_availability(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    async def reserve_credits_for_job(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        estimated_credits: int | None,
        project_id: str | None = None,
        user_id: str | None = None,
        operation_type: str,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        caller_key: str | None = None,
    ) -> CreditReservationResult:
        normalized_organization_id = self._require_text(organization_id, "organization_id")
        normalized_job_id = self._require_text(job_id, "job_id")
        normalized_estimated_credits = self._require_positive_credits(
            estimated_credits,
            "estimated_credits",
        )
        normalized_input_asset_ids = self._normalize_asset_ids(input_asset_ids)
        idempotency_key = self.build_idempotency_key(
            action="reserve",
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            caller_key=caller_key,
        )
        metadata = self._build_metadata(
            job_id=normalized_job_id,
            project_id=project_id,
            user_id=user_id,
            operation_type=operation_type,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="reserved",
        )
        return await self.costing_service.reserve_ai_job_credits(
            session,
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            operation_type=operation_type,
            estimated_credits=normalized_estimated_credits,
            project_id=project_id,
            user_id=user_id,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="reserved",
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def consume_reserved_credits_for_job(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        reservation_entry_id: str | None,
        actual_credits: int | None,
        project_id: str | None = None,
        user_id: str | None = None,
        operation_type: str,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        caller_key: str | None = None,
    ) -> CreditConsumptionResult:
        normalized_organization_id = self._require_text(organization_id, "organization_id")
        normalized_job_id = self._require_text(job_id, "job_id")
        normalized_reservation_entry_id = self._require_text(
            reservation_entry_id,
            "reservation_entry_id",
        )
        normalized_actual_credits = self._require_positive_credits(
            actual_credits,
            "actual_credits",
        )
        normalized_input_asset_ids = self._normalize_asset_ids(input_asset_ids)
        idempotency_key = self.build_idempotency_key(
            action="consume",
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            caller_key=caller_key,
        )
        metadata = self._build_metadata(
            job_id=normalized_job_id,
            project_id=project_id,
            user_id=user_id,
            operation_type=operation_type,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="consumed",
            reservation_entry_id=normalized_reservation_entry_id,
        )
        return await self.costing_service.consume_ai_job_credits(
            session,
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            operation_type=operation_type,
            estimated_credits=normalized_actual_credits,
            project_id=project_id,
            user_id=user_id,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="consumed",
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    async def release_reserved_credits_for_job(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        reservation_entry_id: str | None,
        release_credits: int | None,
        project_id: str | None = None,
        user_id: str | None = None,
        operation_type: str,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        caller_key: str | None = None,
    ) -> CreditReleaseResult:
        normalized_organization_id = self._require_text(organization_id, "organization_id")
        normalized_job_id = self._require_text(job_id, "job_id")
        normalized_reservation_entry_id = self._require_text(
            reservation_entry_id,
            "reservation_entry_id",
        )
        normalized_release_credits = self._require_positive_credits(
            release_credits,
            "release_credits",
        )
        normalized_input_asset_ids = self._normalize_asset_ids(input_asset_ids)
        idempotency_key = self.build_idempotency_key(
            action="release",
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            caller_key=caller_key,
        )
        metadata = self._build_metadata(
            job_id=normalized_job_id,
            project_id=project_id,
            user_id=user_id,
            operation_type=operation_type,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="released",
            reservation_entry_id=normalized_reservation_entry_id,
        )
        return await self.costing_service.release_ai_job_credits(
            session,
            organization_id=normalized_organization_id,
            job_id=normalized_job_id,
            operation_type=operation_type,
            estimated_credits=normalized_release_credits,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=normalized_input_asset_ids,
            job_status="released",
            metadata=metadata,
            idempotency_key=idempotency_key,
        )

    def _build_metadata(
        self,
        *,
        job_id: str,
        project_id: str | None,
        user_id: str | None,
        operation_type: str,
        provider_type: str | None,
        provider_name: str | None,
        workflow_id: str | None,
        workflow_version: str | None,
        workflow_hash: str | None,
        model_name: str | None,
        input_asset_ids: Iterable[str] | None,
        job_status: str,
        reservation_entry_id: str | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "job_id": job_id,
            "project_id": self._normalize_optional_text(project_id),
            "user_id": self._normalize_optional_text(user_id),
            "operation_type": self._require_text(operation_type, "operation_type"),
            "provider_type": self._normalize_optional_text(provider_type),
            "provider_name": self._normalize_optional_text(provider_name),
            "workflow_id": self._normalize_optional_text(workflow_id),
            "workflow_version": self._normalize_optional_text(workflow_version),
            "workflow_hash": self._normalize_optional_text(workflow_hash),
            "model_name": self._normalize_optional_text(model_name),
            "input_asset_ids": self._normalize_asset_ids(input_asset_ids),
            "job_status": job_status,
        }
        if reservation_entry_id is not None:
            metadata["reservation_entry_id"] = reservation_entry_id
        return metadata
