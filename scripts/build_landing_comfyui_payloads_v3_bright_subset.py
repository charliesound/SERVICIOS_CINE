#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3_bright.json"
TEMPLATE_PATH = ROOT / "src/comfyui_workflows/imported_templates/flux_cine_2.template.json"
REVIEW_DIR = ROOT / ".tmp" / "landing_comfyui_v3" / "review"
SUBSET_PATH = REVIEW_DIR / "landing_v3_regenerate_subset.json"
PAYLOADS_DIR = ROOT / ".tmp" / "landing_comfyui_v3" / "bright_image_payloads"

WIDTH = 1536
HEIGHT = 864
STEPS = 36
CFG = 3.5

UNET_NAME = "FLUX/flux1-dev-fp8.safetensors"
CLIP_L_NAME = "clip_l.safetensors"
T5XXL_NAME = "t5/t5xxl_fp16.safetensors"
VAE_NAME = "FLUX/ae.safetensors"

DEFAULT_SUBSET = {
    "regenerate": [
        "landing-hero-main-v3",
        "landing-problem-fragmented-v3",
        "landing-ai-reasoning-v3",
        "landing-comfyui-generation-v3",
        "landing-cid-orchestration-v3",
        "landing-storyboard-preview-v3",
        "landing-concept-keyvisual-v3",
        "landing-producers-studios-v3",
        "landing-professional-differential-v3",
        "landing-delivery-final-v3"
    ]
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def deterministic_seed(image_key: str) -> int:
    digest = hashlib.sha256((image_key + "-bright").encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % 2147483647


def join_prompt_parts(*parts: str) -> str:
    cleaned = [part.strip().strip(",") for part in parts if part and part.strip()]
    return ", ".join(cleaned)


def replace_placeholders(value: Any, replacements: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: replace_placeholders(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_placeholders(item, replacements) for item in value]
    if isinstance(value, str):
        if value in replacements:
            return replacements[value]
        updated = value
        for placeholder, replacement in replacements.items():
            if isinstance(replacement, (str, int, float)):
                updated = updated.replace(placeholder, str(replacement))
        return updated
    return value


def ensure_subset_file() -> dict[str, Any]:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    if not SUBSET_PATH.exists():
        dump_json(SUBSET_PATH, DEFAULT_SUBSET)
        return dict(DEFAULT_SUBSET)
    return load_json(SUBSET_PATH)


def validate_payload_text(payload: dict[str, Any]) -> None:
    payload_text = json.dumps(payload, ensure_ascii=True)
    blocked_literals = ["{{", ".env", "/mnt/g", "G:\\\\", "G:\\", "/prompt", "api_key", "password", "secret", "sk-"]
    for literal in blocked_literals:
        if literal in payload_text:
            raise ValueError(f"Blocked literal found in payload for {payload.get('image_key')}: {literal}")


def main() -> int:
    prompt_pack = load_json(PROMPTS_PATH)
    items = prompt_pack.get("items", [])
    template = load_json(TEMPLATE_PATH)
    subset = ensure_subset_file()
    subset_keys = [str(value) for value in subset.get("regenerate", [])]
    item_by_key = {item["image_key"]: item for item in items}

    PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for image_key in subset_keys:
        item = item_by_key.get(image_key)
        if item is None:
            raise KeyError(f"Unknown image_key in subset: {image_key}")

        seed = deterministic_seed(image_key)
        prompt = item["image_prompt"]
        negative_prompt = join_prompt_parts(
            prompt_pack.get("visual_identity", {}).get("image_negative_prompt_global", ""),
            item.get("image_negative_prompt", ""),
        )
        replacements = {
            "{{POSITIVE_PROMPT}}": prompt,
            "{{NEGATIVE_PROMPT}}": negative_prompt,
            "{{WIDTH}}": WIDTH,
            "{{HEIGHT}}": HEIGHT,
            "{{STEPS}}": STEPS,
            "{{CFG}}": CFG,
            "{{SEED}}": seed,
            "{{UNET_NAME}}": UNET_NAME,
            "{{CLIP_L_NAME}}": CLIP_L_NAME,
            "{{T5XXL_NAME}}": T5XXL_NAME,
            "{{VAE_NAME}}": VAE_NAME,
        }

        compiled_workflow = replace_placeholders(template, replacements)
        save_image_node = compiled_workflow.get("10")
        if isinstance(save_image_node, dict):
            save_image_node.setdefault("inputs", {})["filename_prefix"] = f"landing_v3_bright/{image_key}"

        payload = {
            "image_key": image_key,
            "image_file_name": item["image_file_name"],
            "workflow_id": "cinematic_flux_cine_2",
            "width": WIDTH,
            "height": HEIGHT,
            "steps": STEPS,
            "cfg": CFG,
            "seed": seed,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "compiled_workflow": compiled_workflow,
            "render_mode": "bright_subset_dry_run",
        }
        validate_payload_text(payload)
        dump_json(PAYLOADS_DIR / f"{image_key}.json", payload)

    print(f"Bright subset payloads generated in {PAYLOADS_DIR.relative_to(ROOT)}")
    print(f"Subset file: {SUBSET_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
