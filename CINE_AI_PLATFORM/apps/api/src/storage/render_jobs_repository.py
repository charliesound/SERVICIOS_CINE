from typing import Any, Dict, List, Optional

from src.storage.sqlite_render_jobs_store import SQLiteRenderJobsStore


class RenderJobsRepository:
    def __init__(self, store: SQLiteRenderJobsStore):
        self.store = store

    def create(self, job: Dict[str, Any]) -> Dict[str, Any]:
        return self.store.create_job(job)

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.store.list_jobs(limit=limit)

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.store.get_job(job_id)

    def update(self, job_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.store.update_job(job_id, updates)
