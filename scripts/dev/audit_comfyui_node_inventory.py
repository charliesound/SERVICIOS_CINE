#!/usr/bin/env python3
"""Audit ComfyUI node inventory — COMFYUI.1A

Queries /object_info and /system_stats from 5 configured ComfyUI instances,
classifies every node into 6 functional families, computes a suitability
diagnostic per instance, and writes:
  - Raw evidence JSON per port under docs/validation/comfyui_node_inventory_20260521/
  - Aggregate markdown report at docs/validation/comfyui_node_inventory_audit_20260521.md

Families: image_still, video_cine, audio_dubbing, restoration, three_d, utility_general, unknown
"""
import json
import subprocess
import sys
import os
import re
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

RAW_DIR = Path("docs/validation/comfyui_node_inventory_20260521")
REPORT_PATH = Path("docs/validation/comfyui_node_inventory_audit_20260521.md")

# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

FAMILY_PATTERNS = {
    "image_still": [
        "image_still", "image still",
        "checkpoint", "vae", "clip", "sampler", "scheduler", "latent",
        "conditioning", "controlnet", "ip.?adapter", "lora", "load image",
        "preview image", "save image", "image (to|save|load|scale|resize|crop|paste|invert|batch|composite|blend)",
        "inpaint", "outpaint", "upscale? (image|model|laten)",
        "style", "prompt", "text encode", "image encode", "image decode",
        "KSampler", "VAE", "CLIP", "UNET",
    ],
    "video_cine": [
        "video cine", "video_cine",
        "video", "frame", "interpolation", "animate", "animation",
        "wan", "ltx", "svd", "temporal", "flow", "combine",
        "encode video", "decode video",
        "img2vid", "text.?to.?video",
    ],
    "audio_dubbing": [
        "audio dubbing", "audio_dubbing",
        "audio", "wav", "speech", "tts", "voice", "whisper",
        "phoneme", "alignment", "lipsync", "wav2lip", "dubbing",
        "sound", "music",
    ],
    "restoration": [
        "restoration",
        "restore", "denoise", "deblur", "face restore",
        "face enhance", "cleanup", "artifact", "color (grade|match|correct)",
        "conform", "resize", "crop",
    ],
    "three_d": [
        "three_d", "3d",
        "depth", "normal", "mesh", "nerf", "gaussian", "splat",
        "camera", "pose", "scene", "geometry", "point cloud",
        "texture", "blender",
    ],
    "utility_general": [
        "utility general", "utility_general",
        "json", "file", "debug", "preview", "mask", "segment",
        "metadata", "primitive", "int", "float", "string", "boolean",
        "math", "routing", "switch", "logic", "repeat", "batch",
        "save", "load", "note", "node", "reroute",
    ],
}

# Prepend the family slug itself to catch e.g. "AudioEnhance" -> audio_dubbing
for fam in list(FAMILY_PATTERNS):
    slug = fam.replace("_", " ")
    if slug not in FAMILY_PATTERNS[fam]:
        FAMILY_PATTERNS[fam].insert(0, slug)

FAMILY_REGEX = {}
for fam, patterns in FAMILY_PATTERNS.items():
    FAMILY_REGEX[fam] = re.compile(
        "(" + "|".join(f"(?:{p})" for p in patterns) + ")",
        re.IGNORECASE,
    )

NAME_OVERRIDES = {
    # Image / Still
    "CheckpointLoaderSimple": "image_still",
    "CLIPSetLastLayer": "image_still",
    "CLIPTextEncode": "image_still",
    "CLIPVisionEncode": "image_still",
    "VAEDecode": "image_still",
    "VAEEncode": "image_still",
    "VAELoader": "image_still",
    "EmptyLatentImage": "image_still",
    "LatentFromBatch": "image_still",
    "LatentUpscale": "image_still",
    "LatentUpscaleBy": "image_still",
    "LatentComposite": "image_still",
    "LatentBlend": "image_still",
    "LatentRotate": "image_still",
    "LatentFlip": "image_still",
    "LatentCrop": "image_still",
    "LatentScale": "image_still",
    "UpscaleModelLoader": "image_still",
    "ImageUpscaleWithModel": "image_still",
    "ImageScale": "image_still",
    "ImageScaleToTotalPixels": "image_still",
    "ImageCrop": "image_still",
    "ImagePaste": "image_still",
    "ImageInvert": "image_still",
    "ImageBatch": "image_still",
    "LoadImage": "image_still",
    "SaveImage": "image_still",
    "PreviewImage": "image_still",
    "ETN_LoadImage": "image_still",
    "ETN_SaveImage": "image_still",
    "ControlNetLoader": "image_still",
    "ControlNetApply": "image_still",
    "ControlNetApplyAdvanced": "image_still",
    "LoraLoader": "image_still",
    "LoraLoaderModelOnly": "image_still",
    "DualCFGGuider": "image_still",
    "BasicGuider": "image_still",
    "SamplerCustom": "image_still",
    "KSampler": "image_still",
    "KSamplerAdvanced": "image_still",
    "UNETLoader": "image_still",
    "UNETLoad": "image_still",
    "DiffControlNetLoader": "image_still",
    "StableZero123_Conditioning": "image_still",
    "ModelSamplingDiscrete": "image_still",
    "ModelSamplingStableCascade": "image_still",
    "SolventNormalize": "image_still",
    "CNetPatch": "image_still",
    "PatchModelAddDownscale": "image_still",
    "GLIGENTextBoxApply": "image_still",
    "CLIPInputSwitch": "image_still",
    "TimestepKeyframe": "image_still",
    # Video
    "VideoCombine": "video_cine",
    "VHS_VideoCombine": "video_cine",
    "VHS_LoadVideo": "video_cine",
    "VHS_SplitVideo": "video_cine",
    "VHS_VideoInfo": "video_cine",
    "SaveAnimatedWEBP": "video_cine",
    "SaveAnimatedPNG": "video_cine",
    "WanVideoToImage": "video_cine",
    "WanVideoSimple": "video_cine",
    "LTXVideo": "video_cine",
    "LTXVModelLoader": "video_cine",
    "SVD_stuff": "video_cine",
    "FrameInterpolation": "video_cine",
    "AnimateDiff": "video_cine",
    "AnimateDiffLoader": "video_cine",
    # Audio / Dubbing
    "DubbingAudio": "audio_dubbing",
    "SaveAudioWav": "audio_dubbing",
    "LoadAudioWav": "audio_dubbing",
    "WhisperTranscribe": "audio_dubbing",
    "Wav2Lip": "audio_dubbing",
    "FaceRestore": "restoration",
    "FaceRestoreWithModel": "restoration",
    "ImageRestoreWithModel": "restoration",
    "DFLDenoise": "restoration",
    "ImageResize": "restoration",
    "RestoreModelLoader": "restoration",
    "FaceEnhance": "restoration",
    # 3D
    "DepthMap": "three_d",
    "DepthMapPreprocessor": "three_d",
    "MeshRenderer": "three_d",
    "GaussianSplat": "three_d",
    "SplatRenderer": "three_d",
    "CameraPose": "three_d",
    "NormalMap": "three_d",
    # Utility
    "Note": "utility_general",
    "Primitive": "utility_general",
    "Int": "utility_general",
    "Float": "utility_general",
    "String": "utility_general",
    "Boolean": "utility_general",
    "Reroute": "utility_general",
    "MaskToImage": "utility_general",
    "ImageToMask": "utility_general",
    "SaveFloat": "utility_general",
    "LoadFloat": "utility_general",
    "MathExpression": "utility_general",
    "MaskComposite": "utility_general",
    "FeatherMask": "utility_general",
    "GrowMask": "utility_general",
    "ThresholdMask": "utility_general",
    "EmptyMask": "utility_general",
    "Mask": "utility_general",
    "SolidMask": "utility_general",
    "BitwiseAndMask": "utility_general",
    "BitwiseOrMask": "utility_general",
    "BitwiseXorMask": "utility_general",
    "BitwiseNotMask": "utility_general",
    "MaskToMask": "utility_general",
    "BinaryMask": "utility_general",
    "SplitMask": "utility_general",
    "CropMask": "utility_general",
    "Range": "utility_general",
    "Time": "utility_general",
    "Sleep": "utility_general",
    "Log": "utility_general",
}

FAMILY_LABELS = {
    "image_still": "Image / Still",
    "video_cine": "Video / Cine",
    "audio_dubbing": "Audio / Dubbing",
    "restoration": "Restoration",
    "three_d": "3D",
    "utility_general": "Utility / General",
    "unknown": "Unknown",
}

FAMILIES_ORDER = [
    "image_still", "video_cine", "audio_dubbing", "restoration",
    "three_d", "utility_general", "unknown",
]

INSTANCE_PREFERRED = {
    8188: "image_still",
    8189: "video_cine",
    8190: "audio_dubbing",
    8191: "restoration",
    8192: "three_d",
}

INSTANCE_SECONDARY = {
    8188: "utility_general",
    8189: "image_still",
    8190: "utility_general",
    8191: "utility_general",
    8192: "utility_general",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify_node(class_type: str, category: str | None = None,
                  display_name: str | None = None) -> str:
    if class_type in NAME_OVERRIDES:
        return NAME_OVERRIDES[class_type]
    ct = class_type.lower()
    cat = (category or "").lower()
    dn = (display_name or "").lower()
    for fam in FAMILIES_ORDER:
        if fam == "unknown":
            continue
        if FAMILY_REGEX[fam].search(ct):
            return fam
        if cat and FAMILY_REGEX[fam].search(cat):
            return fam
        if dn and FAMILY_REGEX[fam].search(dn):
            return fam
    return "unknown"


def fetch_json(url: str, timeout: int = 30) -> dict | None:
    try:
        result = subprocess.check_output(
            ["curl", "-sS", "--max-time", str(timeout), url],
            text=True, timeout=timeout + 5,
        )
        if not result.strip():
            return None
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        print(f"  [WARN] curl failed for {url}: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"  [WARN] invalid JSON from {url}: {e}", file=sys.stderr)
        return None
    except OSError as e:
        print(f"  [WARN] OS error for {url}: {e}", file=sys.stderr)
        return None


def safe_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    now = datetime.now()
    print("=" * 70)
    print("ComfyUI Node Inventory Audit")
    print(f"Started: {now.isoformat()}")
    print("=" * 70)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_reports = {}

    for port, short_name, long_name in PORTS:
        print(f"\n--- :{port} {long_name} ---")
        base_url = f"http://127.0.0.1:{port}"

        # --- system_stats ---
        stats = fetch_json(f"{base_url}/system_stats")
        if stats:
            safe_write(RAW_DIR / f"system_stats_{port}.json",
                       json.dumps(stats, indent=2))
            print(f"  system_stats: OK ({len(json.dumps(stats))} bytes)")
            version = stats.get("system", {}).get("comfyui_version", "unknown")
        else:
            print(f"  system_stats: FAILED")
            version = "unknown"

        # --- object_info ---
        obj_info = fetch_json(f"{base_url}/object_info")
        if not obj_info:
            print(f"  object_info: FAILED")
            all_reports[port] = {"error": "object_info unavailable",
                                 "instance": short_name, "port": port}
            continue

        safe_write(RAW_DIR / f"object_info_{port}.json",
                   json.dumps(obj_info, indent=2))
        pb = len(json.dumps(obj_info))
        print(f"  object_info: {len(obj_info)} class types, {pb} bytes")

        # Sorted node keys
        sorted_keys = sorted(obj_info.keys())
        safe_write(RAW_DIR / f"node_keys_{port}.txt",
                   "\n".join(sorted_keys))
        print(f"  node_keys: {len(sorted_keys)} unique class types")

        # --- Classify ---
        families: dict[str, list[dict]] = defaultdict(list)
        for class_type, node_def in obj_info.items():
            category = node_def.get("category")
            display_name = node_def.get("display_name")
            fam = classify_node(class_type, category=category,
                                display_name=display_name)
            families[fam].append({
                "class_type": class_type,
                "display_name": display_name,
                "category": category,
                "input_required": list(node_def.get("input", {}).get("required", {}).keys()),
                "input_optional": list(node_def.get("input", {}).get("optional", {}).keys()),
                "output": node_def.get("output"),
            })

        total = len(obj_info)
        family_counts = {}
        family_pct = {}
        for fam in FAMILIES_ORDER:
            count = len(families.get(fam, []))
            family_counts[fam] = count
            family_pct[fam] = round(count / total * 100, 1) if total else 0

        print(f"  total_nodes: {total}")
        for fam in FAMILIES_ORDER:
            if family_counts[fam]:
                print(f"    {FAMILY_LABELS[fam]}: {family_counts[fam]} "
                      f"({family_pct[fam]}%)")

        # Top categories
        cat_counter = defaultdict(int)
        for node_def in obj_info.values():
            cat_counter[node_def.get("category", "unknown")] += 1
        top_categories = sorted(cat_counter.items(),
                                key=lambda x: -x[1])[:30]

        # Top per family
        top_per_family = {}
        for fam in FAMILIES_ORDER:
            items = sorted(families.get(fam, []),
                           key=lambda x: x["class_type"])
            top_per_family[fam] = [
                {"class_type": x["class_type"],
                 "category": x["category"],
                 "display_name": x["display_name"]}
                for x in items[:50]
            ]

        # Out-of-profile
        preferred = INSTANCE_PREFERRED[port]
        secondary = INSTANCE_SECONDARY[port]
        oop = {}
        for fam in FAMILIES_ORDER:
            if fam in (preferred, secondary, "unknown"):
                continue
            if families.get(fam):
                oop[fam] = [x["class_type"]
                            for x in sorted(families[fam],
                                             key=lambda x: x["class_type"])
                            ][:20]

        # Diagnostic
        preferred_pct = family_pct.get(preferred, 0)
        secondary_pct = family_pct.get(secondary, 0)
        combined_pct = preferred_pct + secondary_pct

        if preferred_pct >= 25:
            diagnostic = "GO"
            diagnostic_detail = (
                f"Preferred family '{FAMILY_LABELS[preferred]}' represents "
                f"{preferred_pct}% of all nodes — adequate for purpose."
            )
        elif combined_pct >= 30:
            diagnostic = "WARNING"
            diagnostic_detail = (
                f"Preferred '{FAMILY_LABELS[preferred]}' is only "
                f"{preferred_pct}%, but combined with "
                f"'{FAMILY_LABELS[secondary]}' reaches {combined_pct}%. "
                f"COMFYUI.1B cross-check needed."
            )
        elif total == 0:
            diagnostic = "NO-GO"
            diagnostic_detail = "No nodes found — instance unreachable."
        else:
            diagnostic = "NO-GO"
            diagnostic_detail = (
                f"Preferred '{FAMILY_LABELS[preferred]}' is only "
                f"{preferred_pct}% — insufficient coverage."
            )

        report = {
            "port": port,
            "instance": short_name,
            "comfyui_version": version,
            "total_nodes": total,
            "family_counts": family_counts,
            "family_percentages": family_pct,
            "top_categories": top_categories,
            "top_per_family": top_per_family,
            "out_of_profile_nodes": oop,
            "diagnostic": diagnostic,
            "diagnostic_detail": diagnostic_detail,
        }
        all_reports[port] = report

        inv_path = RAW_DIR / f"node_inventory_{port}.json"
        safe_write(inv_path, json.dumps(report, indent=2, default=str))
        print(f"  node_inventory saved")

        print(f"  >> Diagnostic: {diagnostic}")
        print(f"     {diagnostic_detail}")

    # -------------------------------------------------------------------
    # Markdown report
    # -------------------------------------------------------------------
    lines = [
        "# ComfyUI Node Inventory Audit",
        "",
        f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Script:** `scripts/dev/audit_comfyui_node_inventory.py`",
        "",
        "## Executive Summary",
        "",
    ]

    go_count = sum(1 for r in all_reports.values()
                   if r.get("diagnostic") == "GO")
    warn_count = sum(1 for r in all_reports.values()
                     if r.get("diagnostic") == "WARNING")
    nogo_count = sum(1 for r in all_reports.values()
                     if r.get("diagnostic") == "NO-GO")
    err_count = sum(1 for r in all_reports.values()
                    if "error" in r)

    lines.append(f"- **Total instances:** {len(PORTS)}")
    lines.append(f"- **GO:** {go_count}")
    lines.append(f"- **WARNING:** {warn_count}")
    lines.append(f"- **NO-GO:** {nogo_count}")
    lines.append(f"- **Unreachable:** {err_count}")
    lines.append("")

    for port, short_name, long_name in PORTS:
        r = all_reports.get(port, {})
        lines.append(f"### :{port} — {long_name}")
        lines.append("")
        if "error" in r:
            lines.append(f"**Unreachable:** {r['error']}")
            lines.append("")
            continue

        lines.append(f"- **ComfyUI version:** {r.get('comfyui_version', 'unknown')}")
        lines.append(f"- **Total nodes:** {r['total_nodes']}")
        lines.append("")
        lines.append("#### Family Distribution")
        lines.append("")
        lines.append("| Family | Count | % |")
        lines.append("|--------|------:|---:|")
        for fam in FAMILIES_ORDER:
            cnt = r["family_counts"].get(fam, 0)
            pct = r["family_percentages"].get(fam, 0)
            if cnt:
                lines.append(f"| {FAMILY_LABELS[fam]} | {cnt} | {pct}% |")
        lines.append("")

        lines.append("#### Top Categories")
        lines.append("")
        for cat, cnt in r.get("top_categories", [])[:10]:
            lines.append(f"- {cat}: {cnt}")
        lines.append("")

        oop = r.get("out_of_profile_nodes", {})
        if oop:
            lines.append("#### Out-of-Profile Nodes")
            lines.append("")
            for fam, nodes in oop.items():
                if nodes:
                    lines.append(f"- **{FAMILY_LABELS[fam]}** ({len(nodes)}): "
                                 f"{', '.join(nodes[:10])}")
            lines.append("")

        diag = r.get("diagnostic", "?")
        detail = r.get("diagnostic_detail", "")
        icon = {"GO": "✅", "WARNING": "⚠️", "NO-GO": "❌"}.get(diag, "?")
        lines.append(f"**{icon} {diag}** — {detail}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    lines.append("### ComfyUI-Copilot")
    lines.append("")
    lines.append("- Do **not** install ComfyUI-Copilot yet.")
    lines.append("- **Candidato preliminar:** 8188 (Image/Still) if its inventory diagnostic is GO.")
    lines.append("- Do not install on 8189/8190/8191/8192 until profile validation (COMFYUI.1B) is complete.")
    lines.append("")

    safe_write(REPORT_PATH, "\n".join(lines))
    print(f"\n{'=' * 70}")
    print(f"Report: {REPORT_PATH}")
    print(f"Raw:    {RAW_DIR}/")

    # CLI summary table
    print(f"\n{'=' * 70}")
    hdr = f"{'Port':<6} {'Instance':<18} {'Total':<8} {'Preferred':<18} {'%':<6} {'Diag':<10}"
    print(hdr)
    print("=" * 70)
    for port, short_name, long_name in PORTS:
        r = all_reports.get(port, {})
        if "error" in r:
            print(f"{port:<6} {short_name:<18} {'ERR':<8} {'':<18} {'':<6} {'NO-GO':<10}")
            continue
        pref = INSTANCE_PREFERRED[port]
        pref_pct = r.get("family_percentages", {}).get(pref, 0)
        diag = r.get("diagnostic", "?")
        print(f"{port:<6} {short_name:<18} {r.get('total_nodes', 0):<8} "
              f"{FAMILY_LABELS[pref]:<18} {pref_pct:<6} {diag:<10}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
