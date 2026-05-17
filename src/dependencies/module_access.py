from __future__ import annotations

from fastapi import Depends, HTTPException

from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from services.account_service import normalize_plan_name
from services.module_catalog_service import (
    ModuleCatalogError,
    ModuleNotFoundError,
    module_catalog_service,
)


def require_module_access(module_key: str):
    async def _dependency(
        tenant: TenantContext = Depends(get_tenant_context),
    ) -> TenantContext:
        plan_name = normalize_plan_name(getattr(tenant, "plan", "free"))
        try:
            access_state = module_catalog_service.get_module_access_state(
                plan_name,
                module_key,
            )
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ModuleCatalogError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        if not access_state.enabled:
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
