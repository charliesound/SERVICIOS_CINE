from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import yaml
import aiohttp
import asyncio
import os
from pathlib import Path


class BackendType(Enum):
    STILL = "still"
    VIDEO = "video"
    DUBBING = "dubbing"
    RESTORATION = "restoration"
    THREE_D = "3d"
    LAB = "lab"


@dataclass
class BackendInstance:
    name: str
    type: BackendType
    host: str
    port: int
    base_url: str
    health_endpoint: str
    max_concurrent_jobs: int
    priority: int
    enabled: bool
    capabilities: List[str]
    current_jobs: int = 0
    healthy: bool = True
    last_health_check: Optional[float] = None

    @property
    def available_slots(self) -> int:
        return self.max_concurrent_jobs - self.current_jobs

    @property
    def is_available(self) -> bool:
        return self.enabled and self.healthy and self.available_slots > 0


@dataclass
class RoutingRules:
    task_type_mapping: Dict[str, str]
    fallback_backend: str
    experimental_backend: str


class InstanceRegistry:
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
        self._backends: Dict[str, BackendInstance] = {}
        self._routing_rules: Optional[RoutingRules] = None
        self._config_path = Path(__file__).parent.parent / "config" / "instances.yml"

    def load_config(self, config_path: Optional[str] = None) -> None:
        if config_path:
            self._config_path = Path(config_path)

        with open(self._config_path, 'r') as f:
            config = yaml.safe_load(f)

        self._backends.clear()
        for key, data in config['backends'].items():
            base_url = self._resolve_backend_base_url(key, data['base_url'])
            self._backends[key] = BackendInstance(
                name=data['name'],
                type=BackendType(key),
                host=data['host'],
                port=data['port'],
                base_url=base_url,
                health_endpoint=data['health_endpoint'],
                max_concurrent_jobs=data['max_concurrent_jobs'],
                priority=data['priority'],
                enabled=data['enabled'],
                capabilities=data['capabilities']
            )

        self._routing_rules = RoutingRules(
            task_type_mapping=config['routing_rules']['task_type_mapping'],
            fallback_backend=config['routing_rules']['fallback_backend'],
            experimental_backend=config['routing_rules']['experimental_backend']
        )

    def _resolve_backend_base_url(self, backend_key: str, yaml_base_url: str) -> str:
        if backend_key == "still":
            return (
                os.getenv("COMFYUI_STILL_BASE_URL")
                or os.getenv("COMFYUI_BASE_URL")
                or os.getenv("COMFYUI_STORYBOARD_BASE_URL")
                or yaml_base_url
            )
        if backend_key == "video":
            return os.getenv("COMFYUI_VIDEO_BASE_URL") or yaml_base_url
        if backend_key == "dubbing":
            return os.getenv("COMFYUI_DUBBING_BASE_URL") or yaml_base_url
        if backend_key == "restoration":
            return os.getenv("COMFYUI_RESTORATION_BASE_URL") or yaml_base_url
        if backend_key == "3d":
            return os.getenv("COMFYUI_3D_BASE_URL") or yaml_base_url
        if backend_key == "lab":
            return os.getenv("COMFYUI_LAB_BASE_URL") or yaml_base_url
        return yaml_base_url

    def get_backend(self, backend_key: str) -> Optional[BackendInstance]:
        return self._backends.get(backend_key)

    def get_all_backends(self) -> Dict[str, BackendInstance]:
        return self._backends.copy()

    def get_available_backends(self) -> List[BackendInstance]:
        return [b for b in self._backends.values() if b.is_available]

    def resolve_backend_for_task(self, task_type: str) -> Optional[BackendInstance]:
        if not self._routing_rules:
            return None

        backend_key = self._routing_rules.task_type_mapping.get(
            task_type,
            self._routing_rules.fallback_backend
        )
        return self.get_backend(backend_key)

    def get_backend_for_workflow(self, workflow_key: str) -> Optional[BackendInstance]:
        workflow_backend_map = {
            "sd_xl": "still",
            "sd15": "still",
            "sdxl_turbo": "still",
            "animatediff": "video",
            "svd": "video",
            "wav2lip": "dubbing",
            "tts": "dubbing",
            "xtts": "dubbing",
            "experimental_001": "lab",
        }
        backend_key = workflow_backend_map.get(workflow_key)
        if backend_key:
            return self.get_backend(backend_key)
        return self.resolve_backend_for_task(workflow_key.split('_')[0])

    async def check_health(self, backend_key: str) -> bool:
        backend = self.get_backend(backend_key)
        if not backend:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{backend.base_url}{backend.health_endpoint}"
                async with session.get(url, timeout=5) as resp:
                    backend.healthy = resp.status == 200
                    return backend.healthy
        except Exception:
            backend.healthy = False
            return False

    async def check_all_health(self) -> Dict[str, bool]:
        tasks = [self.check_health(key) for key in self._backends.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(self._backends.keys(), results))

    def increment_jobs(self, backend_key: str) -> bool:
        backend = self.get_backend(backend_key)
        if backend and backend.is_available:
            backend.current_jobs += 1
            return True
        return False

    def decrement_jobs(self, backend_key: str) -> bool:
        backend = self.get_backend(backend_key)
        if backend and backend.current_jobs > 0:
            backend.current_jobs -= 1
            return True
        return False

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "total_backends": len(self._backends),
            "available_backends": len(self.get_available_backends()),
            "backends": {
                key: {
                    "name": b.name,
                    "type": b.type.value,
                    "enabled": b.enabled,
                    "healthy": b.healthy,
                    "current_jobs": b.current_jobs,
                    "max_jobs": b.max_concurrent_jobs,
                    "available_slots": b.available_slots,
                    "base_url": b.base_url
                }
                for key, b in self._backends.items()
            }
        }


registry = InstanceRegistry()
