#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_semantic_prompts_v5_reference_guided.json"
REFERENCE_MAP_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.json"
REFERENCE_MAP_EXAMPLE_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.example.json"
BIBLE_PATH = ROOT / "src_frontend/src/data/landingVisualBibleV4.ts"
MANIFEST_PATH = ROOT / ".tmp" / "landing_comfyui_v5" / "manifest.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
FRONTEND_DIR = ROOT / "src_frontend" / "src"

EXPECTED_V5_IMAGES = [
    "landing-hero-main-v5.webp",
    "landing-problem-fragmented-v5.webp",
    "landing-ai-reasoning-v5.webp",
    "landing-concept-keyvisual-v5.webp",
    "landing-storyboard-preview-v5.webp",
    "landing-comfyui-generation-v5.webp",
    "landing-cid-orchestration-v5.webp",
    "landing-producers-studios-v5.webp",
    "landing-professional-differential-v5.webp",
    "landing-delivery-final-v5.webp",
    "landing-visual-bible-v5.webp",
]

V5_VISUAL_IDS = [
    "hero_control_center",
    "fragmented_departments",
    "script_analysis_breakdown",
    "moodboard_bible",
    "storyboard_sequence",
    "comfyui_generation_engine",
    "pipeline_orchestration",
    "collaboration_review",
    "professional_traceability",
    "delivery_qc_suite",
    "visual_bible_overview",
]

BLOCKED_PATTERNS = [
    ".tmp",
    "/candidates/",
    "candidates/",
    "/mnt/g",
    "G:\\",
    "C:\\",
    "COMFYUI_HUB",
    "/mnt/c/Users/Charliesound/Downloads",
]


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if len(items) < 10:
        raise RuntimeError(f"Prompt pack V5 must have at least 10 items, got {len(items)}")
    return items


def read_frontend_sources() -> list[tuple[Path, str]]:
    sources: list[tuple[Path, str]] = []
    for path in FRONTEND_DIR.rglob("*"):
        if path.suffix not in {".ts", ".tsx", ".css"}:
            continue
        sources.append((path, path.read_text(encoding="utf-8", errors="ignore")))
    return sources


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    print("=== Smoke Test: Landing V5 Reference-Guided Contract ===\n")

    items = load_prompt_items()
    frontend_sources = read_frontend_sources()
    frontend_blob = "\n".join(text for _, text in frontend_sources)

    failures: list[str] = []

    # 1. Check prompt pack V5 exists
    if not PROMPTS_PATH.exists():
        failures.append(f"Prompt pack V5 not found: {PROMPTS_PATH.relative_to(ROOT)}")

    # 2. Check reference map (real or example)
    if REFERENCE_MAP_PATH.exists():
        ref_map_path = REFERENCE_MAP_PATH
        ref_map_type = "real"
    elif REFERENCE_MAP_EXAMPLE_PATH.exists():
        ref_map_path = REFERENCE_MAP_EXAMPLE_PATH
        ref_map_type = "example"
    else:
        failures.append("No reference map found (neither .json nor .example.json)")
        ref_map_path = None
        ref_map_type = "missing"

    if ref_map_path:
        try:
            ref_map_data = json.loads(ref_map_path.read_text(encoding="utf-8"))
            ref_map_items = ref_map_data.get("items", [])
            if len(ref_map_items) != 11:
                failures.append(f"Reference map must have 11 items, got {len(ref_map_items)}")
            else:
                map_keys = [item["image_key"] for item in ref_map_items]
                expected_keys = [item["image_key"] for item in items]
                for ek in expected_keys:
                    if ek not in map_keys:
                        failures.append(f"Reference map missing entry for: {ek}")
        except (json.JSONDecodeError, IOError) as exc:
            failures.append(f"Reference map parse error: {exc}")

    # 3. Check V4 bible exists (V5 uses same bible)
    if not BIBLE_PATH.exists():
        failures.append(f"Bible V4 not found: {BIBLE_PATH.relative_to(ROOT)}")
    else:
        bible_text = BIBLE_PATH.read_text(encoding="utf-8")
        for vid in V5_VISUAL_IDS:
            if vid not in bible_text:
                failures.append(f"Visual ID '{vid}' not found in V4 bible")

    # 4. Check 11 blocks defined in prompt pack
    if len(items) != 11:
        failures.append(f"Prompt pack must have 11 items, got {len(items)}")

    # 5. Check payloads generated
    if not MANIFEST_PATH.exists():
        failures.append(f"Payload manifest not found: {MANIFEST_PATH.relative_to(ROOT)}")
    else:
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            if manifest.get("image_count") != 11:
                failures.append(f"Manifest image_count should be 11, got {manifest.get('image_count')}")
            payload_keys = [p["image_key"] for p in manifest.get("image_payloads", [])]
            expected_keys = [item["image_key"] for item in items]
            for ek in expected_keys:
                if ek not in payload_keys:
                    failures.append(f"Payload missing for: {ek}")
            manifest_mode_count = sum(1 for p in manifest.get("image_payloads", []) if p.get("mode"))
            print(f"  Payloads in manifest: {len(payload_keys)} (mode info: {manifest_mode_count}/{len(payload_keys)})")
        except (json.JSONDecodeError, IOError) as exc:
            failures.append(f"Manifest parse error: {exc}")

    # 6. Check V5 images on disk
    existing_count = 0
    missing_images: list[str] = []
    for img in EXPECTED_V5_IMAGES:
        path = MEDIA_DIR / img
        if path.exists():
            existing_count += 1
        else:
            missing_images.append(img)
    all_missing = existing_count == 0 and len(missing_images) == len(EXPECTED_V5_IMAGES)
    if all_missing:
        print("  [PIPELINE MODE] No V5 images on disk — payload contract OK, images pending render+import.")
    elif missing_images:
        for img in missing_images:
            failures.append(f"Missing V5 image on disk: {img}")
        print(f"  Note: {existing_count}/{len(EXPECTED_V5_IMAGES)} images present.")

    # 7. Check no blocked patterns in frontend
    for pattern in BLOCKED_PATTERNS:
        if pattern in frontend_blob:
            failures.append(f"Blocked pattern in frontend: {pattern}")

    # 8. Check no absolute Windows paths in frontend
    if "G:\\" in frontend_blob or "C:\\" in frontend_blob:
        failures.append("Absolute Windows paths (G:\\ or C:\\) in frontend")

    # 9. Check no downloads path directly referenced in frontend
    if "/mnt/c/Users/Charliesound/Downloads" in frontend_blob:
        failures.append("Direct Downloads path reference in frontend")

    # 10. Check prompt pack items have required fields
    required_fields = [
        "image_key", "v4_source_key", "visual_intent",
        "positive_prompt", "negative_prompt",
        "composition_lock", "lighting_lock",
        "semantic_must_have", "semantic_must_not_have", "qa_rules",
    ]
    for item in items:
        for field in required_fields:
            if field not in item:
                failures.append(f"Item {item.get('image_key', 'unknown')} missing field: {field}")
        qa_rules = item.get("qa_rules", [])
        if not qa_rules:
            failures.append(f"Item {item.get('image_key', 'unknown')} has empty qa_rules")
        for qa in qa_rules:
            if not qa.startswith("VERIFICAR:"):
                failures.append(f"QA rule in {item.get('image_key', 'unknown')} does not start with VERIFICAR: {qa[:60]}")

    # Summary
    if failures:
        print(f"SMOKE FAIL: {len(failures)} issues found\n")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"SMOKE PASS")
    print(f"  Prompt pack V5: {PROMPTS_PATH.exists()}")
    print(f"  Reference map: {ref_map_type} ({len(ref_map_items if ref_map_path else [])} entries)")
    print(f"  V5 images on disk: {existing_count}/{len(EXPECTED_V5_IMAGES)}")
    print(f"  Visual IDs in bible: {len(V5_VISUAL_IDS)}")
    print(f"  Prompt items: {len(items)}")
    print(f"  Payloads generated: {len(payload_keys if MANIFEST_PATH.exists() else [])}")
    print(f"  Frontend files scanned: {len(frontend_sources)}")
    print(f"  Blocked patterns: none")
    if all_missing:
        print(f"  Pipeline mode: payload contract OK, images pending render+import")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"\nSMOKE FAIL: {exc}")
        raise SystemExit(1)
