from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class SystemMetrics:
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    uptime_seconds: int = 0
    total_requests: int = 0
    total_jobs: int = 0
    active_jobs: int = 0
    failed_jobs: int = 0
    success_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    backend_health: Dict[str, bool] = field(default_factory=dict)
    queue_size: int = 0


class MetricsCollector:
    def __init__(self):
        self._start_time = datetime.utcnow()
        self._request_count = 0
        self._response_times: list = []
        self._job_stats = {"total": 0, "active": 0, "failed": 0, "completed": 0}

    def record_request(self, duration_ms: float):
        self._request_count += 1
        self._response_times.append(duration_ms)
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]

    def record_job(self, status: str):
        self._job_stats["total"] += 1
        if status == "running":
            self._job_stats["active"] += 1
        elif status in ["failed", "error"]:
            self._job_stats["failed"] += 1
        elif status in ["completed", "succeeded"]:
            self._job_stats["completed"] += 1

    def get_metrics(self) -> SystemMetrics:
        uptime = (datetime.utcnow() - self._start_time).total_seconds()

        avg_response = 0.0
        if self._response_times:
            avg_response = sum(self._response_times) / len(self._response_times)

        success_rate = 0.0
        if self._job_stats["total"] > 0:
            success_rate = (
                self._job_stats["completed"] / self._job_stats["total"]
            ) * 100

        return SystemMetrics(
            uptime_seconds=int(uptime),
            total_requests=self._request_count,
            total_jobs=self._job_stats["total"],
            active_jobs=self._job_stats["active"],
            failed_jobs=self._job_stats["failed"],
            success_rate=round(success_rate, 2),
            avg_response_time_ms=round(avg_response, 2),
        )


metrics_collector = MetricsCollector()
