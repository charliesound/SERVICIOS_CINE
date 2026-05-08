#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v4/landing_semantic_prompts_v4.json"
IMAGE_TEMPLATE_PATH = ROOT / "src/comfyui_workflows/imported_templates/flux_cine_2.template.json"

TMP_BASE = ROOT / ".tmp" / "landing_comfyui_v4"
IMAGE_PAYLOADS_DIR = TMP_BASE / "image_payloads"
MANIFEST_PATH = TMP_BASE / "manifest.json"

IMAGE_WIDTH = 1536
IMAGE_HEIGHT = 864
IMAGE_STEPS = 32
IMAGE_CFG = 3.5

DEFAULT_FLUX_MODELS = {
    "UNET_NAME": "FLUX/flux1-dev-fp8.safetensors",
    "CLIP_L_NAME": "clip_l.safetensors",
    "T5XXL_NAME": "t5/t5xxl_fp16.safetensors",
    "VAE_NAME": "FLUX/ae.safetensors",
}

BLOCKED_STRINGS = ["{{", ".env", "/mnt/g", "G:\\", "C:\\", "COMFYUI_HUB"]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def has_unresolved_placeholders(value: Any) -> bool:
    if isinstance(value, dict):
        return any(has_unresolved_placeholders(item) for item in value.values())
    if isinstance(value, list):
        return any(has_unresolved_placeholders(item) for item in value)
    return isinstance(value, str) and "{{" in value and "}}" in value


def validate_blocked_strings(value: Any, source_label: str) -> None:
    if isinstance(value, dict):
        for item in value.values():
            validate_blocked_strings(item, source_label)
    elif isinstance(value, list):
        for item in value:
            validate_blocked_strings(item, source_label)
    elif isinstance(value, str):
        for blocked in BLOCKED_STRINGS:
            if blocked in value:
                raise ValueError(f"BLOCKED string '{blocked}' found in {source_label}")


def deterministic_seed(image_key: str) -> int:
    digest = hashlib.sha256(image_key.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % 2147483647


def join_prompt_parts(*parts: str) -> str:
    cleaned = [part.strip().strip(",") for part in parts if part and part.strip()]
    return ", ".join(cleaned)


def patch_model_dimensions(workflow: dict[str, Any]) -> dict[str, Any]:
    for node_id, node in workflow.items():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs", {})
        if node.get("class_type") in ("ModelSamplingFlux",):
            pass
        if node.get("class_type") in ("EmptySD3LatentImage",):
            inputs["width"] = IMAGE_WIDTH
            inputs["height"] = IMAGE_HEIGHT
    return workflow


def build_image_payload(item: dict[str, Any], prompt_pack: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    visual_identity = prompt_pack.get("visual_identity", {})
    seed = deterministic_seed(item["image_key"])
    positive_prompt = join_prompt_parts(
        visual_identity.get("image_prompt_prefix", ""),
        item.get("positive_prompt", ""),
    )
    negative_prompt = join_prompt_parts(
        visual_identity.get("image_negative_prompt_global", ""),
        item.get("negative_prompt", ""),
    )

    replacements = {
        "{{POSITIVE_PROMPT}}": positive_prompt,
        "{{NEGATIVE_PROMPT}}": negative_prompt,
        "{{WIDTH}}": IMAGE_WIDTH,
        "{{HEIGHT}}": IMAGE_HEIGHT,
        "{{STEPS}}": IMAGE_STEPS,
        "{{CFG}}": IMAGE_CFG,
        "{{SEED}}": seed,
        "{{UNET_NAME}}": DEFAULT_FLUX_MODELS["UNET_NAME"],
        "{{CLIP_L_NAME}}": DEFAULT_FLUX_MODELS["CLIP_L_NAME"],
        "{{T5XXL_NAME}}": DEFAULT_FLUX_MODELS["T5XXL_NAME"],
        "{{VAE_NAME}}": DEFAULT_FLUX_MODELS["VAE_NAME"],
    }

    workflow = replace_placeholders(template, replacements)
    workflow = patch_model_dimensions(workflow)

    save_image_node = workflow.get("10")
    if isinstance(save_image_node, dict):
        inputs = save_image_node.setdefault("inputs", {})
        inputs["filename_prefix"] = f"landing_v4/{item['image_key']}"

    if has_unresolved_placeholders(workflow):
        raise ValueError(f"Unresolved placeholders remain for {item['image_key']}")

    validate_blocked_strings(workflow, f"payload {item['image_key']}")

    return {
        "image_key": item["image_key"],
        "block_label": item["block_label"],
        "target_file_name": item["target_file_name"],
        "landing_copy_focus": item.get("landing_copy_focus", ""),
        "semantic_intent": item.get("semantic_intent", ""),
        "workflow_id": "cinematic_flux_cine_2",
        "workflow_template": "src/comfyui_workflows/imported_templates/flux_cine_2.template.json",
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
        "steps": IMAGE_STEPS,
        "cfg": IMAGE_CFG,
        "seed": seed,
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "compiled_workflow": workflow,
    }


def main() -> int:
    prompt_pack = load_json(PROMPTS_PATH)
    items = prompt_pack.get("items", [])
    if len(items) < 10:
        raise ValueError(f"Expected at least 10 landing V4 prompt items, got {len(items)}")

    template = load_json(IMAGE_TEMPLATE_PATH)

    IMAGE_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image_records: list[dict[str, Any]] = []

    for item in items:
        image_payload = build_image_payload(item, prompt_pack, template)
        image_payload_path = IMAGE_PAYLOADS_DIR / f"{item['image_key']}.json"
        dump_json(image_payload_path, image_payload)
        image_records.append({
            "image_key": item["image_key"],
            "target_file_name": item["target_file_name"],
            "payload_path": str(image_payload_path.relative_to(ROOT)).replace("\\", "/"),
            "seed": image_payload["seed"],
        })

    manifest = {
        "version": "v4",
        "prompt_pack": str(PROMPTS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "image_template": str(IMAGE_TEMPLATE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "image_count": len(image_records),
        "image_payloads": image_records,
    }
    dump_json(MANIFEST_PATH, manifest)

    print("=== Landing ComfyUI V4 payloads generated ===")
    print(f"  payloads: {IMAGE_PAYLOADS_DIR.relative_to(ROOT)}/")
    print(f"  manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"  count: {len(image_records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
