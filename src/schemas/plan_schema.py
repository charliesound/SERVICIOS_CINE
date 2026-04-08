from pydantic import BaseModel
from typing import List, Optional


class PlanLimits(BaseModel):
    max_active_jobs: int
    max_queued_jobs: int
    priority_score: int
    allowed_task_types: List[str]


class PlanInfo(BaseModel):
    id: str
    name: str
    display_name: str
    price: float
    billing_period: str
    limits: PlanLimits
    features: List[str]


class UserPlanStatus(BaseModel):
    plan: str
    active_jobs: int
    max_active_jobs: int
    queued_jobs: int
    max_queued_jobs: int
    can_submit_active: bool
    can_submit_queued: bool
    priority_score: int
