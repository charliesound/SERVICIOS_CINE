from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.funding_catalog_schema import (
    FundingCallCreate,
    FundingCallUpdate,
    FundingSeedRequest,
    FundingSourceCreate,
)
from services.funding_ingestion_service import funding_ingestion_service


router = APIRouter(prefix="/api/admin/funding", tags=["admin-funding"])


def _require_admin(tenant: TenantContext) -> None:
    if not tenant.is_global_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")


@router.get("/sources")
async def list_funding_sources(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    sources = await funding_ingestion_service.list_sources(db)
    return JSONResponse(content={"count": len(sources), "sources": sources})


@router.post("/sources", status_code=201)
async def create_funding_source(
    payload: FundingSourceCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    source = await funding_ingestion_service.create_source(db, payload.model_dump())
    return JSONResponse(status_code=201, content=source)


@router.get("/calls")
async def list_funding_calls(
    region_scope: str | None = Query(default=None),
    phase: str | None = Query(default=None),
    opportunity_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    source_code: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    calls = await funding_ingestion_service.list_calls(
        db,
        region_scope=region_scope,
        phase=phase,
        opportunity_type=opportunity_type,
        status=status,
        source_code=source_code,
    )
    return JSONResponse(content={"count": len(calls), "calls": calls})


@router.post("/calls", status_code=201)
async def create_funding_call(
    payload: FundingCallCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    try:
        call = await funding_ingestion_service.create_call(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return JSONResponse(status_code=201, content=call)


@router.patch("/calls/{call_id}")
async def update_funding_call(
    call_id: str,
    payload: FundingCallUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    call = await funding_ingestion_service.update_call(
        db, call_id, payload.model_dump(exclude_unset=True)
    )
    if call is None:
        raise HTTPException(status_code=404, detail="Funding call not found")
    return JSONResponse(content=call)


@router.get("/calls/{call_id}")
async def get_funding_call(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    call = await funding_ingestion_service.get_call(db, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Funding call not found")
    return JSONResponse(content=call)


@router.post("/sync/seed")
async def sync_seed_funding_catalog(
    payload: FundingSeedRequest | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    result = await funding_ingestion_service.seed_catalog(
        db, force=bool(payload.force if payload else False)
    )
    return JSONResponse(content=result)


@router.post("/sync/mock-refresh")
async def sync_mock_refresh_funding_catalog(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    _require_admin(tenant)
    result = await funding_ingestion_service.seed_catalog(db, force=True)
    return JSONResponse(content=result)
