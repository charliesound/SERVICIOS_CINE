from fastapi import APIRouter
from src.schemas.job import Job

# LEGACY-MOCK: `/jobs` is intentionally hardcoded/transient (no persistence).
router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=list[Job])
def list_jobs():
    # LEGACY-MOCK: static response used as temporary mock source.
    return [
        {
            "id": "job_001",
            "shot_id": "shot_001",
            "status": "completed",
            "prompt_id": "mock_prompt_001",
            "error": None
        },
        {
            "id": "job_002",
            "shot_id": "shot_002",
            "status": "queued",
            "prompt_id": "mock_prompt_002",
            "error": None
        },
        {
            "id": "job_003",
            "shot_id": "shot_004",
            "status": "failed",
            "prompt_id": "mock_prompt_003",
            "error": "Mock render timeout"
        }
    ]
