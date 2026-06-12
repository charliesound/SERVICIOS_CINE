#!/usr/bin/env python
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

FIXTURE_DIR_NAME = "demo_sync_dialogue"
DUMMY_TEXT = "dummy demo fixture, not real media\n"

MEDIA_FILES = {
    "video/scene01_take01.mov": DUMMY_TEXT,
    "video/scene01_take02.mov": DUMMY_TEXT,
    "video/scene02_take01.mxf": DUMMY_TEXT,
    "audio/scene01_take01.wav": DUMMY_TEXT,
    "audio/scene01_take02.wav": DUMMY_TEXT,
    "audio/scene02_take01.wav": DUMMY_TEXT,
    "notes/readme.txt": (
        "AILink Sync Dialogue demo fixture.\n"
        "These files are dummy placeholders, not real media.\n"
        "Use --no-probe when scanning this fixture.\n"
    ),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a local dummy fixture for AILink Sync Dialogue demos."
    )
    parser.add_argument("--output-dir", required=True, help="Base directory for the fixture")
    parser.add_argument("--force", action="store_true", help="Regenerate fixture if it already exists")
    parser.add_argument("--quiet", action="store_true", help="Do not print the created fixture path")
    return parser


def create_fixture(output_dir: str | Path, *, force: bool = False) -> Path:
    base_dir = _validate_output_dir(output_dir)
    fixture_dir = base_dir / FIXTURE_DIR_NAME

    if fixture_dir.exists():
        if not force:
            raise ValueError("fixture already exists; use --force to regenerate")
        if not fixture_dir.is_dir():
            raise ValueError("fixture path exists and is not a directory")
        shutil.rmtree(fixture_dir)

    for relative_path, content in MEDIA_FILES.items():
        target = fixture_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    return fixture_dir


def _validate_output_dir(output_dir: str | Path) -> Path:
    raw = str(output_dir).strip()
    if not raw:
        raise ValueError("output-dir must be non-empty")
    if "\\" in raw or raw.startswith("/mnt/") or _looks_like_drive_path(raw):
        raise ValueError("output-dir must be a WSL/Linux/macOS path")

    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor):
        raise ValueError("output-dir must not be filesystem root")
    return path


def _looks_like_drive_path(value: str) -> bool:
    return len(value) >= 2 and value[1] == ":" and value[0].isalpha()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        fixture_dir = create_fixture(args.output_dir, force=args.force)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: fixture creation failed: {exc}", file=sys.stderr)
        return 3

    if not args.quiet:
        print(f"created fixture: {fixture_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
