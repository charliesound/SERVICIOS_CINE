from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend_capability_service import capability_service
from services.instance_registry import registry
from services.llm.llm_service import llm_service
from database import get_db
from services.comfyui_model_inventory_service import (
    ComfyUIInventoryError,
    build_models_api_payload,
)
from services.comfyui_model_classifier_service import classify_comfyui_models
from services.comfyui_search_service import (
    recommend_for_task,
    search_models,
    search_workflows as search_comfyui_workflows,
)
from services.comfyui_pipeline_builder_service import build_optimal_comfyui_pipeline
from services.comfyui_api_client_service import get_prompt_status, poll_prompt_until_complete
from services.comfyui_storyboard_render_service import comfyui_storyboard_render_service
from services.comfyui_workflow_template_service import build_compiled_workflow_preview

router = APIRouter(prefix="/api/ops", tags=["ops"])

# ---------------------------------------------------------------------------
# Pipeline Builder aliases: avoid 404 when frontend calls /api/pipelines/*
# ---------------------------------------------------------------------------
pipeline_router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])

@pipeline_router.get("/presets")
async def list_pipeline_presets(
    user_id: str | None = Query(default=None),
    category: str | None = Query(default=None),
    include_public: bool = Query(default=True),
):
    """Alias → /api/workflows/presets (or legacy catalog)."""
    from services.cid_pipeline_preset_service import cid_pipeline_preset_service
    presets = cid_pipeline_preset_service.list_presets()
    return presets or []


@pipeline_router.get("/jobs")
async def list_pipeline_jobs(
    project_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Return an empty list (or real jobs when a model exists)."""
    return []


@pipeline_router.post("/plan")
async def plan_pipeline(payload: dict):
    """Alias → /api/workflows/plan."""
    from services.workflow_planner import planner
    from services.cid_pipeline_preset_service import cid_pipeline_preset_service

    intent = payload.get("intent", "")
    context = payload.get("context", {})
    analysis = planner.analyze_intent(intent, context)
    llm_preset = await cid_pipeline_preset_service.recommend_preset_with_llm(
        preset_key=None, intent=intent, context=context
    )
    return {
        "task_type": analysis.task_type,
        "backend": analysis.backend,
        "detected_workflow": analysis.detected_workflow,
        "confidence": analysis.confidence,
        "missing_inputs": analysis.missing_inputs,
        "suggested_params": analysis.suggested_params,
        "llm_recommendation": llm_preset.get("llm_recommendation") if isinstance(llm_preset, dict) else None,
        "recommended_preset": {
            "key": llm_preset.get("key"),
            "name": llm_preset.get("name"),
            "default_workflow_key": llm_preset.get("default_workflow_key"),
            "default_backend": llm_preset.get("default_backend"),
        } if isinstance(llm_preset, dict) else None,
    }


class CapabilitiesResponse(BaseModel):
    backends: Dict[str, Any]
    timestamp: str


class LLMStatusResponse(BaseModel):
    provider: str
    model: str
    base_url: str
    available: bool
    error_message: Optional[str] = None


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


@router.get("/llm/status", response_model=LLMStatusResponse)
async def get_llm_status() -> LLMStatusResponse:
    status = await llm_service.get_status()
    return LLMStatusResponse(
        provider=status.provider,
        model=status.model,
        base_url=status.base_url,
        available=status.available,
        error_message=status.error_message,
    )

@router.get("/comfyui/models")
async def get_comfyui_models():
    try:
        return build_models_api_payload()
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc


@router.get("/comfyui/classify")
async def get_comfyui_classification():
    try:
        return classify_comfyui_models()
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc


@router.get("/comfyui/workflows")
async def get_comfyui_workflows(
    task_type: str | None = Query(default=None),
    model_family: str | None = Query(default=None),
):
    try:
        return search_comfyui_workflows(task_type=task_type, model_family=model_family)
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc


@router.get("/comfyui/search")
async def get_comfyui_search(
    q: str = Query(...),
    category: str | None = Query(default=None),
    family: str | None = Query(default=None),
):
    try:
        return search_models(query=q, category=category, family=family)
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc


@router.get("/comfyui/recommend")
async def get_comfyui_recommendation(
    task_type: str = Query(...),
    style: str = Query(default="cinematic_realistic"),
    quality: str = Query(default="balanced"),
    speed: str = Query(default="medium"),
    preferred_model_family: str | None = Query(default=None),
):
    try:
        return recommend_for_task(
            task_type=task_type,
            style=style,
            quality=quality,
            speed=speed,
            preferred_model_family=preferred_model_family,
        )
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc


@router.post("/comfyui/pipeline-builder")
async def build_comfyui_pipeline(payload: dict):
    try:
        return build_optimal_comfyui_pipeline(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/comfyui/storyboard/render-dry-run")
async def storyboard_render_dry_run(payload: dict):
    try:
        request_payload = dict(payload)
        request_payload["dry_run"] = True
        request_payload["render"] = False
        return comfyui_storyboard_render_service.render_storyboard_with_plan(
            project_id=None,
            payload=request_payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/comfyui/storyboard/render")
async def storyboard_render(payload: dict):
    try:
        return comfyui_storyboard_render_service.render_storyboard_with_plan(
            project_id=None,
            payload=payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/comfyui/prompt/{prompt_id}/status")
async def get_comfyui_prompt_status_endpoint(
    prompt_id: str,
    poll: bool = Query(default=False),
    timeout_seconds: int = Query(default=30),
):
    try:
        if poll:
            return poll_prompt_until_complete(
                prompt_id=prompt_id,
                timeout_seconds=timeout_seconds,
            )
        return get_prompt_status(prompt_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/comfyui/concept-art/compile-workflow-dry-run")
async def compile_concept_art_workflow_dry_run(payload: dict):
    try:
        request_payload = dict(payload)
        request_payload["dry_run"] = True
        request_payload["task_type"] = str(request_payload.get("task_type") or "concept_art").strip().lower()
        request_payload["generation_mode"] = "SELECTED_SCENES"
        if "selected_scenes" not in request_payload:
            request_payload["selected_scenes"] = [1]
        plan = build_optimal_comfyui_pipeline(request_payload)
        compiled = build_compiled_workflow_preview(
            plan=plan,
            prompt=request_payload.get("prompt"),
            negative_prompt=request_payload.get("negative_prompt"),
        )
        return {
            "status": "ok",
            "workflow_id": compiled.get("workflow_id", plan.get("pipeline", {}).get("workflow_id")),
            "pipeline": plan.get("pipeline", {}),
            "compiled_workflow_preview": compiled,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/comfyui/storyboard/compile-workflow-dry-run")
async def compile_storyboard_workflow_dry_run(payload: dict):
    try:
        request_payload = dict(payload)
        request_payload["dry_run"] = True
        plan = build_optimal_comfyui_pipeline(request_payload)
        return build_compiled_workflow_preview(
            plan=plan,
            prompt=request_payload.get("prompt"),
            negative_prompt=request_payload.get("negative_prompt"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
