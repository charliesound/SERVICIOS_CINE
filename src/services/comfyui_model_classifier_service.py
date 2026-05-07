from __future__ import annotations

from typing import Any

from services.comfyui_model_inventory_service import load_comfyui_model_inventory


FAMILY_KEYWORDS = {
    "sdxl": [
        "sdxl",
        "xl",
        "realvisxl",
        "juggernaut",
        "dreamshaperxl",
        "copax",
        "dynavision",
    ],
    "sd15": ["sd15", "sd1.5", "1.5", "realistic vision", "realistic_vision"],
    "flux": ["flux"],
    "wan": ["wan", "wan2", "wan2.1", "wan2.2"],
    "ltx": ["ltx", "ltxv"],
    "video": ["video", "i2v", "t2v", "animate", "motion"],
}

STYLE_TAG_KEYWORDS = {
    "cinematic": ["cinematic", "film", "movie", "analog", "kodak", "cinestill", "vision", "holocine"],
    "realistic": ["realistic", "realvis", "juggernaut", "epicrealism", "photon", "absolute", "dreamshaper"],
    "animation": ["animation", "animated", "cartoon", "illustration", "toon"],
    "anime": ["anime", "manga"],
    "storyboard": ["storyboard", "board", "sketch", "lineart", "line art", "pencil"],
    "inpaint": ["inpaint", "fill"],
    "upscale": ["upscale", "esrgan", "4x", "8x"],
    "video": ["video", "i2v", "t2v", "animate", "motion"],
    "fast": ["fast", "rapid", "schnell", "turbo", "lightning"],
    "high_quality": ["high", "quality", "pro", "dev", "bf16", "fp16", "14b", "19b", "22b"],
}

CATEGORY_FAMILY_MAP = {
    "controlnet": "controlnet",
    "loras": "lora",
    "vae": "vae",
    "clip": "clip",
    "text_encoders": "text_encoder",
    "upscale_models": "upscale",
}

FAMILY_KEYS = [
    "sdxl",
    "sd15",
    "flux",
    "wan",
    "ltx",
    "video",
    "upscale",
    "controlnet",
    "lora",
    "vae",
    "clip",
    "text_encoder",
]

STYLE_KEYS = [
    "cinematic",
    "realistic",
    "animation",
    "anime",
    "storyboard",
    "inpaint",
    "upscale",
    "video",
    "fast",
    "high_quality",
]


def normalize_name(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _match_keywords(name: str, keywords: list[str]) -> bool:
    normalized = normalize_name(name)
    return any(keyword.lower() in normalized for keyword in keywords)


def classify_model_name(name: str, category: str | None = None) -> dict[str, list[str]]:
    families: list[str] = []
    style_tags: list[str] = []

    if category in CATEGORY_FAMILY_MAP:
        _append_unique(families, CATEGORY_FAMILY_MAP[category])

    for family, keywords in FAMILY_KEYWORDS.items():
        if _match_keywords(name, keywords):
            _append_unique(families, family)

    for style_tag, keywords in STYLE_TAG_KEYWORDS.items():
        if _match_keywords(name, keywords):
            _append_unique(style_tags, style_tag)

    return {"families": families, "style_tags": style_tags}


def _get_inventory_categories() -> dict[str, list[dict[str, Any]]]:
    inventory = load_comfyui_model_inventory()
    return inventory.get("categories", {})


def _category_names(categories: dict[str, list[dict[str, Any]]], category: str) -> list[str]:
    return [item.get("name", "") for item in categories.get(category, []) if item.get("name")]


def _first_name(categories: dict[str, list[dict[str, Any]]], category: str) -> str | None:
    names = _category_names(categories, category)
    return names[0] if names else None


def _filter_existing_names(candidates: list[str], available_names: list[str]) -> list[str]:
    available = set(available_names)
    return [candidate for candidate in candidates if candidate in available]


def get_recommended_model_sets() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    categories = inventory.get("categories", {})
    defaults = inventory.get("recommended_defaults", {})

    checkpoint_names = _category_names(categories, "checkpoints")
    vae_names = _category_names(categories, "vae")
    upscale_names = _category_names(categories, "upscale_models")
    diffusion_names = _category_names(categories, "diffusion_models")
    unet_names = _category_names(categories, "unet")

    flux_candidates = _filter_existing_names(defaults.get("flux_candidates", []), diffusion_names + unet_names + checkpoint_names)
    wan_candidates = _filter_existing_names(defaults.get("wan_candidates", []), diffusion_names + unet_names + checkpoint_names)
    ltx_candidates = _filter_existing_names(defaults.get("ltx_candidates", []), diffusion_names + unet_names + checkpoint_names)

    storyboard_checkpoint = defaults.get("storyboard_checkpoint")
    storyboard_vae = defaults.get("storyboard_vae")

    cinematic_checkpoint = flux_candidates[0] if flux_candidates else storyboard_checkpoint
    cinematic_family = "flux" if flux_candidates else "sdxl"

    video_model = wan_candidates[0] if wan_candidates else (ltx_candidates[0] if ltx_candidates else None)
    video_family = "wan" if wan_candidates else ("ltx" if ltx_candidates else None)

    return {
        "storyboard": {
            "model_family": "sdxl",
            "checkpoint": storyboard_checkpoint,
            "vae": storyboard_vae,
            "lora": None,
        },
        "cinematic_still": {
            "model_family": cinematic_family,
            "checkpoint": cinematic_checkpoint,
            "vae": storyboard_vae if cinematic_family == "sdxl" else None,
            "lora": None,
        },
        "video_generation": {
            "model_family": video_family,
            "checkpoint": video_model,
            "vae": None,
            "lora": None,
        },
        "upscale": {
            "model_family": "upscale",
            "checkpoint": upscale_names[0] if upscale_names else None,
            "vae": None,
            "lora": None,
        },
    }


def classify_comfyui_models() -> dict[str, Any]:
    inventory = load_comfyui_model_inventory()
    categories = inventory.get("categories", {})

    families = {family: [] for family in FAMILY_KEYS}
    style_tags = {style_tag: [] for style_tag in STYLE_KEYS}

    for category, models in categories.items():
        for model in models:
            name = model.get("name", "")
            if not name:
                continue
            classification = classify_model_name(name, category)
            for family in classification["families"]:
                if family in families:
                    _append_unique(families[family], name)
            for style_tag in classification["style_tags"]:
                if style_tag in style_tags:
                    _append_unique(style_tags[style_tag], name)

    return {
        "status": "ok",
        "families": families,
        "style_tags": style_tags,
        "recommended": get_recommended_model_sets(),
    }


def get_model_families() -> dict[str, list[str]]:
    return classify_comfyui_models()["families"]


def get_style_tags() -> dict[str, list[str]]:
    return classify_comfyui_models()["style_tags"]
