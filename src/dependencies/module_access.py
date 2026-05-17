from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, Request

from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from services.account_service import normalize_plan_name
from services.module_catalog_service import (
    ModuleCatalogError,
    ModuleNotFoundError,
    module_catalog_service,
)

logger = logging.getLogger("servicios_cine.module_access")


def _log_module_event(
    event: str,
    module_key: str,
    tenant: TenantContext,
    request: Request = None,
    *,
    plan: str = "",
    locked_reason: str = "",
) -> None:
    parts = [
        f"event={event}",
        f"module={module_key}",
        f"source=module_access_dependency",
        f"user_id={tenant.user_id}",
        f"organization_id={tenant.organization_id}",
        f"role={tenant.role}",
        f"is_admin={str(tenant.is_admin).lower()}",
    ]
    if plan:
        parts.append(f"plan={plan}")
    if locked_reason:
        parts.append(f"locked_reason={locked_reason}")
    if request is not None:
        parts.append(f"path={request.url.path}")
        parts.append(f"method={request.method}")
        rid = getattr(request.state, "request_id", None)
        if rid:
            parts.append(f"request_id={rid}")

    msg = " | ".join(parts)
    if "BLOCKED" in event or "ERROR" in event:
        logger.warning(msg)
    else:
        logger.info(msg)


def require_module_access(module_key: str):
    async def _dependency(
        tenant: TenantContext = Depends(get_tenant_context),
        request: Request = None,
    ) -> TenantContext:
        if tenant.is_admin or tenant.is_global_admin:
            _log_module_event("MODULE_ACCESS_GRANTED_BY_ADMIN", module_key, tenant, request)
            return tenant

        plan_name = normalize_plan_name(getattr(tenant, "plan", "free"))
        try:
            access_state = module_catalog_service.get_module_access_state(
                plan_name,
                module_key,
            )
        except ModuleNotFoundError as exc:
            _log_module_event(
                "MODULE_ACCESS_ERROR", module_key, tenant, request,
                plan=plan_name, locked_reason=f"module_not_found:{module_key}",
            )
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ModuleCatalogError as exc:
            _log_module_event(
                "MODULE_ACCESS_ERROR", module_key, tenant, request,
                plan=plan_name, locked_reason="catalog_error",
            )
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        if not access_state.enabled:
            _log_module_event(
                "MODULE_ACCESS_BLOCKED", module_key, tenant, request,
                plan=plan_name, locked_reason=access_state.locked_reason,
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "MODULE_ACCESS_BLOCKED",
                    "module": module_key,
                    "plan": plan_name,
                    "reason": access_state.locked_reason,
                },
            )
        return tenant

    return _dependency
