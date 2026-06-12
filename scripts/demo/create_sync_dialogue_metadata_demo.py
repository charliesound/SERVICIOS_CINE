#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ailink_tools.sync_dialogue.exports import (
    write_matches_csv,
    write_media_csv,
    write_scan_json,
)
from ailink_tools.sync_dialogue.matching import suggest_matches
from ailink_tools.sync_dialogue.report_html import write_report_html
from ailink_tools.sync_dialogue.schemas import SyncDialogueMediaFile, SyncDialogueScanResult

EXPECTED_OUTPUTS = (
    "scan_result.json",
    "media_files.csv",
    "match_suggestions.csv",
    "report.html",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create controlled metadata outputs for AILink Sync Dialogue demos."
    )
    parser.add_argument("--output-dir", required=True, help="Output directory for demo files")
    parser.add_argument("--force", action="store_true", help="Overwrite expected demo outputs")
    parser.add_argument("--quiet", action="store_true", help="Suppress success summary")
    return parser


def create_metadata_demo(output_dir: str | Path, *, force: bool = False) -> dict[str, object]:
    output_path = _validate_output_dir(output_dir)
    _prepare_output_dir(output_path, force=force)
    scan_result = build_controlled_scan_result()
    result = replace(scan_result, match_suggestions=suggest_matches(scan_result))

    write_scan_json(result, output_path / "scan_result.json")
    write_media_csv(result, output_path / "media_files.csv")
    write_matches_csv(result, output_path / "match_suggestions.csv")
    write_report_html(result, output_path / "report.html")

    missing = [name for name in EXPECTED_OUTPUTS if not (output_path / name).exists()]
    if missing:
        raise RuntimeError(f"missing expected outputs: {', '.join(missing)}")

    high_count = sum(1 for item in result.match_suggestions if item.confidence == "high")
    return {
        "output_path": output_path,
        "video_count": result.video_count,
        "audio_count": result.audio_count,
        "match_suggestions_count": len(result.match_suggestions),
        "high_confidence_count": high_count,
        "report_html": output_path / "report.html",
    }


def build_controlled_scan_result() -> SyncDialogueScanResult:
    media_files = [
        _video("video/scene01_take01.mov", 12.0, "01:00:00:00", 24.0, "prores", "mov"),
        _video("video/scene01_take02.mov", 15.2, "01:00:20:00", 24.0, "prores", "mov"),
        _video("video/scene02_take01.mxf", 18.0, "01:01:00:00", 25.0, "dnxhd", "mxf"),
        _audio("audio/scene01_take01.wav", 12.1, "01:00:00:00", 2),
        _audio("audio/scene01_take02.wav", 15.0, "01:00:20:00", 2),
        _audio("audio/scene02_take01.wav", 20.7, None, 2),
        _audio("audio/wildtrack_roomtone.wav", 60.0, None, 2),
    ]
    return SyncDialogueScanResult(
        root_path="controlled-metadata-demo",
        total_files=len(media_files),
        video_count=3,
        audio_count=4,
        unsupported_count=0,
        media_files=media_files,
    )


def _video(
    relative_path: str,
    duration: float,
    timecode: str,
    fps: float,
    codec_name: str,
    format_name: str,
) -> SyncDialogueMediaFile:
    filename = relative_path.rsplit("/", 1)[-1]
    return SyncDialogueMediaFile(
        path=f"controlled/{relative_path}",
        relative_path=relative_path,
        filename=filename,
        extension="." + filename.rsplit(".", 1)[-1],
        kind="video",
        size_bytes=1024,
        probe_status="ok",
        duration_seconds=duration,
        timecode=timecode,
        fps=fps,
        audio_channels=None,
        codec_name=codec_name,
        format_name=format_name,
        error_message=None,
    )


def _audio(
    relative_path: str,
    duration: float,
    timecode: str | None,
    channels: int,
) -> SyncDialogueMediaFile:
    filename = relative_path.rsplit("/", 1)[-1]
    return SyncDialogueMediaFile(
        path=f"controlled/{relative_path}",
        relative_path=relative_path,
        filename=filename,
        extension="." + filename.rsplit(".", 1)[-1],
        kind="audio",
        size_bytes=2048,
        probe_status="ok",
        duration_seconds=duration,
        timecode=timecode,
        fps=None,
        audio_channels=channels,
        codec_name="pcm_s24le",
        format_name="wav",
        error_message=None,
    )


def _prepare_output_dir(output_path: Path, *, force: bool) -> None:
    if output_path.exists() and not output_path.is_dir():
        raise ValueError("output-dir exists and is not a directory")
    if output_path.exists():
        existing_outputs = [name for name in EXPECTED_OUTPUTS if (output_path / name).exists()]
        if existing_outputs and not force:
            raise ValueError("output-dir already contains demo outputs; use --force")
        if force:
            for name in EXPECTED_OUTPUTS:
                target = output_path / name
                if target.exists():
                    target.unlink()
    output_path.mkdir(parents=True, exist_ok=True)


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


def _print_summary(summary: dict[str, object]) -> None:
    print("AILink Sync Dialogue metadata demo created.")
    print(f"Output path: {summary['output_path']}")
    print(f"Video count: {summary['video_count']}")
    print(f"Audio count: {summary['audio_count']}")
    print(f"Match suggestions count: {summary['match_suggestions_count']}")
    print(f"High confidence count: {summary['high_confidence_count']}")
    print(f"Report HTML: {summary['report_html']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = create_metadata_demo(args.output_dir, force=args.force)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"error: metadata demo failed: {exc}", file=sys.stderr)
        return 3

    if not args.quiet:
        _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
