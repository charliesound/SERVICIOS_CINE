from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import yaml
from pathlib import Path


@dataclass
class PlanLimits:
    name: str
    display_name: str
    price: float
    billing_period: str
    max_active_jobs: int
    max_queued_jobs: int
    priority_score: int
    allowed_task_types: List[str]
    features: List[str]


class PlanLimitsService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._plans: Dict[str, PlanLimits] = {}
        self._load_plans()

    def _load_plans(self, config_path: Optional[str] = None):
        if config_path:
            path = Path(config_path)
        else:
            path = Path(__file__).parent.parent / "config" / "plans.yml"

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        for key, plan_data in data['plans'].items():
            self._plans[key] = PlanLimits(
                name=key,
                display_name=plan_data['display_name'],
                price=plan_data['price'],
                billing_period=plan_data['billing_period'],
                max_active_jobs=plan_data['max_active_jobs'],
                max_queued_jobs=plan_data['max_queued_jobs'],
                priority_score=plan_data['priority_score'],
                allowed_task_types=plan_data['allowed_task_types'],
                features=plan_data['features']
            )

    def get_plan(self, plan_name: str) -> Optional[PlanLimits]:
        return self._plans.get(plan_name)

    def get_all_plans(self) -> Dict[str, PlanLimits]:
        return self._plans.copy()

    def get_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": key,
                "name": plan.display_name,
                "price": plan.price,
                "billing_period": plan.billing_period,
                "max_active_jobs": plan.max_active_jobs,
                "max_queued_jobs": plan.max_queued_jobs,
                "priority_score": plan.priority_score,
                "allowed_task_types": plan.allowed_task_types,
                "features": plan.features
            }
            for key, plan in self._plans.items()
        ]

    def can_run_task(self, plan_name: str, task_type: str) -> bool:
        plan = self.get_plan(plan_name)
        if not plan:
            return False
        return task_type in plan.allowed_task_types

    def get_priority_score(self, plan_name: str) -> int:
        plan = self.get_plan(plan_name)
        return plan.priority_score if plan else 0


class UserPlanTracker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._user_jobs: Dict[str, Dict[str, int]] = {}
        self._limits_service = PlanLimitsService()

    def track_active_job(self, user_id: str, plan_name: str) -> bool:
        if user_id not in self._user_jobs:
            self._user_jobs[user_id] = {"active": 0, "queued": 0}

        plan = self._limits_service.get_plan(plan_name)
        if not plan:
            return False

        if self._user_jobs[user_id]["active"] >= plan.max_active_jobs:
            return False

        self._user_jobs[user_id]["active"] += 1
        return True

    def track_queued_job(self, user_id: str, plan_name: str) -> bool:
        if user_id not in self._user_jobs:
            self._user_jobs[user_id] = {"active": 0, "queued": 0}

        plan = self._limits_service.get_plan(plan_name)
        if not plan:
            return False

        if self._user_jobs[user_id]["queued"] >= plan.max_queued_jobs:
            return False

        self._user_jobs[user_id]["queued"] += 1
        return True

    def release_active_job(self, user_id: str):
        if user_id in self._user_jobs and self._user_jobs[user_id]["active"] > 0:
            self._user_jobs[user_id]["active"] -= 1

    def release_queued_job(self, user_id: str):
        if user_id in self._user_jobs and self._user_jobs[user_id]["queued"] > 0:
            self._user_jobs[user_id]["queued"] -= 1

    def get_user_status(self, user_id: str, plan_name: str) -> Dict[str, Any]:
        plan = self._limits_service.get_plan(plan_name)
        if not plan:
            return {"error": "Plan not found"}

        user_data = self._user_jobs.get(user_id, {"active": 0, "queued": 0})

        return {
            "plan": plan_name,
            "active_jobs": user_data["active"],
            "max_active_jobs": plan.max_active_jobs,
            "queued_jobs": user_data["queued"],
            "max_queued_jobs": plan.max_queued_jobs,
            "can_submit_active": user_data["active"] < plan.max_active_jobs,
            "can_submit_queued": user_data["queued"] < plan.max_queued_jobs,
            "priority_score": plan.priority_score
        }

    def validate_job_submission(self, user_id: str, plan_name: str) -> tuple[bool, Optional[str]]:
        plan = self._limits_service.get_plan(plan_name)
        if not plan:
            return False, f"Plan '{plan_name}' not found"

        status = self.get_user_status(user_id, plan_name)

        if not status.get("can_submit_active") and not status.get("can_submit_queued"):
            return False, f"Job limits reached. Max {plan.max_active_jobs} active + {plan.max_queued_jobs} queued"

        return True, None


plan_limits_service = PlanLimitsService()
user_plan_tracker = UserPlanTracker()
