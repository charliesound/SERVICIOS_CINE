import json
from datetime import datetime, timezone

from math import ceil

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import AsyncSessionLocal, get_db
from models.core import Project, ProjectJob
from models.production import ProductionBreakdown
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.funding_dossier_service import funding_dossier_service
from services.funding_matcher_service import funding_matcher_service
from services.job_tracking_service import job_tracking_service
from services.budget_estimator_service import budget_estimator_service
from services.funding_ingestion_service import funding_ingestion_service
from services.delivery_service import delivery_service
from services.pdf_service import PdfRenderError


router = APIRouter(tags=["funding"])

funding_router = APIRouter(prefix="/api/funding", tags=["funding-public"])


@funding_router.post("/sources/sync")
async def sync_funding_sources(
    force: bool = False,
    db: AsyncSession = Depends(get_db),
):
    result = await funding_ingestion_service.sync_sources(db, force=force)
    return JSONResponse(content=result)


@funding_router.get("/opportunities")
async def list_funding_opportunities(
    region: str | None = None,
    phase: str | None = None,
    opportunity_type: str | None = None,
    status: str = "open",
    db: AsyncSession = Depends(get_db),
):
    opportunities = await funding_ingestion_service.list_opportunities(
        db,
        region=region,
        phase=phase,
        opportunity_type=opportunity_type,
        status=status,
    )
    return JSONResponse(content={
        "count": len(opportunities),
        "opportunities": opportunities,
    })


@funding_router.get("/opportunities/{opportunity_id}")
async def get_funding_opportunity(
    opportunity_id: str,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from models.production import FundingCall, FundingSource

    result = await db.execute(
        select(FundingCall).where(FundingCall.id == opportunity_id)
    )
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    src_result = await db.execute(
        select(FundingSource).where(FundingSource.id == call.source_id)
    )
    source = src_result.scalar_one_or_none()

    return JSONResponse(content={
        "id": call.id,
        "title": call.title,
        "description": call.description,
        "amount_range": call.amount_range,
        "amount_min": call.amount_min,
        "amount_max": call.amount_max,
        "opportunity_type": call.opportunity_type,
        "phase": call.phase,
        "collaboration_mode": call.collaboration_mode,
        "region": call.region,
        "territory": call.territory,
        "eligibility_summary": call.eligibility_summary,
        "status": call.status,
        "official_url": call.official_url,
        "source": source.name if source else None,
    })


router = APIRouter(prefix="/api/projects", tags=["funding"])


async def _record_funding_job_event(
    db: AsyncSession,
    *,
    job: ProjectJob,
    event_type: str,
    status_from: str | None,
    status_to: str | None,
    message: str,
    detail: str | None = None,
    metadata_json: dict | None = None,
) -> None:
    await job_tracking_service.record_project_job_event(
        db,
        job=job,
        event_type=event_type,
        status_from=status_from,
        status_to=status_to,
        message=message,
        detail=detail,
        metadata_json=metadata_json,
    )


async def _run_funding_rag_job(job_id: str, project_id: str, organization_id: str) -> None:
    async with AsyncSessionLocal() as job_db:
        job = await job_db.get(ProjectJob, job_id)
        if job is None:
            return
        if str(job.project_id) != str(project_id) or str(job.organization_id) != str(organization_id):
            return

        try:
            previous_status = job.status
            job.status = "processing"
            await _record_funding_job_event(
                job_db,
                job=job,
                event_type="job_running",
                status_from=previous_status,
                status_to=job.status,
                message="Document-aware funding matcher job started",
                metadata_json={"job_type": job.job_type, "matcher_mode": funding_matcher_service.RAG_MODE},
            )
            await job_db.commit()

            result_payload = await funding_matcher_service.compute_rag_matches(
                job_db,
                project_id=project_id,
                organization_id=organization_id,
            )

            job = await job_db.get(ProjectJob, job_id)
            if job is None:
                return
            job.status = "completed"
            job.result_data = json.dumps(
                {
                    "project_id": project_id,
                    "organization_id": organization_id,
                    "matches_count": len(result_payload.get("matches", [])),
                    "top_match_ids": [item.get("match_id") for item in result_payload.get("matches", [])[:5]],
                    "evaluation_version": funding_matcher_service.RAG_EVALUATION_VERSION,
                },
                ensure_ascii=True,
            )
            job.completed_at = datetime.now(timezone.utc)
            await _record_funding_job_event(
                job_db,
                job=job,
                event_type="job_succeeded",
                status_from="processing",
                status_to=job.status,
                message="Document-aware funding matcher job completed",
                metadata_json={
                    "matcher_mode": funding_matcher_service.RAG_MODE,
                    "matches_count": len(result_payload.get("matches", [])),
                    "evaluation_version": funding_matcher_service.RAG_EVALUATION_VERSION,
                },
            )
            await job_db.commit()
        except Exception as exc:
            await job_db.rollback()
            failed_job = await job_db.get(ProjectJob, job_id)
            if failed_job is None:
                return
            previous_status = failed_job.status
            failed_job.status = "failed"
            failed_job.error_message = str(exc)[:2000]
            failed_job.completed_at = datetime.now(timezone.utc)
            await _record_funding_job_event(
                job_db,
                job=failed_job,
                event_type="job_failed",
                status_from=previous_status,
                status_to=failed_job.status,
                message="Document-aware funding matcher job failed",
                detail=failed_job.error_message,
                metadata_json={"matcher_mode": funding_matcher_service.RAG_MODE},
            )
            await job_db.commit()


async def _get_project_or_403(
    project_id: str,
    db: AsyncSession,
    tenant: TenantContext,
) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


async def _get_latest_rag_job(
    db: AsyncSession,
    *,
    project_id: str,
    organization_id: str,
) -> ProjectJob | None:
    result = await db.execute(
        select(ProjectJob)
        .where(
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == organization_id,
            ProjectJob.job_type == "funding_matcher_rag",
        )
        .order_by(ProjectJob.created_at.desc(), ProjectJob.id.desc())
    )
    return result.scalars().first()


def _fit_level_rank(value: str | None) -> int:
    mapping = {"high": 3, "medium": 2, "low": 1, "blocked": 0}
    return mapping.get(str(value or "").lower(), -1)


def _match_sort_value(match: dict, sort_by: str) -> object:
    if sort_by == "deadline":
        return match.get("deadline_at") or "9999-12-31T23:59:59"
    if sort_by == "fit_level":
        return _fit_level_rank(match.get("fit_level"))
    return float(match.get("match_score") or 0.0)


def _filter_sort_paginate_matches(
    matches: list[dict],
    *,
    page: int | None,
    size: int | None,
    sort_by: str,
    sort_dir: str,
    fit_level: str | None,
    region_scope: str | None,
    q: str | None,
) -> dict:
    filtered = list(matches)

    if fit_level:
        allowed = {item.strip().lower() for item in fit_level.split(",") if item.strip()}
        filtered = [item for item in filtered if str(item.get("fit_level") or "").lower() in allowed]

    if region_scope:
        allowed_regions = {item.strip().lower() for item in region_scope.split(",") if item.strip()}
        filtered = [item for item in filtered if str(item.get("source_region") or "").lower() in allowed_regions]

    if q:
        needle = q.strip().lower()
        filtered = [
            item for item in filtered
            if needle in str(item.get("title") or "").lower()
            or needle in str(item.get("source_name") or "").lower()
            or needle in str(item.get("source_code") or "").lower()
            or needle in str(item.get("fit_summary") or "").lower()
            or needle in str(item.get("rag_rationale") or "").lower()
        ]

    reverse = sort_dir.lower() != "asc"
    filtered.sort(key=lambda item: _match_sort_value(item, sort_by), reverse=reverse)

    for item in filtered:
        item["region_scope"] = item.get("source_region")

    if page is None and size is None:
        return {
            "items": filtered,
            "count": len(filtered),
            "total": len(filtered),
            "page": None,
            "size": None,
            "pages": 1 if filtered else 0,
        }

    normalized_page = max(1, page or 1)
    normalized_size = max(1, min(size or 20, 100))
    start = (normalized_page - 1) * normalized_size
    end = start + normalized_size
    paged = filtered[start:end]
    total = len(filtered)
    return {
        "items": paged,
        "count": len(paged),
        "total": total,
        "page": normalized_page,
        "size": normalized_size,
        "pages": ceil(total / normalized_size) if total else 0,
    }


@router.get("/{project_id}/funding/dossier")
async def get_funding_dossier(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)

    dossier = await funding_dossier_service.build_dossier(db, project_id, organization_id)
    if "error" in dossier:
        raise HTTPException(status_code=400, detail=dossier["error"])
    return JSONResponse(content=dossier)


@router.get("/{project_id}/funding/dossier/export/pdf")
async def export_funding_dossier_pdf(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)

    dossier = await funding_dossier_service.build_dossier(db, project_id, organization_id)
    if "error" in dossier:
        raise HTTPException(status_code=400, detail=dossier["error"])

    try:
        pdf_bytes = funding_dossier_service.export_dossier_pdf(dossier)
    except (PdfRenderError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=dossier_{project_id}.pdf"
        },
    )


@router.post("/{project_id}/funding/dossier/export/pdf/persist")
async def persist_funding_dossier_pdf(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)

    dossier = await funding_dossier_service.build_dossier(db, project_id, organization_id)
    if "error" in dossier:
        raise HTTPException(status_code=400, detail=dossier["error"])

    try:
        pdf_bytes = funding_dossier_service.export_dossier_pdf(dossier)
    except (PdfRenderError, Exception) as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    file_name = f"funding_dossier_{project_id}.pdf"
    manifest_summary = {
        "project_id": project_id,
        "organization_id": organization_id,
        "project_title": project.name,
        "dossier_version": dossier.get("dossier_version"),
        "generated_at": dossier.get("generated_at"),
        "funding_match_summary": dossier.get("funding_match_summary", {}),
        "current_funding_gap": dossier.get("private_funding_summary", {}).get("current_funding_gap", 0.0),
        "optimistic_funding_gap": dossier.get("private_funding_summary", {}).get("optimistic_funding_gap", 0.0),
    }
    deliverable = await delivery_service.create_project_file_deliverable(
        db,
        project_id=project_id,
        organization_id=organization_id,
        name=f"{project.name} Funding Dossier PDF",
        format_type="FUNDING_DOSSIER_PDF",
        file_bytes=pdf_bytes,
        file_name=file_name,
        mime_type="application/pdf",
        category="funding_dossier_pdf",
        payload_extra={
            "project_name": project.name,
            "source_endpoint": f"/api/projects/{project_id}/funding/dossier/export/pdf",
            "dossier_json": dossier,
        },
        manifest_payload=manifest_summary,
    )

    return JSONResponse(content={
        "id": deliverable.id,
        "project_id": project_id,
        "name": deliverable.name,
        "format_type": deliverable.format_type,
        "delivery_payload": deliverable.delivery_payload,
        "status": deliverable.status,
    }, status_code=201)


@router.post("/{project_id}/funding/recompute")
async def recompute_funding_matches(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)

    result_payload = await funding_matcher_service.compute_matches(db, project_id, organization_id)

    return JSONResponse(content={
        "project_id": project_id,
        "matches_count": len(result_payload["matches"]),
        "project_profile": result_payload["project_profile"],
        "checklist": result_payload["checklist"],
        "matches": result_payload["matches"],
    })


@router.get("/{project_id}/funding/matches")
async def get_funding_matches(
    project_id: str,
    page: int | None = Query(default=None, ge=1),
    size: int | None = Query(default=None, ge=1, le=100),
    sort_by: str = Query(default="match_score", pattern="^(match_score|deadline|fit_level)$"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    fit_level: str | None = None,
    region_scope: str | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)
    matches = await funding_matcher_service.get_matches(db, project_id, organization_id)
    listing = _filter_sort_paginate_matches(
        matches,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        fit_level=fit_level,
        region_scope=region_scope,
        q=q,
    )
    return JSONResponse(content={
        "project_id": project_id,
        "count": listing["count"],
        "total": listing["total"],
        "page": listing["page"],
        "size": listing["size"],
        "pages": listing["pages"],
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "filters": {
            "fit_level": fit_level,
            "region_scope": region_scope,
            "q": q,
        },
        "matches": listing["items"],
    })


@router.post("/{project_id}/funding/recompute-rag")
async def recompute_funding_matches_rag(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    organization_id = str(project.organization_id)

    job = ProjectJob(
        organization_id=organization_id,
        project_id=project_id,
        job_type="funding_matcher_rag",
        status="queued",
        created_by=tenant.user_id,
    )
    db.add(job)
    await db.flush()
    await _record_funding_job_event(
        db,
        job=job,
        event_type="job_created",
        status_from=None,
        status_to=job.status,
        message="Document-aware funding matcher job created",
        metadata_json={"matcher_mode": funding_matcher_service.RAG_MODE, "project_id": project_id},
    )
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(_run_funding_rag_job, str(job.id), project_id, organization_id)

    return JSONResponse(
        status_code=202,
        content={
            "job_id": str(job.id),
            "project_id": project_id,
            "organization_id": organization_id,
            "status": job.status,
            "matcher_mode": funding_matcher_service.RAG_MODE,
            "evaluation_version": funding_matcher_service.RAG_EVALUATION_VERSION,
        },
    )


@router.get("/{project_id}/funding/matches-rag")
async def get_funding_matches_rag(
    project_id: str,
    page: int | None = Query(default=None, ge=1),
    size: int | None = Query(default=None, ge=1, le=100),
    sort_by: str = Query(default="match_score", pattern="^(match_score|deadline|fit_level)$"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    fit_level: str | None = None,
    region_scope: str | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    organization_id = str(project.organization_id)
    matches = await funding_matcher_service.get_matches(
        db,
        project_id,
        organization_id,
        matcher_mode=funding_matcher_service.RAG_MODE,
    )
    latest_job = await _get_latest_rag_job(
        db,
        project_id=project_id,
        organization_id=organization_id,
    )
    listing = _filter_sort_paginate_matches(
        matches,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        fit_level=fit_level,
        region_scope=region_scope,
        q=q,
    )
    return JSONResponse(content={
        "project_id": project_id,
        "count": listing["count"],
        "total": listing["total"],
        "page": listing["page"],
        "size": listing["size"],
        "pages": listing["pages"],
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "filters": {
            "fit_level": fit_level,
            "region_scope": region_scope,
            "q": q,
        },
        "matches": listing["items"],
        "job": {
            "job_id": str(latest_job.id),
            "status": latest_job.status,
            "error_message": latest_job.error_message,
            "completed_at": latest_job.completed_at.isoformat() if latest_job and latest_job.completed_at else None,
        } if latest_job else None,
    })


@router.get("/{project_id}/funding/matches/{match_id}/evidence")
async def get_funding_match_evidence(
    project_id: str,
    match_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    organization_id = str(project.organization_id)
    evidence = await funding_matcher_service.get_match_evidence(
        db,
        project_id=project_id,
        organization_id=organization_id,
        match_id=match_id,
    )
    if evidence is None:
        raise HTTPException(status_code=404, detail="RAG funding match evidence not found")
    return JSONResponse(content=evidence)


@router.get("/{project_id}/funding/matcher-status")
async def get_funding_matcher_status(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    organization_id = str(project.organization_id)
    latest_job = await _get_latest_rag_job(
        db,
        project_id=project_id,
        organization_id=organization_id,
    )
    matches = await funding_matcher_service.get_matches(
        db,
        project_id,
        organization_id,
        matcher_mode=funding_matcher_service.RAG_MODE,
    )
    return JSONResponse(content={
        "project_id": project_id,
        "organization_id": organization_id,
        "matcher_mode": funding_matcher_service.RAG_MODE,
        "has_results": bool(matches),
        "matches_count": len(matches),
        "job": {
            "job_id": str(latest_job.id),
            "status": latest_job.status,
            "error_message": latest_job.error_message,
            "created_at": latest_job.created_at.isoformat() if latest_job and latest_job.created_at else None,
            "completed_at": latest_job.completed_at.isoformat() if latest_job and latest_job.completed_at else None,
            "result_data": json.loads(latest_job.result_data) if latest_job and latest_job.result_data else None,
        } if latest_job else None,
    })


@router.get("/{project_id}/funding/checklist")
async def get_funding_checklist(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)
    checklist = await funding_matcher_service.get_checklist(db, project_id, organization_id)

    return JSONResponse(content=checklist)


@router.get("/{project_id}/funding/profile")
async def get_funding_profile(
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
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    organization_id = str(project.organization_id)
    profile = await funding_matcher_service.build_project_profile(db, project_id, organization_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Funding profile not available")

    return JSONResponse(content=profile)


@router.post("/{project_id}/budget/estimate")
async def estimate_budget(
    project_id: str,
    scenario_type: str = "standard",
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")

    breakdown_result = await db.execute(
        select(ProductionBreakdown).where(ProductionBreakdown.project_id == project_id)
    )
    breakdown = breakdown_result.scalar_one_or_none()

    breakdown_data = {}
    if breakdown and breakdown.breakdown_json:
        import json
        try:
            breakdown_data = json.loads(breakdown.breakdown_json)
        except:
            breakdown_data = {}

    organization_id = str(project.organization_id)
    budget = await budget_estimator_service.estimate_budget(
        db, project_id, organization_id, breakdown_data, scenario_type
    )

    return JSONResponse(content={
        "project_id": project_id,
        "scenario_type": scenario_type,
        "budget": budget,
    })
