#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMFYUI_BASE_URL = os.environ.get("COMFYUI_BASE_URL", "http://127.0.0.1:8188")
OBJECT_INFO_URL = f"{COMFYUI_BASE_URL}/object_info"
OUTPUT_DIR = ROOT / ".tmp" / "landing_comfyui_v5"
OUTPUT_PATH = OUTPUT_DIR / "reference_node_capabilities.json"

REFERENCE_NODE_CLASSES = [
    "LoadImage",
    "ImageScale",
    "VAEEncode",
    "KSampler",
    "CLIPVisionLoader",
    "CLIPVisionEncode",
    "IPAdapter",
    "IPAdapterAdvanced",
    "IPAdapterApply",
    "ApplyIPAdapter",
    "IPAdapterModelLoader",
    "Redux",
    "StyleModelLoader",
    "StyleModelApply",
    "ControlNetLoader",
    "ControlNetApply",
    "FluxGuidance",
    "ImageOnlyCheckpointLoader",
    "InstructPixToPixConditioning",
    "ImageBlend",
    "ImageComposite",
    "ImagePadForOutpaint",
]


def query_object_info() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(OBJECT_INFO_URL, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return {"_connection_error": str(exc.reason)}
    except Exception as exc:
        return {"_connection_error": str(exc)}


def detect_reference_capabilities(available_nodes: dict[str, Any]) -> dict[str, Any]:
    capabilities: dict[str, Any] = {
        "img2img_via_vae_encode": False,
        "ip_adapter": False,
        "redux_flux": False,
        "controlnet": False,
        "style_model": False,
        "load_image": False,
        "details": {},
    }

    for class_name in REFERENCE_NODE_CLASSES:
        present = class_name in available_nodes
        capabilities["details"][class_name] = {
            "available": present,
            "input_info": _extract_inputs(available_nodes.get(class_name, {})),
        }

    if "LoadImage" in available_nodes:
        capabilities["load_image"] = True

    if "VAEEncode" in available_nodes and "LoadImage" in available_nodes and "KSampler" in available_nodes:
        capabilities["img2img_via_vae_encode"] = True

    if ("IPAdapter" in available_nodes or "IPAdapterAdvanced" in available_nodes
            or "IPAdapterApply" in available_nodes or "ApplyIPAdapter" in available_nodes):
        has_clip_vision = "CLIPVisionLoader" in available_nodes
        capabilities["ip_adapter"] = has_clip_vision
        capabilities["details"]["_ip_adapter_ready"] = has_clip_vision

    if "ImageOnlyCheckpointLoader" in available_nodes:
        capabilities["redux_flux"] = True

    if "ControlNetLoader" in available_nodes and "ControlNetApply" in available_nodes:
        capabilities["controlnet"] = True

    if "StyleModelLoader" in available_nodes and "StyleModelApply" in available_nodes:
        capabilities["style_model"] = True

    return _recommend_strategy(capabilities)


def _extract_inputs(node_info: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(node_info, dict):
        return {}
    inputs = node_info.get("input", node_info.get("inputs", {}))
    if isinstance(inputs, dict):
        required = inputs.get("required", {})
        return {k: True for k in required}
    return {}


def _recommend_strategy(capabilities: dict[str, Any]) -> dict[str, Any]:
    if capabilities["img2img_via_vae_encode"]:
        capabilities["recommended_strategy"] = "img2img_vae_encode"
        capabilities["strategy_description"] = (
            "Usar LoadImage + VAEEncode para codificar referencia como latent, "
            "luego KSampler con denoise < 1.0. Compatible con cualquier instalacion basica de ComfyUI."
        )
    elif capabilities["redux_flux"]:
        capabilities["recommended_strategy"] = "redux_flux"
        capabilities["strategy_description"] = (
            "Usar ImageOnlyCheckpointLoader para FLUX Redux. "
            "Requiere modelo Redux especifico."
        )
    elif capabilities["ip_adapter"]:
        capabilities["recommended_strategy"] = "ip_adapter"
        capabilities["strategy_description"] = (
            "Usar CLIPVisionLoader + IPAdapter para guiar estilo desde referencia. "
            "Requiere modelo IP-Adapter."
        )
    else:
        capabilities["recommended_strategy"] = "text_only_fallback"
        capabilities["strategy_description"] = (
            "No se detectaron nodos de referencia. "
            "Los payloads incluiiran reference_image_path como metadata "
            "pero el workflow compilado sera text-only. "
            "Instalar nodos: LoadImage, VAEEncode, o IPAdapter, o Redux."
        )

    return capabilities


def main() -> int:
    print("=== ComfyUI Reference Node Inspection ===\n")
    print(f"  ComfyUI URL: {COMFYUI_BASE_URL}")
    print(f"  Object info: {OBJECT_INFO_URL}\n")

    available_nodes = query_object_info()

    if "_connection_error" in available_nodes:
        print(f"  CONNECTION ERROR: {available_nodes['_connection_error']}")
        print("  Cannot inspect ComfyUI. Generating fallback report.\n")
        capabilities: dict[str, Any] = {
            "connection_status": "error",
            "error": available_nodes["_connection_error"],
            "recommended_strategy": "text_only_fallback",
            "strategy_description": (
                "No se pudo conectar con ComfyUI. "
                "Los payloads se generaran con text-only fallback. "
                "Ejecuta este script cuando ComfyUI este corriendo."
            ),
            "details": {},
            "inspected_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        print(f"  Nodes available: {len(available_nodes)}\n")
        capabilities = detect_reference_capabilities(available_nodes)

        for class_name in REFERENCE_NODE_CLASSES:
            status = "YES" if class_name in available_nodes else "no"
            print(f"    {status:3s}  {class_name}")

        print(f"\n  Recommended strategy: {capabilities['recommended_strategy']}")
        print(f"  Description: {capabilities['strategy_description']}")

    capabilities["inspected_at"] = datetime.now(timezone.utc).isoformat()
    capabilities["comfyui_url"] = COMFYUI_BASE_URL

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(capabilities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n  Report: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
