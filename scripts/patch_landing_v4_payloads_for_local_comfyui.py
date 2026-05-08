#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path("/opt/SERVICIOS_CINE")
PAYLOAD_DIR = REPO / ".tmp/landing_comfyui_v4/image_payloads"
OUT_REPORT = REPO / ".tmp/landing_comfyui_v4/payload_model_patch_report.json"

# Modelos reales detectados en tu ComfyUI
UNET_NAME = "FLUX/flux1-dev-fp8.safetensors"
CLIP_L_NAME = "clip_l.safetensors"
T5XXL_NAME = "t5/t5xxl_fp16.safetensors"
VAE_NAME = "FLUX/ae.safetensors"

WIDTH = 1536
HEIGHT = 864


def patch_node(node: dict[str, Any]) -> list[str]:
    patched: list[str] = []

    class_type = node.get("class_type")
    if not isinstance(class_type, str):
        return patched

    inputs = node.setdefault("inputs", {})
    if not isinstance(inputs, dict):
        return patched

    if class_type == "UNETLoader":
        inputs["unet_name"] = UNET_NAME
        patched.append("UNETLoader.unet_name")

    if class_type == "DualCLIPLoader":
        inputs["clip_name1"] = CLIP_L_NAME
        inputs["clip_name2"] = T5XXL_NAME
        patched.append("DualCLIPLoader.clip_name1")
        patched.append("DualCLIPLoader.clip_name2")

    if class_type == "VAELoader":
        inputs["vae_name"] = VAE_NAME
        patched.append("VAELoader.vae_name")

    if class_type == "ModelSamplingFlux":
        inputs["width"] = WIDTH
        inputs["height"] = HEIGHT
        patched.append("ModelSamplingFlux.width")
        patched.append("ModelSamplingFlux.height")

    if class_type in {"EmptySD3LatentImage", "EmptyLatentImage"}:
        inputs["width"] = WIDTH
        inputs["height"] = HEIGHT
        patched.append(f"{class_type}.width")
        patched.append(f"{class_type}.height")

    return patched


def walk(obj: Any, path: str, changes: list[dict[str, Any]]) -> None:
    if isinstance(obj, dict):
        node_changes = patch_node(obj)
        if node_changes:
            changes.append({"path": path, "patched": node_changes, "class_type": obj.get("class_type")})
        for key, value in obj.items():
            walk(value, f"{path}.{key}", changes)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            walk(value, f"{path}[{index}]", changes)


def main() -> int:
    if not PAYLOAD_DIR.exists():
        print(f"ERROR: no existe {PAYLOAD_DIR}")
        return 1

    report: dict[str, Any] = {
        "payload_dir": str(PAYLOAD_DIR),
        "unet": UNET_NAME,
        "clip_l": CLIP_L_NAME,
        "t5xxl": T5XXL_NAME,
        "vae": VAE_NAME,
        "width": WIDTH,
        "height": HEIGHT,
        "files": [],
    }

    print("===== PATCH LANDING V4 MODELOS LOCALES =====")
    print(f"UNET:  {UNET_NAME}")
    print(f"CLIP1: {CLIP_L_NAME}")
    print(f"CLIP2: {T5XXL_NAME}")
    print(f"VAE:   {VAE_NAME}")
    print(f"SIZE:  {WIDTH}x{HEIGHT}")

    for path in sorted(PAYLOAD_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))

        data["width"] = WIDTH
        data["height"] = HEIGHT

        changes: list[dict[str, Any]] = []
        walk(data, "$", changes)

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        report["files"].append(
            {
                "file": path.name,
                "patched_nodes": len(changes),
                "changes": changes,
            }
        )

        print(f"OK {path.name}: {len(changes)} nodos parcheados")
        for change in changes:
            print(f"  - {change['path']} {change['patched']}")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Report: {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
