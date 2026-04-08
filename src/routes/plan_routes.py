from fastapi import APIRouter, HTTPException
from typing import Optional, List

from schemas.plan_schema import PlanInfo, PlanLimits, UserPlanStatus
from services.plan_limits_service import plan_limits_service, user_plan_tracker

router = APIRouter(prefix="/api/plans", tags=["plans"])


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
                allowed_task_types=plan.allowed_task_types
            ),
            features=plan.features
        )
        for key, plan in plans.items()
    ]


@router.get("/me", response_model=UserPlanStatus)
async def get_my_plan(user_id: str, plan_name: str = "free"):
    status = user_plan_tracker.get_user_status(user_id, plan_name)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return UserPlanStatus(**status)


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
            "allowed_task_types": plan.allowed_task_types
        },
        "features": plan.features
    }


@router.get("/{plan_name}/can-run/{task_type}")
async def check_plan_can_run(plan_name: str, task_type: str):
    can_run = plan_limits_service.can_run_task(plan_name, task_type)
    return {
        "plan": plan_name,
        "task_type": task_type,
        "allowed": can_run
    }
