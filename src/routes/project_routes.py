import json
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project, ProjectJob, User as DBUser
from models.storage import MediaAsset, MediaAssetType, MediaAssetStatus
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from services.document_service import document_service
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

    try:
        job.status = "processing"
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

        await _upsert_project_asset(
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
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
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

    try:
        job.status = "processing"
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

        await _upsert_project_asset(
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

        await db.commit()
        await db.refresh(job)

        return storyboard
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
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
    result = await db.execute(
        select(MediaAsset).where(
            MediaAsset.project_id == project_id,
            MediaAsset.job_id == job_id,
            MediaAsset.asset_source == asset_source,
        )
    )
    asset = result.scalar_one_or_none()

    if asset is None:
        asset = MediaAsset(
            organization_id=organization_id,
            project_id=project_id,
            storage_source_id=None,
            file_name=file_name,
            relative_path=content_ref,
            canonical_path=content_ref,
            content_ref=content_ref,
            file_extension="json",
            mime_type="application/json",
            asset_type=MediaAssetType.DOCUMENT,
            metadata_json=json.dumps(metadata_json, ensure_ascii=False),
            asset_source=asset_source,
            job_id=str(job_id),
            status=MediaAssetStatus.INDEXED,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )
        db.add(asset)
    else:
        asset.file_name = file_name
        asset.relative_path = content_ref
        asset.canonical_path = content_ref
        asset.content_ref = content_ref
        asset.metadata_json = json.dumps(metadata_json, ensure_ascii=False)
        asset.status = MediaAssetStatus.INDEXED

    return asset


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

    return _job_dict(job)


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

    job.status = "pending"
    job.error_message = None
    job.result_data = None
    job.completed_at = None
    await db.commit()
    await db.refresh(job)

    try:
        job.status = "processing"
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
            await _upsert_project_asset(
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
            await _upsert_project_asset(
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
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")

        await db.commit()
        await db.refresh(job)

    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(job)

    return _job_dict(job)


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
