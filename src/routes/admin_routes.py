from fastapi import APIRouter, HTTPException
from typing import Optional

from services.job_scheduler import scheduler
from services.backend_capability_service import capability_service
from services.instance_registry import registry

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/scheduler/status")
async def get_scheduler_status():
    return await scheduler.get_status()


@router.post("/scheduler/start")
async def start_scheduler():
    await scheduler.start()
    return {"message": "Scheduler started"}


@router.post("/scheduler/stop")
async def stop_scheduler():
    await scheduler.stop()
    return {"message": "Scheduler stopped"}


@router.post("/cache/invalidate")
async def invalidate_cache(backend: Optional[str] = None):
    capability_service.invalidate_cache(backend)
    return {"message": "Cache invalidated", "backend": backend or "all"}


@router.post("/backends/reload")
async def reload_backends():
    registry.load_config()
    return {"message": "Backend configuration reloaded"}


@router.get("/system/overview")
async def get_system_overview():
    queue_status = queue_service.get_all_status()
    scheduler_status = await scheduler.get_status()
    instance_status = registry.get_status_summary()
    
    return {
        "queue": queue_status,
        "scheduler": scheduler_status,
        "instances": instance_status
    }


from services.queue_service import queue_service
