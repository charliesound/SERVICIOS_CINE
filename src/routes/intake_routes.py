from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext
from services.script_intake_service import script_intake_service, analysis_service


router = APIRouter(prefix="/api/projects", tags=["intake"])


class IdeaIntakePayload(BaseModel):
    title: str
    logline: Optional[str] = None
    synopsis: Optional[str] = None
    genre: Optional[str] = None


class ScriptIntakePayload(BaseModel):
    script_text: str


@router.post("/intake/idea")
async def create_project_from_idea(
    payload: IdeaIntakePayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: Any = Depends(require_write_permission),
):
    project = Project(
        id=str(uuid.uuid4()),
        organization_id=tenant.organization_id,
        name=payload.title,
        description=payload.logline,
        script_text=payload.synopsis,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return JSONResponse(content={
        "project_id": project.id,
        "name": project.name,
        "message": "Project created from idea. Add script to run analysis.",
    })


@router.post("/{project_id}/intake/script")
async def intake_script(
    project_id: str,
    payload: ScriptIntakePayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: Any = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    project.script_text = payload.script_text[:16000000]
    await db.commit()

    return JSONResponse(content={
        "project_id": project_id,
        "message": "Script saved. Run analysis to get breakdown.",
    })


@router.post("/{project_id}/analysis/run")
async def run_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: Any = Depends(require_write_permission),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    if not project.script_text:
        raise HTTPException(status_code=400, detail="No script text found. Upload script first.")

    organization_id = str(project.organization_id)

    analysis_result = await analysis_service.run_analysis(
        db, project_id, organization_id, project.script_text
    )

    return JSONResponse(content=analysis_result)


@router.get("/{project_id}/analysis/summary")
async def get_analysis_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    summary = await analysis_service.get_summary(db, project_id)
    return JSONResponse(content=summary)


@router.get("/{project_id}/breakdown/scenes")
async def get_breakdown_scenes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    scenes = await analysis_service.get_scenes(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "scenes": scenes,
    })


@router.get("/{project_id}/breakdown/departments")
async def get_breakdown_departments(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    departments = await analysis_service.get_departments(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "departments": departments,
    })
