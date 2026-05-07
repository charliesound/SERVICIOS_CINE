from __future__ import annotations

from typing import Any

from services.comfyui_search_service import recommend_for_task
from services.comfyui_workflow_catalog_service import get_workflow
from services.comfyui_model_inventory_service import load_comfyui_model_inventory


FLUX_UNET_PRIORITY = [
    "flux1-dev_fp8_scaled.safetensors",
    "flux1-dev-fp8.safetensors",
    "flux1-dev.safetensors",
]

FLUX_CLIP_L = "clip_l.safetensors"
FLUX_T5XXL_PRIORITY = ["t5xxl_fp16.safetensors", "t5xxl_fp8_e4m3fn.safetensors", "t5xxl_fp8_e4m3fn_scaled.safetensors"]
FLUX_VAE = "ae.safetensors"


def _resolve_flux_models() -> dict[str, str | None]:
    inventory = load_comfyui_model_inventory()
    categories = inventory.get("categories", {})
    all_names: dict[str, list[str]] = {}
    for cat_name, models in categories.items():
        all_names[cat_name] = [m.get("name", "") for m in models if isinstance(m, dict)]

    unet_names = all_names.get("unet", []) + all_names.get("diffusion_models", [])
    vae_names = all_names.get("vae", [])

    unet: str | None = None
    for candidate in FLUX_UNET_PRIORITY:
        if candidate in unet_names:
            unet = candidate
            break

    t5xxl: str | None = None
    for candidate in FLUX_T5XXL_PRIORITY:
        if candidate in all_names.get("text_encoders", []):
            t5xxl = candidate
            break

    clip_l = FLUX_CLIP_L if FLUX_CLIP_L in all_names.get("clip", []) else None
    vae = FLUX_VAE if FLUX_VAE in vae_names else None

    return {"unet": unet, "clip_l": clip_l, "t5xxl": t5xxl, "vae": vae}


def normalize_pipeline_quality(quality: str | None) -> str:
    normalized = (quality or "balanced").strip().lower()
    allowed = {"draft", "fast", "balanced", "high", "high_quality"}
    return normalized if normalized in allowed else "balanced"


def normalize_pipeline_speed(speed: str | None) -> str:
    normalized = (speed or "medium").strip().lower()
    allowed = {"slow", "medium", "fast"}
    return normalized if normalized in allowed else "medium"


def validate_selected_scenes(selected_scenes) -> list[int]:
    if not selected_scenes:
        raise ValueError("selected_scenes is required and must contain at least one scene number")

    validated: list[int] = []
    seen: set[int] = set()

    for value in selected_scenes:
        try:
            scene_number = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid scene number: {value}") from exc

        if scene_number <= 0:
            raise ValueError(f"Scene numbers must be positive integers: {scene_number}")

        if scene_number not in seen:
            validated.append(scene_number)
            seen.add(scene_number)

    if not validated:
        raise ValueError("selected_scenes is required and must contain at least one valid scene number")

    return validated


def _build_safe_to_render_flag(recommendation: dict[str, Any], workflow: dict[str, Any] | None) -> bool:
    return bool(
        recommendation.get("workflow_id")
        and recommendation.get("checkpoint")
        and recommendation.get("model_family")
        and recommendation.get("lora") is None
        and recommendation.get("loras") == []
        and workflow
        and workflow.get("status") == "functional_candidate"
        and workflow.get("workflow_exists") is True
    )


def build_optimal_comfyui_pipeline(request: dict) -> dict:
    task_type = str(request.get("task_type") or "storyboard").strip().lower()
    visual_style = str(request.get("visual_style") or "cinematic_realistic").strip() or "cinematic_realistic"
    quality = normalize_pipeline_quality(request.get("quality"))
    speed = normalize_pipeline_speed(request.get("speed"))
    generation_mode = str(request.get("generation_mode") or "SELECTED_SCENES").strip().upper()
    preferred_model_family = request.get("preferred_model_family")
    selected_scenes = validate_selected_scenes(request.get("selected_scenes"))

    flux_task_types = {"concept_art", "key_visual", "flux_concept_art"}

    if task_type == "storyboard" and preferred_model_family and str(preferred_model_family).lower() != "sdxl":
        raise ValueError(
            "preferred_model_family is not compatible with storyboard planning; only sdxl is currently supported"
        )

    recommendation_payload = recommend_for_task(
        task_type=task_type,
        style=visual_style,
        quality=quality,
        speed=speed,
        preferred_model_family=preferred_model_family,
    )
    recommendation = recommendation_payload.get("recommendation", {})

    workflow_id = recommendation.get("workflow_id")
    checkpoint = recommendation.get("checkpoint")
    model_family = recommendation.get("model_family")

    if not workflow_id:
        raise RuntimeError(f"No workflow recommendation available for task_type={task_type}")

    workflow = get_workflow(workflow_id)
    if workflow is None:
        raise RuntimeError(f"Recommended workflow not found in catalog: {workflow_id}")

    unet_name: str | None = None
    clip_l_name: str | None = None
    t5xxl_name: str | None = None
    vae_name: str | None = None
    missing_flux_models: list[str] = []

    if model_family == "flux":
        flux_models = _resolve_flux_models()
        unet_name = recommendation.get("unet") or flux_models.get("unet")
        clip_l_name = recommendation.get("clip_l") or flux_models.get("clip_l")
        t5xxl_name = recommendation.get("t5xxl") or flux_models.get("t5xxl")
        vae_name = recommendation.get("vae") or flux_models.get("vae")
        checkpoint = unet_name
        if not unet_name:
            missing_flux_models.append("unet")
        if not clip_l_name:
            missing_flux_models.append("clip_l")
        if not t5xxl_name:
            missing_flux_models.append("t5xxl")
        if not vae_name:
            missing_flux_models.append("vae")
    else:
        if not checkpoint:
            raise RuntimeError(f"No checkpoint recommendation available for task_type={task_type}")
        if task_type == "storyboard" and model_family != "sdxl":
            raise RuntimeError("Storyboard planning requires an SDXL recommendation")

    safe_to_render = _build_safe_to_render_flag(recommendation, workflow)
    if model_family == "flux" and missing_flux_models:
        safe_to_render = False

    pipeline = {
        "task_type": task_type,
        "generation_mode": generation_mode,
        "selected_scenes": selected_scenes,
        "workflow_id": workflow_id,
        "workflow_status": workflow.get("status"),
        "model_family": model_family,
        "checkpoint": checkpoint,
        "unet": unet_name,
        "clip_l": clip_l_name,
        "t5xxl": t5xxl_name,
        "vae": vae_name,
        "missing_models": missing_flux_models if missing_flux_models else [],
        "lora": None,
        "loras": [],
        "params": dict(recommendation.get("params", {})),
        "reason": recommendation.get("reason"),
        "alternatives": list(recommendation.get("alternatives", [])),
        "safe_to_render": safe_to_render,
    }

    return {
        "status": "ok",
        "project_id": request.get("project_id"),
        "pipeline": pipeline,
    }


def build_storyboard_pipeline_plan(project_id: str, payload: dict) -> dict:
    request = dict(payload)
    request["project_id"] = project_id
    request["task_type"] = str(request.get("task_type") or "storyboard").strip().lower() or "storyboard"
    request["visual_style"] = request.get("visual_style") or "cinematic_realistic"
    request["quality"] = normalize_pipeline_quality(request.get("quality"))
    request["speed"] = normalize_pipeline_speed(request.get("speed"))
    request["generation_mode"] = str(request.get("generation_mode") or "SELECTED_SCENES").strip().upper()
    return build_optimal_comfyui_pipeline(request)
