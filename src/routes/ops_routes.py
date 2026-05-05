from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.backend_capability_service import capability_service
from services.instance_registry import registry

router = APIRouter(prefix="/api/ops", tags=["ops"])


class CapabilitiesResponse(BaseModel):
    backends: Dict[str, Any]
    timestamp: str


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities(
    force_refresh: bool = Query(False, description="Force fresh detection")
):
    """Get capabilities for all backends."""
    results = await capability_service.detect_all_capabilities(force=force_refresh)
    
    return {
        "backends": results,
        "timestamp": results.get("still", {}).get("last_check", "")
    }


@router.get("/capabilities/{backend}")
async def get_backend_capabilities(
    backend: str,
    force_refresh: bool = Query(False)
):
    """Get capabilities for a specific backend."""
    if backend == "comfyui":
        raise HTTPException(
            status_code=400,
            detail=(
                "Backend 'comfyui' is an alias. Valid backends are: "
                "still, video, dubbing, lab"
            ),
        )

    caps = await capability_service.detect_capabilities(backend, force=force_refresh)
    
    if not caps:
        raise HTTPException(status_code=404, detail=f"Backend '{backend}' not found")
    
    return caps.to_dict()


@router.get("/instances")
async def get_instances():
    """Get status of all backend instances."""
    return registry.get_status_summary()


@router.get("/instances/{backend}")
async def get_instance(backend: str):
    """Get status of a specific backend instance."""
    inst = registry.get_backend(backend)
    if not inst:
        raise HTTPException(status_code=404, detail=f"Backend '{backend}' not found")
    
    return {
        "name": inst.name,
        "type": inst.type.value,
        "host": inst.host,
        "port": inst.port,
        "base_url": inst.base_url,
        "enabled": inst.enabled,
        "healthy": inst.healthy,
        "current_jobs": inst.current_jobs,
        "max_concurrent_jobs": inst.max_concurrent_jobs,
        "available_slots": inst.available_slots,
        "capabilities": inst.capabilities
    }


@router.post("/instances/{backend}/health-check")
async def health_check_backend(backend: str):
    """Trigger health check for a specific backend."""
    healthy = await registry.check_health(backend)
    return {"backend": backend, "healthy": healthy}


@router.post("/health-check-all")
async def health_check_all():
    """Trigger health check for all backends."""
    results = await registry.check_all_health()
    return {"results": results}


@router.get("/can-run")
async def can_run_workflow(
    backend: str = Query(..., description="Backend to check"),
    capabilities: str = Query(..., description="Comma-separated required capabilities")
):
    """Check if a backend can run a workflow with given requirements."""
    required = [c.strip() for c in capabilities.split(",")]
    can_run, missing = capability_service.can_workflow_run(backend, required)
    
    return {
        "backend": backend,
        "can_run": can_run,
        "required_capabilities": required,
        "missing_capabilities": missing if not can_run else []
    }


@router.get("/status")
async def get_ops_status():
    """Get consolidated system status for monitoring."""
    from services.queue_service import queue_service
    from datetime import datetime
    
    instances_status = registry.get_status_summary()
    queue_status = queue_service.get_all_status()
    
    total_running = sum(
        status.get("running", 0) 
        for status in queue_status.values()
    )
    total_queued = sum(
        status.get("queue_size", 0) 
        for status in queue_status.values()
    )
    
    backends_summary = []
    for backend_key, instance in instances_status.get("backends", {}).items():
        q_status = queue_status.get(backend_key, {})
        backends_summary.append({
            "key": backend_key,
            "name": instance.get("name", backend_key),
            "healthy": instance.get("healthy", False),
            "enabled": instance.get("enabled", True),
            "current_jobs": instance.get("current_jobs", 0),
            "max_jobs": instance.get("max_jobs", 0),
            "available_slots": instance.get("available_slots", 0),
            "queue_size": q_status.get("queue_size", 0),
            "running": q_status.get("running", 0),
            "saturation_percent": round(
                (q_status.get("running", 0) / max(q_status.get("max_concurrent", 1), 1)) * 100, 1
            )
        })
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy" if all(b.get("healthy", False) for b in backends_summary) else "degraded",
        "summary": {
            "total_backends": instances_status.get("total_backends", 0),
            "available_backends": instances_status.get("available_backends", 0),
            "total_running": total_running,
            "total_queued": total_queued
        },
        "backends": backends_summary
    }
