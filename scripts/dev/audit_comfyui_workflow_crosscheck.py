#!/usr/bin/env python3
"""ComfyUI Workflow Cross-Check Audit — COMFYUI.1B

Scans real workflow files, classifies them, cross-references required nodes
against each instance's object_info, maps existing custom_nodes per instance,
detects missing nodes/models, and generates install plan and report.

Outputs:
  - docs/validation/comfyui_workflow_crosscheck_20260521/raw/
  - docs/validation/comfyui_workflow_crosscheck_20260521.md
  - docs/validation/comfyui_missing_nodes_install_plan_20260521.md
"""
import json
import subprocess
import sys
import re
import shutil
import hashlib
import os
import fnmatch
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PORTS = [
    (8188, "still", "Image / Still"),
    (8189, "video", "Video / Cine"),
    (8190, "dubbing", "Dubbing / Audio"),
    (8191, "restoration", "Restoration"),
    (8192, "3d", "3D"),
]

PORT_PROFILES = {p[0]: p[1] for p in PORTS}

# Filesystem locations to scan for workflows (keep targeted, max depth)
WORKFLOW_SEARCH_PATHS = [
    (Path("/opt/SERVICIOS_CINE/data/workflows/comfyui"), 3),
    (Path("/opt/SERVICIOS_CINE/src/comfyui_workflows"), 3),
    (Path("/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/00_VIDEO"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/video_cine"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/dubbing_audio"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/restoration"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/00_3D"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows/image"), 2),
    (Path("/mnt/g/COMFYUI_HUB/workflows"), 0),
]

# Exclude patterns
EXCLUDE_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", "dist", "build",
    "OLD", "_archive", "ZIPs", ".ruff_cache", "venv",
    "custom_nodes__OFF", "custom_nodes.BACKUP.2026-02-18",
    ".venv_broken_20260217_205213",
}

EXCLUDE_FILE_PATTERNS = [
    re.compile(r"\.(jpg|jpeg|gif|svg|ico|pyc|py|ts|js|map)$", re.I),
    re.compile(r"(package|yarn|node_modules)"),
    re.compile(r"^__pycache__"),
    re.compile(r"_thumb\.(png|webp)$", re.I),
]

# Image paths for embedded workflow extraction (directories with PNG/WebP)
IMAGE_SEARCH_DIRS = [
    "/mnt/g/COMFYUI_HUB/workflows/00_IMAGEN_fija",
    "/mnt/g/COMFYUI_HUB/workflows/00_VIDEO",
    "/mnt/g/COMFYUI_HUB/workflows/video_cine",
    "/mnt/g/COMFYUI_HUB/workflows/image",
    "/mnt/g/COMFYUI_HUB/workflows/restoration",
    "/opt/SERVICIOS_CINE/data",
]

# Raw evidence dir from COMFYUI.1A
COMFYUI_1A_RAW = Path("docs/validation/comfyui_node_inventory_20260521")

# Output dirs
RAW_DIR = Path("docs/validation/comfyui_workflow_crosscheck_20260521/raw")
REPORT_PATH = Path("docs/validation/comfyui_workflow_crosscheck_20260521.md")
INSTALL_PLAN_PATH = Path("docs/validation/comfyui_missing_nodes_install_plan_20260521.md")

# Instance user-directories for custom_nodes
INSTANCE_CUSTOM_NODES_DIRS = {
    8188: Path("/home/harliesound/ai/ComfyUI_profiles/image/custom_nodes"),
    8189: Path("/home/harliesound/ai/ComfyUI_profiles/video_cine/custom_nodes"),
    8190: Path("/home/harliesound/ai/ComfyUI_profiles/dubbing_audio/custom_nodes"),
    8191: Path("/home/harliesound/ai/ComfyUI_profiles/restoration/custom_nodes"),
    8192: Path("/home/harliesound/ai/ComfyUI_profiles/3d/custom_nodes"),
}

# G: hub custom_nodes repo for lookup
G_HUB_CUSTOM_NODES = Path("/mnt/g/COMFYUI_HUB/custom_nodes_repo_real")

# Model root directories (only the primary model store for speed)
MODEL_ROOTS = [
    Path("/mnt/i/COMFYUI_OK/models"),
]

# Model type subdirs for matching
MODEL_TYPE_DIRS = {
    "checkpoints": ["checkpoints", "checkpoint"],
    "unet": ["unet", "UNET"],
    "clip": ["clip", "CLIP"],
    "clip_vision": ["clip_vision", "clip-vision"],
    "vae": ["vae", "VAE"],
    "lora": ["lora", "loras", "LoRA"],
    "controlnet": ["controlnet", "ControlNet"],
    "upscale_models": ["upscale_models", "upscaler", "ESRGAN"],
    "style_models": ["style_models"],
    "ipadapter": ["ipadapter", "IPAdapter"],
    "animatediff_models": ["animatediff_models"],
    "insightface": ["insightface"],
    "ultralytics": ["ultralytics"],
    "classification": ["classification"],
    "mmdets": ["mmdets"],
    "onnx": ["onnx"],
    "grounding": ["grounding"],
    "mmdit": ["mmdit"],
    "liveportrait": ["liveportrait"],
    "depth": ["depth", "Depth"],
    "facerestore": ["facerestore", "facerestore_models"],
    "reactor": ["reactor"],
    "sams": ["sams"],
    "wav2lip": ["wav2lip"],
    "whisper": ["whisper"],
    "audio_encoders": ["audio_encoders"],
}

# Family classification for workflows (same keywords as COMFYUI.1A)
FAMILY_KEYWORDS = {
    "image_still":    ["checkpoint", "vae", "clip", "sampler", "scheduler", "latent", "conditioning", "controlnet", "ipadapter", "lora", "load image", "preview image", "save image", "inpaint", "outpaint", "upscale", "style", "prompt", "text encode", "image encode", "image decode", "ksampler", "flux", "sdxl", "sd15", "sd3"],
    "storyboard":     ["storyboard", "cinematic", "previz", "pre-vis", "moodboard"],
    "video_cine":     ["video", "frame", "interpolation", "animate", "animation", "wan", "ltx", "svd", "temporal", "flow", "combine", "img2vid", "text-to-video", "mochi", "cogvideo", "hunyuan"],
    "dubbing_audio":  ["audio", "wav", "speech", "tts", "voice", "whisper", "phoneme", "alignment", "lipsync", "wav2lip", "dubbing", "sound"],
    "restoration":    ["restore", "restoration", "denoise", "deblur", "face restore", "face enhance", "cleanup", "artifact", "color", "conform", "resize"],
    "three_d":        ["depth", "normal", "mesh", "nerf", "gaussian", "splat", "camera", "pose", "scene", "geometry", "point cloud", "texture", "3d"],
    "utility":        ["json", "file", "debug", "preview", "mask", "segment", "metadata", "primitive", "math", "routing", "switch", "logic"],
}

# Priority for CID usage
CID_PRIORITY = {
    "storyboard": "HIGH",
    "image_still": "HIGH",
    "video_cine": "HIGH",
    "dubbing_audio": "HIGH",
    "restoration": "HIGH",
    "three_d": "HIGH",
    "utility": "MEDIUM",
    "unknown": "LOW",
}

# Family -> recommended instance port
FAMILY_PORT = {
    "storyboard": 8188,
    "image_still": 8188,
    "video_cine": 8189,
    "dubbing_audio": 8190,
    "restoration": 8191,
    "three_d": 8192,
    "utility": 8188,
}

OUTPUT_DIRS_CREATED = set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_dir(path: Path):
    if path not in OUTPUT_DIRS_CREATED:
        path.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIRS_CREATED.add(path)


def safe_write(path: Path, content: str):
    ensure_dir(path.parent)
    path.write_text(content)


def fetch_json(url: str, timeout: int = 30) -> dict | None:
    try:
        result = subprocess.check_output(
            ["curl", "-sS", "--max-time", str(timeout), url],
            text=True, timeout=timeout + 5,
        )
        if not result.strip():
            return None
        return json.loads(result)
    except (subprocess.CalledProcessError, json.JSONDecodeError, OSError) as e:
        return None


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
        return json.loads(raw)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError, UnicodeError):
        # Try with latin-1 as fallback for binary-ish files
        try:
            return json.loads(path.read_text("latin-1"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def is_excluded(path: Path) -> bool:
    parts = path.parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    for pattern in EXCLUDE_FILE_PATTERNS:
        if pattern.search(path.name):
            return True
    # Exclude .venv* directories
    if any(p.startswith(".venv") for p in parts):
        return True
    # Exclude custom_nodes* directories from workflow search
    if "custom_nodes" in parts:
        return True
    # Exclude big non-workflow dirs
    if any(p in ("node_modules", "dist", "build", "ZIPs", "_archive", "OLD") for p in parts):
        return True
    return False


def classify_workflow_by_path(path: Path, class_types: list[str]) -> str:
    """Classify a workflow by its path and contained class_types."""
    path_str = str(path).lower()
    scores = defaultdict(int)

    # Score by path keywords
    for fam, keywords in FAMILY_KEYWORDS.items():
        for kw in keywords:
            if kw in path_str:
                scores[fam] += 3

    # Score by class_types
    for ct in class_types:
        ct_lower = ct.lower()
        for fam, keywords in FAMILY_KEYWORDS.items():
            for kw in keywords:
                if kw in ct_lower:
                    scores[fam] += 1

    if scores:
        best = max(scores, key=scores.get)
        if scores[best] >= 2:
            return best
    return "unknown"


_MODEL_INDEX: dict[str, list[Path]] | None = None


def _build_model_index() -> dict[str, list[Path]]:
    """Build an index of all model files: stem_lower -> [paths]."""
    index = {}
    exts = {".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx", ".pkl"}
    for root in MODEL_ROOTS:
        if not root.exists():
            continue
        # Walk top-level subdirs only (depth 1-2) for speed
        for subdir in root.iterdir():
            if not subdir.is_dir() or subdir.name.startswith("."):
                continue
            try:
                for fpath in subdir.rglob("*"):
                    if fpath.suffix.lower() in exts:
                        stem = fpath.stem.lower()
                        index.setdefault(stem, []).append(fpath)
            except (PermissionError, OSError):
                continue
    return index


def find_model_file(model_name: str) -> Path | None:
    """Fast model lookup using pre-built index."""
    global _MODEL_INDEX
    if _MODEL_INDEX is None:
        _MODEL_INDEX = _build_model_index()
    stem = Path(model_name).stem.lower()
    candidates = _MODEL_INDEX.get(stem, [])
    if candidates:
        return candidates[0]
    # Try partial match
    for idx_stem, paths in _MODEL_INDEX.items():
        if stem in idx_stem or idx_stem in stem:
            return paths[0]
    return None


def check_models(workflows: list[dict]) -> list[dict]:
    """Check model availability using pre-built index."""
    global _MODEL_INDEX
    t0 = time.monotonic()
    if _MODEL_INDEX is None:
        print("  Building model index...", flush=True)
        _MODEL_INDEX = _build_model_index()
        print(f"  Model index built: {len(_MODEL_INDEX)} unique stems in {time.monotonic()-t0:.1f}s", flush=True)

    all_models = []
    for wf in workflows:
        for m in wf.get("models", []):
            if not m:
                continue
            found = find_model_file(m)
            all_models.append({
                "model": m,
                "workflow": str(wf["path"]),
                "found": found is not None,
                "found_path": str(found) if found else None,
            })
    return all_models


# ---------------------------------------------------------------------------
# Workflow discovery (JSON files)
# ---------------------------------------------------------------------------

def discover_workflows() -> list[dict]:
    """Find all ComfyUI workflow JSON files using targeted glob walks."""
    workflows = []
    seen = set()

    for search_root, max_depth in WORKFLOW_SEARCH_PATHS:
        if not search_root.exists():
            continue
        t0 = time.monotonic()
        count = 0
        for fpath in _walk_json_depth(search_root, max_depth):
            if is_excluded(fpath):
                continue
            real = fpath.resolve()
            if str(real) in seen:
                continue
            seen.add(str(real))
            try:
                rel = str(real.relative_to(search_root))
            except ValueError:
                rel = str(real)
            count += 1
            workflows.append({
                "path": real,
                "relative_path": rel,
                "size_bytes": real.stat().st_size,
            })
        t1 = time.monotonic()
        print(f"  {search_root.name}: {count} files in {t1-t0:.1f}s", flush=True)

    return workflows


def _walk_json_depth(root: Path, max_depth: int):
    """Yield .json files from root up to max_depth levels deep."""
    if max_depth == 0:
        yield from root.glob("*.json")
        return
    yield from root.glob("*.json")
    for d in range(1, max_depth + 1):
        pat = "/".join(["*"] * d) + "/*.json"
        try:
            yield from root.glob(pat)
        except (PermissionError, OSError):
            continue


# ---------------------------------------------------------------------------
# Image-based workflow extraction
# ---------------------------------------------------------------------------

def discover_images() -> list[Path]:
    """Find PNG/WebP images in specific directories."""
    images = []
    seen = set()
    for dir_str in IMAGE_SEARCH_DIRS:
        root = Path(dir_str)
        if not root.exists():
            continue
        t0 = time.monotonic()
        try:
            entries = os.listdir(root)
        except (PermissionError, OSError) as e:
            print(f"  [WARN] Failed to list {root}: {e}", flush=True)
            continue
        count = 0
        for name in entries:
            if not name.lower().endswith((".png", ".webp")):
                continue
            if "_thumb" in name.lower():
                continue
            fpath = root / name
            try:
                if os.path.getsize(fpath) < 1024:
                    continue
            except OSError:
                continue
            images.append(fpath)
            count += 1
        t1 = time.monotonic()
        print(f"  {root.name}: {count} images in {t1-t0:.1f}s", flush=True)
    images.sort()
    return images


def extract_workflow_from_image(image_path: Path) -> dict | None:
    """Try to extract embedded workflow JSON from PNG/WebP metadata."""
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            info = img.info
    except Exception:
        return None

    workflow_keys = [k for k in info.keys() if k.lower() in (
        "workflow", "prompt", "parameters", "comfy", "comfyui"
    )]
    if not workflow_keys:
        return None

    result = {
        "image_path": str(image_path),
        "metadata_keys": list(info.keys()),
        "workflow_json": None,
        "prompt_json": None,
        "class_types": [],
        "models": [],
        "format": "embedded",
        "family": "unknown",
        "priority": "LOW",
        "error": None,
    }

    for key in workflow_keys:
        raw = info.get(key)
        if not isinstance(raw, str):
            continue
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                if key.lower() in ("workflow", "comfy", "comfyui"):
                    result["workflow_json"] = parsed
                elif key.lower() in ("prompt", "parameters"):
                    result["prompt_json"] = parsed
        except (json.JSONDecodeError, ValueError):
            continue

    source = result.get("workflow_json") or result.get("prompt_json")
    if source and isinstance(source, dict):
        ct, models, fmt = extract_class_types_from_dict(source)
        result["class_types"] = sorted(set(ct))
        result["models"] = sorted(set(models))
        result["family"] = classify_workflow_by_path(image_path, ct)
        result["priority"] = CID_PRIORITY.get(result["family"], "LOW")

    return result


# ---------------------------------------------------------------------------
# Workflow parsing
# ---------------------------------------------------------------------------

def extract_class_types_from_dict(data: dict) -> tuple[list[str], list[str], str]:
    """Extract class_types, models, and format from a dict (API or UI format)."""
    class_types = []
    models = []
    format_type = "unknown"

    # Try API format: dict keyed by string node IDs with "class_type"
    api_nodes = {}
    for key, val in data.items():
        if isinstance(val, dict) and "class_type" in val:
            api_nodes[key] = val

    if api_nodes:
        format_type = "api"
        for node_id, node_data in api_nodes.items():
            ct = node_data.get("class_type", "")
            class_types.append(ct)
            inputs = node_data.get("inputs", {})
            for inp_name, inp_val in inputs.items():
                if isinstance(inp_val, str) and any(
                    ext in inp_val.lower()
                    for ext in [".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx"]
                ):
                    models.append(inp_val)
                if isinstance(inp_val, str) and inp_name.lower() in (
                    "ckpt_name", "checkpoint", "model_name", "lora_name",
                    "vae_name", "control_net_name", "filename_prefix",
                    "file_name"
                ):
                    models.append(inp_val)

    # Try UI format: "nodes" list with "type" key
    if not class_types:
        nodes_list = data.get("nodes", data.get("workflow", {}).get("nodes", []))
        if nodes_list and isinstance(nodes_list, list):
            format_type = "ui"
            for node in nodes_list:
                ct = node.get("type", "")
                class_types.append(ct)
                widgets = node.get("widgets_values", [])
                for wv in widgets:
                    if isinstance(wv, str) and any(
                        ext in wv.lower() for ext in
                        [".safetensors", ".ckpt", ".pt", ".pth"]
                    ):
                        models.append(wv)

    # Try prompt wrapper
    if not class_types:
        prompt = data.get("prompt", data)
        if isinstance(prompt, dict):
            for key, val in prompt.items():
                if isinstance(val, dict) and "class_type" in val:
                    class_types.append(val["class_type"])
                    if format_type == "unknown":
                        format_type = "api"

    return class_types, models, format_type


def parse_workflow(wf: dict) -> dict:
    """Parse a workflow JSON, detect format, extract class_types and models."""
    path = wf["path"]
    data = load_json(path)

    if isinstance(data, dict):
        class_types, models, format_type = extract_class_types_from_dict(data)
    elif isinstance(data, list):
        class_types = []
        models = []
        format_type = "array"
        for item in data:
            if isinstance(item, dict):
                ct = item.get("class_type", item.get("type", ""))
                if ct:
                    class_types.append(ct)
        if not class_types:
            format_type = "invalid"
        else:
            class_types = list(set(class_types))
    else:
        class_types = []
        models = []
        format_type = "invalid"

    wf["format"] = format_type
    wf["class_types"] = sorted(set(class_types))
    wf["models"] = sorted(set(models))
    wf["error"] = None if class_types else ("unparseable" if format_type == "invalid" else "no nodes detected")
    wf["family"] = classify_workflow_by_path(path, class_types)
    wf["priority"] = CID_PRIORITY.get(wf["family"], "LOW")
    return wf


# ---------------------------------------------------------------------------
# Instance object_info loader
# ---------------------------------------------------------------------------

def load_instance_object_info() -> dict:
    """Load object_info for each port from raw files or fresh fetch."""
    instance_info = {}
    for port, short_name, long_name in PORTS:
        raw_file = COMFYUI_1A_RAW / f"object_info_{port}.json"
        obj_info = load_json(raw_file)
        if not obj_info:
            print(f"  [INFO] Fetching object_info from :{port}...", flush=True)
            obj_info = fetch_json(f"http://127.0.0.1:{port}/object_info")

        if obj_info:
            instance_info[port] = {
                "object_info": obj_info,
                "class_types": set(obj_info.keys()),
                "instance": short_name,
            }
            if raw_file:
                safe_write(raw_file, json.dumps(obj_info, indent=2))
        else:
            print(f"  [WARN] No object_info for :{port}", file=sys.stderr)
            instance_info[port] = {
                "object_info": {},
                "class_types": set(),
                "instance": short_name,
            }
    return instance_info


# ---------------------------------------------------------------------------
# Custom nodes mapping per instance
# ---------------------------------------------------------------------------

def map_custom_nodes() -> dict:
    """Scan custom_nodes directories per instance."""
    instance_nodes: dict[int, list[dict]] = defaultdict(list)

    for port, custom_dir in INSTANCE_CUSTOM_NODES_DIRS.items():
        if not custom_dir.exists():
            continue
        for child in sorted(custom_dir.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith(".") or child.name == "__pycache__":
                continue
            node_info = {
                "name": child.name,
                "path": str(child),
                "git_remote": None,
                "git_branch": None,
                "has_requirements": (child / "requirements.txt").exists(),
                "instances": [port],
            }
            git_dir = child / ".git"
            if git_dir.exists():
                try:
                    remote = subprocess.check_output(
                        ["git", "-C", str(child), "remote", "-v"],
                        text=True, stderr=subprocess.DEVNULL, timeout=10
                    )
                    for line in remote.strip().split("\n"):
                        if "(fetch)" in line:
                            node_info["git_remote"] = line.split("\t")[1].split()[0]
                            break
                    branch = subprocess.check_output(
                        ["git", "-C", str(child), "rev-parse", "--abbrev-ref", "HEAD"],
                        text=True, stderr=subprocess.DEVNULL, timeout=5
                    )
                    node_info["git_branch"] = branch.strip()
                except (subprocess.CalledProcessError, OSError):
                    pass
            instance_nodes[port].append(node_info)

    # Cross-instance merge
    all_by_name = defaultdict(list)
    for port, nodes in instance_nodes.items():
        for node in nodes:
            all_by_name[node["name"]].append(port)
    for port, nodes in instance_nodes.items():
        for node in nodes:
            node["all_instances"] = sorted(all_by_name[node["name"]])

    return dict(instance_nodes)


def scan_g_hub_custom_nodes() -> list[dict]:
    """Scan G: hub custom_nodes_repo_real."""
    hub_nodes = []
    if not G_HUB_CUSTOM_NODES.exists():
        return hub_nodes
    for child in sorted(G_HUB_CUSTOM_NODES.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        info = {
            "name": child.name,
            "path": str(child),
            "git_remote": None,
            "has_requirements": (child / "requirements.txt").exists(),
        }
        git_dir = child / ".git"
        if git_dir.exists():
            try:
                remote = subprocess.check_output(
                    ["git", "-C", str(child), "remote", "-v"],
                    text=True, stderr=subprocess.DEVNULL, timeout=10
                )
                for line in remote.strip().split("\n"):
                    if "(fetch)" in line:
                        info["git_remote"] = line.split("\t")[1].split()[0]
                        break
            except (subprocess.CalledProcessError, OSError):
                pass
        hub_nodes.append(info)
    return hub_nodes


# ---------------------------------------------------------------------------
# Cross-reference
# ---------------------------------------------------------------------------

def cross_reference(workflows: list[dict],
                    instance_info: dict,
                    custom_nodes: dict) -> list[dict]:
    """For each workflow, compute missing nodes per instance."""
    results = []
    node_catalog = build_node_catalog(instance_info, custom_nodes)

    for wf in workflows:
        if wf.get("error"):
            continue
        required = set(wf["class_types"])
        if not required:
            continue

        entry = {
            "path": str(wf["path"]),
            "relative_path": wf.get("relative_path", ""),
            "family": wf.get("family", "unknown"),
            "priority": wf.get("priority", "LOW"),
            "format": wf.get("format", "unknown"),
            "n_required_nodes": len(required),
            "required_nodes": sorted(required),
            "models": wf.get("models", []),
            "per_instance": {},
            "best_instance": None,
            "best_missing": 999,
        }

        for port, short_name, long_name in PORTS:
            info = instance_info.get(port, {})
            available = info.get("class_types", set())
            missing = required - available
            missing_list = sorted(missing)

            resolved = []
            external = []
            for node in missing_list:
                src = node_catalog.get(node, {})
                if src:
                    resolved.append({"node": node, "available_in": src.get("instances", []),
                                     "local_package": src.get("package")})
                else:
                    external.append(node)

            entry["per_instance"][port] = {
                "available": len(required - missing),
                "missing_count": len(missing),
                "missing_nodes": missing_list,
                "missing_resolved": resolved,
                "missing_external": external,
            }

            if len(missing) < entry["best_missing"]:
                entry["best_missing"] = len(missing)
                entry["best_instance"] = port

        if entry["best_instance"] is not None:
            best_data = entry["per_instance"][entry["best_instance"]]
            if best_data["missing_count"] == 0:
                entry["diagnostic"] = "GO"
            elif best_data["missing_count"] <= 5:
                entry["diagnostic"] = "WARNING"
            else:
                entry["diagnostic"] = "NO-GO"
        else:
            entry["diagnostic"] = "NO-GO"

        results.append(entry)

    return results


def build_node_catalog(instance_info: dict,
                       custom_nodes: dict) -> dict:
    """Build a global catalog: node_name -> {instances, package}."""
    catalog = defaultdict(lambda: {"instances": [], "package": None})
    for port, info in instance_info.items():
        for ct in info.get("class_types", set()):
            catalog[ct]["instances"].append(port)
    return dict(catalog)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_reports(workflows: list[dict],
                     parsed: list[dict],
                     cross_results: list[dict],
                     model_results: list[dict],
                     custom_nodes: dict,
                     hub_nodes: list[dict],
                     instance_info: dict):
    """Generate the markdown reports."""
    now = datetime.now()

    # ==============================
    # Cross-check report
    # ==============================
    lines = [
        "# ComfyUI Workflow Cross-Check Audit",
        "",
        f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Script:** `scripts/dev/audit_comfyui_workflow_crosscheck.py`",
        "",
        "## Executive Summary",
        "",
    ]

    total_wf = len(parsed)
    valid_wf = [w for w in parsed if not w.get("error")]
    invalid_wf = [w for w in parsed if w.get("error")]
    high_wf = [w for w in valid_wf if w.get("priority") == "HIGH"]
    med_wf = [w for w in valid_wf if w.get("priority") == "MEDIUM"]
    low_wf = [w for w in valid_wf if w.get("priority") == "LOW"]

    lines.append(f"- **Total workflows found:** {total_wf}")
    lines.append(f"- **Valid (parsed successfully):** {len(valid_wf)}")
    lines.append(f"- **Invalid/unparseable:** {len(invalid_wf)}")
    lines.append(f"- **HIGH priority for CID:** {len(high_wf)}")
    lines.append(f"- **MEDIUM priority:** {len(med_wf)}")
    lines.append(f"- **LOW priority:** {len(low_wf)}")
    lines.append("")

    # Family distribution
    lines.append("### Workflows by Family")
    lines.append("")
    fam_count = defaultdict(int)
    for w in valid_wf:
        fam_count[w.get("family", "unknown")] += 1
    lines.append("| Family | Count |")
    lines.append("|--------|------:|")
    for fam in sorted(fam_count, key=lambda f: -fam_count[f]):
        lines.append(f"| {fam} | {fam_count[fam]} |")
    lines.append("")

    # Per-instance cross-reference summary
    lines.append("## Cross-Reference: Workflows vs Instances")
    lines.append("")
    lines.append("### Best Instance per Workflow")
    lines.append("")
    lines.append("| Workflow | Family | Priority | Nodes Req. | Best Instance | Missing | Diag |")
    lines.append("|----------|--------|----------|-----------|---------------|--------|------|")
    for cr in cross_results[:50]:
        lines.append(
            f"| {Path(cr['path']).name} | {cr['family']} | {cr['priority']} | "
            f"{cr['n_required_nodes']} | :{cr['best_instance']} | "
            f"{cr['best_missing']} | {cr['diagnostic']} |"
        )
    if len(cross_results) > 50:
        lines.append(f"| *... and {len(cross_results)-50} more* | | | | | | |")
    lines.append("")

    # Aggregate by instance
    lines.append("### Aggregate Missing Nodes per Instance")
    lines.append("")
    instance_missing = defaultdict(int)
    instance_external = defaultdict(set)
    for cr in cross_results:
        for port, data in cr["per_instance"].items():
            instance_missing[port] += data["missing_count"]
            for ext in data["missing_external"]:
                instance_external[port].add(ext)

    lines.append("| Instance | Total Missing | External Nodes |")
    lines.append("|----------|-------------:|----------------|")
    for port, short_name, long_name in PORTS:
        ext_count = len(instance_external.get(port, set()))
        lines.append(f"| :{port} {short_name} | {instance_missing.get(port, 0)} | {ext_count} |")
    lines.append("")

    # External nodes that need lookup
    all_external = set()
    for port, nodes in instance_external.items():
        all_external.update(nodes)
    if all_external:
        lines.append("### Nodes Requiring External Installation")
        lines.append("")
        lines.append("These nodes are not found in any instance's object_info nor in local custom_nodes:")
        lines.append("")
        for node in sorted(all_external)[:50]:
            lines.append(f"- `{node}`")
        lines.append("")

    # Models
    lines.append("## Model Availability")
    lines.append("")
    found_models = sum(1 for m in model_results if m["found"])
    missing_models = sum(1 for m in model_results if not m["found"])
    lines.append(f"- **Models referenced in workflows:** {len(model_results)}")
    lines.append(f"- **Found:** {found_models}")
    lines.append(f"- **Missing:** {missing_models}")
    lines.append("")
    if missing_models:
        lines.append("### Missing Models")
        lines.append("")
        for m in model_results:
            if not m["found"]:
                lines.append(f"- `{m['model']}` (from `{Path(m['workflow']).name}`)")
        lines.append("")

    # Custom nodes per instance
    lines.append("## Custom Nodes per Instance")
    lines.append("")
    for port, short_name, long_name in PORTS:
        nodes = custom_nodes.get(port, [])
        lines.append(f"### :{port} — {long_name} ({len(nodes)} custom nodes)")
        lines.append("")
        for n in nodes[:20]:
            git_info = f" | git: {n.get('git_remote', 'none')}" if n.get("git_remote") else ""
            req_info = " | has requirements.txt" if n.get("has_requirements") else ""
            lines.append(f"- **{n['name']}**{git_info}{req_info}")
        if len(nodes) > 20:
            lines.append(f"  *... and {len(nodes)-20} more*")
        lines.append("")

    # G: hub custom nodes
    lines.append("### G: Hub Custom Nodes Repository")
    lines.append("")
    for hn in hub_nodes:
        git_info = f" | git: {hn.get('git_remote', 'none')}" if hn.get("git_remote") else ""
        lines.append(f"- **{hn['name']}**{git_info}")
    lines.append("")

    # Workflow detail (most important ones)
    lines.append("## Key Workflow Details")
    lines.append("")
    for cr in cross_results:
        if cr["priority"] != "HIGH":
            continue
        lines.append(f"### {Path(cr['path']).name}")
        lines.append(f"- **Family:** {cr['family']}")
        lines.append(f"- **Format:** {cr['format']}")
        lines.append(f"- **Required nodes:** {cr['n_required_nodes']}")
        lines.append(f"- **Best instance:** :{cr['best_instance']} (missing {cr['best_missing']})")
        for port, short_name, long_name in PORTS:
            pd = cr["per_instance"][port]
            if pd["missing_external"]:
                lines.append(f"  - :{port}: {pd['missing_count']} missing "
                             f"({len(pd['missing_external'])} external: "
                             f"{', '.join(pd['missing_external'][:5])})")
            else:
                lines.append(f"  - :{port}: {pd['missing_count']} missing")
        lines.append("")

    safe_write(REPORT_PATH, "\n".join(lines))
    print(f"\nReport: {REPORT_PATH}")

    # ==============================
    # Install plan
    # ==============================
    plan_lines = [
        "# ComfyUI Missing Nodes Install Plan",
        "",
        f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source:** COMFYUI.1B cross-check audit",
        "",
        "## Rules",
        "",
        "1. **Do NOT execute any command in this document.**",
        "2. This is a planning document for COMFYUI.1C controlled installation.",
        "3. Each installation must have a backup and rollback plan.",
        "4. Prefer local sources (G: hub, other instance) before git clone.",
        "",
        "## Missing Nodes Requiring Installation",
        "",
        "| Missing Node | Workflow | Recommended Instance | Local Source | External Source Needed | Risk |",
        "|-------------|----------|--------------------|-------------|----------------------|------|",
    ]

    # Generate rows
    install_rows = []
    seen_install = set()
    for cr in cross_results:
        if cr["priority"] not in ("HIGH", "MEDIUM"):
            continue
        for port, short_name, long_name in PORTS:
            pd = cr["per_instance"][port]
            for ext in pd["missing_external"]:
                if ext in seen_install:
                    continue
                seen_install.add(ext)
                # Try to find in hub
                hub_match = None
                for hn in hub_nodes:
                    if ext.lower() in hn["name"].lower():
                        hub_match = hn["name"]
                        break
                # Try to find in another instance
                cross_instance = []
                for other_port, other_nodes in custom_nodes.items():
                    if other_port == port:
                        continue
                    for on in other_nodes:
                        if ext.lower() in on["name"].lower():
                            cross_instance.append(f":{other_port} {on['name']}")
                            break
                local = hub_match or (cross_instance[0] if cross_instance else "none")
                ext_needed = "no" if hub_match or cross_instance else "YES"
                risk = "low" if hub_match else ("medium" if cross_instance else "high")
                install_rows.append(
                    f"| `{ext}` | {Path(cr['path']).name} | :{port} {short_name} | "
                    f"{local} | {ext_needed} | {risk} |"
                )

    if install_rows:
        plan_lines.extend(install_rows[:100])
    else:
        plan_lines.append("| *No external nodes found* | | | | | |")
    plan_lines.append("")

    safe_write(INSTALL_PLAN_PATH, "\n".join(plan_lines))
    print(f"Install plan: {INSTALL_PLAN_PATH}")


def embed_report(embedded_workflows: list[dict],
                 instance_info: dict,
                 cross_results: list[dict]):
    """Generate embedded workflow report."""
    now = datetime.now()
    embed_path = RAW_DIR.parent / "comfyui_embedded_workflows_from_images_20260521.md"

    lines = [
        "# ComfyUI Embedded Workflows from Images",
        "",
        f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
    ]

    valid_embed = [e for e in embedded_workflows if e.get("class_types")]
    total_images = len(embedded_workflows)  # all images with any metadata
    lines.append(f"- **Images with ComfyUI metadata:** {total_images}")
    lines.append(f"- **Valid embedded workflows extracted:** {len(valid_embed)}")
    lines.append("")

    if valid_embed:
        # Family distribution
        fam_count = defaultdict(int)
        for e in valid_embed:
            fam_count[e.get("family", "unknown")] += 1
        lines.append("### By Family")
        lines.append("")
        lines.append("| Family | Count |")
        lines.append("|--------|------:|")
        for fam in sorted(fam_count, key=lambda f: -fam_count[f]):
            lines.append(f"| {fam} | {fam_count[fam]} |")
        lines.append("")

        # Most useful for CID
        cid = [e for e in valid_embed if e.get("priority") in ("HIGH", "MEDIUM")]
        lines.append(f"### Most Useful for CID ({len(cid)} workflows)")
        lines.append("")
        for e in cid[:20]:
            lines.append(f"- `{e['image_path']}`")
            lines.append(f"  - Family: {e['family']}, Priority: {e['priority']}")
            lines.append(f"  - Class types ({len(e['class_types'])}): {', '.join(e['class_types'][:10])}")
            lines.append(f"  - Models: {', '.join(e['models'][:5])}")
            lines.append("")

        # Cross-ref with instances
        lines.append("### Cross-Reference with Instances")
        lines.append("")
        for e in cid:
            required = set(e["class_types"])
            lines.append(f"#### {Path(e['image_path']).name}")
            lines.append(f"- **Family:** {e['family']}")
            lines.append(f"- **Required nodes:** {len(required)}")
            for port, short_name, long_name in PORTS:
                info = instance_info.get(port, {})
                available = info.get("class_types", set())
                missing = required - available
                ext_missing = [m for m in sorted(missing)
                               if m not in available]
                if not missing:
                    lines.append(f"  - :{port}: **GO** — all nodes available")
                else:
                    lines.append(f"  - :{port}: {len(missing)} missing "
                                 f"({', '.join(sorted(missing)[:8])})")
            lines.append("")

    safe_write(embed_path, "\n".join(lines))
    print(f"Embedded workflow report: {embed_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== AUDIT MAIN STARTING ===", flush=True)
    now = datetime.now()
    print("=" * 70)
    print("ComfyUI Workflow Cross-Check Audit (COMFYUI.1B)")
    print(f"Started: {now.isoformat()}")
    print("=" * 70)

    ensure_dir(RAW_DIR)

    # Step 1: Discover workflows
    print("\n[1/7] Discovering workflows...", flush=True)
    raw_workflows = discover_workflows()
    print(f"  Found {len(raw_workflows)} JSON files")

    # Step 2: Discover images with embedded workflows
    print("\n[2/7] Discovering images with embedded ComfyUI metadata...", flush=True)
    try:
        raw_images = discover_images()
        print(f"  Found {len(raw_images)} candidate images", flush=True)
    except Exception as e:
        print(f"  [WARN] Image discovery failed: {e}", flush=True)
        raw_images = []

    embedded_workflows = []
    img_scan_count = 0
    for img_path in raw_images:
        try:
            result = extract_workflow_from_image(img_path)
        except Exception as e:
            print(f"  [WARN] Failed to process {img_path}: {e}", flush=True)
            continue
        img_scan_count += 1
        if result and result.get("class_types"):
            embedded_workflows.append(result)
            # Save extracted workflow files
            img_hash = hashlib.md5(str(img_path).encode()).hexdigest()[:12]
            ext_dir = RAW_DIR.parent / "extracted_from_images"
            ext_dir.mkdir(parents=True, exist_ok=True)
            if result.get("workflow_json"):
                safe_write(ext_dir / f"extracted_{img_hash}_workflow.json",
                           json.dumps(result["workflow_json"], indent=2))
            if result.get("prompt_json"):
                safe_write(ext_dir / f"extracted_{img_hash}_prompt.json",
                           json.dumps(result["prompt_json"], indent=2))
            safe_write(ext_dir / f"extracted_{img_hash}_meta.json",
                       json.dumps({
                           "image_path": result["image_path"],
                           "metadata_keys": result["metadata_keys"],
                           "class_types": result["class_types"],
                           "models": result["models"],
                           "family": result["family"],
                       }, indent=2))
        if img_scan_count % 100 == 0:
            print(f"  Scanned {img_scan_count} images, found {len(embedded_workflows)} with metadata...")

    print(f"  Embedded workflows found in images: {len(embedded_workflows)}")

    # Step 3: Parse and classify JSON workflows
    print("\n[3/7] Parsing and classifying JSON workflows...", flush=True)
    parsed = []
    for i, wf in enumerate(raw_workflows):
        parse_workflow(wf)
        parsed.append(wf)
        if (i + 1) % 100 == 0:
            print(f"  Parsed {i+1}/{len(raw_workflows)}...", flush=True)

    # Merge embedded workflows into parsed list
    for ew in embedded_workflows:
        parsed.append({
            "path": Path(ew["image_path"]),
            "relative_path": str(Path(ew["image_path"])),
            "size_bytes": Path(ew["image_path"]).stat().st_size if Path(ew["image_path"]).exists() else 0,
            "format": ew.get("format", "embedded"),
            "class_types": ew.get("class_types", []),
            "models": ew.get("models", []),
            "error": ew.get("error"),
            "family": ew.get("family", "unknown"),
            "priority": ew.get("priority", "LOW"),
            "class_types_count": len(ew.get("class_types", [])),
            "models_count": len(ew.get("models", [])),
            "is_embedded": True,
        })

    valid = [w for w in parsed if not w.get("error")]
    invalid = [w for w in parsed if w.get("error")]
    print(f"  Valid: {len(valid)}, Invalid: {len(invalid)}")

    # Save raw workflow inventory
    safe_write(RAW_DIR / "workflow_inventory.json",
               json.dumps([{
                   "path": str(w["path"]),
                   "format": w.get("format"),
                   "family": w.get("family", "unknown"),
                   "priority": w.get("priority", "LOW"),
                   "class_types_count": len(w.get("class_types", [])),
                   "models_count": len(w.get("models", [])),
                   "error": w.get("error"),
               } for w in parsed], indent=2))
    print(f"  Raw inventory saved")

    # Step 4: Load instance object_info
    print("\n[4/7] Loading instance object_info...", flush=True)
    instance_info = load_instance_object_info()
    for port, short_name, long_name in PORTS:
        info = instance_info.get(port, {})
        print(f"  :{port} {short_name}: {len(info.get('class_types', set()))} node types", flush=True)

    # Step 5: Map custom nodes
    print("\n[5/7] Mapping custom nodes...", flush=True)
    custom_nodes = map_custom_nodes()
    for port, short_name, long_name in PORTS:
        print(f"  :{port} {short_name}: {len(custom_nodes.get(port, []))} custom nodes", flush=True)
    hub = scan_g_hub_custom_nodes()
    print(f"  G: hub repos: {len(hub)}", flush=True)

    # Step 6: Cross-reference
    print("\n[6/7] Cross-referencing workflows vs instances...", flush=True)
    cross_results = cross_reference(valid, instance_info, custom_nodes)

    # Summarize cross-ref
    go = sum(1 for c in cross_results if c.get("diagnostic") == "GO")
    warn = sum(1 for c in cross_results if c.get("diagnostic") == "WARNING")
    nogo = sum(1 for c in cross_results if c.get("diagnostic") == "NO-GO")
    print(f"  GO: {go}, WARNING: {warn}, NO-GO: {nogo} (best-instance)", flush=True)

    # Step 7: Check models
    print("\n[7/7] Checking models...", flush=True)
    model_results = check_models(valid)
    found = sum(1 for m in model_results if m["found"])
    missing = sum(1 for m in model_results if not m["found"])
    print(f"  Models referenced: {len(model_results)}, Found: {found}, Missing: {missing}", flush=True)

    # Generate reports
    print("\nGenerating reports...")
    generate_reports(raw_workflows, parsed, cross_results, model_results,
                     custom_nodes, hub, instance_info)

    # Generate embedded workflow report
    embed_report(embedded_workflows, instance_info, cross_results)

    # CLI summary
    embedded_valid = len([e for e in embedded_workflows if e.get("class_types")])
    print(f"\n{'=' * 70}")
    print(f"{'Metric':<40} {'Value':<10}")
    print(f"{'─' * 40} {'─' * 10}")
    print(f"{'Total JSON files scanned':<40} {len(raw_workflows):<10}")
    print(f"{'Total images scanned':<40} {img_scan_count:<10}")
    print(f"{'Embedded workflows found':<40} {embedded_valid:<10}")
    print(f"{'Valid workflows (JSON+embedded)':<40} {len(valid):<10}")
    print(f"{'Invalid/unparseable':<40} {len(invalid):<10}")
    print(f"{'HIGH priority workflows':<40} {len([w for w in valid if w.get('priority')=='HIGH']):<10}")
    print(f"{'Cross-ref GO (best inst)':<40} {go:<10}")
    print(f"{'Cross-ref WARNING':<40} {warn:<10}")
    print(f"{'Cross-ref NO-GO':<40} {nogo:<10}")
    print(f"{'Models found':<40} {found:<10}")
    print(f"{'Models missing':<40} {missing:<10}")

    print(f"\nFiles written:")
    print(f"  {REPORT_PATH}")
    print(f"  {INSTALL_PLAN_PATH}")
    print(f"  {RAW_DIR}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
