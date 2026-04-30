from __future__ import annotations

import io
import zipfile
from typing import Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.distribution_pack_service import (
    generate_distribution_pack,
    get_distribution_pack,
    get_active_distribution_pack,
    list_distribution_packs,
    update_distribution_pack,
    approve_distribution_pack,
    archive_distribution_pack,
    export_distribution_pack_json,
    export_distribution_pack_markdown,
)
from models.distribution import PACK_TYPE


router = APIRouter(prefix="/api/projects", tags=["distribution"])


class DistributionPackUpdate(BaseModel):
    title: Optional[str] = None
    logline: Optional[str] = None
    short_synopsis: Optional[str] = None
    commercial_positioning: Optional[str] = None
    target_audience: Optional[str] = None


class GenerateDistributionPayload(BaseModel):
    pack_type: str = "general_sales"


@router.get("/{project_id}/distribution-packs")
async def list_distribution_packs_endpoint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    packs = await list_distribution_packs(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(packs),
        "packs": [
            {
                "id": p.id,
                "title": p.title,
                "pack_type": p.pack_type,
                "status": p.status,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in packs
        ],
    })


@router.post("/{project_id}/distribution-packs/generate")
async def generate_distribution_pack_endpoint(
    project_id: str,
    payload: GenerateDistributionPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible")

    if payload.pack_type not in PACK_TYPE:
        raise HTTPException(status_code=400, detail="Invalid pack type")

    try:
        pack = await generate_distribution_pack(
            db,
            project_id,
            tenant.organization_id,
            pack_type=payload.pack_type,
            created_by=tenant.user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
        "pack_type": pack.pack_type,
    })


@router.get("/{project_id}/distribution-packs/{pack_id}")
async def get_distribution_pack_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    return JSONResponse(content={"pack": {
        "id": pack.id,
        "project_id": pack.project_id,
        "title": pack.title,
        "pack_type": pack.pack_type,
        "status": pack.status,
        "logline": pack.logline,
        "short_synopsis": pack.short_synopsis,
        "commercial_positioning": pack.commercial_positioning,
        "target_audience": pack.target_audience,
        "comparable_titles": pack.comparable_titles_json,
        "release_strategy": pack.release_strategy_json,
        "exploitation_windows": pack.exploitation_windows_json,
        "territory_strategy": pack.territory_strategy_json,
        "marketing_hooks": pack.marketing_hooks_json,
        "available_materials": pack.available_materials_json,
        "technical_specs": pack.technical_specs_json,
        "sales_arguments": pack.sales_arguments_json,
        "risks": pack.risks_json,
    }})


@router.patch("/{project_id}/distribution-packs/{pack_id}")
async def update_distribution_pack_endpoint(
    project_id: str,
    pack_id: str,
    payload: DistributionPackUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    try:
        pack = await update_distribution_pack(db, pack_id, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
    })


@router.post("/{project_id}/distribution-packs/{pack_id}/approve")
async def approve_distribution_pack_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    try:
        pack = await approve_distribution_pack(db, pack_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
    })


@router.post("/{project_id}/distribution-packs/{pack_id}/archive")
async def archive_distribution_pack_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    try:
        pack = await archive_distribution_pack(db, pack_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
    })


@router.get("/{project_id}/distribution-packs/{pack_id}/export/json")
async def export_distribution_pack_json_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    return JSONResponse(content=export_distribution_pack_json(pack))


@router.get("/{project_id}/distribution-packs/{pack_id}/export/markdown")
async def export_distribution_pack_markdown_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    markdown = export_distribution_pack_markdown(pack)
    return Response(content=markdown.encode("utf-8"), media_type="text/markdown")


@router.get("/{project_id}/distribution-packs/{pack_id}/export/zip")
async def export_distribution_pack_zip_endpoint(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_distribution_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Distribution pack not found")

    json_data = export_distribution_pack_json(pack)
    markdown = export_distribution_pack_markdown(pack)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("distribution_pack.json", str(json_data))
        zf.writestr("distribution_pack.md", markdown)

    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=distribution_pack_{pack_id}.zip"},
    )