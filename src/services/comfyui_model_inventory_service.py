from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ComfyUIInventoryError(RuntimeError):
    pass


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_inventory_path() -> Path:
    return get_repo_root() / "docs" / "validation" / "comfyui_models_inventory.json"


def missing_inventory_message() -> str:
    return (
        "No existe inventario de modelos ComfyUI. Ejecuta: "
        "COMFYUI_ROOT=/mnt/i/COMFYUI_OK "
        "COMFYUI_MODELS_ROOT=/mnt/i/COMFYUI_OK/models "
        "python3 scripts/export_comfyui_models_inventory.py"
    )


def load_comfyui_model_inventory() -> dict[str, Any]:
    inventory_path = get_inventory_path()

    if not inventory_path.exists():
        raise ComfyUIInventoryError(missing_inventory_message())

    try:
        return json.loads(inventory_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ComfyUIInventoryError(
            f"El inventario ComfyUI existe pero no es JSON válido: {inventory_path}"
        ) from exc


def get_categories() -> dict[str, list[dict[str, Any]]]:
    inventory = load_comfyui_model_inventory()
    return inventory.get("categories", {})


def get_recommended_defaults() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    return inventory.get("recommended_defaults", {})


def get_storyboard_default_checkpoint() -> str | None:
    return get_recommended_defaults().get("storyboard_checkpoint")


def get_storyboard_default_vae() -> str | None:
    return get_recommended_defaults().get("storyboard_vae")


def list_category(category: str) -> list[dict[str, Any]]:
    return get_categories().get(category, [])


def list_checkpoints() -> list[dict[str, Any]]:
    return list_category("checkpoints")


def list_loras() -> list[dict[str, Any]]:
    return list_category("loras")


def list_vaes() -> list[dict[str, Any]]:
    return list_category("vae")


def list_controlnet_models() -> list[dict[str, Any]]:
    return list_category("controlnet")


def list_diffusion_models() -> list[dict[str, Any]]:
    return list_category("diffusion_models")


def list_unet_models() -> list[dict[str, Any]]:
    return list_category("unet")


def get_inventory_summary() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    categories = inventory.get("categories", {})

    counts = {
        category: len(items) if isinstance(items, list) else 0
        for category, items in categories.items()
    }

    return {
        "inventory_found": True,
        "comfyui_root": inventory.get("comfyui_root"),
        "models_root": inventory.get("models_root"),
        "generated_at": inventory.get("generated_at"),
        "counts": counts,
        "recommended_defaults": inventory.get("recommended_defaults", {}),
    }


def build_models_api_payload() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    summary = get_inventory_summary()

    return {
        "status": "ok",
        "inventory_found": True,
        "comfyui_root": summary["comfyui_root"],
        "models_root": summary["models_root"],
        "generated_at": summary["generated_at"],
        "counts": summary["counts"],
        "recommended_defaults": summary["recommended_defaults"],
        "categories": inventory.get("categories", {}),
    }
