#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
IMAGE_TEMPLATE_PATH = ROOT / "src/comfyui_workflows/imported_templates/flux_cine_2.template.json"
VIDEO_WAN_PATH = ROOT / "src/comfyui_workflows/video_wan.json"
VIDEO_LTX_PATH = ROOT / "src/comfyui_workflows/video_ltx.json"

TMP_BASE = ROOT / ".tmp" / "landing_comfyui_v3"
IMAGE_PAYLOADS_DIR = TMP_BASE / "image_payloads"
VIDEO_PAYLOADS_DIR = TMP_BASE / "video_payloads"
MANIFEST_PATH = TMP_BASE / "manifest.json"
README_PATH = TMP_BASE / "README.md"

IMAGE_WIDTH = 1536
IMAGE_HEIGHT = 864
IMAGE_STEPS = 32
IMAGE_CFG = 3.5
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_DURATION_SECONDS = 5
VIDEO_FPS = 24

DEFAULT_FLUX_MODELS = {
    "UNET_NAME": "flux1-dev_fp8_scaled.safetensors",
    "CLIP_L_NAME": "clip_l.safetensors",
    "T5XXL_NAME": "t5xxl_fp16.safetensors",
    "VAE_NAME": "ae.safetensors",
}


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


def deterministic_seed(image_key: str) -> int:
    digest = hashlib.sha256(image_key.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % 2147483647


def join_prompt_parts(*parts: str) -> str:
    cleaned = [part.strip().strip(",") for part in parts if part and part.strip()]
    return ", ".join(cleaned)


def build_image_payload(item: dict[str, Any], prompt_pack: dict[str, Any], template: dict[str, Any]) -> dict[str, Any]:
    visual_identity = prompt_pack.get("visual_identity", {})
    seed = deterministic_seed(item["image_key"])
    positive_prompt = join_prompt_parts(
        visual_identity.get("image_prompt_prefix", ""),
        item.get("image_prompt", ""),
    )
    negative_prompt = join_prompt_parts(
        visual_identity.get("image_negative_prompt_global", ""),
        item.get("image_negative_prompt", ""),
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
    save_image_node = workflow.get("10")
    if isinstance(save_image_node, dict):
        inputs = save_image_node.setdefault("inputs", {})
        inputs["filename_prefix"] = f"landing_v3/{item['image_key']}"

    if has_unresolved_placeholders(workflow):
        raise ValueError(f"Unresolved placeholders remain for {item['image_key']}")

    return {
        "image_key": item["image_key"],
        "block_label": item["block_label"],
        "image_file_name": item["image_file_name"],
        "image_alt": item.get("image_alt", ""),
        "landing_copy_focus": item.get("landing_copy_focus", ""),
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


def detect_video_candidate() -> dict[str, Any] | None:
    candidates = [
        ("video_wan", VIDEO_WAN_PATH, True),
        ("video_ltx", VIDEO_LTX_PATH, False),
    ]
    for workflow_id, path, preferred in candidates:
        if not path.exists():
            continue
        payload = load_json(path)
        executable_nodes = [
            key for key, value in payload.items()
            if isinstance(value, dict) and value.get("class_type")
        ]
        compatible = bool(executable_nodes)
        return {
            "workflow_id": workflow_id,
            "workflow_path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "preferred": preferred,
            "compatible": compatible,
            "node_count": len(executable_nodes),
            "note": payload.get("note"),
        }
    return None


def build_video_plan(item: dict[str, Any], candidate: dict[str, Any] | None) -> dict[str, Any]:
    preferred_workflow_id = candidate.get("workflow_id") if candidate else None
    preferred_workflow_path = candidate.get("workflow_path") if candidate else None
    return {
        "image_key": item["image_key"],
        "source_image": f"src_frontend/public/landing-media/{item['image_file_name']}",
        "video_file_name": item["video_file_name"],
        "video_prompt": item["video_prompt"],
        "video_negative_prompt": item["video_negative_prompt"],
        "duration_seconds": VIDEO_DURATION_SECONDS,
        "fps": VIDEO_FPS,
        "width": VIDEO_WIDTH,
        "height": VIDEO_HEIGHT,
        "motion_strength": "low",
        "camera_motion": "slow cinematic push or parallax",
        "safe_to_render": False,
        "requires_approved_source_image": True,
        "video_motion_intent": item["video_motion_intent"],
        "preferred_workflow_id": preferred_workflow_id,
        "preferred_workflow_path": preferred_workflow_path,
        "workflow_mapping_status": "requires_manual_image_to_video_mapping",
    }


def write_readme(manifest: dict[str, Any]) -> None:
    candidate = manifest.get("video_candidate") or {}
    lines = [
        "# Landing ComfyUI V3 Dry Run",
        "",
        "Se generaron payloads de imagen y planes de video coherentes para la landing V3.",
        "",
        "## Estructura",
        "- `image_payloads/*.json`: payloads Flux listos para enviar manualmente a ComfyUI.",
        "- `video_payloads/*.video_plan.json`: planes image-to-video dependientes de imagen base aprobada.",
        "- `manifest.json`: resumen de prompts, seeds y candidatos de workflow.",
        "",
        "## Render",
        "- Las imagenes usan `flux_cine_2.template.json` con 1536x864, 32 steps y CFG 3.5.",
        "- Los videos no llaman a `/prompt` por defecto y requieren adaptar un workflow image-to-video.",
    ]
    if candidate:
        lines.extend([
            "",
            "## Video candidate",
            f"- Workflow preferido detectado: `{candidate.get('workflow_id')}`.",
            f"- Ruta relativa: `{candidate.get('workflow_path')}`.",
            f"- Compatible de forma directa: `{candidate.get('compatible')}`.",
        ])
    README_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    prompt_pack = load_json(PROMPTS_PATH)
    items = prompt_pack.get("items", [])
    if len(items) != 10:
        raise ValueError("Expected 10 landing V3 prompt items")

    template = load_json(IMAGE_TEMPLATE_PATH)
    video_candidate = detect_video_candidate()

    IMAGE_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image_records: list[dict[str, Any]] = []
    video_records: list[dict[str, Any]] = []

    for item in items:
        image_payload = build_image_payload(item, prompt_pack, template)
        image_payload_path = IMAGE_PAYLOADS_DIR / f"{item['image_key']}.json"
        dump_json(image_payload_path, image_payload)
        image_records.append({
            "image_key": item["image_key"],
            "image_file_name": item["image_file_name"],
            "payload_path": str(image_payload_path.relative_to(ROOT)).replace("\\", "/"),
            "seed": image_payload["seed"],
        })

        video_plan = build_video_plan(item, video_candidate)
        video_plan_path = VIDEO_PAYLOADS_DIR / f"{item['image_key']}.video_plan.json"
        dump_json(video_plan_path, video_plan)
        video_records.append({
            "image_key": item["image_key"],
            "video_file_name": item["video_file_name"],
            "payload_path": str(video_plan_path.relative_to(ROOT)).replace("\\", "/"),
            "safe_to_render": False,
        })

    manifest = {
        "version": "v3",
        "prompt_pack": str(PROMPTS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "image_template": str(IMAGE_TEMPLATE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "video_candidate": video_candidate,
        "image_count": len(image_records),
        "video_count": len(video_records),
        "image_payloads": image_records,
        "video_payloads": video_records,
    }
    dump_json(MANIFEST_PATH, manifest)
    write_readme(manifest)

    print("Landing ComfyUI V3 payloads generated.")
    print(f"- image payloads: {IMAGE_PAYLOADS_DIR.relative_to(ROOT)}")
    print(f"- video payloads: {VIDEO_PAYLOADS_DIR.relative_to(ROOT)}")
    print(f"- manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"- readme: {README_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
