from pydantic import BaseModel
from typing import List, Optional


class PlanLimits(BaseModel):
    max_active_jobs: int
    max_queued_jobs: int
    priority_score: int
    max_projects: int
    max_total_jobs: int
    max_analyses: int
    max_storyboards: int
    export_json: bool
    export_zip: bool = False
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
    projects_count: int = 0
    jobs_count: int = 0
    analyses_count: int = 0
    storyboards_count: int = 0
    max_projects: int = -1
    max_total_jobs: int = -1
    max_analyses: int = -1
    max_storyboards: int = -1
    export_json: bool = False
    export_zip: bool = False
    recommended_upgrade: Optional[str] = None


class PlanChangeRequest(BaseModel):
    target_plan: str


class PlanChangeResponse(BaseModel):
    previous_plan: str
    current_plan: str
    activation_mode: str
    message: str
    effective_immediately: bool = True
