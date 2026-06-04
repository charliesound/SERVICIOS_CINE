from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Any, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.module_access import require_module_access
from dependencies.tenant_context import (
    get_tenant_context,
    require_write_permission,
    validate_project_access,
)
from models.core import Project
from schemas.auth_schema import TenantContext
from services.script_analysis_export_service import script_analysis_export_service
from services.breakdown_export_service import breakdown_export_service
from services.script_intake_service import analysis_service


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
    _module_access: TenantContext = Depends(require_module_access("script_analysis")),
    project: Project = Depends(validate_project_access),
):
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
    _module_access: TenantContext = Depends(require_module_access("script_analysis")),
    project: Project = Depends(validate_project_access),
):
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
    _module_access: TenantContext = Depends(require_module_access("script_analysis")),
    project: Project = Depends(validate_project_access),
):
    summary = await analysis_service.get_summary(db, project_id)
    return JSONResponse(content=summary)


@router.get("/{project_id}/breakdown/scenes")
async def get_breakdown_scenes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _module_access: TenantContext = Depends(require_module_access("breakdown")),
    project: Project = Depends(validate_project_access),
):
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
    _module_access: TenantContext = Depends(require_module_access("breakdown")),
    project: Project = Depends(validate_project_access),
):
    departments = await analysis_service.get_departments(db, project_id)
    return JSONResponse(content={
        "project_id": project_id,
        "departments": departments,
    })


@router.get("/{project_id}/analysis/export")
async def export_script_analysis(
    project_id: str,
    format: str = Query("json", alias="format"),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _module_access: TenantContext = Depends(require_module_access("script_analysis")),
    project: Project = Depends(validate_project_access),
):
    if format not in ("json", "md"):
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported format '{format}'. Use 'json' or 'md'.",
        )

    payload = await script_analysis_export_service.build_export_payload(
        db, project_id
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if format == "json":
        return JSONResponse(
            content=payload,
            headers={
                "Content-Disposition": f'attachment; filename="CID_script_analysis_{project_id}.json"',
            },
        )

    body = script_analysis_export_service.to_markdown(payload)
    return Response(
        content=body,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="CID_script_analysis_{project_id}.md"',
        },
    )


@router.get("/{project_id}/breakdown/export")
async def export_breakdown(
    project_id: str,
    format: str = Query("json", alias="format"),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _module_access: TenantContext = Depends(require_module_access("breakdown")),
    project: Project = Depends(validate_project_access),
):
    if format not in ("json", "csv", "md"):
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported format '{format}'. Use 'json', 'csv', or 'md'.",
        )

    payload = await breakdown_export_service.build_export_payload(
        db, project_id
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if not payload.get("has_breakdown"):
        raise HTTPException(status_code=404, detail="No breakdown found for project")

    if format == "json":
        # Remove the internal flag before returning
        payload.pop("_project_exists", None)
        payload.pop("has_breakdown", None)
        return JSONResponse(
            content=payload,
            headers={
                "Content-Disposition": f'attachment; filename="CID_breakdown_{project_id}.json"',
            },
        )

    if format == "csv":
        body = breakdown_export_service.to_csv(payload)
        return Response(
            content=body,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="CID_breakdown_{project_id}.csv"',
            },
        )

    body = breakdown_export_service.to_markdown(payload)
    return Response(
        content=body,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="CID_breakdown_{project_id}.md"',
        },
    )
