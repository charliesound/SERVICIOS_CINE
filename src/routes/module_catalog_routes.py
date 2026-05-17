from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.module_catalog_schema import (
    ModuleAccessInfo,
    ModuleCatalogResponse,
    ModuleInfo,
    UserModulesResponse,
)
from services.account_service import get_user_by_id, normalize_plan_name, resolve_effective_plan
from services.module_catalog_service import (
    ModuleCatalogError,
    ModuleNotFoundError,
    module_catalog_service,
)

router = APIRouter(prefix="/api/modules", tags=["modules"])


def _serialize_module(module) -> ModuleInfo:
    return ModuleInfo(**module_catalog_service.to_dict(module))


def _serialize_module_access(module, *, enabled: bool, locked_reason: str | None = None) -> ModuleAccessInfo:
    payload = module_catalog_service.to_dict(module)
    payload.update({
        "enabled": enabled,
        "locked_reason": locked_reason,
    })
    return ModuleAccessInfo(**payload)


@router.get("/catalog", response_model=ModuleCatalogResponse)
async def get_module_catalog():
    modules = module_catalog_service.get_visible_modules()
    return ModuleCatalogResponse(
        modules=[_serialize_module(module) for module in modules],
        total=len(modules),
    )


@router.get("/me", response_model=UserModulesResponse)
async def get_my_modules(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse | None = Depends(get_current_user_optional),
):
    plan_name = "free"
    organization_id: str | None = None

    if current_user is not None:
        db_user = await get_user_by_id(db, current_user.user_id)
        if db_user is not None:
            plan_name = await resolve_effective_plan(db, db_user)
            organization_id = (
                str(db_user.organization_id)
                if getattr(db_user, "organization_id", None)
                else None
            )
        else:
            plan_name = normalize_plan_name(current_user.plan)

    plan_name = normalize_plan_name(plan_name)
    modules = module_catalog_service.get_visible_modules()
    available_modules: list[ModuleAccessInfo] = []
    locked_modules: list[ModuleAccessInfo] = []
    for module in modules:
        access_state = module_catalog_service.get_module_access_state(plan_name, module.key)
        if access_state.enabled:
            available_modules.append(
                _serialize_module_access(module, enabled=True)
            )
        else:
            locked_modules.append(
                _serialize_module_access(
                    module,
                    enabled=False,
                    locked_reason=access_state.locked_reason,
                )
            )

    return UserModulesResponse(
        plan=plan_name,
        organization_id=organization_id,
        available_modules=available_modules,
        locked_modules=locked_modules,
        total_available=len(available_modules),
        total_locked=len(locked_modules),
    )


@router.get("/{module_key}", response_model=ModuleInfo)
async def get_module_detail(module_key: str):
    try:
        module = module_catalog_service.get_module_by_key(module_key)
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ModuleCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _serialize_module(module)
