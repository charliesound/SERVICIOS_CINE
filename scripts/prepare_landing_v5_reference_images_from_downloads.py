#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DOWNLOADS_DIR = Path("/mnt/c/Users/Charliesound/Downloads")
TMP_REF_DIR = Path(__file__).resolve().parents[1] / ".tmp" / "landing_comfyui_v5" / "reference_images"
MANIFEST_PATH = TMP_REF_DIR.parent / "reference_images_manifest.json"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def collect_images(source_dir: Path) -> list[Path]:
    if not source_dir.is_dir():
        print(f"  WARN: Downloads directory not found: {source_dir}")
        return []
    images: list[Path] = []
    for ext in ALLOWED_EXTENSIONS:
        images.extend(sorted(source_dir.glob(f"*{ext}")))
        images.extend(sorted(source_dir.glob(f"*{ext.upper()}")))
    return images


def copy_image(src: Path, dst_dir: Path) -> Path | None:
    dst = dst_dir / src.name
    counter = 1
    while dst.exists():
        stem = src.stem
        suffix = src.suffix
        dst = dst_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    try:
        shutil.copy2(src, dst)
        return dst
    except OSError as exc:
        print(f"    COPY FAILED: {src.name} -> {exc}")
        return None


def main() -> int:
    print("=== Prepare Landing V5 Reference Images ===\n")

    TMP_REF_DIR.mkdir(parents=True, exist_ok=True)
    source_images = collect_images(DOWNLOADS_DIR)

    if not source_images:
        print(f"  No images found in {DOWNLOADS_DIR}")
        print(f"  Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        print("\n  Copy reference images manually to:")
        print(f"    {TMP_REF_DIR}/")
        print("\n  Or place them in Downloads and re-run this script.")
        dump_json(MANIFEST_PATH, {
            "version": "v5",
            "source": str(DOWNLOADS_DIR),
            "copied_at": datetime.now(timezone.utc).isoformat(),
            "total_found": 0,
            "total_copied": 0,
            "images": [],
        })
        return 0

    print(f"  Source: {DOWNLOADS_DIR}")
    print(f"  Destination: {TMP_REF_DIR}")
    print(f"  Images found: {len(source_images)}\n")

    copied_records: list[dict[str, Any]] = []
    for src in source_images:
        dst = copy_image(src, TMP_REF_DIR)
        if dst is None:
            continue
        record = {
            "original_path": str(src),
            "local_path": str(dst),
            "file_name": dst.name,
            "original_name": src.name,
            "size_bytes": dst.stat().st_size,
            "detected_extension": dst.suffix.lower(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        copied_records.append(record)
        print(f"  COPIED: {src.name} -> {dst.name}")

    manifest = {
        "version": "v5",
        "source": str(DOWNLOADS_DIR),
        "copied_at": datetime.now(timezone.utc).isoformat(),
        "total_found": len(source_images),
        "total_copied": len(copied_records),
        "images": copied_records,
    }
    dump_json(MANIFEST_PATH, manifest)

    print(f"\n  Manifest: {MANIFEST_PATH.relative_to(Path(__file__).resolve().parents[1])}")
    print(f"  Copied: {len(copied_records)}/{len(source_images)} images")
    return 0


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
