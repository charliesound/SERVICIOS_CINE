"""CID Local Media Agent — Windows Operator Experience.

Launches the read-only folder scanner and presents a human-readable
summary. No backend, no database, no network, no media-byte reads.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_media_agent.read_only_folder_scanner import (
    scan_read_only_folder,
)


HEADER = r"""
  ======================================================
   CID  Local Media Agent  V0.1
  ======================================================
"""

SEPARATOR = "  ------------------------------------------------------"


def _category_counts(ext_summary: dict[str, int]) -> dict[str, int]:
    video_exts = {".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"}
    audio_exts = {".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
    image_exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf"}
    video = sum(v for ext, v in ext_summary.items() if ext in video_exts)
    audio = sum(v for ext, v in ext_summary.items() if ext in audio_exts)
    images = sum(v for ext, v in ext_summary.items() if ext in image_exts)
    other = sum(v for ext, v in ext_summary.items() if ext not in video_exts | audio_exts | image_exts)
    return {"video": video, "audio": audio, "images": images, "other": other}


def _display_result(folder: str, result: dict) -> None:
    status = result.get("status", "UNKNOWN")
    summary = result.get("scanner_summary", {})
    ext_summary = result.get("extension_summary", {})
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    cats = _category_counts(ext_summary)

    print(SEPARATOR)
    print(f"  Folder:              {folder}")
    print(SEPARATOR)
    print(f"  Media files:         {summary.get('media_candidates', 0)}")
    print(f"  Video:               {cats['video']}")
    print(f"  Audio:               {cats['audio']}")
    print(f"  Images:              {cats['images']}")
    if cats["other"]:
        print(f"  Other files:         {cats['other']}")
    print(f"  Directories scanned: {summary.get('directories_seen', 0)}")
    print(f"  Errors:              {len(errors)}")
    print(f"  Warnings:            {len(warnings)}")
    print(SEPARATOR)
    print(f"  Status: {status}")
    print(SEPARATOR)

    if errors:
        print()
        print("  Errors:")
        for e in errors[:5]:
            print(f"    - {e}")
    if warnings:
        print()
        print("  Warnings:")
        for w in warnings[:5]:
            print(f"    - {w}")


def _try_folder_dialog() -> str | None:
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select folder to scan")
        root.destroy()
        return folder if folder else None
    except Exception:
        return None


def _prompt_folder() -> str:
    print("  Enter a folder path to scan, or press Enter to browse.")
    print()
    raw = input("  Folder: ").strip().strip('"').strip("'")
    if not raw:
        print()
        print("  Opening folder browser...")
        folder = _try_folder_dialog()
        if folder:
            return folder
        print("  Folder browser unavailable. Please type a path.")
        return _prompt_folder()
    return raw


def _run(folder: str) -> int:
    if not os.path.isdir(folder):
        print()
        print(f"  ERROR: Folder not found: {folder}")
        print()
        return 1

    result = scan_read_only_folder(folder)
    print()
    _display_result(folder, result)
    print()
    return 0


def main() -> int:
    os.system("cls" if os.name == "nt" else "clear")
    print(HEADER)

    interactive = len(sys.argv) <= 1
    if interactive:
        folder = _prompt_folder()
    else:
        folder = " ".join(sys.argv[1:])

    exit_code = _run(folder)

    if interactive:
        print("  Press Enter to exit...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
