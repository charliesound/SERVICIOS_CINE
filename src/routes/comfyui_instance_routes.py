from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Path as FPath, Request

from dependencies.security import TokenData, require_auth, require_scope
from services.instance_registry import registry

logger = logging.getLogger("servicios_cine.comfyui_routes")

router = APIRouter(prefix="/api/v1/comfyui", tags=["comfyui"])

LEGACY_TO_BACKEND_KEY = {
    "image": "still",
    "video_cine": "video",
    "dubbing_audio": "dubbing",
    "restoration": "restoration",
    "three_d": "3d",
    "lab": "lab",
}

BACKEND_TO_LEGACY_KEY = {
    value: key for key, value in LEGACY_TO_BACKEND_KEY.items()
}

LEGACY_TASK_ALIASES = {
    "i2v": "img2vid",
    "t2v": "text_to_video",
    "lipsync": "audio",
    "upscale": "restoration",
    "mesh": "3d",
    "scene": "scene_3d",
}


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


def _load_registry() -> None:
    registry.load_config()


def _to_legacy_key(backend_key: str) -> str:
    return BACKEND_TO_LEGACY_KEY.get(backend_key, backend_key)


def _to_backend_key(instance_key: str) -> str:
    return LEGACY_TO_BACKEND_KEY.get(instance_key, instance_key)


def _backend_to_payload(backend_key: str, backend) -> dict:
    return {
        "key": _to_legacy_key(backend_key),
        "name": backend.name,
        "base_url": backend.base_url,
        "port": backend.port,
        "enabled": backend.enabled,
        "task_types": [
            task
            for task, target in registry._routing_rules.task_type_mapping.items()
            if target == backend_key
        ]
        if registry._routing_rules
        else [],
        "health_endpoint": backend.health_endpoint,
    }


def _supports_task(task_type: str) -> bool:
    if not registry._routing_rules:
        return False
    return task_type in registry._routing_rules.task_type_mapping


def _normalize_task_type(task_type: str) -> str:
    return LEGACY_TASK_ALIASES.get(task_type, task_type)


@router.get("/instances")
async def list_instances(
    request: Request,
    _token: TokenData = Depends(require_scope("comfyui:read")),
) -> list[dict]:
    _load_registry()
    backends = registry.get_all_backends()
    return [_backend_to_payload(key, rec) for key, rec in backends.items()]


@router.get("/instances/{instance_key}")
async def get_instance(
    request: Request,
    instance_key: str = FPath(..., description="Instance key identifier"),
    _token: TokenData = Depends(require_scope("comfyui:read")),
) -> dict:
    _load_registry()
    backend_key = _to_backend_key(instance_key)
    rec = registry.get_backend(backend_key)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"Instance '{instance_key}' not found",
                "request_id": _request_id(request),
            },
        )
    return _backend_to_payload(backend_key, rec)


@router.get("/instances/{instance_key}/health")
async def get_instance_health(
    request: Request,
    instance_key: str = FPath(..., description="Instance key identifier"),
    _token: TokenData = Depends(require_scope("comfyui:health")),
) -> dict:
    _load_registry()
    backend_key = _to_backend_key(instance_key)
    rec = registry.get_backend(backend_key)
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
    healthy = await registry.check_health(backend_key)
    status = "online" if healthy else "offline"
    return {
        "instance_key": _to_legacy_key(backend_key),
        "instance_name": rec.name,
        "base_url": rec.base_url,
        "status": status,
        "healthy": healthy,
        "detail": {"timeout_seconds": timeout},
    }


@router.get("/health")
async def comfyui_health_summary(
    request: Request,
    _token: TokenData = Depends(require_scope("comfyui:health")),
) -> dict:
    _load_registry()
    settings = request.app.state.settings
    timeout = getattr(settings, "comfyui_health_timeout_seconds", 5.0)
    health_map = await registry.check_all_health()
    backends = registry.get_all_backends()
    results = []
    for key, healthy in health_map.items():
        backend = backends.get(key)
        if backend is None:
            continue
        results.append(
            {
                "instance_key": _to_legacy_key(key),
                "instance_name": backend.name,
                "base_url": backend.base_url,
                "status": "online" if healthy else "offline",
                "healthy": bool(healthy),
                "detail": {"timeout_seconds": timeout},
            }
        )
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
    _token: TokenData = Depends(require_scope("comfyui:read")),
) -> dict:
    _load_registry()
    normalized_task_type = _normalize_task_type(task_type)
    if not _supports_task(normalized_task_type):
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"No instance found for task_type '{task_type}'",
                "task_type": task_type,
                "request_id": _request_id(request),
            },
        )
    rec = registry.resolve_backend_for_task(normalized_task_type)
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
        "instance_key": _to_legacy_key(rec.type.value),
        "instance_name": rec.name,
        "base_url": rec.base_url,
        "port": rec.port,
    }
