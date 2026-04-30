from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import aiohttp
import asyncio
import os
from enum import Enum

from .instance_registry import InstanceRegistry, BackendInstance, BackendType

COMFYUI_HTTP_TIMEOUT = float(os.getenv("COMFYUI_HTTP_TIMEOUT", "30"))
COMFYUI_CONNECT_TIMEOUT = float(os.getenv("COMFYUI_CONNECT_TIMEOUT", "10"))


class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobRequest:
    task_type: str
    workflow_key: str
    prompt: Dict[str, Any]
    priority: int = 5
    target_instance: Optional[str] = None
    user_id: Optional[str] = None
    user_plan: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "workflow_key": self.workflow_key,
            "prompt": self.prompt,
            "priority": self.priority,
            "target_instance": self.target_instance,
            "user_id": self.user_id,
            "user_plan": self.user_plan,
            "parameters": self.parameters or {},
        }


@dataclass
class JobResponse:
    job_id: str
    status: JobStatus
    backend: str
    backend_url: str
    queue_position: Optional[int] = None
    estimated_time: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "backend": self.backend,
            "backend_url": self.backend_url,
            "queue_position": self.queue_position,
            "estimated_time": self.estimated_time,
            "error": self.error,
        }


@dataclass
class JobResult:
    job_id: str
    status: JobStatus
    outputs: Optional[List[str]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "outputs": self.outputs,
            "error": self.error,
            "execution_time": self.execution_time,
        }


class ComfyUIClient:
    def __init__(self, backend: BackendInstance):
        self.backend = backend
        self.base_url = backend.base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._timeout = aiohttp.ClientTimeout(
            total=None,
            connect=COMFYUI_CONNECT_TIMEOUT,
            sock_read=COMFYUI_HTTP_TIMEOUT,
        )

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def post_prompt(
        self, prompt: Dict[str, Any], workflow_key: str
    ) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/prompt"
        payload = {"prompt": prompt, "workflow_key": workflow_key}
        async with self.session.post(endpoint, json=payload) as resp:
            result = await resp.json()
            return result

    async def get_history(self, prompt_id: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/history/{prompt_id}"
        async with self.session.get(endpoint) as resp:
            return await resp.json()

    async def get_queue(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/queue"
        async with self.session.get(endpoint) as resp:
            return await resp.json()

    async def get_system_stats(self) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/system_stats"
        async with self.session.get(endpoint) as resp:
            return await resp.json()

    async def delete_queue_item(self, prompt_id: str) -> bool:
        endpoint = f"{self.base_url}/queue"
        payload = {"prompt_id": prompt_id}
        async with self.session.delete(endpoint, json=payload) as resp:
            return resp.status == 200


class ComfyUIFactory:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.registry = InstanceRegistry()

    def get_client(self, backend_key: str) -> Optional[ComfyUIClient]:
        backend = self.registry.get_backend(backend_key)
        if backend:
            return ComfyUIClient(backend)
        return None

    def get_client_for_task(self, task_type: str) -> Optional[ComfyUIClient]:
        backend = self.registry.resolve_backend_for_task(task_type)
        if backend:
            return ComfyUIClient(backend)
        return None

    def get_client_for_workflow(self, workflow_key: str) -> Optional[ComfyUIClient]:
        backend = self.registry.get_backend_for_workflow(workflow_key)
        if backend:
            return ComfyUIClient(backend)
        return None


factory = ComfyUIFactory()
