from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context, TenantContext
from models.core import Project
from services.script_version_service import ScriptVersionService, ScriptChangeAnalysisService

router = APIRouter(prefix="/api/projects", tags=["script versioning"])


class CreateScriptVersionPayload(BaseModel):
    script_text: str
    filename: Optional[str] = None
    notes: Optional[str] = None


class ActivateVersionPayload(BaseModel):
    version_id: str


class CompareVersionsPayload(BaseModel):
    from_version_id: str
    to_version_id: str


async def _get_project_for_tenant_or_404(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
) -> Project:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == str(tenant.organization_id),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/script/versions")
async def list_script_versions(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    
    project = await _get_project_for_tenant_or_404(db, project_id, tenant)
    
    service = ScriptVersionService(db)
    versions = await service.list_versions(project_id)
    
    return [
        {
            "id": v.id,
            "project_id": v.project_id,
            "version_number": v.version_number,
            "title": v.title,
            "source_filename": v.source_filename,
            "content_hash": v.content_hash,
            "word_count": v.word_count,
            "scene_count": v.scene_count,
            "status": v.status,
            "notes": v.notes,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@router.post("/{project_id}/script/versions")
async def create_script_version(
    project_id: str,
    payload: CreateScriptVersionPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    
    project = await _get_project_for_tenant_or_404(db, project_id, tenant)
    
    service = ScriptVersionService(db)
    
    existing_versions = await service.list_versions(project_id)
    
    if not existing_versions:
        version = await service.create_initial_version(
            project_id,
            payload.script_text,
            payload.filename,
            user_org_id,
        )
    else:
        version = await service.create_new_version(
            project_id,
            payload.script_text,
            payload.filename,
            payload.notes,
            user_org_id,
        )
    
    if version:
        project.script_text = payload.script_text
        await db.commit()
    
    return {
        "id": version.id if version else None,
        "version_number": version.version_number if version else None,
        "status": version.status if version else "unchanged",
        "created_at": version.created_at.isoformat() if version and version.created_at else None,
    }


@router.get("/{project_id}/script/versions/{version_id}")
async def get_script_version(
    project_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    
    from models.script_versioning import ScriptVersion
    result = await db.execute(
        select(ScriptVersion).where(
            ScriptVersion.id == version_id,
            ScriptVersion.project_id == project_id,
        )
    )
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "id": version.id,
        "project_id": version.project_id,
        "version_number": version.version_number,
        "title": version.title,
        "source_filename": version.source_filename,
        "script_text": version.script_text,
        "content_hash": version.content_hash,
        "word_count": version.word_count,
        "scene_count": version.scene_count,
        "status": version.status,
        "notes": version.notes,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


@router.post("/{project_id}/script/versions/{version_id}/activate")
async def activate_script_version(
    project_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    
    project = await _get_project_for_tenant_or_404(db, project_id, tenant)
    
    service = ScriptVersionService(db)
    version = await service.activate_version(project_id, version_id, project)
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "id": version.id,
        "version_number": version.version_number,
        "status": version.status,
    }


@router.post("/{project_id}/script/versions/compare")
async def compare_script_versions(
    project_id: str,
    payload: CompareVersionsPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    
    from models.script_versioning import ScriptVersion
    result = await db.execute(
        select(ScriptVersion).where(
            ScriptVersion.id.in_([payload.from_version_id, payload.to_version_id]),
            ScriptVersion.project_id == project_id,
        )
    )
    versions = {v.id: v for v in result.scalars().all()}
    
    if payload.from_version_id not in versions or payload.to_version_id not in versions:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    from_version = versions[payload.from_version_id]
    to_version = versions[payload.to_version_id]
    
    analysis_service = ScriptChangeAnalysisService(db)
    change_report = await analysis_service.compare_versions(
        project_id,
        user_org_id,
        from_version,
        to_version,
    )
    
    return {
        "id": change_report.id,
        "project_id": change_report.project_id,
        "from_version_id": change_report.from_version_id,
        "to_version_id": change_report.to_version_id,
        "summary": change_report.summary,
        "added_scenes": change_report.added_scenes_json,
        "removed_scenes": change_report.removed_scenes_json,
        "modified_scenes": change_report.modified_scenes_json,
        "added_characters": change_report.added_characters_json,
        "production_impact": change_report.production_impact_json,
        "budget_impact": change_report.budget_impact_json,
        "storyboard_impact": change_report.storyboard_impact_json,
        "recommended_actions": change_report.recommended_actions_json,
        "created_at": change_report.created_at.isoformat() if change_report.created_at else None,
    }


@router.get("/{project_id}/script/change-reports")
async def list_change_reports(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)

    project = await _get_project_for_tenant_or_404(db, project_id, tenant)

    from models.script_versioning import ScriptChangeReport
    result = await db.execute(
        select(ScriptChangeReport).where(
            ScriptChangeReport.project_id == project_id,
        ).order_by(ScriptChangeReport.created_at.desc())
    )
    reports = result.scalars().all()

    return [
        {
            "id": r.id,
            "from_version_id": r.from_version_id,
            "to_version_id": r.to_version_id,
            "summary": r.summary,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


@router.get("/{project_id}/module-status")
async def get_module_statuses(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)

    project = await _get_project_for_tenant_or_404(db, project_id, tenant)

    service = ScriptVersionService(db)
    statuses = await service.get_module_statuses(project_id)
    
    return [
        {
            "module_name": s.module_name,
            "status": s.status,
            "source_script_version_id": s.source_script_version_id,
            "affected_by_change_report_id": s.affected_by_change_report_id,
            "summary": s.summary,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in statuses
    ]