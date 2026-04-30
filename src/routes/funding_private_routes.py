from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.production import PrivateFundingSource, PrivateOpportunity, FundingCall, FundingSource as PublicFundingSource
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.funding_alert_service import funding_alert_service


private_source_router = APIRouter(prefix="/api/funding", tags=["funding-private"])


class PrivateSourceCreate(BaseModel):
    name: str
    source_type: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    amount_range: Optional[str] = None
    eligibility_criteria: Optional[str] = None


class PrivateOpportunityCreate(BaseModel):
    source_id: str
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None
    opportunity_type: Optional[str] = None
    phase: Optional[str] = None
    deadline: Optional[datetime] = None
    requirements: Optional[str] = None


@private_source_router.get("/sources/private")
async def list_private_sources(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(PrivateFundingSource)
        .where(PrivateFundingSource.organization_id == tenant.organization_id)
        .order_by(PrivateFundingSource.name.asc())
    )
    sources = result.scalars().all()

    return JSONResponse(content={
        "count": len(sources),
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "source_type": s.source_type,
                "description": s.description,
                "contact_info": s.contact_info,
                "amount_range": s.amount_range,
                "eligibility_criteria": s.eligibility_criteria,
                "status": s.status,
            }
            for s in sources
        ]
    })


@private_source_router.post("/sources/private", response_model=PrivateSourceCreate)
async def create_private_source(
    payload: PrivateSourceCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    source = PrivateFundingSource(
        organization_id=tenant.organization_id,
        name=payload.name,
        source_type=payload.source_type,
        description=payload.description,
        contact_info=payload.contact_info,
        amount_range=payload.amount_range,
        eligibility_criteria=payload.eligibility_criteria,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    return JSONResponse(content={
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
    })


@private_source_router.put("/sources/private/{source_id}")
async def update_private_source(
    source_id: str,
    payload: PrivateSourceCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(PrivateFundingSource).where(
            PrivateFundingSource.id == source_id,
            PrivateFundingSource.organization_id == tenant.organization_id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    source.name = payload.name
    source.source_type = payload.source_type
    source.description = payload.description
    source.contact_info = payload.contact_info
    source.amount_range = payload.amount_range
    source.eligibility_criteria = payload.eligibility_criteria
    await db.commit()

    return JSONResponse(content={"id": source.id, "status": "updated"})


@private_source_router.delete("/sources/private/{source_id}")
async def delete_private_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(PrivateFundingSource).where(
            PrivateFundingSource.id == source_id,
            PrivateFundingSource.organization_id == tenant.organization_id,
        )
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    await db.delete(source)
    await db.commit()

    return JSONResponse(content={"status": "deleted"})


@private_source_router.get("/opportunities/private")
async def list_private_opportunities(
    source_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    query = select(PrivateOpportunity).where(PrivateOpportunity.organization_id == tenant.organization_id)
    if source_id:
        query = query.where(PrivateOpportunity.source_id == source_id)

    result = await db.execute(query.order_by(PrivateOpportunity.deadline.asc()))
    opportunities = result.scalars().all()

    return JSONResponse(content={
        "count": len(opportunities),
        "opportunities": [
            {
                "id": o.id,
                "source_id": o.source_id,
                "title": o.title,
                "description": o.description,
                "amount": o.amount,
                "opportunity_type": o.opportunity_type,
                "phase": o.phase,
                "deadline": o.deadline.isoformat() if o.deadline else None,
                "requirements": o.requirements,
                "status": o.status,
            }
            for o in opportunities
        ]
    })


@private_source_router.post("/opportunities/private")
async def create_private_opportunity(
    payload: PrivateOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    source_result = await db.execute(
        select(PrivateFundingSource).where(
            PrivateFundingSource.id == payload.source_id,
            PrivateFundingSource.organization_id == tenant.organization_id,
        )
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    opp = PrivateOpportunity(
        organization_id=tenant.organization_id,
        source_id=payload.source_id,
        title=payload.title,
        description=payload.description,
        amount=payload.amount,
        opportunity_type=payload.opportunity_type,
        phase=payload.phase,
        deadline=payload.deadline,
        requirements=payload.requirements,
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)

    return JSONResponse(content={"id": opp.id, "title": opp.title})


@private_source_router.get("/dashboard/opportunities")
async def get_opportunities_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    public_result = await db.execute(
        select(FundingCall).where(FundingCall.status == "open")
    )
    public_calls = list(public_result.scalars().all())

    public_sources_result = await db.execute(
        select(PublicFundingSource)
    )
    public_sources = list(public_sources_result.scalars().all())
    public_sources_map = {s.id: s.name for s in public_sources}

    private_sources_result = await db.execute(
        select(PrivateFundingSource).where(
            PrivateFundingSource.organization_id == tenant.organization_id,
            PrivateFundingSource.status == "active",
        )
    )
    private_sources = list(private_sources_result.scalars().all())

    private_opps_result = await db.execute(
        select(PrivateOpportunity).where(
            PrivateOpportunity.organization_id == tenant.organization_id,
            PrivateOpportunity.status == "open",
        )
    )
    private_opps = list(private_opps_result.scalars().all())

    public_by_region = {"spain": 0, "europe": 0, "iberoamerica_latam": 0}
    for call in public_calls:
        region = call.region or "spain"
        if region in public_by_region:
            public_by_region[region] += 1

    private_by_type = {}
    for source in private_sources:
        stype = source.source_type or "unknown"
        private_by_type[stype] = private_by_type.get(stype, 0) + 1

    deadline_opps = sorted(
        [o for o in private_opps if o.deadline],
        key=lambda x: x.deadline
    )[:5]

    return JSONResponse(content={
        "summary": {
            "public_opportunities": len(public_calls),
            "private_opportunities": len(private_opps),
            "private_sources": len(private_sources),
        },
        "public_by_region": public_by_region,
        "private_by_type": private_by_type,
        "upcoming_deadlines": [
            {
                "title": o.title,
                "deadline": o.deadline.isoformat() if o.deadline else None,
                "amount": o.amount,
            }
            for o in deadline_opps
        ],
    })


@private_source_router.get("/alerts")
async def get_funding_alerts(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    organization_id = tenant.organization_id

    alerts = await funding_alert_service.get_funding_dashboard_alerts(
        db, organization_id, project_id
    )

    return JSONResponse(content=alerts)