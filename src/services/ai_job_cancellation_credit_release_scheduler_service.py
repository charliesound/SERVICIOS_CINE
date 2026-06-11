from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable

DANGEROUS_ORG_IDS = frozenset({"*", "all", "all-tenants", "global"})
SECRET_ERROR_MESSAGE = "tenant processing failed; inspect internal logs"
MAX_ITEMS_DEFAULT = 50
MAX_ITEMS_CAP = 100
REQUESTED_BY_DEFAULT = "scheduler"


@dataclass(frozen=True)
class AIJobCancellationCreditReleaseSchedulerTenantConfig:
    organization_id: str
    max_items: int = MAX_ITEMS_DEFAULT
    enabled: bool = True


@dataclass(frozen=True)
class AIJobCancellationCreditReleaseSchedulerTickRequest:
    enabled: bool = True
    dry_run: bool = False
    requested_by: str = REQUESTED_BY_DEFAULT
    tenants: tuple[AIJobCancellationCreditReleaseSchedulerTenantConfig, ...] = ()


@dataclass(frozen=True)
class AIJobCancellationCreditReleaseSchedulerTenantResult:
    organization_id: str
    status: str  # "processed" | "disabled" | "failed"
    max_items: int
    scanned_count: int = 0
    processed_count: int = 0
    released_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    error_message: str | None = None


@dataclass(frozen=True)
class AIJobCancellationCreditReleaseSchedulerTickResult:
    scheduler_run_id: str
    enabled: bool
    dry_run: bool
    requested_by: str
    tenant_count: int
    processed_tenant_count: int = 0
    skipped_tenant_count: int = 0
    failed_tenant_count: int = 0
    total_scanned_count: int = 0
    total_processed_count: int = 0
    total_released_count: int = 0
    total_skipped_count: int = 0
    total_failed_count: int = 0
    per_tenant_results: tuple[AIJobCancellationCreditReleaseSchedulerTenantResult, ...] = ()


def _validate_tick_request(request: AIJobCancellationCreditReleaseSchedulerTickRequest) -> None:
    requested_by = request.requested_by.strip() if request.requested_by else ""
    if not requested_by:
        raise ValueError("requested_by must be non-empty")

    seen: set[str] = set()
    for tenant in request.tenants:
        org_id = tenant.organization_id.strip() if tenant.organization_id else ""
        normalized = org_id.lower()
        if not org_id:
            raise ValueError("organization_id must be explicit and non-empty")
        if normalized in DANGEROUS_ORG_IDS:
            raise ValueError(
                f"Rejected dangerous organization_id: {org_id!r}"
            )
        if normalized in seen:
            raise ValueError(
                f"Duplicate organization_id: {org_id!r}"
            )
        seen.add(normalized)

        if tenant.max_items <= 0:
            raise ValueError(
                f"max_items must be >= 1, got {tenant.max_items} for {org_id}"
            )


class AIJobCancellationCreditReleaseSchedulerService:
    def __init__(
        self,
        *,
        orchestration_service: Any,
        session_provider: Callable[[], AsyncIterator[Any]],
    ) -> None:
        self._orchestration_service = orchestration_service
        self._session_provider = session_provider

    async def run_tick(
        self,
        request: AIJobCancellationCreditReleaseSchedulerTickRequest,
    ) -> AIJobCancellationCreditReleaseSchedulerTickResult:
        run_id = uuid.uuid4().hex[:12]

        if not request.enabled:
            return AIJobCancellationCreditReleaseSchedulerTickResult(
                scheduler_run_id=run_id,
                enabled=False,
                dry_run=request.dry_run,
                requested_by=request.requested_by,
                tenant_count=0,
                processed_tenant_count=0,
                skipped_tenant_count=0,
                failed_tenant_count=0,
            )

        tenants = request.tenants
        if not tenants:
            return AIJobCancellationCreditReleaseSchedulerTickResult(
                scheduler_run_id=run_id,
                enabled=True,
                dry_run=request.dry_run,
                requested_by=request.requested_by,
                tenant_count=0,
            )

        _validate_tick_request(request)

        per_tenant: list[AIJobCancellationCreditReleaseSchedulerTenantResult] = []
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        total_scanned = 0
        total_processed = 0
        total_released = 0
        total_skipped = 0
        total_failed = 0

        for tenant in tenants:
            org_id = tenant.organization_id.strip()
            max_items = tenant.max_items
            if max_items > MAX_ITEMS_CAP:
                max_items = MAX_ITEMS_CAP

            if not tenant.enabled:
                per_tenant.append(
                    AIJobCancellationCreditReleaseSchedulerTenantResult(
                        organization_id=org_id,
                        status="disabled",
                        max_items=max_items,
                    )
                )
                skipped_count += 1
                continue

            try:
                from services.ai_job_async_orchestration_service import (
                    AIJobAsyncCancelCreditReleaseReconciliationRequest,
                )

                reconcile_request = AIJobAsyncCancelCreditReleaseReconciliationRequest(
                    organization_id=org_id,
                    max_items=max_items,
                    dry_run=request.dry_run,
                    requested_by=request.requested_by.strip(),
                )

                async with self._session_provider() as session:
                    try:
                        result = await self._orchestration_service.process_cancelled_ai_job_credit_releases(
                            session, reconcile_request
                        )
                    except Exception:
                        rollback_fn = getattr(session, "rollback", None)
                        if rollback_fn is not None:
                            try:
                                await rollback_fn()
                            except Exception:
                                pass
                        raise

                    await session.commit()

                per_tenant.append(
                    AIJobCancellationCreditReleaseSchedulerTenantResult(
                        organization_id=org_id,
                        status="processed",
                        max_items=max_items,
                        scanned_count=getattr(result, "scanned_count", 0) or 0,
                        processed_count=getattr(result, "processed_count", 0) or 0,
                        released_count=getattr(result, "released_count", 0) or 0,
                        skipped_count=getattr(result, "skipped_count", 0) or 0,
                        failed_count=getattr(result, "failed_count", 0) or 0,
                    )
                )
                processed_count += 1
                total_scanned += getattr(result, "scanned_count", 0) or 0
                total_processed += getattr(result, "processed_count", 0) or 0
                total_released += getattr(result, "released_count", 0) or 0
                total_skipped += getattr(result, "skipped_count", 0) or 0
                total_failed += getattr(result, "failed_count", 0) or 0

            except Exception:
                per_tenant.append(
                    AIJobCancellationCreditReleaseSchedulerTenantResult(
                        organization_id=org_id,
                        status="failed",
                        max_items=max_items,
                        error_message=SECRET_ERROR_MESSAGE,
                    )
                )
                failed_count += 1

        return AIJobCancellationCreditReleaseSchedulerTickResult(
            scheduler_run_id=run_id,
            enabled=True,
            dry_run=request.dry_run,
            requested_by=request.requested_by,
            tenant_count=len(tenants),
            processed_tenant_count=processed_count,
            skipped_tenant_count=skipped_count,
            failed_tenant_count=failed_count,
            total_scanned_count=total_scanned,
            total_processed_count=total_processed,
            total_released_count=total_released,
            total_skipped_count=total_skipped,
            total_failed_count=total_failed,
            per_tenant_results=tuple(per_tenant),
        )
