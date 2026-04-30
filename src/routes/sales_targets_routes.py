from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.sales_target_service import (
    create_sales_target,
    get_sales_target,
    list_sales_targets,
    suggest_sales_targets_for_project,
    create_sales_opportunity,
    update_sales_opportunity,
    list_project_sales_opportunities,
)
from models.distribution import SALES_TARGET_TYPES, SALES_OPPORTUNITY_STATUS


router = APIRouter(prefix="/api", tags=["sales-targets"])


class SalesTargetCreate(BaseModel):
    name: str
    target_type: str = "distributor"
    country: Optional[str] = None
    region: Optional[str] = None
    genres_json: Optional[list] = None
    formats_json: Optional[list] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class SalesOpportunityCreate(BaseModel):
    sales_target_id: Optional[str] = None
    distribution_pack_id: Optional[str] = None
    target_type: str = "distributor"


class SalesOpportunityUpdate(BaseModel):
    status: Optional[str] = None
    fit_score: Optional[int] = None
    fit_summary: Optional[str] = None
    recommended_pitch_angle: Optional[str] = None
    next_action: Optional[str] = None
    notes: Optional[str] = None


@router.get("/sales-targets")
async def list_sales_targets_endpoint(
    target_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    targets = await list_sales_targets(
        db,
        tenant.organization_id,
        target_type=target_type,
        status=status,
    )
    return JSONResponse(content={
        "count": len(targets),
        "targets": [
            {
                "id": t.id,
                "name": t.name,
                "target_type": t.target_type,
                "country": t.country,
                "region": t.region,
                "source_type": t.source_type,
                "status": t.status,
            }
            for t in targets
        ],
    })


@router.post("/sales-targets")
async def create_sales_target_endpoint(
    payload: SalesTargetCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    if payload.target_type not in SALES_TARGET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid target type")

    target = await create_sales_target(
        db,
        tenant.organization_id,
        payload.model_dump(),
    )
    return JSONResponse(content={
        "target_id": target.id,
        "name": target.name,
    })


@router.get("/sales-targets/{target_id}")
async def get_sales_target_endpoint(
    target_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    target = await get_sales_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Sales target not found")

    return JSONResponse(content={"target": {
        "id": target.id,
        "name": target.name,
        "target_type": target.target_type,
        "country": target.country,
        "region": target.region,
        "genres": target.genres_json,
        "formats": target.formats_json,
        "contact_name": target.contact_name,
        "email": target.email,
        "website": target.website,
        "notes": target.notes,
        "source_type": target.source_type,
    }})


@router.patch("/sales-targets/{target_id}")
async def update_sales_target_endpoint(
    target_id: str,
    payload: SalesTargetCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    target = await get_sales_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Sales target not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        if value is not None:
            setattr(target, field, value)

    await db.commit()
    return JSONResponse(content={"target_id": target.id})


@router.get("/projects/{project_id}/sales-opportunities")
async def list_project_sales_opportunities_endpoint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    opps = await list_project_sales_opportunities(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(opps),
        "opportunities": [
            {
                "id": o.id,
                "target_type": o.target_type,
                "status": o.status,
                "fit_score": o.fit_score,
                "fit_summary": o.fit_summary,
                "next_action": o.next_action,
            }
            for o in opps
        ],
    })


@router.post("/projects/{project_id}/sales-opportunities/suggest")
async def suggest_sales_opportunities_endpoint(
    project_id: str,
    target_type: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    targets = await suggest_sales_targets_for_project(
        db,
        project_id,
        tenant.organization_id,
        target_type=target_type,
    )
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(targets),
        "suggested_targets": [
            {
                "id": t.id,
                "name": t.name,
                "target_type": t.target_type,
                "country": t.country,
                "source_type": t.source_type,
            }
            for t in targets
        ],
    })


@router.post("/projects/{project_id}/sales-opportunities")
async def create_sales_opportunity_endpoint(
    project_id: str,
    payload: SalesOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    opp = await create_sales_opportunity(
        db,
        project_id,
        tenant.organization_id,
        sales_target_id=payload.sales_target_id,
        distribution_pack_id=payload.distribution_pack_id,
        target_type=payload.target_type,
    )
    return JSONResponse(content={
        "opportunity_id": opp.id,
        "status": opp.status,
    })


@router.patch("/projects/{project_id}/sales-opportunities/{opportunity_id}")
async def update_sales_opportunity_endpoint(
    project_id: str,
    opportunity_id: str,
    payload: SalesOpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        opp = await update_sales_opportunity(
            db,
            opportunity_id,
            payload.model_dump(exclude_none=True),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "opportunity_id": opp.id,
        "status": opp.status,
    })