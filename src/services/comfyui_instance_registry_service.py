from __future__ import annotations

"""
DEPRECATED — Legacy ComfyUI instance registry.

Use services.instance_registry instead.
This module is kept as a backward-compatible wrapper.
"""

import logging
from typing import Any, Optional

from services.instance_registry import registry as unified_registry

logger = logging.getLogger("servicios_cine.comfyui_registry")

LEGACY_TO_BACKEND_KEY = {
    "image": "still",
    "video_cine": "video",
    "dubbing_audio": "dubbing",
    "restoration": "restoration",
    "three_d": "3d",
    "lab": "lab",
}

BACKEND_TO_LEGACY_KEY = {value: key for key, value in LEGACY_TO_BACKEND_KEY.items()}

LEGACY_TASK_ALIASES = {
    "i2v": "img2vid",
    "t2v": "text_to_video",
    "previz": "video",
    "lipsync": "audio",
    "upscale": "restoration",
    "repair": "restoration",
    "mesh": "3d",
    "scene": "scene_3d",
}


class ComfyUIInstanceRecord:
    def __init__(
        self,
        key: str,
        name: str,
        base_url: str,
        port: int,
        enabled: bool,
        task_types: list[str],
        health_endpoint: str,
    ) -> None:
        self.key = key
        self.name = name
        self.base_url = base_url
        self.port = port
        self.enabled = enabled
        self.task_types = task_types
        self.health_endpoint = health_endpoint


class ComfyUIInstanceRegistry:
    _instance: Optional[ComfyUIInstanceRegistry] = None

    def __new__(cls) -> ComfyUIInstanceRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._instances: dict[str, ComfyUIInstanceRecord] = {}

    def _to_backend_key(self, instance_key: str) -> str:
        return LEGACY_TO_BACKEND_KEY.get(instance_key, instance_key)

    def _to_legacy_key(self, backend_key: str) -> str:
        return BACKEND_TO_LEGACY_KEY.get(backend_key, backend_key)

    def _normalize_task_type(self, task_type: str) -> str:
        return LEGACY_TASK_ALIASES.get(task_type, task_type)

    def _routing_tasks_for_backend(self, backend_key: str) -> list[str]:
        rules = unified_registry._routing_rules
        if not rules:
            return []
        legacy_tasks = []
        for task, target in rules.task_type_mapping.items():
            if target == backend_key:
                legacy_tasks.append(task)
        for task, normalized in LEGACY_TASK_ALIASES.items():
            if normalized in legacy_tasks:
                legacy_tasks.append(task)
        return sorted(set(legacy_tasks))

    def _to_legacy_record(
        self,
        backend_key: str,
        backend,
    ) -> ComfyUIInstanceRecord:
        return ComfyUIInstanceRecord(
            key=self._to_legacy_key(backend_key),
            name=backend.name,
            base_url=backend.base_url,
            port=backend.port,
            enabled=backend.enabled,
            task_types=self._routing_tasks_for_backend(backend_key),
            health_endpoint=backend.health_endpoint,
        )

    def load_instances(self, config_path: str | None = None) -> None:
        if config_path:
            logger.warning(
                "Deprecated config_path '%s' ignored; using unified instances registry",
                config_path,
            )

        unified_registry.load_config()
        backends = unified_registry.get_all_backends()
        self._instances.clear()

        for backend_key, backend in backends.items():
            legacy_key = self._to_legacy_key(backend_key)
            self._instances[legacy_key] = self._to_legacy_record(backend_key, backend)

        logger.info(
            "Loaded %d legacy ComfyUI instances from unified registry",
            len(self._instances),
        )

    def get_all_instances(self) -> dict[str, ComfyUIInstanceRecord]:
        return dict(self._instances)

    def get_instance(self, instance_key: str) -> Optional[ComfyUIInstanceRecord]:
        self.load_instances()
        legacy_key = self._to_legacy_key(self._to_backend_key(instance_key))
        return self._instances.get(legacy_key)

    def get_instance_for_task(self, task_type: str) -> Optional[ComfyUIInstanceRecord]:
        self.load_instances()
        normalized = self._normalize_task_type(task_type)
        rules = unified_registry._routing_rules
        if not rules or normalized not in rules.task_type_mapping:
            return None

        backend = unified_registry.resolve_backend_for_task(normalized)
        if backend is None:
            return None

        backend_key = backend.type.value
        return self._to_legacy_record(backend_key, backend)

    async def check_instance_health(
        self, instance_key: str, timeout: float = 5.0
    ) -> dict[str, Any]:
        self.load_instances()
        record = self.get_instance(instance_key)
        if record is None:
            return {
                "instance_key": instance_key,
                "status": "unknown",
                "healthy": False,
                "detail": {"error": "instance not found"},
            }

        backend_key = self._to_backend_key(instance_key)
        healthy = await unified_registry.check_health(backend_key)
        return {
            "instance_key": self._to_legacy_key(backend_key),
            "instance_name": record.name,
            "base_url": record.base_url,
            "status": "online" if healthy else "offline",
            "healthy": bool(healthy),
            "detail": {"timeout_seconds": timeout},
        }

    async def check_all_instances_health(
        self, timeout: float = 5.0
    ) -> list[dict[str, Any]]:
        self.load_instances()
        health_map = await unified_registry.check_all_health()
        output: list[dict[str, Any]] = []
        for backend_key, healthy in health_map.items():
            legacy_key = self._to_legacy_key(backend_key)
            rec = self._instances.get(legacy_key)
            if rec is None:
                continue
            output.append(
                {
                    "instance_key": legacy_key,
                    "instance_name": rec.name,
                    "base_url": rec.base_url,
                    "status": "online" if healthy else "offline",
                    "healthy": bool(healthy),
                    "detail": {"timeout_seconds": timeout},
                }
            )
        return output


registry = ComfyUIInstanceRegistry()
