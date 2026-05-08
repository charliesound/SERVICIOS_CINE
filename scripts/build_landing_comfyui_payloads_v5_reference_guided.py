#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_semantic_prompts_v5_reference_guided.json"
REFERENCE_MAP_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.json"
REFERENCE_MAP_EXAMPLE_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.example.json"
IMAGE_TEMPLATE_PATH = ROOT / "src/comfyui_workflows/imported_templates/flux_cine_2.template.json"
REF_IMAGES_DIR = ROOT / ".tmp" / "landing_comfyui_v5" / "reference_images"

TMP_BASE = ROOT / ".tmp" / "landing_comfyui_v5"
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
        if node.get("class_type") in ("EmptySD3LatentImage",):
            inputs["width"] = IMAGE_WIDTH
            inputs["height"] = IMAGE_HEIGHT
    return workflow


def inject_reference_nodes(
    workflow: dict[str, Any],
    reference_image_path: Path,
    reference_strength: float,
) -> dict[str, Any]:
    next_id = 100
    while str(next_id) in workflow:
        next_id += 1

    load_id = str(next_id)
    workflow[load_id] = {
        "inputs": {"image": str(reference_image_path)},
        "class_type": "LoadImage",
        "_meta": {"title": "Load Reference Image V5"},
    }

    encode_id = str(next_id + 1)
    workflow[encode_id] = {
        "inputs": {
            "samples": [load_id, 0],
            "vae": ["3", 0],
        },
        "class_type": "VAEEncode",
        "_meta": {"title": "VAEEncode (Reference V5)"},
    }

    ksampler = workflow.get("8")
    if isinstance(ksampler, dict):
        ksampler["inputs"]["latent_image"] = [encode_id, 0]
        ksampler["inputs"]["denoise"] = reference_strength

    empty_latent = workflow.get("7")
    if isinstance(empty_latent, dict) and empty_latent.get("class_type") == "EmptySD3LatentImage":
        pass

    return workflow


def build_image_payload(
    item: dict[str, Any],
    prompt_pack: dict[str, Any],
    template: dict[str, Any],
    reference_path: Path | None,
    reference_strength: float,
) -> dict[str, Any]:
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
        inputs["filename_prefix"] = f"landing_v5/{item['image_key']}"

    has_reference = reference_path is not None and reference_path.exists()
    workflow_text_only_fallback = not has_reference

    if has_reference:
        workflow = inject_reference_nodes(workflow, reference_path, reference_strength)

    if has_unresolved_placeholders(workflow):
        raise ValueError(f"Unresolved placeholders remain for {item['image_key']}")

    validate_blocked_strings(workflow, f"payload {item['image_key']}")

    return {
        "image_key": item["image_key"],
        "target_file_name": f"{item['image_key']}.webp",
        "v4_source_key": item.get("v4_source_key", ""),
        "visual_intent": item.get("visual_intent", ""),
        "composition_lock": item.get("composition_lock", ""),
        "lighting_lock": item.get("lighting_lock", ""),
        "workflow_id": "cinematic_flux_cine_2",
        "workflow_template": "src/comfyui_workflows/imported_templates/flux_cine_2.template.json",
        "width": IMAGE_WIDTH,
        "height": IMAGE_HEIGHT,
        "steps": IMAGE_STEPS,
        "cfg": IMAGE_CFG,
        "seed": seed,
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "reference_image_path": str(reference_path) if has_reference else "",
        "reference_strength": reference_strength if has_reference else 0.0,
        "workflow_text_only_fallback": workflow_text_only_fallback,
        "compiled_workflow": workflow,
    }


def load_reference_map() -> dict[str, dict[str, Any]]:
    ref_map_path = REFERENCE_MAP_PATH if REFERENCE_MAP_PATH.exists() else REFERENCE_MAP_EXAMPLE_PATH
    ref_data = load_json(ref_map_path)
    items = ref_data.get("items", [])
    return {item["image_key"]: item for item in items}


def main() -> int:
    print("=== Build Landing V5 Reference-Guided Payloads ===\n")

    prompt_pack = load_json(PROMPTS_PATH)
    items = prompt_pack.get("items", [])
    if len(items) < 10:
        raise ValueError(f"Expected at least 10 landing V5 prompt items, got {len(items)}")
    print(f"  Prompt items: {len(items)}")

    ref_map = load_reference_map()
    mapped_count = sum(1 for item in items if item["image_key"] in ref_map)
    print(f"  Reference map entries: {len(ref_map)}")
    print(f"  Items with reference map entry: {mapped_count}")

    template = load_json(IMAGE_TEMPLATE_PATH)
    IMAGE_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image_records: list[dict[str, Any]] = []
    for item in items:
        image_key = item["image_key"]
        ref_entry = ref_map.get(image_key, {})
        ref_filename = ref_entry.get("reference_image_file", "")
        ref_strength = ref_entry.get("reference_strength", 0.55)

        reference_path: Path | None = None
        if ref_filename:
            candidate = REF_IMAGES_DIR / ref_filename
            if candidate.exists():
                reference_path = candidate
                print(f"  REFERENCE FOUND: {image_key} -> {ref_filename} (strength={ref_strength})")
            else:
                ref_alt = REF_IMAGES_DIR / ref_filename
                if ref_alt.exists():
                    reference_path = ref_alt
                    print(f"  REFERENCE FOUND: {image_key} -> {ref_filename} (strength={ref_strength})")
                else:
                    print(f"  REFERENCE MISSING: {image_key} -> {ref_filename} (will use text-only)")

        image_payload = build_image_payload(item, prompt_pack, template, reference_path, ref_strength)
        payload_path = IMAGE_PAYLOADS_DIR / f"{image_key}.json"
        dump_json(payload_path, image_payload)

        mode = "reference-guided" if reference_path else "text-only"
        image_records.append({
            "image_key": image_key,
            "target_file_name": f"{image_key}.webp",
            "payload_path": str(payload_path.relative_to(ROOT)).replace("\\", "/"),
            "seed": image_payload["seed"],
            "mode": mode,
            "reference_image_path": str(reference_path) if reference_path else "",
            "reference_strength": ref_strength if reference_path else 0.0,
            "workflow_text_only_fallback": image_payload["workflow_text_only_fallback"],
        })
        print(f"  PAYLOAD: {image_key} [{mode}]")

    manifest = {
        "version": "v5",
        "prompt_pack": str(PROMPTS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "reference_map": str(
            (REFERENCE_MAP_PATH if REFERENCE_MAP_PATH.exists() else REFERENCE_MAP_EXAMPLE_PATH)
            .relative_to(ROOT)
        ).replace("\\", "/"),
        "image_template": str(IMAGE_TEMPLATE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "image_count": len(image_records),
        "image_payloads": image_records,
    }
    dump_json(MANIFEST_PATH, manifest)

    ref_count = sum(1 for r in image_records if r["mode"] == "reference-guided")
    text_count = sum(1 for r in image_records if r["mode"] == "text-only")

    print(f"\n=== Summary ===")
    print(f"  Payloads: {len(image_records)}")
    print(f"  Reference-guided: {ref_count}")
    print(f"  Text-only: {text_count}")
    print(f"  Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
