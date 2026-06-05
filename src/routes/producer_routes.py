from datetime import datetime
from typing import Optional, List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from dependencies.tenant_context import (
    TenantContext,
    get_tenant_context,
    require_write_permission,
)
from models.producer import DemoRequestRecord, SavedOpportunity, FundingOpportunity
from models.core import Project
from services.producer_catalog import DEMO_OPPORTUNITIES
from services.logging_service import logger


router = APIRouter(prefix="/api/producer", tags=["producer"])


def _is_admin_tenant(tenant: TenantContext) -> bool:
    return bool(
        getattr(tenant, "is_global_admin", False)
        or getattr(tenant, "role", None) == "admin"
    )


def _require_admin_tenant(tenant: TenantContext) -> None:
    if not _is_admin_tenant(tenant):
        raise HTTPException(status_code=403, detail="Admin access required")


async def _validate_producer_project_access(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
) -> Project:
    query = select(Project).where(Project.id == project_id)
    if not _is_admin_tenant(tenant):
        query = query.where(Project.organization_id == tenant.organization_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project


class DemoRequestCreate(BaseModel):
    name: str
    email: str
    organization: Optional[str] = None
    role: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = "website"


class DemoRequestResponse(BaseModel):
    id: str
    name: str
    email: str
    organization: Optional[str]
    role: Optional[str]
    message: Optional[str]
    source: Optional[str]
    status: str
    created_at: datetime


class SavedOpportunityCreate(BaseModel):
    project_id: str
    funding_opportunity_id: str
    notes: Optional[str] = None


class SavedOpportunityResponse(BaseModel):
    id: str
    project_id: str
    funding_opportunity_id: str
    notes: Optional[str]
    created_at: datetime


class DashboardResponse(BaseModel):
    saved_opportunities: int
    demo_requests: int
    funding_opportunities: int


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DashboardResponse:
    _require_admin_tenant(tenant)

    saved_result = await db.execute(select(SavedOpportunity))
    saved_count = len(saved_result.scalars().all())

    demo_result = await db.execute(select(DemoRequestRecord))
    demo_count = len(demo_result.scalars().all())

    return DashboardResponse(
        saved_opportunities=saved_count,
        demo_requests=demo_count,
        funding_opportunities=len(DEMO_OPPORTUNITIES),
    )


@router.get("/funding/opportunities")
async def list_funding_opportunities():
    return DEMO_OPPORTUNITIES


@router.get("/demo-requests", response_model=List[DemoRequestResponse])
async def list_demo_requests(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> List[DemoRequestResponse]:
    _require_admin_tenant(tenant)

    result = await db.execute(
        select(DemoRequestRecord).order_by(DemoRequestRecord.created_at.desc())
    )
    records = result.scalars().all()
    return [
        DemoRequestResponse(
            id=str(r.id),
            name=r.name,
            email=r.email,
            organization=r.organization,
            role=r.role,
            message=r.message,
            source=r.source,
            status=r.status,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.post("/demo-request", response_model=DemoRequestResponse)
async def create_demo_request(
    request: DemoRequestCreate, db: AsyncSession = Depends(get_db)
) -> DemoRequestResponse:
    record = DemoRequestRecord(
        id=uuid.uuid4().hex,
        name=request.name,
        email=request.email,
        organization=request.organization,
        role=request.role,
        message=request.message,
        source=request.source or "website",
        status="new",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return DemoRequestResponse(
        id=str(record.id),
        name=record.name,
        email=record.email,
        organization=record.organization,
        role=record.role,
        message=record.message,
        source=record.source,
        status=record.status,
        created_at=record.created_at,
    )


@router.get("/saved-opportunities", response_model=List[SavedOpportunityResponse])
async def list_saved_opportunities(
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> List[SavedOpportunityResponse]:
    query = select(SavedOpportunity)
    if project_id:
        project = await _validate_producer_project_access(db, project_id, tenant)
        validated_project_id = str(project.id)
        query = query.where(SavedOpportunity.project_id == validated_project_id)
    else:
        _require_admin_tenant(tenant)

    result = await db.execute(query.order_by(SavedOpportunity.created_at.desc()))
    records = result.scalars().all()

    return [
        SavedOpportunityResponse(
            id=str(r.id),
            project_id=r.project_id,
            funding_opportunity_id=r.funding_opportunity_id,
            notes=r.notes,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.post("/saved-opportunities", response_model=SavedOpportunityResponse)
async def create_saved_opportunity(
    request: SavedOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
) -> SavedOpportunityResponse:
    project = await _validate_producer_project_access(db, request.project_id, tenant)
    validated_project_id = str(project.id)

    opportunity_id = request.funding_opportunity_id
    valid_ids = [opp["id"] for opp in DEMO_OPPORTUNITIES]
    if opportunity_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")

    existing = await db.execute(
        select(SavedOpportunity).where(
            SavedOpportunity.project_id == validated_project_id,
            SavedOpportunity.funding_opportunity_id == request.funding_opportunity_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Opportunity already saved for this project"
        )

    saved = SavedOpportunity(
        id=uuid.uuid4().hex,
        project_id=validated_project_id,
        funding_opportunity_id=request.funding_opportunity_id,
        notes=request.notes,
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)

    return SavedOpportunityResponse(
        id=str(saved.id),
        project_id=validated_project_id,
        funding_opportunity_id=saved.funding_opportunity_id,
        notes=saved.notes,
        created_at=saved.created_at,
    )


@router.delete("/saved-opportunities/{saved_id}")
async def delete_saved_opportunity(
    saved_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    result = await db.execute(
        select(SavedOpportunity).where(SavedOpportunity.id == saved_id)
    )
    saved = result.scalar_one_or_none()

    if not saved:
        raise HTTPException(status_code=404, detail="Saved opportunity not found")

    await _validate_producer_project_access(db, saved.project_id, tenant)

    await db.delete(saved)
    await db.commit()

    return {"status": "deleted", "id": saved_id}
