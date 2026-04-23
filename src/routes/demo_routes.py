from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.demo_service import demo_service

router = APIRouter(prefix="/api/demo", tags=["demo"])

NARRATIVE_DEMO_PROJECT_ID = "demo-narrative-001"


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
        return {"message": "Demo data already seeded", **demo_service.get_demo_status()}

    results = await demo_service.seed_demo_data()
    return results


@router.post("/reset")
async def reset_demo_data():
    """Reset and reseed all demo data."""
    results = await demo_service.reset_demo_data()
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


@router.get("/narrative-project")
async def get_demo_narrative_project():
    """Get demo narrative project structure."""
    return {
        "project": demo_service.DEMO_NARRATIVE_PROJECT,
        "sequences": demo_service.DEMO_SEQUENCES,
        "scenes": demo_service.DEMO_SCENES,
        "characters": demo_service.DEMO_CHARACTERS,
    }


@router.get("/narrative-html", response_class=HTMLResponse)
async def get_narrative_html_demo():
    """Get HTML demo page for narrative structure."""
    project = demo_service.DEMO_NARRATIVE_PROJECT
    sequences = demo_service.DEMO_SEQUENCES
    scenes = demo_service.DEMO_SCENES
    characters = demo_service.DEMO_CHARACTERS

    # Group scenes by sequence
    scenes_by_seq = {}
    for scene in scenes:
        seq_idx = int(scene["scene_number"][0]) - 1 if scene["scene_number"] else 0
        if seq_idx not in scenes_by_seq:
            scenes_by_seq[seq_idx] = []
        scenes_by_seq[seq_idx].append(scene)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project["name"]} - AILinkCinema Demo</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
              max-width: 900px; margin: 0 auto; padding: 20px; 
              background: #1a1a2e; color: #eee; }}
        h1 {{ color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
        h2 {{ color: #0f3460; background: #16213e; padding: 10px; margin-top: 30px; }}
        h3 {{ color: #e94560; }}
        .card {{ background: #16213e; border-radius: 8px; padding: 15px; margin: 10px 0; }}
        .scene {{ background: #1a1a2e; border-left: 3px solid #e94560; padding: 12px; margin: 8px 0; }}
        .character {{ display: inline-block; background: #0f3460; padding: 8px 15px; margin: 5px; border-radius: 20px; }}
        .meta {{ color: #888; font-size: 0.9em; }}
        .badge {{ display: inline-block; background: #e94560; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }}
        .badge-ext {{ background: #f39c12; }}
        .badge-int {{ background: #3498db; }}
        a {{ color: #e94560; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #0f3460; padding: 15px 25px; border-radius: 8px; text-align: center; }}
        .stat-num {{ font-size: 2em; color: #e94560; font-weight: bold; }}
        .stat-label {{ color: #888; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>🎬 {project["name"]}</h1>
    <p class="meta">{project["description"]}</p>
    
    <div class="stats">
        <div class="stat-box"><div class="stat-num">{
        len(sequences)
    }</div><div class="stat-label">Secuencias</div></div>
        <div class="stat-box"><div class="stat-num">{
        len(scenes)
    }</div><div class="stat-label">Escenas</div></div>
        <div class="stat-box"><div class="stat-num">{
        len(characters)
    }</div><div class="stat-label">Personajes</div></div>
    </div>
    
    <h2>📖 Personajes</h2>
    <div>
        {"".join(f'<span class="character">{c["name"]}</span>' for c in characters)}
    </div>
    
    <h2>🎞️ Secuencias y Escenas</h2>
    {
        "".join(
            f'''
    <h3>Secuencia {s["sequence_number"]}: {s["title"]} <span class="meta">({
                s.get("description", "")
            })</span></h3>
    <div>
        {
                "".join(
                    f"""
        <div class="scene">
            <strong>Escena {scene["scene_number"]}</strong> 
            <span class="badge {"badge-int" if scene["setting"] == "INT" else "badge-ext"}">{scene["setting"]}</span>
            <span class="meta">| {scene["location"]} | {scene["time_of_day"]}</span><br>
            <p>{scene["action_text"]}</p>
        </div>
        """
                    for scene in scenes_by_seq.get(s["sequence_number"] - 1, [])
                )
            }
    </div>
    '''
            for s in sequences
        )
    }
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #333; color: #666;">
        <p>AILinkCinema - Pipeline Audiovisual Demo | <a href="/docs">API Docs</a></p>
    </footer>
</body>
</html>"""
    return html


@router.post("/seed-narrative")
async def seed_narrative_to_db():
    """Seed the narrative project to the database."""
    results = await demo_service.seed_narrative_to_db()
    return {"message": "Narrative project seeded to database", **results}


@router.get("/presets")
async def get_demo_presets():
    """Get list of demo presets."""
    return {"presets": demo_service.DEMO_PRESETS}


@router.post("/quick-start")
async def quick_start_demo():
    """Initialize demo with seed and return credentials."""
    await demo_service.seed_demo_data()

    return {
        "message": "Demo initialized successfully",
        "credentials": {
            "free": {"email": "demo_free@servicios-cine.com", "password": "demo123"},
            "creator": {
                "email": "demo_creator@servicios-cine.com",
                "password": "demo123",
            },
            "studio": {
                "email": "demo_studio@servicios-cine.com",
                "password": "demo123",
            },
            "enterprise": {
                "email": "demo_enterprise@servicios-cine.com",
                "password": "demo123",
            },
            "admin": {"email": "admin@servicios-cine.com", "password": "admin123"},
        },
        "urls": {
            "frontend": "http://localhost:3000",
            "backend": "http://localhost:8000",
            "docs": "http://localhost:8000/docs",
        },
        "status": demo_service.get_demo_status(),
    }
