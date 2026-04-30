import json
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project, ProjectJob, User as DBUser
from models.storage import MediaAsset, MediaAssetType, MediaAssetStatus
from routes.auth_routes import get_current_user_optional, get_tenant_context
from schemas.auth_schema import UserResponse, TenantContext
from services.document_service import document_service
from services.job_tracking_service import job_tracking_service
from services.plan_limits_service import plan_limits_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectPayload(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateScriptPayload(BaseModel):
    script_text: str


class ScriptAnalysisResponse(BaseModel):
    document_id: str
    doc_type: str
    confidence_score: Optional[float]
    structured_payload: dict[str, Any]


class ShotData(BaseModel):
    shot_number: int
    shot_type: str
    description: str


class StoryboardScene(BaseModel):
    scene_number: int
    heading: str
    location: str
    time_of_day: str
    shots: list[ShotData]


class StoryboardResponse(BaseModel):
    project_id: str
    total_scenes: int
    scenes: list[StoryboardScene]


class ProjectJobHistoryResponse(BaseModel):
    id: str
    event_type: str
    status_from: Optional[str] = None
    status_to: Optional[str] = None
    message: Optional[str] = None
    detail: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None


class ProjectJobAssetResponse(BaseModel):
    id: str
    job_id: Optional[str] = None
    file_name: str
    file_extension: str
    asset_type: str
    asset_source: Optional[str] = None
    content_ref: Optional[str] = None
    mime_type: Optional[str] = None
    status: str
    metadata_json: Optional[Any] = None
    created_at: Optional[str] = None


class ProjectJobResponse(BaseModel):
    id: str
    organization_id: str
    project_id: str
    job_type: str
    status: str
    result_data: Optional[Any]
    error_message: Optional[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    history: list[ProjectJobHistoryResponse] = Field(default_factory=list)
    assets: list[ProjectJobAssetResponse] = Field(default_factory=list)


class ProjectJobListResponse(BaseModel):
    jobs: list[ProjectJobResponse]


class ProjectResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    status: str
    script_text: Optional[str]


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


def _project_dict(project: Project) -> dict:
    return {
        "id": str(project.id),
        "organization_id": str(project.organization_id),
        "name": str(project.name),
        "description": project.description,
        "status": str(project.status),
        "script_text": project.script_text,
    }


async def _record_project_job_event(
    db: AsyncSession,
    *,
    job: ProjectJob,
    event_type: str,
    status_from: Optional[str],
    status_to: Optional[str],
    message: str,
    detail: Optional[str] = None,
    metadata_json: Optional[dict[str, Any]] = None,
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


async def _job_detail_dict(db: AsyncSession, job: ProjectJob) -> dict[str, Any]:
    payload = _job_dict(job)
    payload.update(
        await job_tracking_service.build_job_tracking_payload(
            db,
            job_id=str(job.id),
            organization_id=str(job.organization_id),
            project_id=str(job.project_id),
        )
    )
    return payload


def _resolve_effective_plan(plan_name: Optional[str]) -> str:
    normalized = (plan_name or "free").lower()
    if normalized == "demo":
        return "demo"
    if normalized in {"free", "creator", "producer", "studio", "enterprise"}:
        return normalized
    return "free"


async def _get_org_usage_counts(
    db: AsyncSession, organization_id: str
) -> dict[str, int]:
    projects_count = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.organization_id == organization_id
            )
        )
    ).scalar_one() or 0
    jobs_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.organization_id == organization_id
            )
        )
    ).scalar_one() or 0
    analyses_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.organization_id == organization_id,
                ProjectJob.job_type == "analyze",
            )
        )
    ).scalar_one() or 0
    storyboards_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.organization_id == organization_id,
                ProjectJob.job_type == "storyboard",
            )
        )
    ).scalar_one() or 0

    return {
        "projects_count": int(projects_count),
        "jobs_count": int(jobs_count),
        "analyses_count": int(analyses_count),
        "storyboards_count": int(storyboards_count),
    }


def _next_upgrade_plan(plan_name: str) -> str:
    order = ["demo", "free", "creator", "producer", "studio", "enterprise"]
    try:
        idx = order.index(plan_name)
    except ValueError:
        return "creator"
    return order[min(idx + 1, len(order) - 1)]


def _resource_label(resource: str) -> str:
    labels = {
        "projects": "proyectos",
        "jobs": "automatizaciones",
        "analyses": "analisis",
        "storyboards": "storyboards",
    }
    return labels.get(resource, resource)


async def _enforce_plan_limit(
    *,
    db: AsyncSession,
    organization_id: str,
    user_plan: Optional[str],
    resource: str,
) -> None:
    plan_name = _resolve_effective_plan(user_plan)
    plan = plan_limits_service.get_plan(plan_name)
    if not plan:
        return

    usage = await _get_org_usage_counts(db, organization_id)
    limits_map = {
        "projects": plan.max_projects,
        "jobs": plan.max_total_jobs,
        "analyses": plan.max_analyses,
        "storyboards": plan.max_storyboards,
    }
    current_map = {
        "projects": usage["projects_count"],
        "jobs": usage["jobs_count"],
        "analyses": usage["analyses_count"],
        "storyboards": usage["storyboards_count"],
    }
    limit = limits_map[resource]
    current = current_map[resource]
    if limit != -1 and current >= limit:
        recommended_plan = _next_upgrade_plan(plan_name)
        recommended = plan_limits_service.get_plan(recommended_plan)
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "message": (
                    f"Tu organizacion ya ha consumido {current} de {limit} {_resource_label(resource)} incluidos en {plan.display_name}. "
                    f"Activa {recommended.display_name if recommended else recommended_plan} para seguir operando sin friccion durante la demo."
                ),
                "resource": resource,
                "current": current,
                "limit": limit,
                "plan": plan_name,
                "recommended_plan": recommended_plan,
            },
        )


async def _enforce_export_permission(
    user_plan: Optional[str],
    export_format: str = "json",
) -> None:
    plan_name = _resolve_effective_plan(user_plan)
    plan = plan_limits_service.get_plan(plan_name)
    can_export = False
    if plan:
        if export_format == "zip":
            can_export = plan.export_zip
        else:
            can_export = plan.export_json

    if not plan or not can_export:
        recommended_plan = _next_upgrade_plan(plan_name)
        recommended = plan_limits_service.get_plan(recommended_plan)
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLAN_EXPORT_BLOCKED",
                "message": (
                    f"Tu plan actual no incluye exportacion en formato {export_format.upper()}. "
                    f"Activa {recommended.display_name if recommended else recommended_plan} para descargar el paquete del proyecto y presentar la demo con material compartible."
                ),
                "plan": plan_name,
                "recommended_plan": recommended_plan,
            },
        )


@router.get("")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(
        select(Project)
        .where(Project.organization_id == user_org_id)
        .order_by(Project.created_at.desc(), Project.id.desc())
    )
    projects = result.scalars().all()

    return {"projects": [_project_dict(p) for p in projects]}


@router.post("", response_model=ProjectResponse)
async def create_project(
    payload: CreateProjectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=current_user.plan,
        resource="projects",
    )

    project = Project(
        organization_id=user_org_id,
        name=payload.name,
        description=payload.description,
        status="active",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return _project_dict(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return _project_dict(project)


@router.get("/{project_id}/dashboard")
async def get_project_dashboard(
    project_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    from sqlalchemy import func, select
    from models.core import User
    
    result = await db.execute(select(User).where(User.id == current_user.user_id))
    user = result.scalar_one_or_none()
    user_role = user.role if user else "viewer"
    
    from services.role_permission_service import (
        get_role_default,
        get_permissions_for_role,
        get_user_dashboard_roles,
        get_module_order_for_role,
        has_admin_access,
        filter_actions_by_permissions,
    )
    
    canonical_user_role = get_role_default(user_role)
    permissions = get_permissions_for_role(canonical_user_role)
    available_roles = get_user_dashboard_roles(user_role)
    
    target_role = role if role and has_admin_access(canonical_user_role) else canonical_user_role
    target_permissions = get_permissions_for_role(target_role)
    
    module_order = get_module_order_for_role(target_role)
    from models.ingest_scan import MediaAsset
    from models.storage import MediaAssetStatus
    from models.storyboard import StoryboardShot, StoryboardSequence
    from models.ingest_document import DocumentAsset
    from models.editorial import AssemblyCut, Take

    media_count_result = await db.execute(
        select(func.count()).select_from(MediaAsset).where(
            MediaAsset.project_id == project_id,
            MediaAsset.status == MediaAssetStatus.INDEXED,
        )
    )
    media_count = media_count_result.scalar_one() or 0

    document_count_result = await db.execute(
        select(func.count()).select_from(DocumentAsset).where(
            DocumentAsset.project_id == project_id,
        )
    )
    document_count = document_count_result.scalar_one() or 0

    storyboard_shots_result = await db.execute(
        select(func.count()).select_from(StoryboardShot).where(
            StoryboardShot.project_id == project_id,
        )
    )
    storyboard_count = storyboard_shots_result.scalar_one() or 0

    has_script_analysis = bool(project.script_text)

    assembly_result = await db.execute(
        select(func.count()).select_from(AssemblyCut).where(
            AssemblyCut.project_id == project_id,
        )
    )
    assembly_count = assembly_result.scalar_one() or 0

    takes_result = await db.execute(
        select(func.count()).select_from(Take).where(
            Take.project_id == project_id,
        )
    )
    takes_count = takes_result.scalar_one() or 0

    from services.budget_estimator_service import get_active_budget
    budget = await get_active_budget(db, project_id)
    has_budget = budget is not None

    from models.production import FundingCall
    funding_match_result = await db.execute(
        select(func.count()).select_from(FundingCall).where(
            FundingCall.status == "active",
        )
    )
    funding_opportunity_count = funding_match_result.scalar_one() or 0
    has_funding = funding_opportunity_count > 0

    from models.producer_pitch import ProducerPitchPack
    pack_result = await db.execute(
        select(func.count()).select_from(ProducerPitchPack).where(
            ProducerPitchPack.project_id == project_id,
            ProducerPitchPack.status.in_(["generated", "approved"]),
        )
    )
    pack_count = pack_result.scalar_one() or 0
    has_producer_pack = pack_count > 0

    from models.distribution import DistributionPack
    dist_result = await db.execute(
        select(func.count()).select_from(DistributionPack).where(
            DistributionPack.project_id == project_id,
            DistributionPack.status.in_(["generated", "approved"]),
        )
    )
    dist_count = dist_result.scalar_one() or 0
    has_distribution = dist_count > 0

    from models.crm import CRMOpportunity
    crm_result = await db.execute(
        select(func.count()).select_from(CRMOpportunity).where(
            CRMOpportunity.project_id == project_id,
        )
    )
    crm_count = crm_result.scalar_one() or 0
    has_crm = crm_count > 0

    modules = {}

    if project.script_text:
        if has_script_analysis:
            modules["script"] = {
                "status": "ready",
                "summary": "Guion analizado",
            }
        else:
            modules["script"] = {
                "status": "partial",
                "summary": "Guion cargado, pendiente de análisis",
            }
    else:
        modules["script"] = {
            "status": "missing",
            "summary": "Sin guion cargado",
        }

    modules["storyboard"] = {
        "status": "ready" if storyboard_count > 0 else "missing",
        "summary": f"{storyboard_count} frames" if storyboard_count > 0 else "Sin storyboard",
    }

    modules["breakdown"] = {
        "status": "missing",
        "summary": "En roadmap — Pending",
    }

    modules["budget"] = {
        "status": "ready" if has_budget else "missing",
        "summary": f"€{budget.total_estimated:,.0f}" if has_budget else "Sin presupuesto estimado",
    }

    modules["funding"] = {
        "status": "ready" if has_funding else "missing",
        "summary": f"{funding_opportunity_count} oportunidades" if has_funding else "Ver oportunidades de ayudas",
    }

    modules["producer_pack"] = {
        "status": "ready" if has_producer_pack else "missing",
        "summary": f"{pack_count} dossier" if has_producer_pack else "Generar dossier productor",
    }

    modules["distribution"] = {
        "status": "ready" if has_distribution else "missing",
        "summary": f"{dist_count} pack" if has_distribution else "Generar pack distribución",
    }

    modules["crm"] = {
        "status": "ready" if has_crm else "missing",
        "summary": f"{crm_count} oportunidad" if has_crm else "Sin oportunidades comerciales",
    }

    modules["media"] = {
        "status": "ready" if media_count > 0 else "missing",
        "summary": f"{media_count} archivos indexados" if media_count > 0 else "Sin media escaneada",
    }

    modules["documents"] = {
        "status": "ready" if document_count > 0 else "missing",
        "summary": f"{document_count} documentos" if document_count > 0 else "Sin documentos ingeridos",
    }

    modules["editorial"] = {
        "status": "ready" if assembly_count > 0 else "missing",
        "summary": f"{assembly_count} AssemblyCut, {takes_count} takes" if assembly_count > 0 else "Sin AssemblyCut",
    }

    ready_count = sum(1 for m in modules.values() if m.get("status") == "ready")
    partial_count = sum(1 for m in modules.values() if m.get("status") == "partial")
    overall_progress = int((ready_count * 100 + partial_count * 50) / (len(modules) * 100) * 100)

    recommended_actions = []

    if project.script_text and not has_script_analysis:
        recommended_actions.append({
            "label": "Analizar guion",
            "route": f"/projects/{project_id}",
            "priority": "high",
        })

    if not storyboard_count:
        recommended_actions.append({
            "label": "Generar storyboard",
            "route": f"/projects/{project_id}/storyboard-builder",
            "priority": "high",
        })

    if not has_budget:
        recommended_actions.append({
            "label": "Generar presupuesto estimado",
            "route": f"/projects/{project_id}/budget",
            "priority": "high",
            "permission": "budget.generate",
        })

    if not has_funding:
        recommended_actions.append({
            "label": "Buscar ayudas y subvenciones",
            "route": f"/projects/{project_id}/funding",
            "priority": "high",
            "permission": "funding.view",
        })

    if not has_producer_pack:
        recommended_actions.append({
            "label": "Generar dossier productor",
            "route": f"/projects/{project_id}/producer-pitch",
            "priority": "medium",
            "permission": "producer_pack.generate",
        })

    if not has_distribution:
        recommended_actions.append({
            "label": "Generar pack distribución",
            "route": f"/projects/{project_id}/distribution",
            "priority": "medium",
            "permission": "distribution.manage",
        })

    if not has_crm:
        recommended_actions.append({
            "label": "Crear oportunidad comercial",
            "route": f"/projects/{project_id}/crm",
            "priority": "medium",
            "permission": "crm.manage",
        })

    if not media_count:
        recommended_actions.append({
            "label": "Escanear media",
            "route": "/ingest/scans",
            "priority": "medium",
        })

    if ready_count or assembly_count:
        recommended_actions.append({
            "label": "Exportar a DaVinci",
            "route": f"/projects/{project_id}/editorial",
            "priority": "medium",
            "permission": "davinci.export",
        })

    from services.change_governance_service import get_pending_changes_count
    try:
        pending_changes = await get_pending_changes_count(db, project_id)
        if pending_changes.get("total", 0) > 0:
            recommended_actions.append({
                "label": f"Revisar {pending_changes['total']} cambio(s) pendientes",
                "route": f"/projects/{project_id}/change-requests",
                "priority": "high",
            })
    except:
        pass

    recommended_actions = filter_actions_by_permissions(recommended_actions, target_role)

    return {
        "project_id": project_id,
        "title": project.name,
        "status": project.status or "active",
        "overall_progress": overall_progress,
        "modules": modules,
        "recommended_next_actions": recommended_actions,
        "warnings": [],
        "role_dashboard": {
            "active_role": target_role,
            "available_roles": available_roles,
            "permissions": target_permissions,
            "user_role": canonical_user_role,
        },
    }


@router.put("/{project_id}/script", response_model=ProjectResponse)
async def update_project_script(
    project_id: str,
    payload: UpdateScriptPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    project.script_text = payload.script_text
    await db.commit()
    await db.refresh(project)

    return _project_dict(project)


async def _parse_storyboard(script_text: str) -> StoryboardResponse:
    lines = script_text.strip().split("\n")
    scenes: list[StoryboardScene] = []
    current_heading = ""
    current_location = ""
    current_tod = ""
    scene_shots: list[ShotData] = []
    scene_number = 0
    shot_counter = 0

    TIME_OF_DAY_PATTERNS = [
        (r"\bDAY\b", "DAY"),
        (r"\bNIGHT\b", "NIGHT"),
        (r"\bDAWN\b", "DAWN"),
        (r"\bDUSK\b", "DUSK"),
        (r"\bMORNING\b", "MORNING"),
        (r"\bEVENING\b", "EVENING"),
        (r"\bAFTERNOON\b", "AFTERNOON"),
        (r"\bCONTINUOUS\b", "CONTINUOUS"),
        (r"\bLATER\b", "LATER"),
        (r"\bMOMENTS?\s*LATER\b", "LATER"),
    ]

    SHOT_KEYWORDS = {
        "WS": ["walks", "enters", "exits", "leaves", "crosses"],
        "CU": ["face", "eyes", "hand", "holding", "close up", "close-up"],
        "ECU": ["tears", "sweat", "blood", "detail", "extreme close"],
        "OTS": ["over", "shoulder", "talking to", "speaking to"],
        "MS": ["medium shot", "mid shot", "waist up"],
        "LS": ["long shot", "establishing", "wide shot", "exterior"],
        "PANNING": ["pans", "pan", "sweeping"],
        "TRACKING": ["tracking", "following", "moves with", "dolly"],
        "POV": ["POV", "point of view", "we see", "we hear"],
    }

    def detect_shot_type(text: str) -> str:
        text_lower = text.lower()
        for shot, keywords in SHOT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return shot
        return "MS"

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"^(INT\.|EXT\.|INT/EXT\.|I/E\.?)\s*", line, re.IGNORECASE):
            if current_heading:
                scenes.append(
                    StoryboardScene(
                        scene_number=scene_number,
                        heading=current_heading,
                        location=current_location,
                        time_of_day=current_tod or "DAY",
                        shots=scene_shots,
                    )
                )
            scene_number += 1
            current_heading = line
            heading_upper = line.upper()

            loc_match = re.sub(
                r"^(INT\.|EXT\.|INT/EXT\.|I/E\.?)\s*",
                "",
                line,
                flags=re.IGNORECASE,
            )
            loc_match = re.sub(
                r"\s*-\s*(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|AFTERNOON|CONTINUOUS|LATER|MOMENTS?\s*LATER).*$",
                "",
                loc_match,
                flags=re.IGNORECASE,
            )
            current_location = loc_match.strip()

            current_tod = "DAY"
            for pattern, tod in TIME_OF_DAY_PATTERNS:
                if re.search(pattern, heading_upper):
                    current_tod = tod
                    break

            scene_shots = []
            shot_counter = 0
        elif current_heading and (line.isupper() or len(line) < 60):
            shot_counter += 1
            scene_shots.append(
                ShotData(
                    shot_number=shot_counter,
                    shot_type=detect_shot_type(line),
                    description=line[:100],
                )
            )

    if current_heading:
        scenes.append(
            StoryboardScene(
                scene_number=scene_number,
                heading=current_heading,
                location=current_location,
                time_of_day=current_tod or "DAY",
                shots=scene_shots,
            )
        )

    if not scenes:
        scenes.append(
            StoryboardScene(
                scene_number=1,
                heading="ESCENA 1",
                location="Ubicacion",
                time_of_day="DAY",
                shots=[
                    ShotData(
                        shot_number=1,
                        shot_type="MS",
                        description="Accion principal del guion",
                    )
                ],
            )
        )

    return StoryboardResponse(
        project_id="",
        total_scenes=len(scenes),
        scenes=scenes,
    )


@router.post("/{project_id}/analyze", response_model=ScriptAnalysisResponse)
async def analyze_project_script(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not project.script_text:
        raise HTTPException(
            status_code=400, detail="Project has no script text to analyze"
        )

    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=current_user.plan,
        resource="jobs",
    )
    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=current_user.plan,
        resource="analyses",
    )

    job = ProjectJob(
        organization_id=user_org_id,
        project_id=project_id,
        job_type="analyze",
        status="pending",
        created_by=current_user.user_id,
    )
    db.add(job)
    await db.flush()
    await _record_project_job_event(
        db,
        job=job,
        event_type="job_created",
        status_from=None,
        status_to=job.status,
        message="Project analysis job created",
        metadata_json={"job_type": job.job_type},
    )

    try:
        previous_status = job.status
        job.status = "processing"
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_running",
            status_from=previous_status,
            status_to=job.status,
            message="Project analysis job started",
        )
        await db.commit()
        await db.refresh(job)

        doc = await document_service.create_script_document(
            db,
            user_org_id=user_org_id,
            project_id=project_id,
            file_name=f"{project.name}_script.txt",
            raw_text=project.script_text,
            uploaded_by=current_user.user_id,
        )

        doc = await document_service.classify_document(
            db, doc, created_by=current_user.user_id
        )
        doc = await document_service.structure_document(
            db, doc, created_by=current_user.user_id
        )

        classification = getattr(doc, "classification", None)
        structured_data = getattr(doc, "structured_data", None)

        structured_payload: dict[str, Any] = {}
        if structured_data and structured_data.structured_payload_json:
            try:
                structured_payload = json.loads(structured_data.structured_payload_json)
            except Exception:
                structured_payload = {}

        result_payload = {
            "document_id": str(doc.id),
            "doc_type": str(classification.doc_type) if classification else "unknown",
            "confidence_score": float(classification.confidence_score)
            if classification and classification.confidence_score is not None
            else None,
            "structured_payload": structured_payload,
        }

        job.status = "completed"
        job.result_data = json.dumps(result_payload, ensure_ascii=False)
        job.completed_at = datetime.now(timezone.utc)

        asset = await _upsert_project_asset(
            db,
            organization_id=user_org_id,
            project_id=project_id,
            job_id=str(job.id),
            file_name=f"{project.name}_analysis.json",
            content_ref=f"virtual://{project_id}/{job.id}/analysis.json",
            asset_source="script_analysis",
            metadata_json=result_payload,
            created_by=current_user.user_id,
        )
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_succeeded",
            status_from="processing",
            status_to=job.status,
            message="Project analysis job completed",
            metadata_json={
                "document_id": result_payload.get("document_id"),
                "doc_type": result_payload.get("doc_type"),
                "asset_id": str(asset.id),
                "asset_source": asset.asset_source,
            },
        )

        await db.commit()
        await db.refresh(job)

        return ScriptAnalysisResponse(
            document_id=str(doc.id),
            doc_type=str(classification.doc_type) if classification else "unknown",
            confidence_score=float(classification.confidence_score)
            if classification and classification.confidence_score is not None
            else None,
            structured_payload=structured_payload,
        )
    except Exception as exc:
        previous_status = job.status
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_failed",
            status_from=previous_status,
            status_to=job.status,
            message="Project analysis job failed",
            detail=job.error_message,
        )
        await db.commit()
        raise


@router.post("/{project_id}/storyboard", response_model=StoryboardResponse)
async def generate_storyboard(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not project.script_text:
        raise HTTPException(
            status_code=400, detail="Project has no script text for storyboard"
        )

    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=current_user.plan,
        resource="jobs",
    )
    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=current_user.plan,
        resource="storyboards",
    )

    job = ProjectJob(
        organization_id=user_org_id,
        project_id=project_id,
        job_type="storyboard",
        status="pending",
        created_by=current_user.user_id,
    )
    db.add(job)
    await db.flush()
    await _record_project_job_event(
        db,
        job=job,
        event_type="job_created",
        status_from=None,
        status_to=job.status,
        message="Storyboard job created",
        metadata_json={"job_type": job.job_type},
    )

    try:
        previous_status = job.status
        job.status = "processing"
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_running",
            status_from=previous_status,
            status_to=job.status,
            message="Storyboard job started",
        )
        await db.commit()
        await db.refresh(job)

        storyboard = await _parse_storyboard(project.script_text)
        storyboard.project_id = project_id

        result_payload = {
            "total_scenes": storyboard.total_scenes,
            "scenes": [
                {
                    "scene_number": s.scene_number,
                    "heading": s.heading,
                    "location": s.location,
                    "time_of_day": s.time_of_day,
                    "shots": [
                        {
                            "shot_number": sh.shot_number,
                            "shot_type": sh.shot_type,
                            "description": sh.description,
                        }
                        for sh in s.shots
                    ],
                }
                for s in storyboard.scenes
            ],
        }

        job.status = "completed"
        job.result_data = json.dumps(result_payload, ensure_ascii=False)
        job.completed_at = datetime.now(timezone.utc)

        asset = await _upsert_project_asset(
            db,
            organization_id=user_org_id,
            project_id=project_id,
            job_id=str(job.id),
            file_name=f"{project.name}_storyboard.json",
            content_ref=f"virtual://{project_id}/{job.id}/storyboard.json",
            asset_source="script_storyboard",
            metadata_json=result_payload,
            created_by=current_user.user_id,
        )
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_succeeded",
            status_from="processing",
            status_to=job.status,
            message="Storyboard job completed",
            metadata_json={
                "total_scenes": result_payload.get("total_scenes"),
                "asset_id": str(asset.id),
                "asset_source": asset.asset_source,
            },
        )

        await db.commit()
        await db.refresh(job)

        return storyboard
    except Exception as exc:
        previous_status = job.status
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_failed",
            status_from=previous_status,
            status_to=job.status,
            message="Storyboard job failed",
            detail=job.error_message,
        )
        await db.commit()
        raise


def _job_dict(job: ProjectJob) -> dict:
    result_data: Any = None
    if job.result_data:
        try:
            result_data = json.loads(job.result_data)
        except Exception:
            result_data = job.result_data
    return {
        "id": str(job.id),
        "organization_id": str(job.organization_id),
        "project_id": str(job.project_id),
        "job_type": str(job.job_type),
        "status": str(job.status),
        "result_data": result_data,
        "error_message": job.error_message,
        "created_by": job.created_by,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "completed_at": job.completed_at,
    }


def _asset_dict(asset: MediaAsset) -> dict:
    return {
        "id": str(asset.id),
        "project_id": str(asset.project_id),
        "job_id": asset.job_id,
        "file_name": str(asset.file_name),
        "file_extension": str(asset.file_extension),
        "asset_type": str(asset.asset_type),
        "asset_source": asset.asset_source,
        "content_ref": asset.content_ref,
        "metadata_json": json.loads(asset.metadata_json)
        if asset.metadata_json
        else None,
        "status": str(asset.status),
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
    }


async def _build_project_export_payload(
    db: AsyncSession,
    *,
    project_id: str,
    user_org_id: str,
) -> dict[str, Any]:
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    jobs_result = await db.execute(
        select(ProjectJob)
        .where(
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == user_org_id,
        )
        .order_by(ProjectJob.created_at.desc(), ProjectJob.id.desc())
    )
    jobs = jobs_result.scalars().all()

    assets_result = await db.execute(
        select(MediaAsset)
        .where(
            MediaAsset.project_id == project_id,
            MediaAsset.organization_id == user_org_id,
        )
        .order_by(MediaAsset.created_at.desc(), MediaAsset.id.desc())
    )
    assets = assets_result.scalars().all()

    payload = {
        "project": _project_dict(project),
        "jobs": [_job_dict(job) for job in jobs],
        "assets": [_asset_dict(asset) for asset in assets],
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    return payload


def _build_project_export_zip(payload: dict[str, Any]) -> bytes:
    project_name = payload.get("project", {}).get("name") or "project"
    archive_buffer = BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(payload, ensure_ascii=False, default=str, indent=2),
        )
        archive.writestr(
            "README.txt",
            "Export comercial del proyecto\n\n"
            f"Proyecto: {project_name}\n"
            f"Exportado: {payload.get('exported_at')}\n\n"
            "Incluye:\n"
            "- manifest.json con proyecto, jobs y assets\n"
            "- Este README para compartir la demo con cliente interno\n",
        )
    return archive_buffer.getvalue()


async def _upsert_project_asset(
    db: AsyncSession,
    *,
    organization_id: str,
    project_id: str,
    job_id: str,
    file_name: str,
    content_ref: str,
    asset_source: str,
    metadata_json: dict[str, Any],
    created_by: Optional[str],
) -> MediaAsset:
    return await job_tracking_service.upsert_job_asset(
        db,
        organization_id=organization_id,
        project_id=project_id,
        job_id=job_id,
        file_name=file_name,
        content_ref=content_ref,
        asset_source=asset_source,
        metadata_json=metadata_json,
        created_by=created_by,
    )


@router.get("/{project_id}/jobs", response_model=ProjectJobListResponse)
async def list_project_jobs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(ProjectJob)
        .where(
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == user_org_id,
        )
        .order_by(ProjectJob.created_at.desc(), ProjectJob.id.desc())
    )
    jobs = result.scalars().all()
    _jobs: list[ProjectJobResponse] = [
        ProjectJobResponse.model_validate(_job_dict(j)) for j in jobs
    ]
    return ProjectJobListResponse(jobs=_jobs)


@router.get("/{project_id}/jobs/{job_id}", response_model=ProjectJobResponse)
async def get_project_job(
    project_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(
        select(ProjectJob).where(
            ProjectJob.id == job_id,
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == user_org_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return await _job_detail_dict(db, job)


# Direct job lookup (no project_id required for cross-endpoint compatibility)
@router.get("/jobs/{job_id}")
async def get_job_by_id(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(
        select(ProjectJob).where(
            ProjectJob.id == job_id,
            ProjectJob.organization_id == user_org_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "status": job.status,
        "result_data": json.loads(job.result_data) if job.result_data else None,
    }


@router.post("/{project_id}/jobs/{job_id}/retry", response_model=ProjectJobResponse)
async def retry_project_job(
    project_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(
        select(ProjectJob).where(
            ProjectJob.id == job_id,
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == user_org_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry job with status '{job.status}'. Only failed jobs can be retried.",
        )

    previous_status = job.status
    job.status = "pending"
    job.error_message = None
    job.result_data = None
    job.completed_at = None
    await _record_project_job_event(
        db,
        job=job,
        event_type="job_retry_requested",
        status_from=previous_status,
        status_to=job.status,
        message="Project job retry requested",
        metadata_json={"job_type": job.job_type},
    )
    await db.commit()
    await db.refresh(job)

    try:
        previous_status = job.status
        job.status = "processing"
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_running",
            status_from=previous_status,
            status_to=job.status,
            message="Retried project job started",
        )
        await db.commit()
        await db.refresh(job)

        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or not project.script_text:
            raise ValueError("Project has no script text")

        if job.job_type == "analyze":
            doc = await document_service.create_script_document(
                db,
                user_org_id=user_org_id,
                project_id=project_id,
                file_name=f"{project.name}_script.txt",
                raw_text=project.script_text,
                uploaded_by=current_user.user_id,
            )
            doc = await document_service.classify_document(
                db, doc, created_by=current_user.user_id
            )
            doc = await document_service.structure_document(
                db, doc, created_by=current_user.user_id
            )
            classification = getattr(doc, "classification", None)
            structured_data = getattr(doc, "structured_data", None)
            structured_payload: dict[str, Any] = {}
            if structured_data and structured_data.structured_payload_json:
                try:
                    structured_payload = json.loads(
                        structured_data.structured_payload_json
                    )
                except Exception:
                    structured_payload = {}
            result_payload = {
                "document_id": str(doc.id),
                "doc_type": str(classification.doc_type)
                if classification
                else "unknown",
                "confidence_score": float(classification.confidence_score)
                if classification and classification.confidence_score is not None
                else None,
                "structured_payload": structured_payload,
            }
            job.status = "completed"
            job.result_data = json.dumps(result_payload, ensure_ascii=False)
            job.completed_at = datetime.now(timezone.utc)
            asset = await _upsert_project_asset(
                db,
                organization_id=user_org_id,
                project_id=project_id,
                job_id=str(job.id),
                file_name=f"{project.name}_analysis.json",
                content_ref=f"virtual://{project_id}/{job.id}/analysis.json",
                asset_source="script_analysis",
                metadata_json=result_payload,
                created_by=current_user.user_id,
            )
            await _record_project_job_event(
                db,
                job=job,
                event_type="job_succeeded",
                status_from="processing",
                status_to=job.status,
                message="Retried project analysis completed",
                metadata_json={
                    "document_id": result_payload.get("document_id"),
                    "doc_type": result_payload.get("doc_type"),
                    "asset_id": str(asset.id),
                    "asset_source": asset.asset_source,
                },
            )

        elif job.job_type == "storyboard":
            storyboard = await _parse_storyboard(project.script_text)
            storyboard.project_id = project_id
            result_payload = {
                "total_scenes": storyboard.total_scenes,
                "scenes": [
                    {
                        "scene_number": s.scene_number,
                        "heading": s.heading,
                        "location": s.location,
                        "time_of_day": s.time_of_day,
                        "shots": [
                            {
                                "shot_number": sh.shot_number,
                                "shot_type": sh.shot_type,
                                "description": sh.description,
                            }
                            for sh in s.shots
                        ],
                    }
                    for s in storyboard.scenes
                ],
            }
            job.status = "completed"
            job.result_data = json.dumps(result_payload, ensure_ascii=False)
            job.completed_at = datetime.now(timezone.utc)
            asset = await _upsert_project_asset(
                db,
                organization_id=user_org_id,
                project_id=project_id,
                job_id=str(job.id),
                file_name=f"{project.name}_storyboard.json",
                content_ref=f"virtual://{project_id}/{job.id}/storyboard.json",
                asset_source="script_storyboard",
                metadata_json=result_payload,
                created_by=current_user.user_id,
            )
            await _record_project_job_event(
                db,
                job=job,
                event_type="job_succeeded",
                status_from="processing",
                status_to=job.status,
                message="Retried storyboard completed",
                metadata_json={
                    "total_scenes": result_payload.get("total_scenes"),
                    "asset_id": str(asset.id),
                    "asset_source": asset.asset_source,
                },
            )
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")

        await db.commit()
        await db.refresh(job)

    except Exception as exc:
        previous_status = job.status
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
        await _record_project_job_event(
            db,
            job=job,
            event_type="job_failed",
            status_from=previous_status,
            status_to=job.status,
            message="Retried project job failed",
            detail=job.error_message,
        )
        await db.commit()
        await db.refresh(job)

    return await _job_detail_dict(db, job)


class ProjectAssetResponse(BaseModel):
    id: str
    project_id: str
    job_id: Optional[str]
    file_name: str
    file_extension: str
    asset_type: str
    asset_source: Optional[str]
    content_ref: Optional[str]
    metadata_json: Optional[dict[str, Any]]
    canonical_path: Optional[str] = None
    status: str
    created_at: Optional[datetime]


class ProjectAssetListResponse(BaseModel):
    assets: list[ProjectAssetResponse]


class ProjectMetricsResponse(BaseModel):
    project_id: str
    jobs_count: int
    analyses_count: int
    storyboards_count: int
    assets_count: int


@router.get("/{project_id}/assets", response_model=ProjectAssetListResponse)
async def list_project_assets(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(MediaAsset)
        .where(
            MediaAsset.project_id == project_id,
            MediaAsset.organization_id == user_org_id,
        )
        .order_by(MediaAsset.created_at.desc(), MediaAsset.id.desc())
    )
    assets = result.scalars().all()
    return ProjectAssetListResponse(
        assets=[
            ProjectAssetResponse(
                id=str(a.id),
                project_id=str(a.project_id),
                job_id=a.job_id,
                file_name=str(a.file_name),
                file_extension=str(a.file_extension),
                asset_type=str(a.asset_type),
                asset_source=a.asset_source,
                content_ref=a.content_ref,
                metadata_json=(
                    json.loads(a.metadata_json) if a.metadata_json else None
                ),
                canonical_path=a.canonical_path,
                status=str(a.status),
                created_at=a.created_at,
            )
            for a in assets
        ]
    )


@router.get("/{project_id}/metrics", response_model=ProjectMetricsResponse)
async def get_project_metrics(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != user_org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    jobs_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.project_id == project_id,
                ProjectJob.organization_id == user_org_id,
            )
        )
    ).scalar_one() or 0
    analyses_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.project_id == project_id,
                ProjectJob.organization_id == user_org_id,
                ProjectJob.job_type == "analyze",
            )
        )
    ).scalar_one() or 0
    storyboards_count = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.project_id == project_id,
                ProjectJob.organization_id == user_org_id,
                ProjectJob.job_type == "storyboard",
            )
        )
    ).scalar_one() or 0
    assets_count = (
        await db.execute(
            select(func.count(MediaAsset.id)).where(
                MediaAsset.project_id == project_id,
                MediaAsset.organization_id == user_org_id,
            )
        )
    ).scalar_one() or 0

    return ProjectMetricsResponse(
        project_id=project_id,
        jobs_count=int(jobs_count),
        analyses_count=int(analyses_count),
        storyboards_count=int(storyboards_count),
        assets_count=int(assets_count),
    )


@router.get("/{project_id}/export/json")
async def export_project_json(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    await _enforce_export_permission(current_user.plan, export_format="json")
    payload = await _build_project_export_payload(
        db,
        project_id=project_id,
        user_org_id=user_org_id,
    )

    return Response(
        content=json.dumps(payload, ensure_ascii=False, default=str, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="project-{project_id}.json"'
        },
    )


@router.get("/{project_id}/export/zip")
async def export_project_zip(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    await _enforce_export_permission(current_user.plan, export_format="zip")
    payload = await _build_project_export_payload(
        db,
        project_id=project_id,
        user_org_id=user_org_id,
    )
    archive_bytes = _build_project_export_zip(payload)

    return Response(
        content=archive_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="project-{project_id}.zip"'
        },
    )


IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


class ProjectImageAssetItem(BaseModel):
    asset_id: str
    file_name: str
    mime_type: str
    created_at: datetime
    preview_url: str
    thumbnail_url: str


class ProjectImageAssetPaginationMeta(BaseModel):
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ProjectImageAssetsResponse(BaseModel):
    items: list[ProjectImageAssetItem]
    meta: ProjectImageAssetPaginationMeta


@router.get("/{project_id}/assets/image-assets", response_model=ProjectImageAssetsResponse)
async def list_project_image_assets(
    project_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """
    Paginated list of image assets for the Asset Picker Modal.
    Tenant-safe: only returns assets belonging to the user's organization.
    Filters to image/* mime types only.
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    if size > 100:
        size = 100

    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != tenant.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    base_query = select(MediaAsset).where(
        MediaAsset.project_id == project_id,
        MediaAsset.organization_id == tenant.organization_id,
        MediaAsset.mime_type.in_(IMAGE_MIME_TYPES),
        MediaAsset.status == MediaAssetStatus.INDEXED,
    )

    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_items = count_result.scalar_one() or 0
    total_pages = (total_items + size - 1) // size if total_items > 0 else 1

    offset = (page - 1) * size
    query = base_query.order_by(MediaAsset.created_at.desc()).offset(offset).limit(size)
    assets = (await db.execute(query)).scalars().all()

    items = [
        ProjectImageAssetItem(
            asset_id=str(a.id),
            file_name=str(a.file_name),
            mime_type=str(a.mime_type) if a.mime_type else "image/unknown",
            created_at=a.created_at,
            preview_url=f"/api/projects/{project_id}/presentation/assets/{a.id}/preview",
            thumbnail_url=f"/api/projects/{project_id}/presentation/assets/{a.id}/thumbnail",
        )
        for a in assets
    ]

    return ProjectImageAssetsResponse(
        items=items,
        meta=ProjectImageAssetPaginationMeta(
            page=page,
            size=size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )
