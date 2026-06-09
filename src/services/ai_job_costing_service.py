from __future__ import annotations

from typing import Any, Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from services.credit_gate_service import (
    CreditAvailabilityCheckResult,
    CreditGateEstimateResult,
    CreditGateService,
)
from services.credit_ledger_service import (
    CreditConsumptionResult,
    CreditReleaseResult,
    CreditReservationResult,
)


CANONICAL_METADATA_KEYS = (
    "operation_type",
    "estimated_credits",
    "provider_type",
    "provider_name",
    "workflow_id",
    "workflow_version",
    "workflow_hash",
    "model_name",
    "input_asset_ids",
    "output_asset_ids",
    "job_status",
    "failure_reason",
)


__all__ = [
    "CANONICAL_METADATA_KEYS",
    "AIJobCostingError",
    "AIJobCostingService",
]


class AIJobCostingError(Exception):
    """Base error for AI job costing helpers."""


class AIJobCostingService:
    """Small facade that applies AI-job metadata on top of CreditGateService."""

    def __init__(self, credit_gate_service: CreditGateService | None = None) -> None:
        self.credit_gate_service = credit_gate_service or CreditGateService()

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise AIJobCostingError("optional textual metadata fields must be strings")
        normalized = value.strip()
        return normalized or None

    def _normalize_asset_ids(
        self,
        asset_ids: Iterable[str] | None,
        field_name: str,
    ) -> list[str]:
        if asset_ids is None:
            return []
        if isinstance(asset_ids, str):
            raise AIJobCostingError("{0} must be a list/tuple of strings".format(field_name))
        normalized: list[str] = []
        for asset_id in asset_ids:
            if not isinstance(asset_id, str):
                raise AIJobCostingError(
                    "{0} entries must be strings".format(field_name)
                )
            cleaned = asset_id.strip()
            if cleaned:
                normalized.append(cleaned)
        return normalized

    def estimate_ai_job_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditGateEstimateResult:
        return self.credit_gate_service.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    async def check_ai_job_credit_availability(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditAvailabilityCheckResult:
        return await self.credit_gate_service.check_credit_availability(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )

    def build_ai_job_costing_metadata(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        output_asset_ids: Iterable[str] | None = None,
        job_status: str | None = None,
        failure_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        estimate = self.estimate_ai_job_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        payload: dict[str, Any] = {}
        if metadata:
            payload.update(metadata)

        payload["operation_type"] = estimate.operation_type
        payload["estimated_credits"] = estimate.estimated_credits
        payload["provider_type"] = self._normalize_optional_text(provider_type)
        payload["provider_name"] = self._normalize_optional_text(provider_name)
        payload["workflow_id"] = self._normalize_optional_text(workflow_id)
        payload["workflow_version"] = self._normalize_optional_text(workflow_version)
        payload["workflow_hash"] = self._normalize_optional_text(workflow_hash)
        payload["model_name"] = self._normalize_optional_text(model_name)
        payload["input_asset_ids"] = self._normalize_asset_ids(
            input_asset_ids,
            "input_asset_ids",
        )
        payload["output_asset_ids"] = self._normalize_asset_ids(
            output_asset_ids,
            "output_asset_ids",
        )
        payload["job_status"] = self._normalize_optional_text(job_status)
        payload["failure_reason"] = self._normalize_optional_text(failure_reason)
        return payload

    async def reserve_ai_job_credits(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        output_asset_ids: Iterable[str] | None = None,
        job_status: str | None = None,
        failure_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
    ) -> CreditReservationResult:
        canonical_metadata = self.build_ai_job_costing_metadata(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            job_status=job_status or "reserved",
            failure_reason=failure_reason,
            metadata=metadata,
        )
        return await self.credit_gate_service.reserve_credits_for_operation(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            job_id=job_id,
            estimated_credits=estimated_credits,
            project_id=project_id,
            user_id=user_id,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=canonical_metadata,
        )

    async def consume_ai_job_credits(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        output_asset_ids: Iterable[str] | None = None,
        job_status: str | None = None,
        failure_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
    ) -> CreditConsumptionResult:
        canonical_metadata = self.build_ai_job_costing_metadata(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            job_status=job_status or "consumed",
            failure_reason=failure_reason,
            metadata=metadata,
        )
        return await self.credit_gate_service.consume_reserved_credits_for_operation(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            job_id=job_id,
            estimated_credits=estimated_credits,
            project_id=project_id,
            user_id=user_id,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=canonical_metadata,
        )

    async def release_ai_job_credits(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        job_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
        provider_type: str | None = None,
        provider_name: str | None = None,
        workflow_id: str | None = None,
        workflow_version: str | None = None,
        workflow_hash: str | None = None,
        model_name: str | None = None,
        input_asset_ids: Iterable[str] | None = None,
        output_asset_ids: Iterable[str] | None = None,
        job_status: str | None = None,
        failure_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
    ) -> CreditReleaseResult:
        canonical_metadata = self.build_ai_job_costing_metadata(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
            provider_type=provider_type,
            provider_name=provider_name,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_hash=workflow_hash,
            model_name=model_name,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            job_status=job_status or "released",
            failure_reason=failure_reason,
            metadata=metadata,
        )
        return await self.credit_gate_service.release_reserved_credits_for_operation(
            session,
            organization_id=organization_id,
            operation_type=operation_type,
            job_id=job_id,
            estimated_credits=estimated_credits,
            reason=reason,
            idempotency_key=idempotency_key,
            metadata=canonical_metadata,
        )
