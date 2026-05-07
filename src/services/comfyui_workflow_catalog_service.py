from __future__ import annotations

from pathlib import Path
from typing import Any


WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / "comfyui_workflows"

WORKFLOW_CATALOG: list[dict[str, Any]] = [
    {
        "id": "cinematic_storyboard_sdxl",
        "label": "Cinematic Storyboard SDXL",
        "task_types": ["storyboard", "shot_visualization"],
        "model_family": "sdxl",
        "status": "functional_candidate",
        "required_categories": ["checkpoints"],
        "optional_categories": ["vae", "loras"],
        "default_params": {
            "width": 1344,
            "height": 768,
            "steps": 28,
            "cfg": 6.5,
            "sampler": "dpmpp_2m",
            "scheduler": "karras",
        },
        "workflow_path": str(WORKFLOWS_DIR / "cinematic_storyboard_sdxl.json"),
    },
    {
        "id": "storyboard_fast_sdxl",
        "label": "Storyboard Fast SDXL",
        "task_types": ["storyboard", "preview"],
        "model_family": "sdxl",
        "status": "functional_candidate",
        "required_categories": ["checkpoints"],
        "optional_categories": ["vae", "loras"],
        "default_params": {
            "width": 1024,
            "height": 576,
            "steps": 18,
            "cfg": 5.5,
        },
        "workflow_path": str(WORKFLOWS_DIR / "storyboard_fast_sdxl.json"),
    },
    {
        "id": "cinematic_still_flux",
        "label": "Cinematic Still Flux",
        "task_types": ["concept_art", "key_visual"],
        "model_family": "flux",
        "status": "requires_node_mapping",
        "required_categories": ["diffusion_models"],
        "optional_categories": ["clip", "text_encoders"],
        "default_params": {
            "width": 1344,
            "height": 768,
            "steps": 24,
            "cfg": 3.5,
        },
        "workflow_path": str(WORKFLOWS_DIR / "cinematic_still_flux.json"),
    },
    {
        "id": "video_wan",
        "label": "Video Wan",
        "task_types": ["video", "shot_animation"],
        "model_family": "wan",
        "status": "requires_node_mapping",
        "required_categories": ["diffusion_models"],
        "optional_categories": ["text_encoders", "loras"],
        "default_params": {},
        "workflow_path": str(WORKFLOWS_DIR / "video_wan.json"),
    },
    {
        "id": "video_ltx",
        "label": "Video LTX",
        "task_types": ["video", "fast_video"],
        "model_family": "ltx",
        "status": "requires_node_mapping",
        "required_categories": ["diffusion_models"],
        "optional_categories": ["text_encoders", "loras"],
        "default_params": {},
        "workflow_path": str(WORKFLOWS_DIR / "video_ltx.json"),
    },
    {
        "id": "upscale_delivery",
        "label": "Upscale Delivery",
        "task_types": ["upscale", "delivery"],
        "model_family": "upscale",
        "status": "requires_node_mapping",
        "required_categories": ["upscale_models"],
        "optional_categories": [],
        "default_params": {},
        "workflow_path": str(WORKFLOWS_DIR / "upscale_delivery.json"),
    },
]


def _with_runtime_fields(workflow: dict[str, Any]) -> dict[str, Any]:
    payload = dict(workflow)
    payload["workflow_exists"] = Path(payload["workflow_path"]).exists()
    return payload


def list_workflows() -> list[dict[str, Any]]:
    return [_with_runtime_fields(workflow) for workflow in WORKFLOW_CATALOG]


def get_workflow(workflow_id: str) -> dict[str, Any] | None:
    for workflow in WORKFLOW_CATALOG:
        if workflow["id"] == workflow_id:
            return _with_runtime_fields(workflow)
    return None


def search_workflows(
    task_type: str | None = None,
    model_family: str | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for workflow in WORKFLOW_CATALOG:
        if task_type and task_type not in workflow["task_types"]:
            continue
        if model_family and workflow["model_family"] != model_family:
            continue
        results.append(_with_runtime_fields(workflow))
    return results


def _workflow_score(
    workflow: dict[str, Any],
    task_type: str,
    preferred_family: str | None,
    quality: str,
    speed: str,
) -> int:
    score = 0

    if task_type in workflow["task_types"]:
        score += 50
    if preferred_family and workflow["model_family"] == preferred_family:
        score += 40
    if workflow["workflow_exists"]:
        score += 10

    workflow_id = workflow["id"]

    if task_type == "storyboard":
        if workflow_id == "cinematic_storyboard_sdxl":
            score += 100
        if workflow_id == "storyboard_fast_sdxl" and speed == "fast":
            score += 80
        if quality in {"balanced", "high", "high_quality"} and workflow_id == "cinematic_storyboard_sdxl":
            score += 20
    elif task_type in {"concept_art", "key_visual"} and workflow_id == "cinematic_still_flux":
        score += 100
    elif task_type in {"video", "shot_animation"}:
        if workflow_id == "video_wan":
            score += 90
        if workflow_id == "video_ltx" and speed == "fast":
            score += 80
    elif task_type in {"upscale", "delivery"} and workflow_id == "upscale_delivery":
        score += 100

    return score


def recommend_workflow_for_task(
    task_type: str,
    preferred_family: str | None = None,
    quality: str = "balanced",
    speed: str = "medium",
) -> dict[str, Any] | None:
    candidates = search_workflows(task_type=task_type, model_family=preferred_family)
    if not candidates and preferred_family:
        candidates = search_workflows(task_type=task_type, model_family=None)
    if not candidates:
        return None

    return max(
        candidates,
        key=lambda workflow: _workflow_score(
            workflow,
            task_type=task_type,
            preferred_family=preferred_family,
            quality=quality,
            speed=speed,
        ),
    )
