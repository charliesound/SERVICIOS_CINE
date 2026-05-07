#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODEL_EXTENSIONS = {
    ".safetensors",
    ".ckpt",
    ".pt",
    ".pth",
    ".bin",
}

CATEGORIES = {
    "checkpoints": "checkpoints",
    "loras": "loras",
    "vae": "vae",
    "controlnet": "controlnet",
    "clip": "clip",
    "clip_vision": "clip_vision",
    "unet": "unet",
    "diffusion_models": "diffusion_models",
    "upscale_models": "upscale_models",
    "embeddings": "embeddings",
    "style_models": "style_models",
    "text_encoders": "text_encoders",
    "vae_approx": "vae_approx",
    "gligen": "gligen",
    "hypernetworks": "hypernetworks",
}

DEFAULT_ROOT_CANDIDATES = [
    "/mnt/i/COMFYUI_OK",
    "/opt/ComfyUI",
    "/opt/comfyui",
    "/mnt/c/ComfyUI",
    "/mnt/c/Users/Charlie/ComfyUI",
    "/mnt/c/Users/charliesound/ComfyUI",
    "/mnt/c/Users/Charliesound/ComfyUI",]

DEFAULT_MODELS_CANDIDATES = [
    "/mnt/i/COMFYUI_OK/models",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_name(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def dedupe_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []

    for model in models:
        key = (
            str(model.get("name", "")),
            str(model.get("category", "")),
            str(model.get("relative_path", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(model)

    return result


def dedupe_names(names: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for name in names:
        if name in seen:
            continue
        seen.add(name)
        result.append(name)

    return result


def resolve_paths() -> tuple[Path, Path]:
    env_models_root = os.getenv("COMFYUI_MODELS_ROOT")
    env_comfyui_root = os.getenv("COMFYUI_ROOT")

    if env_models_root:
        models_root = Path(env_models_root).expanduser().resolve()
        if models_root.exists() and models_root.is_dir():
            return models_root.parent, models_root

    if env_comfyui_root:
        comfyui_root = Path(env_comfyui_root).expanduser().resolve()
        models_root = comfyui_root / "models"
        if models_root.exists() and models_root.is_dir():
            return comfyui_root, models_root

    for candidate in DEFAULT_MODELS_CANDIDATES:
        models_root = Path(candidate).expanduser().resolve()
        if models_root.exists() and models_root.is_dir():
            return models_root.parent, models_root

    for candidate in DEFAULT_ROOT_CANDIDATES:
        comfyui_root = Path(candidate).expanduser().resolve()
        models_root = comfyui_root / "models"
        if models_root.exists() and models_root.is_dir():
            return comfyui_root, models_root

    raise FileNotFoundError(
        "No se encontró ComfyUI models. Ejecuta: "
        "COMFYUI_ROOT=/mnt/i/COMFYUI_OK "
        "COMFYUI_MODELS_ROOT=/mnt/i/COMFYUI_OK/models "
        "python3 scripts/export_comfyui_models_inventory.py"
    )


def file_size_mb(path: Path) -> float:
    try:
        return round(path.stat().st_size / (1024 * 1024), 2)
    except OSError:
        return 0.0


def scan_category(models_root: Path, category: str, folder_name: str) -> list[dict[str, Any]]:
    folder = models_root / folder_name
    if not folder.exists() or not folder.is_dir():
        return []

    items: list[dict[str, Any]] = []

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in MODEL_EXTENSIONS:
            continue

        try:
            relative_path = path.relative_to(models_root).as_posix()
        except ValueError:
            relative_path = path.name

        items.append(
            {
                "name": path.name,
                "category": category,
                "relative_path": relative_path,
                "absolute_path": str(path),
                "size_mb": file_size_mb(path),
            }
        )

    return dedupe_models(items)


def contains_any(name: str, keywords: list[str]) -> bool:
    normalized = normalize_name(name)
    return any(keyword.lower() in normalized for keyword in keywords)


def collect_candidates(models: list[dict[str, Any]], keywords: list[str]) -> list[dict[str, Any]]:
    return dedupe_models([model for model in models if contains_any(model["name"], keywords)])


def candidate_names(models: list[dict[str, Any]]) -> list[str]:
    return dedupe_names([model["name"] for model in models])


def choose_first_by_rules(models: list[dict[str, Any]], rules: list[list[str]]) -> str | None:
    deduped_models = dedupe_models(models)

    for keywords in rules:
        for model in deduped_models:
            normalized = normalize_name(model["name"])
            if all(keyword.lower() in normalized for keyword in keywords):
                return model["name"]

    if deduped_models:
        return deduped_models[0]["name"]

    return None


def build_recommended_defaults(categories: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    checkpoints = dedupe_models(categories.get("checkpoints", []))
    vaes = dedupe_models(categories.get("vae", []))
    loras = dedupe_models(categories.get("loras", []))
    diffusion_models = dedupe_models(categories.get("diffusion_models", []))
    unet_models = dedupe_models(categories.get("unet", []))

    all_generation_models = dedupe_models(checkpoints + diffusion_models + unet_models)

    sdxl_keywords = [
        "sdxl",
        "xl",
        "realvisxl",
        "juggernaut",
        "dreamshaperxl",
        "copax",
        "dynavision",
    ]

    flux_keywords = ["flux"]

    wan_keywords = [
        "wan",
        "wan2",
        "wan2.1",
        "wan2.2",
    ]

    ltx_keywords = [
        "ltx",
        "ltxv",
    ]

    realistic_keywords = [
        "realistic",
        "realvis",
        "juggernaut",
        "epicrealism",
        "photon",
        "absolute reality",
        "absolute",
        "dreamshaper",
    ]

    cinematic_keywords = [
        "cinematic",
        "film",
        "movie",
        "analog",
        "kodak",
        "cinestill",
        "vision",
    ]

    storyboard_lora_keywords = [
        "storyboard",
        "cinematic",
        "film",
    ]

    sdxl_candidates = collect_candidates(checkpoints, sdxl_keywords)
    flux_candidates = collect_candidates(all_generation_models, flux_keywords)
    wan_candidates = collect_candidates(all_generation_models, wan_keywords)
    ltx_candidates = collect_candidates(all_generation_models, ltx_keywords)
    realistic_candidates = collect_candidates(checkpoints, realistic_keywords)
    cinematic_candidates = collect_candidates(checkpoints, cinematic_keywords)
    storyboard_lora_candidates = collect_candidates(loras, storyboard_lora_keywords)

    storyboard_checkpoint = choose_first_by_rules(
        checkpoints,
        [
            ["sdxl", "cinematic"],
            ["realvisxl"],
            ["juggernaut"],
            ["dreamshaperxl"],
            ["sdxl"],
            ["xl"],
        ],
    )

    storyboard_vae = choose_first_by_rules(
        vaes,
        [
            ["sdxl"],
            ["vae"],
        ],
    )

    return {
        "storyboard_checkpoint": storyboard_checkpoint,
        "storyboard_vae": storyboard_vae,
        "storyboard_lora": None,
        "storyboard_lora_candidates": candidate_names(storyboard_lora_candidates),
        "sdxl_candidates": candidate_names(sdxl_candidates),
        "flux_candidates": candidate_names(flux_candidates),
        "wan_candidates": candidate_names(wan_candidates),
        "ltx_candidates": candidate_names(ltx_candidates),
        "realistic_candidates": candidate_names(realistic_candidates),
        "cinematic_candidates": candidate_names(cinematic_candidates),
    }


def build_inventory() -> dict[str, Any]:
    comfyui_root, models_root = resolve_paths()

    categories: dict[str, list[dict[str, Any]]] = {}

    for category, folder_name in CATEGORIES.items():
        categories[category] = scan_category(models_root, category, folder_name)

    return {
        "comfyui_root": str(comfyui_root),
        "models_root": str(models_root),
        "generated_at": now_iso(),
        "categories": categories,
        "recommended_defaults": build_recommended_defaults(categories),
    }


def write_inventory(inventory: dict[str, Any]) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "docs" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "comfyui_models_inventory.json"
    output_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return output_path


def print_summary(inventory: dict[str, Any], output_path: Path) -> None:
    categories = inventory["categories"]
    recommended = inventory["recommended_defaults"]

    counts = {category: len(items) for category, items in categories.items()}

    print("===== COMFYUI MODELS INVENTORY =====")
    print(f"ComfyUI root : {inventory['comfyui_root']}")
    print(f"Models root  : {inventory['models_root']}")
    print(f"Output       : {output_path}")
    print("")
    print("===== COUNTS =====")
    for category, count in counts.items():
        print(f"{category:18s}: {count}")
    print("")
    print("===== RECOMMENDED DEFAULTS =====")
    print(json.dumps(recommended, ensure_ascii=False, indent=2))


def main() -> int:
    try:
        inventory = build_inventory()
        output_path = write_inventory(inventory)
        print_summary(inventory, output_path)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
