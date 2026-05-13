"""
workflow_parser.py — Extrae metadatos de workflows JSON de ComfyUI.

Lee cualquier workflow JSON (formato API o legacy con nodos array),
extrae class_type, genera tags automáticos y resumen semántico.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional

CINEMA_TAGS = [
    "storyboard", "previs", "i2v", "t2i", "decorado", "personaje",
    "contraplano", "restauracion", "audio", "lipsync", "flux",
    "wan", "ltxv", "qwen", "sdxl", "dubbing", "voice_clone",
]

PRODUCTION_PHASES = {
    "storyboard": "preproduccion",
    "previs": "preproduccion",
    "t2i": "preproduccion",
    "i2v": "rodaje_virtual",
    "wan": "rodaje_virtual",
    "ltxv": "rodaje_virtual",
    "decorado": "rodaje_virtual",
    "personaje": "rodaje_virtual",
    "contraplano": "rodaje_virtual",
    "restauracion": "postproduccion",
    "upscale": "postproduccion",
    "deinterlace": "postproduccion",
    "audio": "doblaje_audio",
    "lipsync": "doblaje_audio",
    "dubbing": "doblaje_audio",
    "voice_clone": "doblaje_audio",
    "tts": "doblaje_audio",
}


def extract_nodes(data: dict) -> list[str]:
    nodes = set()
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, dict) and "class_type" in val:
                nodes.add(val["class_type"])
            elif isinstance(val, dict):
                for subkey, subval in val.items():
                    if isinstance(subval, dict) and "class_type" in subval:
                        nodes.add(subval["class_type"])
        if "nodes" in data and isinstance(data["nodes"], list):
            for node in data["nodes"]:
                if isinstance(node, dict) and "type" in node:
                    nodes.add(node["type"])
    return sorted(nodes)


def extract_models(data: dict, nodes: list[str]) -> list[str]:
    models = set()
    for node_lower in (n.lower() for n in nodes):
        if "checkpoint" in node_lower:
            if "sdxl" in node_lower:
                models.add("sdxl")
            elif "flux" in node_lower:
                models.add("flux")
            else:
                models.add("sd15")
        if "unet" in node_lower and "flux" in node_lower:
            models.add("flux")
    return sorted(models)


def auto_tags(name: str, path: str, nodes: list[str]) -> list[str]:
    tags = set()
    lower = name.lower() + " " + path.lower()
    for tag in CINEMA_TAGS:
        if tag in lower:
            tags.add(tag)
    for node in nodes:
        nl = node.lower()
        if "checkpoint" in nl and "sdxl" in nl:
            tags.add("sdxl")
        if "wan" in nl:
            tags.add("wan")
        if "ltx" in nl:
            tags.add("ltxv")
        if "qwen" in nl:
            tags.add("qwen")
        if "saveaudio" in nl or "texttospeech" in nl:
            tags.add("audio")
            tags.add("tts")
        if "voiceclone" in nl:
            tags.add("voice_clone")
            tags.add("dubbing")
        if "wav2lip" in nl:
            tags.add("lipsync")
        if "controlnet" in nl:
            tags.add("controlnet")
        if "ipadapter" in nl:
            tags.add("ipadapter")
    return sorted(tags)


def detect_phase(tags: list[str]) -> str:
    for tag in tags:
        if tag in PRODUCTION_PHASES:
            return PRODUCTION_PHASES[tag]
    return "general"


def make_summary(name: str, nodes: list[str], tags: list[str]) -> str:
    node_str = ", ".join(nodes[:12])
    tag_str = ", ".join(tags)
    phase = detect_phase(tags)
    return (f"Workflow '{name}' con nodos {node_str}. "
            f"Tags: {tag_str}. Fase: {phase}.")


def detect_backend(nodes: list[str], path: str) -> str:
    node_lower = " ".join(n.lower() for n in nodes)
    path_lower = path.lower()
    if any(kw in node_lower for kw in ("texttospeech", "saveaudio", "voiceclone", "wav2lip", "speechtotext")):
        return "dubbing"
    if any(kw in path_lower for kw in ("dubbing", "tts", "voice", "audio")):
        return "dubbing"
    if any(kw in node_lower for kw in ("wan", "ltx", "video")):
        return "video"
    if any(kw in path_lower for kw in ("upscale", "deinterlace", "restoration", "delivery")):
        return "lab"
    if "flux" in node_lower or "flux" in path_lower:
        return "still"
    return "still"


def parse_workflow(filepath: str) -> Optional[dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return None

    nodes = extract_nodes(data)
    if not nodes:
        return None

    path_obj = Path(filepath)
    name = path_obj.stem.replace(".template", "")
    wf_id = hashlib.md5(str(filepath).encode()).hexdigest()[:16]
    tags = auto_tags(name, str(filepath), nodes)
    models = extract_models(data, nodes)
    phase = detect_phase(tags)
    summary = make_summary(name, nodes, tags)
    backend = detect_backend(nodes, str(filepath))

    # Cinema use case enriquecido
    cinema_use_case = _build_cinema_use_case(name, tags, phase, models)

    return {
        "id": wf_id,
        "name": name,
        "path": str(path_obj.absolute()),
        "nodes": nodes,
        "models": models,
        "tags": tags,
        "phase": phase,
        "backend": backend,
        "summary": summary,
        "cinema_use_case": cinema_use_case,
        "file_size_bytes": path_obj.stat().st_size if path_obj.exists() else 0,
    }


def _build_cinema_use_case(name: str, tags: list[str], phase: str, models: list[str]) -> str:
    parts = []
    tag_set = set(tags)

    if "storyboard" in tag_set or "previs" in tag_set:
        parts.append("Generación de storyboard para previsualización cinematográfica")
    if "contraplano" in tag_set:
        parts.append("con planos/contraplanos y consistencia de eje")
    if "personaje" in tag_set:
        parts.append("con consistencia de personaje")
    if "i2v" in tag_set or "wan" in tag_set:
        parts.append("conversión imagen a vídeo con movimiento controlado")
    if "ltxv" in tag_set:
        parts.append("vídeo cinematográfico LTXV con control de eje")
    if "restauracion" in tag_set or "upscale" in tag_set:
        parts.append("restauración y upscaling 4K")
    if "dubbing" in tag_set or "voice_clone" in tag_set:
        parts.append("doblaje y clonación de voz con trazabilidad legal")
    if "lipsync" in tag_set:
        parts.append("sincronización labial con Wav2Lip")
    if "audio" in tag_set or "tts" in tag_set:
        parts.append("generación y procesamiento de audio")

    if models:
        parts.append(f"modelos: {', '.join(models)}")

    return ". ".join(parts) + "." if parts else f"Workflow {name} para fase de {phase}."
