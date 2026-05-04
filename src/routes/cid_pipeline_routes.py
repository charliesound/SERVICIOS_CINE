from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.cid_pipeline_schema import (
    CIDPipelineExecuteRequest,
    CIDPipelineExecuteResponse,
    CIDPipelineGenerateRequest,
    CIDPipelineGenerateResponse,
    CIDPipelineJobListResponse,
    CIDPipelineJobResponse,
    CIDPipelinePresetListResponse,
    CIDPipelinePresetResponse,
    CIDPipelineValidateRequest,
    CIDPipelineValidationResponse,
)
from services.cid_pipeline_builder_service import cid_pipeline_builder_service
from services.cid_pipeline_preset_service import cid_pipeline_preset_service
from services.cid_pipeline_simulated_job_service import cid_pipeline_simulated_job_service
from services.cid_pipeline_validation_service import cid_pipeline_validation_service


router = APIRouter(prefix="/api/pipelines", tags=["cid-pipelines"])


def _is_feature_enabled() -> bool:
    return os.getenv("CID_PIPELINE_BUILDER_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}


def require_cid_pipeline_builder_enabled() -> None:
    if not _is_feature_enabled():
        raise HTTPException(status_code=404, detail="CID Pipeline Builder is disabled")


async def _get_project_or_403(
    project_id: str,
    db: AsyncSession,
    tenant: TenantContext,
) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


async def _resolve_project_id(
    db: AsyncSession,
    tenant: TenantContext,
    explicit_project_id: str | None,
    embedded_project_id: str | None,
) -> str | None:
    if explicit_project_id and embedded_project_id and explicit_project_id != embedded_project_id:
        raise HTTPException(status_code=400, detail="project_id mismatch between request and pipeline")
    project_id = explicit_project_id or embedded_project_id
    if project_id:
        await _get_project_or_403(project_id, db, tenant)
    return project_id


@router.get(
    "/presets",
    response_model=CIDPipelinePresetListResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def list_pipeline_presets(
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelinePresetListResponse:
    del tenant
    presets = [CIDPipelinePresetResponse(**item) for item in cid_pipeline_preset_service.list_presets()]
    return CIDPipelinePresetListResponse(count=len(presets), presets=presets)


@router.post(
    "/generate",
    response_model=CIDPipelineGenerateResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def generate_pipeline(
    payload: CIDPipelineGenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelineGenerateResponse:
    if payload.project_id:
        await _get_project_or_403(payload.project_id, db, tenant)
    pipeline = cid_pipeline_builder_service.build_pipeline(payload)
    validation = cid_pipeline_validation_service.validate_pipeline(pipeline)
    return CIDPipelineGenerateResponse(mode="simulated", pipeline=pipeline, validation=validation)


@router.post(
    "/validate",
    response_model=CIDPipelineValidationResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def validate_pipeline(
    payload: CIDPipelineValidateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelineValidationResponse:
    project_id = await _resolve_project_id(db, tenant, payload.project_id, payload.pipeline.project_id)
    if project_id != payload.pipeline.project_id:
        payload.pipeline.project_id = project_id
    return cid_pipeline_validation_service.validate_pipeline(payload.pipeline)


@router.post(
    "/execute",
    response_model=CIDPipelineExecuteResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def execute_pipeline(
    payload: CIDPipelineExecuteRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelineExecuteResponse:
    project_id = await _resolve_project_id(db, tenant, payload.project_id, payload.pipeline.project_id)
    if project_id != payload.pipeline.project_id:
        payload.pipeline.project_id = project_id

    validation = cid_pipeline_validation_service.validate_pipeline(payload.pipeline)
    if not validation.valid or validation.blocked:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "CID pipeline execution blocked by validation",
                "validation": validation.model_dump(),
            },
        )

    job = cid_pipeline_simulated_job_service.create_job(
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
        project_id=project_id,
        pipeline=payload.pipeline,
        validation=validation,
    )
    return CIDPipelineExecuteResponse(mode="simulated", job=job)


@router.get(
    "/jobs",
    response_model=CIDPipelineJobListResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def list_pipeline_jobs(
    project_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelineJobListResponse:
    if project_id:
        await _get_project_or_403(project_id, db, tenant)
    jobs = cid_pipeline_simulated_job_service.list_jobs(
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
        project_id=project_id,
    )
    return CIDPipelineJobListResponse(count=len(jobs), jobs=jobs)


@router.get(
    "/jobs/{job_id}",
    response_model=CIDPipelineJobResponse,
    dependencies=[Depends(require_cid_pipeline_builder_enabled)],
)
async def get_pipeline_job(
    job_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
) -> CIDPipelineJobResponse:
    job = cid_pipeline_simulated_job_service.get_job(
        job_id=job_id,
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
    )
    if job is None:
        raise HTTPException(status_code=404, detail="CID pipeline job not found")
    return job
