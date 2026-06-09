from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from services.credit_ledger_service import (
    CreditAvailabilityResult,
    CreditConsumptionResult,
    CreditLedgerService,
    CreditReleaseResult,
    CreditReservationResult,
)


DEFAULT_OPERATION_CREDIT_COSTS = {
    "script_analysis": 1,
    "storyboard_generation": 12,
    "image_generation": 8,
    "video_generation": 40,
    "transcription": 3,
    "sound_sync": 6,
    "davinci_bridge_package": 10,
}


__all__ = [
    "DEFAULT_OPERATION_CREDIT_COSTS",
    "CreditGateError",
    "CreditCostEstimationError",
    "CreditGateEstimateResult",
    "CreditAvailabilityCheckResult",
    "CreditGateService",
]


class CreditGateError(Exception):
    """Base error for internal credit gate operations."""


class CreditCostEstimationError(CreditGateError):
    """Raised when an operation cost cannot be derived safely."""


@dataclass
class CreditGateEstimateResult:
    operation_type: str
    estimated_credits: int
    cost_source: str


@dataclass
class CreditAvailabilityCheckResult:
    organization_id: str
    operation_type: str
    required_credits: int
    available_credits: int
    sufficient: bool
    balance_id: Optional[str] = None
    status: str = ""
    message: str = ""


class CreditGateService:
    """Internal facade that wraps the credit ledger for future AI jobs."""

    def __init__(
        self,
        ledger_service: CreditLedgerService | None = None,
        operation_credit_costs: dict[str, int] | None = None,
    ) -> None:
        self.ledger_service = ledger_service or CreditLedgerService()
        self.operation_credit_costs = dict(DEFAULT_OPERATION_CREDIT_COSTS)
        if operation_credit_costs:
            self.operation_credit_costs.update(operation_credit_costs)

    def _normalize_explicit_cost(self, explicit_cost: int | None) -> int | None:
        if explicit_cost is None:
            return None
        if not isinstance(explicit_cost, int) or isinstance(explicit_cost, bool):
            raise CreditCostEstimationError("explicit estimated_credits must be an integer")
        if explicit_cost <= 0:
            raise CreditCostEstimationError(
                "explicit estimated_credits must be > 0 (got {0})".format(explicit_cost)
            )
        return explicit_cost

    def _normalize_operation_type(self, operation_type: str) -> str:
        if not isinstance(operation_type, str):
            raise CreditCostEstimationError("operation_type must be a non-empty string")
        normalized = operation_type.strip()
        if not normalized:
            raise CreditCostEstimationError("operation_type must be a non-empty string")
        return normalized

    def _resolve_operation_cost(self, operation_type: str) -> int:
        cost = self.operation_credit_costs.get(operation_type)
        if cost is None:
            raise CreditCostEstimationError(
                "Unknown operation_type {0}. Provide explicit estimated_credits.".format(
                    operation_type
                )
            )
        if cost <= 0:
            raise CreditCostEstimationError(
                "Configured cost for operation_type {0} must be > 0".format(operation_type)
            )
        return cost

    def _build_reason(self, operation_type: str, reason: str | None, action: str) -> str:
        return reason or "credit_gate.{0}.{1}".format(action, operation_type)

    def _build_metadata(
        self,
        operation_type: str,
        estimated_credits: int,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if metadata:
            payload.update(metadata)
        payload["operation_type"] = operation_type
        payload["estimated_credits"] = estimated_credits
        return payload

    def estimate_credit_cost(
        self,
        *,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditGateEstimateResult:
        normalized_operation_type = self._normalize_operation_type(operation_type)
        explicit_cost = self._normalize_explicit_cost(estimated_credits)
        if explicit_cost is not None:
            return CreditGateEstimateResult(
                operation_type=normalized_operation_type,
                estimated_credits=explicit_cost,
                cost_source="explicit",
            )

        configured_cost = self._resolve_operation_cost(normalized_operation_type)
        return CreditGateEstimateResult(
            operation_type=normalized_operation_type,
            estimated_credits=configured_cost,
            cost_source="table",
        )

    async def check_credit_availability(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        estimated_credits: int | None = None,
    ) -> CreditAvailabilityCheckResult:
        estimate = self.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        availability: CreditAvailabilityResult = await self.ledger_service.get_available_credits(
            session,
            organization_id,
        )
        available = int(availability.available_after or 0)
        return CreditAvailabilityCheckResult(
            organization_id=organization_id,
            operation_type=estimate.operation_type,
            required_credits=estimate.estimated_credits,
            available_credits=available,
            sufficient=available >= estimate.estimated_credits,
            balance_id=availability.balance_id,
            status=availability.status,
            message=availability.message,
        )

    async def reserve_credits_for_operation(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CreditReservationResult:
        estimate = self.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        return await self.ledger_service.reserve_credits(
            session,
            organization_id,
            amount=estimate.estimated_credits,
            project_id=project_id,
            user_id=user_id,
            job_id=job_id,
            reason=self._build_reason(estimate.operation_type, reason, "reserve"),
            metadata=self._build_metadata(
                estimate.operation_type, estimate.estimated_credits, metadata
            ),
            idempotency_key=idempotency_key,
        )

    async def consume_reserved_credits_for_operation(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        project_id: str | None = None,
        user_id: str | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CreditConsumptionResult:
        estimate = self.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        return await self.ledger_service.consume_reserved_credits(
            session,
            organization_id,
            amount=estimate.estimated_credits,
            project_id=project_id,
            user_id=user_id,
            job_id=job_id,
            reason=self._build_reason(estimate.operation_type, reason, "consume"),
            metadata=self._build_metadata(
                estimate.operation_type, estimate.estimated_credits, metadata
            ),
            idempotency_key=idempotency_key,
        )

    async def release_reserved_credits_for_operation(
        self,
        session: AsyncSession,
        *,
        organization_id: str,
        operation_type: str,
        job_id: str,
        estimated_credits: int | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CreditReleaseResult:
        estimate = self.estimate_credit_cost(
            operation_type=operation_type,
            estimated_credits=estimated_credits,
        )
        return await self.ledger_service.release_reserved_credits(
            session,
            organization_id,
            amount=estimate.estimated_credits,
            job_id=job_id,
            reason=self._build_reason(estimate.operation_type, reason, "release"),
            metadata=self._build_metadata(
                estimate.operation_type, estimate.estimated_credits, metadata
            ),
            idempotency_key=idempotency_key,
        )
