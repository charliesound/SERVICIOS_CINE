from typing import Dict, List, Any
from datetime import datetime, timedelta
import random

from .user_service import user_store, User
from .workflow_preset_service import preset_service


class DemoService:
    DEMO_USERS = {
        "demo_free": {
            "username": "demo_free",
            "email": "demo_free@servicios-cine.com",
            "password": "demo123",
            "plan": "free",
            "role": "user"
        },
        "demo_studio": {
            "username": "demo_studio",
            "email": "demo_studio@servicios-cine.com",
            "password": "demo123",
            "plan": "studio",
            "role": "user"
        },
        "demo_creator": {
            "username": "demo_creator",
            "email": "demo_creator@servicios-cine.com",
            "password": "demo123",
            "plan": "creator",
            "role": "user"
        },
        "demo_enterprise": {
            "username": "demo_enterprise",
            "email": "demo_enterprise@servicios-cine.com",
            "password": "demo123",
            "plan": "enterprise",
            "role": "user"
        },
        "demo_admin": {
            "username": "demo_admin",
            "email": "admin@servicios-cine.com",
            "password": "admin123",
            "plan": "enterprise",
            "role": "admin"
        }
    }

    DEMO_PROJECTS = [
        {
            "id": "proj_cine_robot",
            "name": "Cine: Robot en Atardecer",
            "description": "Proyecto demo con secuencias de un robot en diferentes escenarios",
            "workflow_key": "still_text_to_image_pro",
            "status": "active"
        },
        {
            "id": "proj_storyboard_01",
            "name": "Storyboard: Escena de Acción",
            "description": "Storyboarddemo con 6 frames para secuencia de acción",
            "workflow_key": "still_storyboard_frame",
            "status": "active"
        },
        {
            "id": "proj_video_demo",
            "name": "Video: Transición Paisaje",
            "description": "Generación de video con transiciones de paisaje",
            "workflow_key": "video_text_to_video_base",
            "status": "active"
        },
        {
            "id": "proj_dubbing_spanish",
            "name": "Doblaje: Narración Documental",
            "description": "Narración en español con voz clara",
            "workflow_key": "dubbing_tts_es_es",
            "status": "active"
        },
        {
            "id": "proj_character_set",
            "name": "Consistencia de Personaje",
            "description": "Generar mismo personaje en diferentes poses",
            "workflow_key": "still_character_consistency",
            "status": "active"
        }
    ]

    DEMO_PRESETS = [
        {
            "name": "Cinematic Portrait",
            "workflow_key": "still_img2img_cinematic",
            "description": "Retratos cinematográficos con iluminación dramática",
            "inputs": {
                "prompt": "cinematic portrait, dramatic lighting, film grain",
                "negative_prompt": "blurry, low quality",
                "strength": 0.7,
                "steps": 30
            },
            "tags": ["portrait", "cinematic", "dramatic"],
            "is_public": True
        },
        {
            "name": "Fast Storyboard",
            "workflow_key": "still_storyboard_frame",
            "description": "Generación rápida de frames para storyboard",
            "inputs": {
                "prompt": "professional storyboard frame",
                "aspect_ratio": "16:9",
                "steps": 20
            },
            "tags": ["storyboard", "fast", "production"],
            "is_public": True
        },
        {
            "name": "Voice Clone Basic",
            "workflow_key": "dubbing_voice_clone_single",
            "description": "Clonación de voz básica para doblaje",
            "inputs": {
                "similarity": 0.8,
                "stability": 0.7
            },
            "tags": ["voice", "clone", "dubbing"],
            "is_public": True
        }
    ]

    def __init__(self):
        self._demo_jobs: Dict[str, List[Dict]] = {}
        self._seeded = False

    def seed_demo_data(self) -> Dict[str, Any]:
        results = {
            "users_created": 0,
            "presets_created": 0,
            "projects_created": 0,
            "jobs_created": 0
        }

        for user_id, user_data in self.DEMO_USERS.items():
            if not user_store.get_user_by_email(user_data["email"]):
                user = user_store.create_user(
                    username=user_data["username"],
                    email=user_data["email"],
                    password=self._hash_password(user_data["password"]),
                    plan=user_data["plan"]
                )
                results["users_created"] += 1

        for preset_data in self.DEMO_PRESETS:
            try:
                preset_service.create_preset(
                    name=preset_data["name"],
                    workflow_key=preset_data["workflow_key"],
                    inputs=preset_data["inputs"],
                    user_id="system",
                    description=preset_data["description"],
                    tags=preset_data["tags"],
                    is_public=preset_data["is_public"]
                )
                results["presets_created"] += 1
            except Exception:
                pass

        for project in self.DEMO_PROJECTS:
            self._seed_project(project)
            results["projects_created"] += 1

        self._seed_demo_jobs()
        results["jobs_created"] = len(self._demo_jobs.get("demo_studio", []))

        self._seeded = True

        return results

    def _seed_project(self, project: Dict) -> None:
        pass

    def _seed_demo_jobs(self) -> None:
        statuses = ["succeeded", "succeeded", "succeeded", "running", "queued"]
        base_time = datetime.utcnow()

        for user_id in ["demo_studio", "demo_creator"]:
            jobs = []
            for i, status in enumerate(statuses):
                job = {
                    "job_id": f"demo_{user_id}_{i+1:03d}",
                    "task_type": random.choice(["still", "video", "dubbing"]),
                    "workflow_key": random.choice([
                        "still_text_to_image_pro",
                        "still_img2img_cinematic",
                        "video_text_to_video_base",
                        "dubbing_tts_es_es"
                    ]),
                    "status": status,
                    "backend": random.choice(["still", "video", "dubbing"]),
                    "created_at": (base_time - timedelta(hours=i*2)).isoformat(),
                    "started_at": (base_time - timedelta(hours=i*2 - 1)).isoformat() if status != "queued" else None,
                    "completed_at": (base_time - timedelta(hours=i*2 - 2)).isoformat() if status == "succeeded" else None,
                    "error": None if status != "failed" else "Simulated error"
                }
                jobs.append(job)

            self._demo_jobs[user_id] = jobs

    def _hash_password(self, password: str) -> str:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def reset_demo_data(self) -> Dict[str, Any]:
        self._demo_jobs.clear()
        self._seeded = False
        results = self.seed_demo_data()
        results["message"] = "Demo data reset successfully"
        return results

    def get_demo_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "user_id": user_id,
                "username": data["username"],
                "email": data["email"],
                "plan": data["plan"],
                "role": data["role"],
                "password_hint": "Usar la contraseña: demo123 (admin: admin123)"
            }
            for user_id, data in self.DEMO_USERS.items()
        ]

    def get_demo_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        return self._demo_jobs.get(user_id, [])

    def is_demo_user(self, user_id: str) -> bool:
        return user_id in self.DEMO_USERS or user_id.startswith("demo_")

    def is_seeded(self) -> bool:
        return self._seeded

    def get_demo_status(self) -> Dict[str, Any]:
        return {
            "seeded": self._seeded,
            "demo_users_count": len(self.DEMO_USERS),
            "demo_projects_count": len(self.DEMO_PROJECTS),
            "demo_presets_count": len(self.DEMO_PRESETS),
            "total_demo_jobs": sum(len(jobs) for jobs in self._demo_jobs.values())
        }


demo_service = DemoService()
