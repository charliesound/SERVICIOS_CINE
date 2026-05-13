from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import httpx
import yaml

from core.config import get_settings

logger = logging.getLogger("servicios_cine.comfyui_registry")

CONFIG_ROOT = Path(__file__).resolve().parents[1]


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

    @property
    def _config_path(self) -> Path:
        settings = get_settings()
        env_path = settings.comfyui_instances_config
        if env_path:
            return Path(env_path)
        return CONFIG_ROOT / "config" / "comfyui_instances.yml"

    def _override_from_env(self, key: str, base_url: str) -> str:
        env_key = f"COMFYUI_{key.upper()}_URL"
        import os

        return os.environ.get(env_key, base_url)

    def load_instances(self, config_path: str | None = None) -> None:
        path = Path(config_path) if config_path else self._config_path

        if not path.exists():
            logger.error("ComfyUI instances config not found: %s", path)
            return

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        raw = data.get("instances", {})
        self._instances.clear()

        for key, cfg in raw.items():
            base_url = self._override_from_env(key, cfg["base_url"])
            record = ComfyUIInstanceRecord(
                key=key,
                name=cfg["name"],
                base_url=base_url,
                port=cfg["port"],
                enabled=cfg.get("enabled", True),
                task_types=cfg.get("task_types", []),
                health_endpoint=cfg.get("health_endpoint", "/system_stats"),
            )
            self._instances[key] = record

        logger.info(
            "Loaded %d ComfyUI instances from %s", len(self._instances), path
        )

    def get_all_instances(self) -> dict[str, ComfyUIInstanceRecord]:
        return dict(self._instances)

    def get_instance(self, instance_key: str) -> Optional[ComfyUIInstanceRecord]:
        return self._instances.get(instance_key)

    def get_instance_for_task(self, task_type: str) -> Optional[ComfyUIInstanceRecord]:
        for record in self._instances.values():
            if not record.enabled:
                continue
            if task_type in record.task_types:
                return record
        return None

    async def check_instance_health(
        self, instance_key: str, timeout: float = 5.0
    ) -> dict[str, Any]:
        record = self.get_instance(instance_key)
        if record is None:
            return {
                "instance_key": instance_key,
                "status": "unknown",
                "healthy": False,
                "detail": {"error": "instance not found"},
            }

        url = f"{record.base_url}{record.health_endpoint}"
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return {
                        "instance_key": instance_key,
                        "instance_name": record.name,
                        "base_url": record.base_url,
                        "status": "online",
                        "healthy": True,
                        "detail": resp.json() if resp.text else {},
                    }
                else:
                    return {
                        "instance_key": instance_key,
                        "instance_name": record.name,
                        "base_url": record.base_url,
                        "status": "degraded",
                        "healthy": False,
                        "detail": {"status_code": resp.status_code},
                    }
        except httpx.TimeoutException:
            logger.warning("Health check timeout for %s (%s)", instance_key, url)
            return {
                "instance_key": instance_key,
                "instance_name": record.name,
                "base_url": record.base_url,
                "status": "timeout",
                "healthy": False,
                "detail": {"error": "timeout"},
            }
        except httpx.ConnectError:
            logger.warning("Health check connection refused for %s (%s)", instance_key, url)
            return {
                "instance_key": instance_key,
                "instance_name": record.name,
                "base_url": record.base_url,
                "status": "offline",
                "healthy": False,
                "detail": {"error": "connection refused"},
            }
        except Exception as exc:
            logger.error("Health check error for %s (%s): %s", instance_key, url, exc)
            return {
                "instance_key": instance_key,
                "instance_name": record.name,
                "base_url": record.base_url,
                "status": "error",
                "healthy": False,
                "detail": {"error": str(exc)},
            }

    async def check_all_instances_health(
        self, timeout: float = 5.0
    ) -> list[dict[str, Any]]:
        import asyncio

        tasks = [
            self.check_instance_health(key, timeout=timeout)
            for key in self._instances
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output: list[dict[str, Any]] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                key = list(self._instances.keys())[i]
                record = self._instances[key]
                logger.error("Unexpected health check exception for %s: %s", key, result)
                output.append(
                    {
                        "instance_key": key,
                        "instance_name": record.name,
                        "base_url": record.base_url,
                        "status": "error",
                        "healthy": False,
                        "detail": {"error": str(result)},
                    }
                )
            else:
                output.append(result)
        return output


registry = ComfyUIInstanceRegistry()
