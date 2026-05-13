from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Path as FPath, Request
from fastapi.responses import JSONResponse

from schemas.comfyui_instance_schema import (
    ComfyUIInstance,
    InstanceHealth,
    InstancesHealthSummary,
    ResolveResult,
)
from services.comfyui_instance_registry_service import registry

logger = logging.getLogger("servicios_cine.comfyui_routes")

router = APIRouter(prefix="/api/v1/comfyui", tags=["comfyui"])


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


@router.get("/instances")
async def list_instances(request: Request) -> list[dict]:
    registry.load_instances()
    instances = registry.get_all_instances()
    return [
        {
            "key": key,
            "name": rec.name,
            "base_url": rec.base_url,
            "port": rec.port,
            "enabled": rec.enabled,
            "task_types": rec.task_types,
            "health_endpoint": rec.health_endpoint,
        }
        for key, rec in instances.items()
    ]


@router.get("/instances/{instance_key}")
async def get_instance(
    request: Request,
    instance_key: str = FPath(..., description="Instance key identifier"),
) -> dict:
    registry.load_instances()
    rec = registry.get_instance(instance_key)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Instance '{instance_key}' not found",
                "request_id": _request_id(request),
            },
        )
    return {
        "key": rec.key,
        "name": rec.name,
        "base_url": rec.base_url,
        "port": rec.port,
        "enabled": rec.enabled,
        "task_types": rec.task_types,
        "health_endpoint": rec.health_endpoint,
    }


@router.get("/instances/{instance_key}/health")
async def get_instance_health(
    request: Request,
    instance_key: str = FPath(..., description="Instance key identifier"),
) -> dict:
    registry.load_instances()
    rec = registry.get_instance(instance_key)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Instance '{instance_key}' not found",
                "request_id": _request_id(request),
            },
        )
    settings = request.app.state.settings
    timeout = getattr(settings, "comfyui_health_timeout_seconds", 5.0)
    result = await registry.check_instance_health(instance_key, timeout=timeout)
    return result


@router.get("/health")
async def comfyui_health_summary(request: Request) -> dict:
    registry.load_instances()
    settings = request.app.state.settings
    timeout = getattr(settings, "comfyui_health_timeout_seconds", 5.0)
    results = await registry.check_all_instances_health(timeout=timeout)
    total = len(results)
    online = sum(1 for r in results if r.get("healthy"))
    offline = total - online
    return {
        "total": total,
        "online": online,
        "offline": offline,
        "instances": results,
    }


@router.get("/resolve/{task_type}")
async def resolve_task_type(
    request: Request,
    task_type: str = FPath(..., description="Task type to resolve"),
) -> dict:
    registry.load_instances()
    rec = registry.get_instance_for_task(task_type)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"No instance found for task_type '{task_type}'",
                "task_type": task_type,
                "request_id": _request_id(request),
            },
        )
    return {
        "task_type": task_type,
        "instance_key": rec.key,
        "instance_name": rec.name,
        "base_url": rec.base_url,
        "port": rec.port,
    }
