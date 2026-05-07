"""
API routes for Ollama-based script analysis and storyboard prompt generation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.local_script_analysis_service import local_script_analysis_service
from services.storyboard_prompt_refinement_service import storyboard_prompt_refinement_service
from services.ollama_client_service import ollama_client

router = APIRouter(prefix="/api", tags=["ollama-storyboard"])


@router.get("/ops/ollama/status")
async def get_ollama_status():
    """Check Ollama availability and models."""
    settings = {}
    try:
        from config import get_llm_settings
        settings = get_llm_settings()
    except Exception:
        pass
    
    base_url = settings.get("base_url", "http://127.0.0.1:11434")
    analysis_model = settings.get("analysis_model", "qwen3:30b")
    visual_model = settings.get("visual_model", "gemma4:26b")
    fallback_model = settings.get("fallback_model", "qwen3:30b")
    
    health = await ollama_client.healthcheck()
    models = []
    if health.get("ollama_available"):
        models = await ollama_client.list_models()
    
    return {
        "ollama_available": health.get("ollama_available", False),
        "base_url": base_url,
        "models": models,
        "analysis_model": {
            "name": analysis_model,
            "available": await ollama_client.is_model_available(analysis_model),
        },
        "visual_model": {
            "name": visual_model,
            "available": await ollama_client.is_model_available(visual_model),
        },
        "fallback_model": {
            "name": fallback_model,
            "available": await ollama_client.is_model_available(fallback_model),
        },
    }


@router.post("/projects/{project_id}/analyze/local-ollama")
async def analyze_script_local_ollama(
    project_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Analyze script using local Qwen3:30b via Ollama."""
    from models.core import Project
    
    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.script_text:
        raise HTTPException(status_code=400, detail="Project has no script text")
    
    try:
        analysis = await local_script_analysis_service.analyze_script_with_qwen(
            project_id=project_id,
            script_text=project.script_text,
        )
        return analysis
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")
async def generate_storyboard_prompts_from_analysis(
    project_id: str,
    payload: Dict[str, Any],
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """Generate storyboard prompts from existing analysis."""
    from models.core import Project
    
    # Get project
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    mode = payload.get("generation_mode", "FULL_SCRIPT")
    refine_with_visual = payload.get("refine_with_visual_model", True)
    
    # Get latest analysis from JSON storage or DB
    from services.storyboard_service import storyboard_service
    analysis_data = await storyboard_service._get_analysis_payload(
        db, project
    )
    
    if not analysis_data or not analysis_data.get("scenes"):
        raise HTTPException(status_code=400, detail="No script analysis found. Run /analyze/local-ollama first.")
    
    # Filter scenes based on mode
    scenes = analysis_data.get("scenes", [])
    filtered_scenes = scenes
    
    if mode == "SINGLE_SCENE" and payload.get("scene_number"):
        filtered_scenes = [s for s in scenes if s.get("scene_number") == payload["scene_number"]]
    elif mode == "SCENE_RANGE":
        start = payload.get("scene_range", {}).get("start")
        end = payload.get("scene_range", {}).get("end")
        if start and end:
            filtered_scenes = [s for s in scenes if start <= s.get("scene_number", 0) <= end]
    elif mode == "SELECTED_SCENES":
        selected = payload.get("selected_scenes", [])
        filtered_scenes = [s for s in scenes if s.get("scene_number") in selected]
    elif mode == "SEQUENCE":
        seq_id = payload.get("sequence_id")
        sequences = analysis_data.get("sequences", [])
        target_seq = next((sq for sq in sequences if sq.get("sequence_id") == seq_id), None)
        if target_seq:
            included = target_seq.get("scene_numbers", [])
            filtered_scenes = [s for s in scenes if s.get("scene_number") in included]
    
    # Prepare analysis payload for refinement
    analysis_payload = {
        "project_id": project_id,
        "scenes": filtered_scenes,
        "sequences": analysis_data.get("sequences", []),
    }
    
    if not refine_with_visual:
        # Return base prompts only
        return {
            "project_id": project_id,
            "analysis_model": analysis_data.get("model", "qwen3:30b"),
            "visual_model": None,
            "generation_mode": mode,
            "total_scenes": len(filtered_scenes),
            "selected_scenes": [s.get("scene_number") for s in filtered_scenes],
            "storyboard_prompts": [
                {
                    "scene_number": s.get("scene_number"),
                    "sequence_id": s.get("sequence_id", ""),
                    "base_storyboard_prompt": s.get("base_storyboard_prompt", ""),
                    "negative_prompt": s.get("negative_prompt", ""),
                }
                for s in filtered_scenes
            ],
        }
    
    # Refine with visual model
    try:
        refined = await storyboard_prompt_refinement_service.refine_storyboard_prompts(
            analysis_payload=analysis_payload,
            mode=mode,
        )
        return refined
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prompt refinement failed: {exc}") from exc
