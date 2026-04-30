from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.funding_ingestion_service import funding_ingestion_service


router = APIRouter(prefix="/api/funding", tags=["funding-catalog"])


@router.get("/opportunities")
async def list_funding_opportunities(
    region_scope: str | None = Query(default=None),
    phase: str | None = Query(default=None),
    opportunity_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    source_code: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    opportunities = await funding_ingestion_service.list_calls(
        db,
        region_scope=region_scope,
        phase=phase,
        opportunity_type=opportunity_type,
        status=status,
        source_code=source_code,
    )
    return JSONResponse(content={"count": len(opportunities), "opportunities": opportunities})


@router.get("/opportunities/{opportunity_id}")
async def get_funding_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
):
    opportunity = await funding_ingestion_service.get_call(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return JSONResponse(content=opportunity)
