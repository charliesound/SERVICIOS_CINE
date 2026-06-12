#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for import_path in (ROOT, SRC):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from scripts.ailink_sync_dialogue_scan import main as scan_main
from scripts.demo.create_sync_dialogue_demo_fixture import create_fixture

EXPECTED_OUTPUTS = (
    "scan_result.json",
    "media_files.csv",
    "match_suggestions.csv",
    "report.html",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the complete local AILink Sync Dialogue demo flow."
    )
    parser.add_argument("--work-dir", required=True, help="Base directory for fixture and outputs")
    parser.add_argument("--force", action="store_true", help="Regenerate fixture/output folders")
    parser.add_argument("--quiet", action="store_true", help="Suppress success summary")
    return parser


def run_demo(work_dir: str | Path, *, force: bool = False) -> dict[str, object]:
    base_dir = _validate_work_dir(work_dir)
    fixture_base = base_dir / "fixture"
    output_dir = base_dir / "output"

    _prepare_demo_dir(fixture_base, force=force, label="fixture")
    _prepare_demo_dir(output_dir, force=force, label="output")

    fixture_dir = create_fixture(fixture_base, force=False)
    output_dir.mkdir(parents=True, exist_ok=False)
    scan_code = scan_main(
        [
            "--input",
            str(fixture_dir),
            "--output-dir",
            str(output_dir),
            "--no-probe",
        ]
    )
    if scan_code != 0:
        raise RuntimeError(f"scanner failed with exit code {scan_code}")

    missing = [name for name in EXPECTED_OUTPUTS if not (output_dir / name).exists()]
    if missing:
        raise RuntimeError(f"missing expected outputs: {', '.join(missing)}")

    payload = json.loads((output_dir / "scan_result.json").read_text(encoding="utf-8"))
    summary = payload.get("summary") or {}
    return {
        "fixture_path": fixture_dir,
        "output_path": output_dir,
        "video_count": int(summary.get("video_count") or 0),
        "audio_count": int(summary.get("audio_count") or 0),
        "unsupported_count": int(summary.get("unsupported_count") or 0),
        "match_suggestions_count": len(payload.get("match_suggestions") or []),
        "report_html": output_dir / "report.html",
    }


def _prepare_demo_dir(path: Path, *, force: bool, label: str) -> None:
    if path.exists():
        if not force:
            raise ValueError(f"{label} directory already exists; use --force")
        if not path.is_dir():
            raise ValueError(f"{label} path exists and is not a directory")
        shutil.rmtree(path)


def _validate_work_dir(work_dir: str | Path) -> Path:
    raw = str(work_dir).strip()
    if not raw:
        raise ValueError("work-dir must be non-empty")
    if "\\" in raw or raw.startswith("/mnt/") or _looks_like_drive_path(raw):
        raise ValueError("work-dir must be a WSL/Linux/macOS path")
    path = Path(raw).expanduser().resolve()
    if path == Path(path.anchor):
        raise ValueError("work-dir must not be filesystem root")
    return path


def _looks_like_drive_path(value: str) -> bool:
    return len(value) >= 2 and value[1] == ":" and value[0].isalpha()


def _print_summary(summary: dict[str, object]) -> None:
    print("AILink Sync Dialogue demo completed.")
    print(f"Fixture path: {summary['fixture_path']}")
    print(f"Output path: {summary['output_path']}")
    print(f"Video count: {summary['video_count']}")
    print(f"Audio count: {summary['audio_count']}")
    print(f"Unsupported count: {summary['unsupported_count']}")
    print(f"Match suggestions count: {summary['match_suggestions_count']}")
    print(f"Report HTML: {summary['report_html']}")
    print("Note: match suggestions may be 0 because this fixture uses dummy files without real metadata.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_demo(args.work_dir, force=args.force)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: demo failed: {exc}", file=sys.stderr)
        return 3

    if not args.quiet:
        _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
