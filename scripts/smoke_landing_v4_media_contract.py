#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v4/landing_semantic_prompts_v4.json"
BIBLE_PATH = ROOT / "src_frontend/src/data/landingVisualBibleV4.ts"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
FRONTEND_DIR = ROOT / "src_frontend" / "src"

EXPECTED_V4_IMAGES = [
    "landing-hero-main-v4.webp",
    "landing-problem-fragmented-v4.webp",
    "landing-ai-reasoning-v4.webp",
    "landing-concept-keyvisual-v4.webp",
    "landing-storyboard-preview-v4.webp",
    "landing-comfyui-generation-v4.webp",
    "landing-cid-orchestration-v4.webp",
    "landing-producers-studios-v4.webp",
    "landing-professional-differential-v4.webp",
    "landing-delivery-final-v4.webp",
    "landing-visual-bible-v4.webp",
]

V4_VISUAL_IDS = [
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
]


def load_prompt_items() -> list[dict[str, Any]]:
    payload = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if len(items) < 10:
        raise RuntimeError(f"Prompt pack must have at least 10 items, got {len(items)}")
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
    print("=== Smoke Test: Landing V4 Media Contract ===\n")

    items = load_prompt_items()
    frontend_sources = read_frontend_sources()
    frontend_blob = "\n".join(text for _, text in frontend_sources)

    failures: list[str] = []

    # 1. Check V4 bible exists
    if not BIBLE_PATH.exists():
        failures.append(f"Bible V4 not found: {BIBLE_PATH.relative_to(ROOT)}")
    else:
        bible_text = BIBLE_PATH.read_text(encoding="utf-8")
        for vid in V4_VISUAL_IDS:
            if vid not in bible_text:
                failures.append(f"Visual ID '{vid}' not found in V4 bible")

    # 2. Check expected V4 images exist (after import)
    existing_count = 0
    missing_images: list[str] = []
    for img in EXPECTED_V4_IMAGES:
        path = MEDIA_DIR / img
        if path.exists():
            existing_count += 1
        else:
            missing_images.append(img)
    all_missing = existing_count == 0 and len(missing_images) == len(EXPECTED_V4_IMAGES)
    if all_missing:
        print("  [PIPELINE MODE] No V4 images on disk — payload contract OK, images pending render+import.")
    elif missing_images:
        for img in missing_images:
            failures.append(f"Missing V4 image: {img} (expected after import)")
        image_note = (
            f"  Note: {existing_count}/{len(EXPECTED_V4_IMAGES)} images present. "
            f"Missing {len(missing_images)} — run render + import pipeline."
        )
        print(image_note)

    # 3. Check no blocked patterns in frontend
    for pattern in BLOCKED_PATTERNS:
        if pattern in frontend_blob:
            failures.append(f"Blocked pattern in frontend: {pattern}")

    # 4. Check no absolute Windows paths
    if "G:\\" in frontend_blob or "C:\\" in frontend_blob:
        failures.append("Absolute Windows paths (G:\\ or C:\\) in frontend")

    # 5. Check frontend references to V4 images
    for img in EXPECTED_V4_IMAGES:
        if img in frontend_blob:
            pass
        else:
            failures.append(f"V4 image not referenced in frontend: {img}")

    # 6. Check prompt pack items all have required fields
    for item in items:
        for field in ("image_key", "target_file_name", "positive_prompt", "negative_prompt", "qa_rules"):
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
    print(f"  V4 bible: {BIBLE_PATH.exists()}")
    print(f"  V4 images on disk: {existing_count}/{len(EXPECTED_V4_IMAGES)}")
    print(f"  Visual IDs in bible: {len(V4_VISUAL_IDS)}")
    print(f"  Prompt items: {len(items)}")
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
