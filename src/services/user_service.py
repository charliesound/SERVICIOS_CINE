from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from enum import Enum

from .plan_limits_service import plan_limits_service, user_plan_tracker
from .queue_service import queue_service, QueueStatus
from .job_router import router, JobRequest


class UserRole(Enum):
    USER = "user"
    CREATOR = "creator"
    STUDIO = "studio"
    ADMIN = "admin"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    hashed_password: str
    plan: str = "free"
    role: str = "user"
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class UserStore:
    _instance = None
    _users: Dict[str, User] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_user(self, username: str, email: str, password: str, plan: str = "free") -> User:
        user_id = str(uuid.uuid4())[:8]
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=password,
            plan=plan
        )
        self._users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def update_user_plan(self, user_id: str, plan: str) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        user.plan = plan
        return True

    def get_all_users(self) -> List[User]:
        return list(self._users.values())


user_store = UserStore()
