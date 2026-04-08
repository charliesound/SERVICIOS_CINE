from fastapi import APIRouter
from pydantic import BaseModel

from services.metrics_service import metrics_collector

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class MetricsResponse(BaseModel):
    uptime_seconds: int
    total_requests: int
    total_jobs: int
    active_jobs: int
    failed_jobs: int
    success_rate: float
    avg_response_time_ms: float


@router.get("", response_model=MetricsResponse)
async def get_metrics():
    return metrics_collector.get_metrics()


@router.get("/health")
async def health_check():
    metrics = metrics_collector.get_metrics()
    return {
        "status": "healthy" if metrics.success_rate > 50 else "degraded",
        "uptime_seconds": metrics.uptime_seconds,
        "success_rate": metrics.success_rate,
        "active_jobs": metrics.active_jobs,
    }
