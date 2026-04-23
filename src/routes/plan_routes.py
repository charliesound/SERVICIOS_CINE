from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Organization, Project, ProjectJob, User as DBUser
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.plan_schema import (
    PlanChangeRequest,
    PlanChangeResponse,
    PlanInfo,
    PlanLimits,
    UserPlanStatus,
)
from services.account_service import (
    apply_internal_plan_change,
    get_user_by_id,
    normalize_plan_name,
)
from services.plan_limits_service import plan_limits_service

router = APIRouter(prefix="/api/plans", tags=["plans"])


async def _get_effective_user(
    db: AsyncSession,
    *,
    current_user: Optional[UserResponse],
    user_id: Optional[str],
) -> DBUser:
    effective_user_id = current_user.user_id if current_user else user_id
    if not effective_user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user = await get_user_by_id(db, effective_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def _get_org_usage_counts(
    db: AsyncSession,
    organization_id: str,
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
    active_jobs = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.organization_id == organization_id,
                ProjectJob.status == "processing",
            )
        )
    ).scalar_one() or 0
    queued_jobs = (
        await db.execute(
            select(func.count(ProjectJob.id)).where(
                ProjectJob.organization_id == organization_id,
                ProjectJob.status == "pending",
            )
        )
    ).scalar_one() or 0

    return {
        "projects_count": int(projects_count),
        "jobs_count": int(jobs_count),
        "analyses_count": int(analyses_count),
        "storyboards_count": int(storyboards_count),
        "active_jobs": int(active_jobs),
        "queued_jobs": int(queued_jobs),
    }


async def _resolve_effective_plan_for_user(db: AsyncSession, user: DBUser) -> str:
    plan_name = normalize_plan_name(getattr(user, "billing_plan", None))
    if plan_name != "free" or getattr(user, "billing_plan", None):
        return plan_name

    if getattr(user, "organization_id", None):
        org_result = await db.execute(
            select(Organization).where(Organization.id == user.organization_id)
        )
        organization = org_result.scalar_one_or_none()
        return normalize_plan_name(getattr(organization, "billing_plan", None))

    return "free"


def _recommended_upgrade(plan_name: str, usage: dict[str, int], plan) -> Optional[str]:
    if plan.max_projects != -1 and usage["projects_count"] >= plan.max_projects:
        return "creator"
    if plan.max_total_jobs != -1 and usage["jobs_count"] >= plan.max_total_jobs:
        return "producer"
    if (
        plan.max_storyboards != -1
        and usage["storyboards_count"] >= plan.max_storyboards
    ):
        return "studio"
    if not plan.export_json:
        return "creator"
    return None


@router.get("/catalog", response_model=List[PlanInfo])
async def get_plans_catalog():
    plans = plan_limits_service.get_all_plans()
    return [
        PlanInfo(
            id=key,
            name=plan.name,
            display_name=plan.display_name,
            price=plan.price,
            billing_period=plan.billing_period,
            limits=PlanLimits(
                max_active_jobs=plan.max_active_jobs,
                max_queued_jobs=plan.max_queued_jobs,
                priority_score=plan.priority_score,
                max_projects=plan.max_projects,
                max_total_jobs=plan.max_total_jobs,
                max_analyses=plan.max_analyses,
                max_storyboards=plan.max_storyboards,
                export_json=plan.export_json,
                export_zip=plan.export_zip,
                allowed_task_types=plan.allowed_task_types,
            ),
            features=plan.features,
        )
        for key, plan in plans.items()
    ]


@router.get("/me", response_model=UserPlanStatus)
async def get_my_plan(
    user_id: Optional[str] = None,
    plan_name: str = "free",
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    del plan_name
    user = await _get_effective_user(db, current_user=current_user, user_id=user_id)
    effective_plan = await _resolve_effective_plan_for_user(db, user)
    plan = plan_limits_service.get_plan(effective_plan)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    usage = {
        "projects_count": 0,
        "jobs_count": 0,
        "analyses_count": 0,
        "storyboards_count": 0,
        "active_jobs": 0,
        "queued_jobs": 0,
    }
    if user.organization_id:
        usage = await _get_org_usage_counts(db, str(user.organization_id))

    recommended_upgrade = _recommended_upgrade(effective_plan, usage, plan)

    return UserPlanStatus(
        plan=effective_plan,
        active_jobs=usage["active_jobs"],
        max_active_jobs=plan.max_active_jobs,
        queued_jobs=usage["queued_jobs"],
        max_queued_jobs=plan.max_queued_jobs,
        can_submit_active=plan.max_active_jobs == -1
        or usage["active_jobs"] < plan.max_active_jobs,
        can_submit_queued=plan.max_queued_jobs == -1
        or usage["queued_jobs"] < plan.max_queued_jobs,
        priority_score=plan.priority_score,
        projects_count=usage["projects_count"],
        jobs_count=usage["jobs_count"],
        analyses_count=usage["analyses_count"],
        storyboards_count=usage["storyboards_count"],
        max_projects=plan.max_projects,
        max_total_jobs=plan.max_total_jobs,
        max_analyses=plan.max_analyses,
        max_storyboards=plan.max_storyboards,
        export_json=plan.export_json,
        export_zip=plan.export_zip,
        recommended_upgrade=recommended_upgrade,
    )


@router.post("/change", response_model=PlanChangeResponse)
async def change_my_plan(
    payload: PlanChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user = await get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        previous_plan, current_plan = await apply_internal_plan_change(
            db, user, payload.target_plan
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Plan not found")

    return PlanChangeResponse(
        previous_plan=previous_plan,
        current_plan=current_plan,
        activation_mode="internal_manual",
        message=(
            f"Plan activado internamente para tu organizacion: {previous_plan} -> {current_plan}. "
            "No se ha iniciado ningun cobro real y el cambio queda operativo al instante para la demo comercial."
        ),
        effective_immediately=True,
    )


@router.get("/{plan_name}")
async def get_plan_details(plan_name: str):
    plan = plan_limits_service.get_plan(plan_name)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "id": plan.name,
        "name": plan.display_name,
        "price": plan.price,
        "billing_period": plan.billing_period,
        "limits": {
            "max_active_jobs": plan.max_active_jobs,
            "max_queued_jobs": plan.max_queued_jobs,
            "priority_score": plan.priority_score,
            "max_projects": plan.max_projects,
            "max_total_jobs": plan.max_total_jobs,
            "max_analyses": plan.max_analyses,
            "max_storyboards": plan.max_storyboards,
            "export_json": plan.export_json,
            "export_zip": plan.export_zip,
            "allowed_task_types": plan.allowed_task_types,
        },
        "features": plan.features,
    }


@router.get("/{plan_name}/can-run/{task_type}")
async def check_plan_can_run(plan_name: str, task_type: str):
    can_run = plan_limits_service.can_run_task(plan_name, task_type)
    return {"plan": plan_name, "task_type": task_type, "allowed": can_run}
