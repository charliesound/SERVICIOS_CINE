from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.demo_service import demo_service

router = APIRouter(prefix="/api/demo", tags=["demo"])


class DemoStatusResponse(BaseModel):
    seeded: bool
    demo_users_count: int
    demo_projects_count: int
    demo_presets_count: int
    total_demo_jobs: int


class DemoSeedResponse(BaseModel):
    users_created: int
    presets_created: int
    projects_created: int
    jobs_created: int
    message: Optional[str] = None


class DemoUser(BaseModel):
    user_id: str
    username: str
    email: str
    plan: str
    role: str
    password_hint: str


@router.get("/status", response_model=DemoStatusResponse)
async def get_demo_status():
    """Get current demo data status."""
    return demo_service.get_demo_status()


@router.get("/users")
async def get_demo_users():
    """Get list of demo users with credentials."""
    return {"users": demo_service.get_demo_users()}


@router.post("/seed")
async def seed_demo_data():
    """Seed demo data if not already seeded."""
    if demo_service.is_seeded():
        return {
            "message": "Demo data already seeded",
            **demo_service.get_demo_status()
        }
    
    results = demo_service.seed_demo_data()
    return results


@router.post("/reset")
async def reset_demo_data():
    """Reset and reseed all demo data."""
    results = demo_service.reset_demo_data()
    return results


@router.get("/jobs/{user_id}")
async def get_demo_jobs(user_id: str):
    """Get demo jobs for a specific demo user."""
    jobs = demo_service.get_demo_jobs(user_id)
    return {"user_id": user_id, "jobs": jobs}


@router.get("/projects")
async def get_demo_projects():
    """Get list of demo projects."""
    return {"projects": demo_service.DEMO_PROJECTS}


@router.get("/presets")
async def get_demo_presets():
    """Get list of demo presets."""
    return {"presets": demo_service.DEMO_PRESETS}


@router.post("/quick-start")
async def quick_start_demo():
    """Initialize demo with seed and return credentials."""
    demo_service.seed_demo_data()
    
    return {
        "message": "Demo initialized successfully",
        "credentials": {
            "free": {"email": "demo_free@servicios-cine.com", "password": "demo123"},
            "creator": {"email": "demo_creator@servicios-cine.com", "password": "demo123"},
            "studio": {"email": "demo_studio@servicios-cine.com", "password": "demo123"},
            "enterprise": {"email": "demo_enterprise@servicios-cine.com", "password": "demo123"},
            "admin": {"email": "admin@servicios-cine.com", "password": "admin123"}
        },
        "urls": {
            "frontend": "http://localhost:3000",
            "backend": "http://localhost:8000",
            "docs": "http://localhost:8000/docs"
        },
        "status": demo_service.get_demo_status()
    }
