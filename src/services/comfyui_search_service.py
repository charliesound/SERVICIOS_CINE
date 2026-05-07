from __future__ import annotations

from typing import Any

from services.comfyui_model_classifier_service import (
    classify_comfyui_models,
    classify_model_name,
    get_recommended_model_sets,
)
from services.comfyui_model_inventory_service import load_comfyui_model_inventory
from services.comfyui_workflow_catalog_service import (
    get_workflow,
    recommend_workflow_for_task,
    search_workflows as catalog_search_workflows,
)


def _normalize(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ").strip()


def _available_families(classification: dict[str, Any]) -> list[str]:
    return [family for family, models in classification.get("families", {}).items() if models]


def _inventory_categories() -> dict[str, list[dict[str, Any]]]:
    inventory = load_comfyui_model_inventory()
    return inventory.get("categories", {})


def _recommended_defaults() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    return inventory.get("recommended_defaults", {})


def search_models(
    query: str,
    category: str | None = None,
    family: str | None = None,
) -> dict[str, Any]:
    categories = _inventory_categories()
    normalized_query = _normalize(query)
    results: list[dict[str, Any]] = []

    for category_name, models in categories.items():
        if category and category_name != category:
            continue
        for model in models:
            name = model.get("name", "")
            relative_path = model.get("relative_path", "")
            classification = classify_model_name(name, category_name)

            if family and family not in classification["families"]:
                continue

            haystack = f"{name} {relative_path}"
            if normalized_query and normalized_query not in _normalize(haystack):
                continue

            results.append(
                {
                    "name": name,
                    "category": category_name,
                    "relative_path": relative_path,
                    "size_mb": model.get("size_mb"),
                    "families": classification["families"],
                    "style_tags": classification["style_tags"],
                }
            )

    return {
        "status": "ok",
        "query": query,
        "category": category,
        "family": family,
        "total": len(results),
        "results": results,
    }


def search_workflows(
    task_type: str | None = None,
    model_family: str | None = None,
) -> dict[str, Any]:
    results = catalog_search_workflows(task_type=task_type, model_family=model_family)
    return {
        "status": "ok",
        "task_type": task_type,
        "model_family": model_family,
        "total": len(results),
        "results": results,
    }


def explain_recommendation(task_type: str, style: str, quality: str) -> str:
    if task_type == "storyboard":
        return (
            "Se selecciona SDXL/Juggernaut XL porque es una base realista y estable "
            "para storyboard cinematografico."
        )
    if task_type in {"concept_art", "key_visual"}:
        return (
            "Se prioriza Flux para stills cinematicos porque ofrece alternativas de alta "
            "calidad para concept art y key visuals."
        )
    if task_type in {"video", "shot_animation"}:
        return (
            "Se recomienda una familia de video dedicada para mantener consistencia temporal "
            "y evitar adaptar checkpoints pensados para stills."
        )
    if task_type in {"upscale", "delivery"}:
        return "Se recomienda un workflow de upscale dedicado para entrega final y limpieza de detalle."
    return f"Se recomienda la combinacion mas compatible para {task_type} con estilo {style} y calidad {quality}."


def _build_storyboard_recommendation(
    quality: str,
    speed: str,
    preferred_model_family: str | None,
) -> dict[str, Any]:
    defaults = _recommended_defaults()
    workflow = recommend_workflow_for_task(
        task_type="storyboard",
        preferred_family=preferred_model_family,
        quality=quality,
        speed=speed,
    ) or get_workflow("cinematic_storyboard_sdxl")

    checkpoint = defaults.get("storyboard_checkpoint")
    vae = defaults.get("storyboard_vae")
    alternatives = [
        candidate
        for candidate in defaults.get("sdxl_candidates", [])
        if candidate != checkpoint
    ]

    return {
        "task_type": "storyboard",
        "workflow_id": workflow["id"] if workflow else None,
        "model_family": "sdxl",
        "checkpoint": checkpoint,
        "vae": vae,
        "lora": None,
        "storyboard_lora": None,
        "loras": [],
        "params": dict((workflow or {}).get("default_params", {})),
        "reason": explain_recommendation("storyboard", "cinematic_realistic", quality),
        "alternatives": alternatives,
    }


def _build_cinematic_still_recommendation(
    quality: str,
    speed: str,
    preferred_model_family: str | None,
) -> dict[str, Any]:
    recommended_sets = get_recommended_model_sets()
    defaults = _recommended_defaults()
    workflow = recommend_workflow_for_task(
        task_type="concept_art",
        preferred_family=preferred_model_family,
        quality=quality,
        speed=speed,
    ) or get_workflow("cinematic_still_flux")
    model_set = recommended_sets.get("cinematic_still", {})
    family = preferred_model_family or model_set.get("model_family") or "flux"
    alternatives_key = "flux_candidates" if family == "flux" else "sdxl_candidates"
    checkpoint = model_set.get("checkpoint")

    return {
        "task_type": "concept_art",
        "workflow_id": workflow["id"] if workflow else None,
        "model_family": family,
        "checkpoint": checkpoint,
        "vae": model_set.get("vae"),
        "lora": None,
        "loras": [],
        "params": dict((workflow or {}).get("default_params", {})),
        "reason": explain_recommendation("concept_art", "cinematic_realistic", quality),
        "alternatives": [candidate for candidate in defaults.get(alternatives_key, []) if candidate != checkpoint],
    }


def _build_video_recommendation(
    task_type: str,
    style: str,
    quality: str,
    speed: str,
    preferred_model_family: str | None,
) -> dict[str, Any]:
    defaults = _recommended_defaults()
    recommended_sets = get_recommended_model_sets()
    preferred_family = preferred_model_family or recommended_sets.get("video_generation", {}).get("model_family")
    workflow = recommend_workflow_for_task(
        task_type=task_type,
        preferred_family=preferred_family,
        quality=quality,
        speed=speed,
    )

    if workflow is None:
        workflow = get_workflow("video_wan") or get_workflow("video_ltx")

    family = preferred_family or (workflow["model_family"] if workflow else None)
    if family == "ltx":
        checkpoint = defaults.get("ltx_candidates", [None])[0]
        alternatives = defaults.get("ltx_candidates", [])[1:]
    else:
        family = "wan" if family is None else family
        checkpoint = defaults.get("wan_candidates", [None])[0]
        alternatives = [candidate for candidate in defaults.get("wan_candidates", []) if candidate != checkpoint]

    return {
        "task_type": task_type,
        "workflow_id": workflow["id"] if workflow else None,
        "model_family": family,
        "checkpoint": checkpoint,
        "vae": None,
        "lora": None,
        "loras": [],
        "params": dict((workflow or {}).get("default_params", {})),
        "reason": explain_recommendation(task_type, style, quality),
        "alternatives": alternatives,
    }


def _build_upscale_recommendation(quality: str, speed: str) -> dict[str, Any]:
    recommended_sets = get_recommended_model_sets()
    workflow = recommend_workflow_for_task(
        task_type="upscale",
        preferred_family="upscale",
        quality=quality,
        speed=speed,
    ) or get_workflow("upscale_delivery")
    model_set = recommended_sets.get("upscale", {})

    return {
        "task_type": "upscale",
        "workflow_id": workflow["id"] if workflow else None,
        "model_family": "upscale",
        "checkpoint": model_set.get("checkpoint"),
        "vae": None,
        "lora": None,
        "loras": [],
        "params": dict((workflow or {}).get("default_params", {})),
        "reason": explain_recommendation("upscale", "delivery", quality),
        "alternatives": [],
    }


def recommend_for_task(
    task_type: str,
    style: str = "cinematic_realistic",
    quality: str = "balanced",
    speed: str = "medium",
    preferred_model_family: str | None = None,
) -> dict[str, Any]:
    normalized_task_type = task_type.strip().lower()
    classification = classify_comfyui_models()

    if normalized_task_type == "storyboard":
        recommendation = _build_storyboard_recommendation(
            quality=quality,
            speed=speed,
            preferred_model_family=preferred_model_family,
        )
    elif normalized_task_type in {"concept_art", "key_visual"}:
        recommendation = _build_cinematic_still_recommendation(
            quality=quality,
            speed=speed,
            preferred_model_family=preferred_model_family,
        )
    elif normalized_task_type in {"video", "shot_animation", "fast_video"}:
        recommendation = _build_video_recommendation(
            task_type=normalized_task_type,
            style=style,
            quality=quality,
            speed=speed,
            preferred_model_family=preferred_model_family,
        )
    elif normalized_task_type in {"upscale", "delivery"}:
        recommendation = _build_upscale_recommendation(quality=quality, speed=speed)
    else:
        workflow = recommend_workflow_for_task(
            task_type=normalized_task_type,
            preferred_family=preferred_model_family,
            quality=quality,
            speed=speed,
        )
        recommendation = {
            "task_type": normalized_task_type,
            "workflow_id": workflow["id"] if workflow else None,
            "model_family": preferred_model_family,
            "checkpoint": None,
            "vae": None,
            "lora": None,
            "loras": [],
            "params": dict((workflow or {}).get("default_params", {})),
            "reason": explain_recommendation(normalized_task_type, style, quality),
            "alternatives": [],
        }

    workflow_family = recommendation.get("model_family")
    workflow_results = catalog_search_workflows(
        task_type=normalized_task_type,
        model_family=workflow_family,
    )

    return {
        "status": "ok",
        "recommendation": recommendation,
        "available_families": _available_families(classification),
        "workflow_alternatives": [workflow["id"] for workflow in workflow_results if workflow["id"] != recommendation.get("workflow_id")],
    }
