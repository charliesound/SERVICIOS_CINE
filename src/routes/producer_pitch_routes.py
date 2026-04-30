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
from services.producer_pitch_service import (
    generate_pitch_pack,
    get_pitch_pack,
    get_active_pitch_pack,
    list_pitch_packs,
    update_pitch_pack,
    approve_pitch_pack,
    archive_pitch_pack,
    export_pitch_json,
    export_pitch_markdown,
)


router = APIRouter(prefix="/api/projects", tags=["producer-pitch"])


class PitchPackUpdate(BaseModel):
    title: Optional[str] = None
    logline: Optional[str] = None
    short_synopsis: Optional[str] = None
    long_synopsis: Optional[str] = None
    intention_note: Optional[str] = None
    genre: Optional[str] = None
    format: Optional[str] = None
    tone: Optional[str] = None
    target_audience: Optional[str] = None


@router.get("/{project_id}/producer-pitch")
async def list_producer_pitch_packs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    packs = await list_pitch_packs(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "count": len(packs),
        "packs": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "logline": p.logline,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in packs
        ],
    })


@router.get("/{project_id}/producer-pitch/active")
async def get_active_producer_pitch_pack(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_active_pitch_pack(db, project_id)
    if not pack:
        raise HTTPException(status_code=404, detail="No pitch pack found")
    return JSONResponse(content={"pack": {
        "id": pack.id,
        "title": pack.title,
        "status": pack.status,
        "logline": pack.logline,
        "short_synopsis": pack.short_synopsis,
        "long_synopsis": pack.long_synopsis,
        "intention_note": pack.intention_note,
        "genre": pack.genre,
        "format": pack.format,
        "tone": pack.tone,
        "target_audience": pack.target_audience,
        "commercial_strengths": pack.commercial_strengths_json,
        "production_needs": pack.production_needs_json,
        "budget_summary": pack.budget_summary_json,
        "funding_summary": pack.funding_summary_json,
        "storyboard_selection": pack.storyboard_selection_json,
        "risks": pack.risks_json,
    }})


@router.post("/{project_id}/producer-pitch/generate")
async def generate_producer_pitch_pack(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible")

    try:
        pack = await generate_pitch_pack(
            db,
            project_id,
            tenant.organization_id,
            created_by=tenant.user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
        "message": "Pitch pack generated successfully",
    })


@router.get("/{project_id}/producer-pitch/{pack_id}")
async def get_producer_pitch_pack(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    return JSONResponse(content={"pack": {
        "id": pack.id,
        "project_id": pack.project_id,
        "title": pack.title,
        "status": pack.status,
        "logline": pack.logline,
        "short_synopsis": pack.short_synopsis,
        "long_synopsis": pack.long_synopsis,
        "intention_note": pack.intention_note,
        "genre": pack.genre,
        "format": pack.format,
        "tone": pack.tone,
        "target_audience": pack.target_audience,
        "commercial_strengths": pack.commercial_strengths_json,
        "production_needs": pack.production_needs_json,
        "budget_summary": pack.budget_summary_json,
        "funding_summary": pack.funding_summary_json,
        "storyboard_selection": pack.storyboard_selection_json,
        "risks": pack.risks_json,
        "created_at": pack.created_at.isoformat() if pack.created_at else None,
        "updated_at": pack.updated_at.isoformat() if pack.updated_at else None,
    }})


@router.patch("/{project_id}/producer-pitch/{pack_id}")
async def update_producer_pitch_pack(
    project_id: str,
    pack_id: str,
    payload: PitchPackUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    try:
        pack = await update_pitch_pack(db, pack_id, payload.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
        "message": "Pitch pack updated",
    })


@router.post("/{project_id}/producer-pitch/{pack_id}/approve")
async def approve_producer_pitch_pack(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    try:
        pack = await approve_pitch_pack(db, pack_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
        "message": "Pitch pack approved",
    })


@router.post("/{project_id}/producer-pitch/{pack_id}/archive")
async def archive_producer_pitch_pack(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    try:
        pack = await archive_pitch_pack(db, pack_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={
        "pack_id": pack.id,
        "status": pack.status,
        "message": "Pitch pack archived",
    })


@router.get("/{project_id}/producer-pitch/{pack_id}/export/json")
async def export_producer_pitch_json(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    return JSONResponse(content=export_pitch_json(pack))


@router.get("/{project_id}/producer-pitch/{pack_id}/export/markdown")
async def export_producer_pitch_markdown(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    markdown = export_pitch_markdown(pack)
    return Response(content=markdown.encode("utf-8"), media_type="text/markdown")


@router.get("/{project_id}/producer-pitch/{pack_id}/export/zip")
async def export_producer_pitch_zip(
    project_id: str,
    pack_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    pack = await get_pitch_pack(db, pack_id)
    if not pack or pack.project_id != project_id:
        raise HTTPException(status_code=404, detail="Pitch pack not found")

    json_data = export_pitch_json(pack)
    markdown = export_pitch_markdown(pack)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("pitch_pack.json", str(json_data))
        zf.writestr("pitch_pack.md", markdown)

    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=pitch_pack_{pack_id}.zip"},
    )