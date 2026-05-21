#!/usr/bin/env python3
"""Controlled installation of missing ComfyUI custom nodes — COMFYUI.1C.

Reads the install plan from COMFYUI.1B, groups missing nodes by instance,
maps them to known custom_nodes packages, creates backups, and performs
controlled installation with dry-run, install, and rollback modes.

Usage:
  python3 scripts/dev/install_comfyui_missing_nodes_controlled.py --dry-run
  python3 scripts/dev/install_comfyui_missing_nodes_controlled.py --install
  python3 scripts/dev/install_comfyui_missing_nodes_controlled.py --rollback
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ROOT = Path("/opt/SERVICIOS_CINE")
SCRIPTS = ROOT / "scripts" / "dev"
DOCS_VALIDATION = ROOT / "docs" / "validation"

INSTALL_PLAN_PATH = DOCS_VALIDATION / "comfyui_missing_nodes_install_plan_20260521.md"
INSTANCE_NODES_PATH = DOCS_VALIDATION / "comfyui_installation_plan_review_20260521" / "_instance_custom_nodes.json"

MAIN_COMFYUI = Path("/home/harliesound/ai/ComfyUI")
MAIN_VENV = MAIN_COMFYUI / ".venv"
MAIN_PYTHON = MAIN_VENV / "bin" / "python3"
MAIN_PIP = MAIN_VENV / "bin" / "pip"

INSTANCE_DIRS = {
    8188: Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-image"),
    8189: Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-video_cine"),
    8190: Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-dubbing_audio"),
    8191: Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-restoration"),
    8192: Path("/home/harliesound/ai/ComfyUI_instances/ComfyUI-3D"),
}

INSTANCE_VENV_NAMES = {
    8188: ".venv-image",
    8189: ".venv-video",
    8190: ".venv-dubbing",
    8191: ".venv-restoration",
    8192: ".venv-3d",
}

G_HUB_CUSTOM_NODES = Path("/mnt/g/COMFYUI_HUB/custom_nodes_repo_real")

PROFILES = {
    8188: ("image", Path("/home/harliesound/ai/ComfyUI_profiles/image")),
    8189: ("video_cine", Path("/home/harliesound/ai/ComfyUI_profiles/video_cine")),
    8190: ("dubbing_audio", Path("/home/harliesound/ai/ComfyUI_profiles/dubbing_audio")),
    8191: ("restoration", Path("/home/harliesound/ai/ComfyUI_profiles/restoration")),
    8192: ("3d", Path("/home/harliesound/ai/ComfyUI_profiles/3d")),
}

BACKUP_ROOT = ROOT / "OLD" / "comfyui_custom_nodes_backups" / "20260521"
LOG_PATH = DOCS_VALIDATION / "comfyui_installation_log_20260521.md"

ALLOWED_DEST_PORT = 8188
ALLOWED_COPY_PACKAGES = {
    "Comfyui_segformer_b2_clothes",
    "comfyui-fluxtrainer",
}
ALLOWED_PIP_PACKAGES = {
    "ComfyUI-GGUF",
    "Comfyui_segformer_b2_clothes",
    "comfy-mtb",
    "comfyui-easy-use",
    "comfyui-fluxtrainer",
    "comfyui-impact-pack",
    "comfyui-videohelpersuite",
    "comfyui_controlnet_aux",
    "comfyui_instantid",
    "efficiency-nodes-comfyui",
    "rgthree-comfy",
    "was-node-suite-comfyui",
}

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.I,
)

# Nodes that are part of core ComfyUI (should exist, not a custom_nodes issue)
CORE_NODES = {
    "Reroute",
    "Note",
    "Text box",
    "Textbox",
    "PrimitiveNode",
    "SaveText",
    "Int Literal",
    "String Literal",
    "Seed Generator",
    "UpscaleImage",
    "Preview_mask",
    "DF_Text_Box",
    "DF_Get_image_size",
    "AspectSize",
    "Seed Generator",
}

# Additional core/missing nodes
ADDITIONAL_CORE = [
    "preview_mask",  # WAS Suite node
]
CORE_NODES.update(ADDITIONAL_CORE)

# Nodes that map to packages already present in other instances
# Mapping: missing_node -> (package_name, git_url_or_None, needs_pip)
KNOWN_PACKAGES = {
    "Reroute (rgthree)": ("rgthree-comfy", None, True),
    "Label (rgthree)": ("rgthree-comfy", None, True),
    "Fast Groups Bypasser (rgthree)": ("rgthree-comfy", None, True),
    "Fast Bypasser (rgthree)": ("rgthree-comfy", None, True),
    "rgthree.ImageSwitch": ("rgthree-comfy", None, True),
    "rgthree.Int": ("rgthree-comfy", None, True),
    "GetNode": ("efficiency-nodes-comfyui", None, True),
    "SetNode": ("efficiency-nodes-comfyui", None, True),
    "Geometry Sphere (mtb)": ("comfy-mtb", None, True),
    "MarkdownNote": ("rgthree-comfy", None, True),
    "RandomNoise //Inspire": ("comfyui-impact-pack", None, True),
    "LoadImageListFromDir //Inspire": ("comfyui-impact-pack", None, True),
    "LoadPromptsFromFile //Inspire": ("comfyui-impact-pack", None, True),
    "UnzipPrompt //Inspire": ("comfyui-impact-pack", None, True),
    "CatVTONWrapper": ("ComfyUI-CatvtonFluxWrapper", None, True),
    "GroundingDinoModelLoader (segment anything)": ("comfyui-impact-pack", None, True),
    "GroundingDinoSAMSegment (segment anything)": ("comfyui-impact-pack", None, True),
    "SAMModelLoader (segment anything)": ("comfyui-segment-anything-2", None, False),
    "BNK_Unsampler": ("comfyui-impact-pack", None, True),
    "InpaintResize": ("comfyui-inpaint-nodes", None, True),
    "Load Styles CSV": ("was-node-suite-comfyui", None, True),
    "ApplyPulidFlux": ("comfyui_ipadapter_plus", None, False),
    "PulidFluxEvaClipLoader": ("comfyui_ipadapter_plus", None, False),
    "PulidFluxInsightFaceLoader": ("comfyui_ipadapter_plus", None, False),
    "PulidFluxModelLoader": ("comfyui_ipadapter_plus", None, False),
    "IPAdapterApply": ("comfyui_ipadapter_plus", None, False),
    "VHS_FramesToVideoWAudio": ("comfyui-videohelpersuite", None, True),
    "VHS_VideoToFramesWAudio": ("comfyui-videohelpersuite", None, True),
    "MultiAreaConditioning": ("comfyui-advanced-controlnet", None, False),
    "ImageSegmentationCustom": ("was-node-suite-comfyui", None, True),
    "ComfyUIStyler": ("sdxl_prompt_styler", None, False),
    "UltimateSDUpscale": ("comfyui-impact-pack", None, True),
    "CheckpointLoaderNF4": ("ComfyUI-GGUF", None, True),
    "AnimateDiffCombine": ("ComfyUI-AnimateDiff-Evolved", None, False),
    "AnimateDiffLoader": ("ComfyUI-AnimateDiff-Evolved", None, False),
    "AnimateDiffModuleLoader": ("ComfyUI-AnimateDiff-Evolved", None, False),
    "AnimateDiffSampler": ("ComfyUI-AnimateDiff-Evolved", None, False),
    "AnimateDiffSlidingWindowOptions": ("ComfyUI-AnimateDiff-Evolved", None, False),
    "FaceAnalysisModels": ("comfyui_instantid", None, True),
    "FaceEmbedDistance": ("comfyui_instantid", None, True),
    "OpenPosePreprocessor": ("comfyui_controlnet_aux", None, True),
    "PerturbedAttention": ("comfyui-easy-use", None, True),
    "smZ CLIPTextEncode": ("comfyui-custom-scripts", None, False),  # smZ nodes
    "LoraTagLoader": ("comfyui-easy-use", None, True),
    "Searge_Output_Node": ("comfyui-easy-use", None, True),
    "DiffusersCompelPromptEmbedding": ("comfyui-impact-pack", None, True),
    "DiffusersControlnetLoader": ("comfyui-impact-pack", None, True),
    "DiffusersControlnetUnit": ("comfyui-impact-pack", None, True),
    "DiffusersGenerator": ("comfyui-impact-pack", None, True),
    "DiffusersPipeline": ("comfyui-impact-pack", None, True),
    "DiffusersTextureInversionLoader": ("comfyui-impact-pack", None, True),
    "segformer_b2_clothes": ("Comfyui_segformer_b2_clothes", None, True),
    "FluxPromptGenerator": ("comfyui-easy-use", None, True),
    "ApplyFluxControlNet": ("ComfyUI_AdvancedRefluxControl", None, False),
    "LoadFluxControlNet": ("ComfyUI_AdvancedRefluxControl", None, False),
    "InstantX Flux Union ControlNet Loader": ("ComfyUI_AdvancedRefluxControl", None, False),
    "XlabsSampler": ("ComfyUI_AdvancedRefluxControl", None, False),
    "FluxTrainEnd": ("comfyui-fluxtrainer", None, True),
    "FluxTrainLoop": ("comfyui-fluxtrainer", None, True),
    "FluxTrainModelSelect": ("comfyui-fluxtrainer", None, True),
    "FluxTrainSave": ("comfyui-fluxtrainer", None, True),
    "FluxTrainValidate": ("comfyui-fluxtrainer", None, True),
    "FluxTrainValidationSettings": ("comfyui-fluxtrainer", None, True),
    "InitFluxLoRATraining": ("comfyui-fluxtrainer", None, True),
    "OptimizerConfig": ("comfyui-fluxtrainer", None, True),
    "TrainDatasetAdd": ("comfyui-fluxtrainer", None, True),
    "TrainDatasetGeneralConfig": ("comfyui-fluxtrainer", None, True),
    "UploadToHuggingFace": ("comfyui-fluxtrainer", None, True),
    "VisualizeLoss": ("comfyui-fluxtrainer", None, True),
    "SamplerTCD EulerA": ("comfyui-impact-pack", None, True),
    "TCDScheduler": ("comfyui-impact-pack", None, True),
}

# External git repos for packages not in any instance or G: hub
EXTERNAL_REPOS = {
    "ComfyUI-3D-Pack": "https://github.com/MrForExample/ComfyUI-3D-Pack.git",
    "ComfyUI-AnimateDiff-Evolved": "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git",
    "ComfyUI-IPAdapter-Flux": "https://github.com/ostris/ComfyUI-IPAdapter-Flux.git",
    "ComfyUI-GGUF": "https://github.com/city96/ComfyUI-GGUF.git",
    "ComfyUI-AdvancedRefluxControl": None,  # Placeholder - needs research
    "comfyui-fluxtrainer": "https://github.com/kijai/ComfyUI-FluxTrainer.git",
    "ComfyUI-CatvtonFluxWrapper": "https://github.com/huchenlei/ComfyUI-CatvtonFluxWrapper.git",
    "comfyui-segment-anything-2": "https://github.com/kijai/ComfyUI-SegmentAnything2.git",
    "Comfyui_segformer_b2_clothes": None,  # Already in 8189
}

# Nodes that should not be installed (UUIDs, non-nodes, etc.)
def is_uuid(s):
    return bool(UUID_RE.match(s))

def is_workflow_keyword(s):
    """Filter out workflow UI keywords that got parsed as nodes."""
    keywords = {"workflow>Prompt/Model/Clip/Vae Loader", "workflow/GROUP"}
    return s in keywords


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    log(f"Running: {' '.join(str(c) for c in cmd)}")
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 120)
    return subprocess.run(cmd, **kwargs)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def safe_write(path: Path, content: str):
    ensure_dir(path.parent)
    path.write_text(content)
    log(f"Wrote {path}")


def instance_venv_dir(port: int) -> Path:
    return INSTANCE_DIRS[port] / INSTANCE_VENV_NAMES[port]


def instance_python_bin(port: int) -> Path:
    candidates = [
        instance_venv_dir(port) / "bin" / "python3",
        instance_venv_dir(port) / "bin" / "python",
        MAIN_PYTHON,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No python binary found for instance :{port}")


def package_dir(port: int, pkg_name: str) -> Path:
    return PROFILES[port][1] / "custom_nodes" / pkg_name


def load_plan() -> list[dict]:
    lines = INSTALL_PLAN_PATH.read_text().split("\n")
    rows = []
    in_table = False
    for line in lines:
        if line.startswith("| Missing Node |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("| "):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                node = parts[1].strip("`")
                workflow = parts[2]
                instance_raw = parts[3]
                local_src = parts[4]
                ext_needed = parts[5]
                risk = parts[6].strip() if len(parts) > 6 else "high"
                port = 8188  # default
                if "8189" in instance_raw:
                    port = 8189
                elif "8190" in instance_raw:
                    port = 8190
                elif "8191" in instance_raw:
                    port = 8191
                elif "8192" in instance_raw:
                    port = 8192
                rows.append({
                    "node": node,
                    "workflow": workflow,
                    "port": port,
                    "local_source": local_src,
                    "external_needed": ext_needed,
                    "risk": risk,
                })
    log(f"Loaded {len(rows)} entries from install plan")
    return rows


def load_instance_nodes() -> dict:
    if INSTANCE_NODES_PATH.exists():
        data = json.loads(INSTANCE_NODES_PATH.read_text())
        return {int(k): v for k, v in data.items()}
    log("Instance nodes not cached, scanning...", "WARN")
    return {}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_node(node: str, package_from_workflow: str = "") -> dict:
    """Classify a single missing node and return its resolution info."""
    result = {
        "node": node,
        "is_uuid": False,
        "is_core": False,
        "is_workflow_keyword": False,
        "known_package": None,
        "package_name": None,
        "pkg_source": None,
        "needs_pip": False,
        "needs_external_clone": False,
        "exempt": False,
        "exempt_reason": "",
        "risk": "high",
    }

    if is_uuid(node):
        result["is_uuid"] = True
        result["exempt"] = True
        result["exempt_reason"] = "UUID (parsing artifact from API-format workflow)"
        result["risk"] = "low"
        return result

    if is_workflow_keyword(node):
        result["is_workflow_keyword"] = True
        result["exempt"] = True
        result["exempt_reason"] = "Workflow UI keyword, not a node"
        result["risk"] = "low"
        return result

    if node in CORE_NODES:
        result["is_core"] = True
        result["exempt"] = True
        result["exempt_reason"] = "Core ComfyUI node — may need version update or is missing from object_info"
        result["risk"] = "low"
        return result

    if node in KNOWN_PACKAGES:
        pkg_name, git_url, needs_pip = KNOWN_PACKAGES[node]
        result["known_package"] = True
        result["package_name"] = pkg_name
        result["needs_pip"] = needs_pip
        result["risk"] = "medium" if git_url is None else "high"
        return result

    result["exempt"] = True
    result["exempt_reason"] = "Unknown node type — requires manual investigation"
    result["risk"] = "high"
    return result


def resolve_package_source(pkg_name: str, instance_nodes: dict, target_port: int) -> dict:
    """Determine the best source for a package."""
    source = {
        "pkg_name": pkg_name,
        "source_type": "unknown",
        "source_path": None,
        "source_port": None,
        "in_g_hub": False,
        "in_other_instance": None,
        "in_target_instance": False,
        "has_requirements": False,
        "git_remote": None,
        "clone_url": None,
        "action": "unknown",
    }

    # Check G: hub
    gh_path = G_HUB_CUSTOM_NODES / pkg_name
    if gh_path.exists() and gh_path.is_dir():
        source["in_g_hub"] = True
        source["source_type"] = "g_hub"
        source["source_path"] = str(gh_path)
        source["has_requirements"] = (gh_path / "requirements.txt").exists()
        git_dir = gh_path / ".git"
        if git_dir.exists():
            try:
                r = subprocess.run(
                    ["git", "-C", str(gh_path), "remote", "-v"],
                    capture_output=True, text=True, timeout=10
                )
                source["git_remote"] = r.stdout.strip()[:200]
            except Exception:
                pass

    # Check target instance
    target_packages = instance_nodes.get(target_port, {})
    if pkg_name in target_packages:
        pkg_info = target_packages[pkg_name]
        source["in_target_instance"] = True
        source["source_type"] = "already_installed"
        source["source_path"] = str(PROFILES[target_port][1] / "custom_nodes" / pkg_name)
        source["has_requirements"] = pkg_info.get("has_requirements", False)
        # Check if pip deps are installed
        req_path = Path(source["source_path"]) / "requirements.txt"
        if req_path.exists():
            source["needs_pip_install"] = True
        else:
            source["needs_pip_install"] = False
        return source

    # Check other instances
    for port, (name, pdir) in PROFILES.items():
        if port == target_port:
            continue
        other_pkgs = instance_nodes.get(port, {})
        if pkg_name in other_pkgs:
            pkg_info = other_pkgs[pkg_name]
            source["source_port"] = port
            source["in_other_instance"] = port
            source["source_type"] = "cross_instance"
            source["source_path"] = str(pdir / "custom_nodes" / pkg_name)
            source["has_requirements"] = pkg_info.get("has_requirements", False)
            if pkg_info.get("git_remote"):
                source["git_remote"] = pkg_info["git_remote"][:200]
            return source

    # Check external repos
    if pkg_name in EXTERNAL_REPOS:
        clone_url = EXTERNAL_REPOS[pkg_name]
        if clone_url:
            source["source_type"] = "external_git"
            source["clone_url"] = clone_url
            source["action"] = "git_clone"
        else:
            source["source_type"] = "external_unknown"
            source["action"] = "research_needed"
        return source

    # Unknown source
    source["source_type"] = "unknown"
    source["action"] = "research_needed"
    return source


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def backup_instance(port: int, dry_run: bool = False) -> Path | None:
    name = PROFILES[port][0]
    cn_dir = PROFILES[port][1] / "custom_nodes"
    backup_name = f"{port}_{name}_custom_nodes_before.tar.gz"
    backup_path = BACKUP_ROOT / backup_name

    if not cn_dir.exists():
        log(f":{port} custom_nodes dir not found at {cn_dir}", "WARN")
        return None

    ensure_dir(BACKUP_ROOT)
    if dry_run:
        log(f"[DRY-RUN] Would backup {cn_dir} -> {backup_path}")
        return backup_path

    log(f"Backing up {cn_dir} -> {backup_path}...")
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(cn_dir, arcname=f"custom_nodes_{port}")
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        log(f"Backup created: {backup_path} ({size_mb:.1f} MB)")
        return backup_path
    except Exception as e:
        log(f"Backup failed: {e}", "ERROR")
        return None


def rollback_instance(port: int, dry_run: bool = False) -> bool:
    name = PROFILES[port][0]
    cn_dir = PROFILES[port][1] / "custom_nodes"
    backup_name = f"{port}_{name}_custom_nodes_before.tar.gz"
    backup_path = BACKUP_ROOT / backup_name

    if not backup_path.exists():
        log(f"No backup found for :{port}: {backup_path}", "ERROR")
        return False

    if dry_run:
        log(f"[DRY-RUN] Would restore {backup_path} -> {cn_dir}")
        return True

    # Remove current custom_nodes
    if cn_dir.exists():
        log(f"Removing current {cn_dir}...")
        shutil.rmtree(cn_dir)

    # Restore from backup
    log(f"Restoring {backup_path} -> {cn_dir}...")
    cn_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(backup_path, "r:gz") as tar:
        tar.extractall(cn_dir.parent)
    log(f"Rollback complete for :{port}")
    return True


# ---------------------------------------------------------------------------
# Installation actions
# ---------------------------------------------------------------------------

def install_from_g_hub(pkg_name: str, port: int, dry_run: bool = False) -> bool:
    src = G_HUB_CUSTOM_NODES / pkg_name
    dst = PROFILES[port][1] / "custom_nodes" / pkg_name
    if dry_run:
        log(f"[DRY-RUN] Would copy {src} -> {dst}")
        return True
    if dst.exists():
        log(f"  Already exists: {dst}, skipping")
        return True
    log(f"  Copying {src} -> {dst}...")
    shutil.copytree(src, dst, symlinks=True)
    # Install requirements if present
    req = dst / "requirements.txt"
    if req.exists():
        log(f"  Installing requirements for {pkg_name}...")
        r = run([str(MAIN_PIP), "install", "-r", str(req)])
        if r.returncode != 0:
            log(f"  Pip install failed: {r.stderr[:500]}", "ERROR")
            return False
        log(f"  Pip install OK")
    return True


def install_from_cross_instance(pkg_name: str, src_port: int, dst_port: int, dry_run: bool = False) -> bool:
    src = PROFILES[src_port][1] / "custom_nodes" / pkg_name
    dst = PROFILES[dst_port][1] / "custom_nodes" / pkg_name
    if dry_run:
        log(f"[DRY-RUN] Would copy from :{src_port} -> :{dst_port}: {pkg_name}")
        return True
    if dst.exists():
        log(f"  Already exists at destination: {dst}, skipping")
        return True
    log(f"  Copying from :{src_port} -> :{dst_port}: {pkg_name}...")
    shutil.copytree(src, dst, symlinks=True)
    return True


def install_from_git(pkg_name: str, clone_url: str, port: int, dry_run: bool = False) -> bool:
    dst = PROFILES[port][1] / "custom_nodes" / pkg_name
    if dry_run:
        log(f"[DRY-RUN] Would git clone {clone_url} -> {dst}")
        return True
    if dst.exists():
        log(f"  Already exists: {dst}, skipping")
        return True
    log(f"  Cloning {clone_url} -> {dst}...")
    r = run(["git", "clone", clone_url, str(dst)], timeout=300)
    if r.returncode != 0:
        log(f"  Git clone failed: {r.stderr[:500]}", "ERROR")
        return False
    # Install requirements
    req = dst / "requirements.txt"
    if req.exists():
        log(f"  Installing requirements for {pkg_name}...")
        r2 = run([str(MAIN_PIP), "install", "-r", str(req)])
        if r2.returncode != 0:
            log(f"  Pip install failed: {r2.stderr[:500]}", "ERROR")
            return False
        log(f"  Pip install OK")
    return True


def pip_install_requirements(pkg_name: str, port: int, dry_run: bool = False) -> bool:
    req = package_dir(port, pkg_name) / "requirements.txt"
    python_bin = instance_python_bin(port)
    if not req.exists():
        log(f"  No requirements.txt for {pkg_name}, skipping pip step")
        return True
    if dry_run:
        log(f"[DRY-RUN] Would run {python_bin} -m pip install -r {req}")
        return True
    log(f"  Installing requirements for {pkg_name} with :{port} python...")
    result = run([str(python_bin), "-m", "pip", "install", "-r", str(req)], timeout=900)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "")[:800]
        log(f"  Pip install failed for {pkg_name}: {err}", "ERROR")
        return False
    log(f"  Pip install OK for {pkg_name}")
    return True


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def analyze(plan_entries: list[dict], instance_nodes: dict) -> dict:
    """Full analysis of missing nodes per instance."""
    analysis = {
        "per_instance": defaultdict(lambda: {
            "candidates": [],
            "pip_deps": set(),
            "cross_instance_sources": set(),
            "external_needed": [],
            "exempt": [],
            "unknown": [],
        }),
        "summary": {
            "total_entries": len(plan_entries),
            "total_uuid": 0,
            "total_core": 0,
            "total_installable": 0,
            "total_unknown": 0,
        },
    }

    for entry in plan_entries:
        node = entry["node"]
        port = entry["port"]
        classification = classify_node(node)
        dest = analysis["per_instance"][port]

        if classification["exempt"]:
            dest["exempt"].append(classification)
            if classification["is_uuid"]:
                analysis["summary"]["total_uuid"] += 1
            if classification["is_core"]:
                analysis["summary"]["total_core"] += 1
            if classification.get("is_workflow_keyword"):
                analysis["summary"]["total_core"] += 1
            continue

        if classification["known_package"]:
            pkg_name = classification["package_name"]
            source = resolve_package_source(pkg_name, instance_nodes, port)
            entry["source"] = source
            dest["candidates"].append(entry)

            if source.get("has_requirements"):
                dest["pip_deps"].add(pkg_name)

            if source["source_type"] == "cross_instance":
                dest["cross_instance_sources"].add(source["source_port"])

            if source["source_type"] in ("external_git", "external_unknown", "unknown"):
                dest["external_needed"].append(entry)

            analysis["summary"]["total_installable"] += 1
        else:
            dest["unknown"].append(entry)
            analysis["summary"]["total_unknown"] += 1

    return analysis


def dry_run(analysis: dict):
    log("=" * 70)
    log("DRY RUN — No changes will be made")
    log("=" * 70)

    for port, (name, _) in sorted(PROFILES.items()):
        data = analysis["per_instance"][port]
        log(f"\n--- :{port} ({name}) ---")
        log(f"  Candidates: {len(data['candidates'])}")
        log(f"  Pip deps: {sorted(data['pip_deps'])}")
        log(f"  Cross-instance sources: {sorted(data['cross_instance_sources'])}")
        log(f"  External needed: {len(data['external_needed'])}")
        log(f"  Exempt (skip): {len(data['exempt'])}")
        log(f"  Unknown: {len(data['unknown'])}")

        if data["candidates"]:
            log(f"  Candidate nodes:")
            for c in data["candidates"]:
                src = c.get("source", {})
                st = src.get("source_type", "unknown")
                detail = f" -> {st}"
                if st == "g_hub":
                    detail += " (G: hub)"
                elif st == "cross_instance":
                    detail += f" (from :{src.get('source_port')})"
                elif st == "external_git":
                    detail += f" (git: {src.get('clone_url', '?')})"
                elif st == "already_installed":
                    pip_needed = src.get("needs_pip_install", False)
                    if pip_needed:
                        detail += " (dir exists, needs pip install)"
                    else:
                        detail += " (ready)"
                log(f"    - {c['node']}{detail}")

        if data["unknown"]:
            log(f"  Unknown (needs research):")
            for c in data["unknown"]:
                log(f"    - {c['node']} (from {c['workflow']})")

        if data["exempt"]:
            log(f"  Exempt:")
            for c in data["exempt"]:
                log(f"    - {c['node']}: {c['exempt_reason']}")

    s = analysis["summary"]
    log(f"\n--- Summary ---")
    log(f"  Total plan entries: {s['total_entries']}")
    log(f"  UUIDs (skip): {s['total_uuid']}")
    log(f"  Core nodes (skip): {s['total_core']}")
    log(f"  Installable candidates: {s['total_installable']}")
    log(f"  Unknown (research): {s['total_unknown']}")


def do_install(analysis: dict, dry_run_mode: bool = False):
    if dry_run_mode:
        return dry_run(analysis)

    log("=" * 70)
    log("INSTALL — Starting controlled installation")
    log("=" * 70)
    log(f"WARNING: {VENV_RISK['reason']}", "WARN")

    target_data = analysis["per_instance"][ALLOWED_DEST_PORT]
    other_candidates = {
        port: len(analysis["per_instance"][port]["candidates"])
        for port in PROFILES
        if port != ALLOWED_DEST_PORT and analysis["per_instance"][port]["candidates"]
    }
    if other_candidates:
        log(f"Unexpected candidates outside :{ALLOWED_DEST_PORT}: {other_candidates}", "ERROR")
        return False
    if target_data["external_needed"]:
        log("External sources detected in install plan; aborting by policy", "ERROR")
        return False

    copy_plan = {}
    for candidate in target_data["candidates"]:
        source = candidate.get("source", {})
        pkg_name = source.get("pkg_name")
        if source.get("source_type") == "cross_instance" and pkg_name:
            copy_plan[pkg_name] = source.get("source_port")

    if set(copy_plan) != ALLOWED_COPY_PACKAGES:
        log(f"Copy plan mismatch. Expected {sorted(ALLOWED_COPY_PACKAGES)}, got {sorted(copy_plan)}", "ERROR")
        return False
    if set(copy_plan.values()) != {8189}:
        log(f"Cross-instance source mismatch: {copy_plan}", "ERROR")
        return False

    pip_plan = set(target_data["pip_deps"])
    if pip_plan != ALLOWED_PIP_PACKAGES:
        log(f"Pip plan mismatch. Expected {sorted(ALLOWED_PIP_PACKAGES)}, got {sorted(pip_plan)}", "ERROR")
        return False

    log("\n[Step 1/3] Creating backups...")
    backups = {}
    for port in PROFILES:
        backup_path = backup_instance(port)
        if backup_path:
            backups[port] = backup_path
    log(f"  Backups created: {len(backups)}/{len(PROFILES)}")
    if len(backups) != len(PROFILES):
        log("Not all instances backed up — aborting", "ERROR")
        return False

    log("\n[Step 2/3] Copying approved packages to :8188...")
    copied_packages = []
    for pkg_name in sorted(copy_plan):
        success = install_from_cross_instance(pkg_name, 8189, ALLOWED_DEST_PORT)
        if not success:
            return False
        copied_packages.append(pkg_name)

    log("\n[Step 2b/3] Installing approved requirements in :8188 venv...")
    pip_installed = []
    for pkg_name in sorted(pip_plan):
        success = pip_install_requirements(pkg_name, ALLOWED_DEST_PORT)
        if not success:
            return False
        pip_installed.append(pkg_name)

    install_nodes = []
    for candidate in target_data["candidates"]:
        pkg_name = candidate.get("source", {}).get("pkg_name")
        if pkg_name in copied_packages or pkg_name in pip_installed:
            install_nodes.append(candidate["node"])

    log("\n[Step 3/3] Writing installation log...")
    log_content = [
        "# ComfyUI Controlled Installation Log",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Scope:** COMFYUI.1C real execution restricted to :8188",
        "",
        f"- **Venv warning:** {VENV_RISK['reason']}",
        f"- **Destination instance:** :{ALLOWED_DEST_PORT}",
        f"- **Copied packages from :8189:** {', '.join(copied_packages) if copied_packages else 'none'}",
        f"- **Pip packages installed in :8188:** {', '.join(pip_installed) if pip_installed else 'none'}",
        "",
        "## Installed Nodes",
        "",
    ]
    for node_name in sorted(set(install_nodes)):
        log_content.append(f"- {node_name}")
    log_content.extend([
        "",
        "## Backup Files",
        "",
    ])
    for port in sorted(backups):
        log_content.append(f"- :{port}: `{backups[port]}`")
    log_content.append("")
    safe_write(LOG_PATH, "\n".join(log_content))
    log(f"  Log written to {LOG_PATH}")
    log("\nInstallation complete. Restart affected instances before validating APIs.")
    return True


def do_rollback(ports: list[int] | None = None, dry_run: bool = False):
    log("=" * 70)
    if dry_run:
        log("DRY RUN ROLLBACK — No changes will be made")
    else:
        log("ROLLBACK — Restoring from backups")
    log("=" * 70)

    targets = ports or list(PROFILES.keys())
    for port in targets:
        if port not in PROFILES:
            log(f"Invalid port: {port}", "ERROR")
            continue
        rollback_instance(port, dry_run=dry_run)

    if not dry_run:
        log("Rollback complete for all specified instances. Restart ComfyUI instances to apply.")


def generate_review_report(analysis: dict):
    report_path = DOCS_VALIDATION / "comfyui_installation_plan_review_20260521.md"
    lines = [
        "# ComfyUI Installation Plan Review",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Source:** COMFYUI.1C controlled installation analysis",
        "",
        "## Executive Summary",
        "",
    ]
    s = analysis["summary"]
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total plan entries | {s['total_entries']} |")
    lines.append(f"| UUIDs (parsing artifacts, skip) | {s['total_uuid']} |")
    lines.append(f"| Core nodes (already exist, skip) | {s['total_core']} |")
    lines.append(f"| Installable candidates | {s['total_installable']} |")
    lines.append(f"| Unknown (needs research) | {s['total_unknown']} |")
    lines.append("")

    for port, (name, _) in sorted(PROFILES.items()):
        data = analysis["per_instance"][port]
        lines.append(f"## :{port} — {name}")
        lines.append("")
        lines.append(f"### Candidates ({len(data['candidates'])})")
        lines.append("")
        if data["candidates"]:
            lines.append("| Node | Package | Source | Pip? | Risk |")
            lines.append("|------|---------|--------|------|------|")
            for c in data["candidates"]:
                src = c.get("source", {})
                st = src.get("source_type", "unknown")
                pkg = src.get("pkg_name", "?")
                if st == "g_hub":
                    detail = "G: hub copy"
                elif st == "cross_instance":
                    detail = f"From :{src.get('source_port')}"
                elif st == "external_git":
                    detail = "External git clone"
                elif st == "already_installed":
                    pip_n = src.get("needs_pip_install", False)
                    detail = "Dir exists" + (" (needs pip)" if pip_n else "")
                else:
                    detail = "Research needed"
                pip_need = "YES" if src.get("needs_pip_install") else "no"
                risk = c.get("risk", "high")
                lines.append(f"| `{c['node']}` | {pkg} | {detail} | {pip_need} | {risk} |")
        else:
            lines.append("*No candidates for this instance*")
        lines.append("")

        if data["pip_deps"]:
            lines.append("### Pip Dependencies")
            lines.append("")
            for pkg in sorted(data["pip_deps"]):
                lines.append(f"- {pkg}")
            lines.append("")

        if data["external_needed"]:
            lines.append("### External Sources Required")
            lines.append("")
            for c in data["external_needed"]:
                src = c.get("source", {})
                lines.append(f"- `{c['node']}` via {src.get('pkg_name', '?')}")
            lines.append("")

        if data["exempt"]:
            lines.append("### Exempt (Skipped)")
            lines.append("")
            for c in data["exempt"]:
                lines.append(f"- `{c['node']}`: {c['exempt_reason']}")
            lines.append("")

    # Cross-instance availability
    lines.append("## Cross-Instance Package Availability")
    lines.append("")
    lines.append("| Package | 8188 | 8189 | 8190 | 8191 | 8192 | G: hub |")
    lines.append("|---------|------|------|------|------|------|--------|")
    # Collect all unique packages
    all_pkgs = set()
    for port in PROFILES:
        pkgs = set(instance_nodes.get(port, {}).keys())
        all_pkgs.update(pkgs)
    # Also add G: hub
    if G_HUB_CUSTOM_NODES.exists():
        for d in G_HUB_CUSTOM_NODES.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                all_pkgs.add(d.name)

    # Show only packages involved in install plan
    plan_pkgs = set()
    for port in PROFILES:
        for c in analysis["per_instance"][port]["candidates"]:
            pkg = c.get("source", {}).get("pkg_name")
            if pkg:
                plan_pkgs.add(pkg)

    for pkg in sorted(plan_pkgs):
        if pkg in all_pkgs:
            cols = []
            for port in [8188, 8189, 8190, 8191, 8192]:
                pkgs = set(instance_nodes.get(port, {}).keys())
                cols.append("YES" if pkg in pkgs else "no")
            in_ghub = G_HUB_CUSTOM_NODES.exists() and (G_HUB_CUSTOM_NODES / pkg).exists()
            cols.append("YES" if in_ghub else "no")
            lines.append(f"| {pkg} | {' | '.join(cols)} |")
    lines.append("")

    lines.append("## Venv Isolation Assessment")
    lines.append("")
    lines.append(f"- **Verdict:** {VENV_RISK['verdict']}")
    lines.append(f"- **Shared venv:** {VENV_RISK['shared']}")
    lines.append(f"- **Reason:** {VENV_RISK['reason']}")
    lines.append("")
    lines.append("## GO/NO-GO Assessment")
    lines.append("")
    pct_installable = (s['total_installable'] / max(s['total_entries'], 1)) * 100
    lines.append(f"- **{s['total_installable']} / {s['total_entries']}** entries can be installed ({pct_installable:.0f}%)")
    lines.append(f"- **{s['total_uuid']}** UUID entries (skip)")
    lines.append(f"- **{s['total_core']}** core nodes (skip, version check needed)")
    lines.append(f"- **{s['total_unknown']}** unknown entries (manual research)")
    lines.append(f"- **Venv risk:** {VENV_RISK['verdict']} — {VENV_RISK['reason']}")
    lines.append("")
    verdict = "NO-GO"
    if s["total_installable"] > 0 and s["total_unknown"] == 0:
        if VENV_RISK["verdict"] == "NO-GO":
            verdict = "NO-GO (venv isolation failure)"
        elif VENV_RISK["verdict"] == "WARNING" and s["total_installable"] > 0:
            verdict = "GO (with warnings — shared venv accepted, pip install affects all instances)"
        else:
            verdict = "GO — All missing nodes can be resolved. Proceed with `--install` (after --dry-run)."
    elif s["total_unknown"] > 0:
        verdict = "NO-GO (conditional) — Some nodes require manual research before proceeding."
    else:
        verdict = "NO-GO — No installable candidates found."
    lines.append(f"**{verdict}**")
    lines.append("")

    safe_write(report_path, "\n".join(lines))
    log(f"Review report: {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Security checks
# ---------------------------------------------------------------------------

VENV_RISK = {"shared": True, "reason": "", "verdict": "GO"}

def check_8191_venv():
    global VENV_RISK
    image_venv = instance_venv_dir(8188)
    restoration_venv = instance_venv_dir(8191)

    if restoration_venv.is_symlink():
        target = restoration_venv.resolve()
        if image_venv.exists() and target == image_venv.resolve():
            VENV_RISK = {
                "shared": True,
                "reason": (
                    f"8188 uses `{image_venv}` and 8191 `.venv-restoration` is a symlink to it. "
                    "Any pip install done for :8188 also affects :8191."
                ),
                "verdict": "WARNING",
            }
            log(f"SECURITY: {VENV_RISK['reason']}", "WARN")
            return

    if restoration_venv.exists() and image_venv.exists() and restoration_venv.resolve() != image_venv.resolve():
        VENV_RISK = {
            "shared": False,
            "reason": "8188 and 8191 use independent instance venvs.",
            "verdict": "GO",
        }
        log("8191 has independent venv — pip install isolation is OK", "INFO")
        return

    VENV_RISK = {
        "shared": False,
        "reason": "Could not confirm a shared venv between 8188 and 8191.",
        "verdict": "GO",
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Controlled installation of missing ComfyUI custom nodes"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--install", action="store_true", help="Run controlled installation")
    parser.add_argument("--rollback", action="store_true", help="Restore from backup")
    parser.add_argument("--analyze", action="store_true", help="Analyze and generate review report")
    parser.add_argument("--ports", type=int, nargs="*", help="Specific ports for rollback")
    args = parser.parse_args()

    if not any([args.dry_run, args.install, args.rollback, args.analyze]):
        parser.print_help()
        return 1

    # SECURITY: Check 8191 Restoration venv isolation
    check_8191_venv()

    # Load plan and instance data
    log("Loading install plan...")
    plan_entries = load_plan()
    global instance_nodes
    instance_nodes = load_instance_nodes()

    # Analyze
    analysis = analyze(plan_entries, instance_nodes)

    # Generate review report (always, even on dry-run)
    generate_review_report(analysis)

    if args.analyze:
        log("Analysis complete. See report for details.")
        return 0

    if args.dry_run and not args.install:
        dry_run(analysis)
        return 0

    if args.install:
        return 0 if do_install(analysis) else 1

    if args.rollback:
        do_rollback(args.ports, dry_run=False)
        return 0

    return 0


instance_nodes: dict = {}

if __name__ == "__main__":
    sys.exit(main())
