from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.AVAILABILITY.PREFLIGHT.V1"

VIDEO_EXTENSIONS = {".mov", ".mp4", ".mxf"}
AUDIO_EXTENSIONS = {".wav", ".bwf", ".aif", ".aiff", ".flac"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt"}
SIDECAR_EXTENSIONS = {".xml", ".ale", ".edl"}
REPORT_EXTENSIONS = {".json", ".csv"}
NON_MEDIA_REJECTED_EXTENSIONS = {".txt", ".exe"}

CANDIDATE_EXTENSIONS = (
    VIDEO_EXTENSIONS
    | AUDIO_EXTENSIONS
    | SUBTITLE_EXTENSIONS
    | SIDECAR_EXTENSIONS
    | REPORT_EXTENSIONS
)

EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    "EXCLUDED_CACHE",
    "90_temp",
}

SAFE_OUTPUTS = [
    "00_project/project_manifest.json",
    "00_project/processing_status.json",
    "00_project/privacy_report.md",
    "00_project/human_review_index.md",
    "01_media_catalog/media_catalog.json",
    "01_media_catalog/media_catalog.csv",
    "01_media_catalog/media_catalog.md",
    "01_media_catalog/scan_warnings.json",
    "01_media_catalog/manual_media_review.csv",
    "99_logs/processing_log.md",
    "99_logs/errors.json",
    "99_logs/warnings.json",
    "99_logs/privacy_events.json",
]


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _hash_text(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"hash_{digest[:16]}"


def _policy_path(path: Path, input_root: Path, path_policy: str) -> str:
    relative = path.relative_to(input_root).as_posix()
    if path_policy == "local_absolute_path":
        return str(path)
    if path_policy == "local_relative_path":
        return relative
    if path_policy == "hashed_path":
        return _hash_text(relative)
    if path_policy == "redacted_path":
        return f"[REDACTED_LOCAL_PATH]/{path.name}"
    return f"INPUT_ROOT/{relative}"


def _media_type(extension: str) -> str:
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    if extension in SUBTITLE_EXTENSIONS:
        return "subtitle"
    if extension in SIDECAR_EXTENSIONS:
        return "sidecar_metadata"
    if extension in REPORT_EXTENSIONS:
        return "report"
    return "unknown"


def _source_kind(path: Path) -> tuple[str, bool, list[str]]:
    extension = path.suffix.lower()
    file_name = path.name.upper()
    parent_name = path.parent.name.upper()
    local_hint = f"{parent_name} {file_name}"
    warnings: list[str] = []

    if "UNKNOWN" in local_hint or "UNKNOWN_ASSET" in file_name:
        return "unknown", True, ["unknown synthetic placeholder"]

    if "PROXY" in local_hint:
        return "proxy", False, warnings

    if extension in AUDIO_EXTENSIONS:
        return "production_sound", False, warnings

    if extension in VIDEO_EXTENSIONS:
        return "camera_original", False, warnings

    if extension in SUBTITLE_EXTENSIONS:
        return "subtitle", True, ["subtitle requires later-phase validation"]

    if extension in SIDECAR_EXTENSIONS:
        return "sidecar_metadata", True, ["sidecar metadata requires human review"]

    if extension in REPORT_EXTENSIONS:
        return "report", True, ["report-like file requires human review"]

    return "unknown", True, ["unsupported extension"]


def _is_unknown_synthetic_placeholder(path: Path) -> bool:
    file_name = path.name.upper()
    parent_name = path.parent.name.upper()
    local_hint = f"{parent_name} {file_name}"
    return "UNKNOWN" in local_hint or "UNKNOWN_ASSET" in file_name


def _is_candidate_file(path: Path) -> bool:
    return (
        path.suffix.lower() in CANDIDATE_EXTENSIONS
        or _is_unknown_synthetic_placeholder(path)
    )


def _iter_scannable_files(input_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(input_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return files


def _iter_candidate_files(input_root: Path) -> list[Path]:
    return [
        path
        for path in _iter_scannable_files(input_root)
        if _is_candidate_file(path)
    ]


def _count_extensions(paths: list[Path]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in paths:
        extension = path.suffix.lower() or "[no_extension]"
        counts[extension] = counts.get(extension, 0) + 1
    return dict(sorted(counts.items()))


def _extension_semantic_counts(scanned_files: list[Path]) -> dict[str, dict[str, int]]:
    accepted_files = [
        path
        for path in scanned_files
        if path.suffix.lower() in (VIDEO_EXTENSIONS | AUDIO_EXTENSIONS)
    ]
    rejected_files = [
        path
        for path in scanned_files
        if path.suffix.lower() in NON_MEDIA_REJECTED_EXTENSIONS
        or path.suffix.lower() not in CANDIDATE_EXTENSIONS
    ]

    return {
        "accepted_extension_counts": _count_extensions(accepted_files),
        "rejected_extension_counts": _count_extensions(rejected_files),
        "ignored_extension_counts": {},
    }


def _preflight(input_root: Path, output_root: Path, privacy_mode: str, path_policy: str) -> list[str]:
    errors: list[str] = []

    if privacy_mode != "local_only":
        errors.append("privacy mode is not local_only")

    allowed_path_policies = {
        "local_absolute_path",
        "local_relative_path",
        "sanitized_path",
        "hashed_path",
        "redacted_path",
    }
    if path_policy not in allowed_path_policies:
        errors.append("path policy is invalid")

    if not input_root.exists():
        errors.append("--input-root does not exist")
    elif not input_root.is_dir():
        errors.append("--input-root is not a directory")

    if input_root == output_root:
        errors.append("input root equals output root")

    if input_root.exists() and _is_relative_to(output_root, input_root):
        errors.append("output root is inside input root")

    return errors



def _ffprobe_availability_preflight(enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {
            "requested": False,
            "status": "skipped",
            "available": None,
            "warning_code": None,
        }

    if shutil.which("ffprobe") is not None:
        return {
            "requested": True,
            "status": "available",
            "available": True,
            "warning_code": None,
        }

    return {
        "requested": True,
        "status": "missing",
        "available": False,
        "warning_code": "ffprobe_missing",
    }

def _asset_entry(index: int, path: Path, input_root: Path, path_policy: str) -> dict[str, Any]:
    extension = path.suffix.lower()
    source_kind, human_review_required, warnings = _source_kind(path)
    stat = path.stat()

    return {
        "asset_id": f"asset_{index:04d}",
        "media_type": _media_type(extension),
        "source_kind": source_kind,
        "path": _policy_path(path, input_root, path_policy),
        "path_policy": path_policy,
        "file_name": path.name,
        "extension": extension,
        "file_size_bytes": stat.st_size,
        "created_at": None,
        "modified_at": None,
        "technical_metadata": {},
        "privacy": {
            "original_media_left_client_system": False,
            "copied_original_media": False,
            "scanner_local_only": True,
        },
        "warnings": warnings,
        "human_review_required": human_review_required,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "asset_id",
        "media_type",
        "source_kind",
        "path",
        "path_policy",
        "file_name",
        "extension",
        "file_size_bytes",
        "human_review_required",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def _write_outputs(
    output_root: Path,
    project_id: str,
    project_name: str,
    privacy_mode: str,
    path_policy: str,
    assets: list[dict[str, Any]],
    warnings: list[str],
    ffprobe_preflight: dict[str, Any],
    extension_semantic_counts: dict[str, dict[str, int]],
) -> None:
    human_review_assets = [asset for asset in assets if asset["human_review_required"]]

    _write_json(
        output_root / "00_project/project_manifest.json",
        {
            "phase": PHASE,
            "project_id": project_id,
            "project_name": project_name,
            "privacy_mode": privacy_mode,
            "path_policy": path_policy,
            "scanner": "cid-media-agent scan",
            "local_only": True,
            "ffprobe_preflight": ffprobe_preflight,
        },
    )
    _write_json(
        output_root / "00_project/processing_status.json",
        {
            "status": "completed_with_warnings" if warnings or human_review_assets else "completed",
            "candidate_media_count": len(assets),
            "human_review_required_count": len(human_review_assets),
            "ffprobe_preflight": ffprobe_preflight,
            **extension_semantic_counts,
        },
    )
    _write_text(
        output_root / "00_project/privacy_report.md",
        "# Privacy Report\n\nOriginal media never left the client system. No media was copied, modified, transcoded, uploaded, or processed.",
    )
    _write_text(
        output_root / "00_project/human_review_index.md",
        "# Human Review Index\n\n"
        + "\n".join(f"- {asset['asset_id']}: {asset['file_name']}" for asset in human_review_assets),
    )

    _write_json(output_root / "01_media_catalog/media_catalog.json", {"assets": assets})
    _write_csv(output_root / "01_media_catalog/media_catalog.csv", assets)
    _write_text(
        output_root / "01_media_catalog/media_catalog.md",
        "# Media Catalog\n\n"
        + "\n".join(f"- {asset['asset_id']} — {asset['file_name']} — {asset['source_kind']}" for asset in assets),
    )
    _write_json(output_root / "01_media_catalog/scan_warnings.json", {"warnings": warnings})
    _write_csv(output_root / "01_media_catalog/manual_media_review.csv", human_review_assets)

    _write_text(output_root / "99_logs/processing_log.md", "# Processing Log\n\nScanner baseline completed locally.")
    _write_json(output_root / "99_logs/errors.json", {"errors": []})
    _write_json(output_root / "99_logs/warnings.json", {"warnings": warnings})
    _write_json(
        output_root / "99_logs/privacy_events.json",
        {
            "events": [
                {
                    "event": "local_only_scan_completed",
                    "original_media_left_client_system": False,
                }
            ]
        },
    )


def scan(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    input_root = _resolve(Path(args.input_root))
    output_root = _resolve(Path(args.output_root))
    privacy_mode = args.privacy_mode
    path_policy = args.path_policy

    preflight_errors = _preflight(input_root, output_root, privacy_mode, path_policy)
    if preflight_errors:
        return 2, {
            "status": "preflight_error",
            "project_id": args.project_id,
            "privacy_mode": privacy_mode,
            "files_seen": 0,
            "candidate_media_count": 0,
            "warnings_count": len(preflight_errors),
            "human_review_required_count": 0,
            "accepted_extension_counts": {},
            "rejected_extension_counts": {},
            "ignored_extension_counts": {},
            "created_outputs": [],
            "errors": preflight_errors,
            "exit_code": 2,
        }

    ffprobe_preflight = _ffprobe_availability_preflight(args.ffprobe_preflight)

    scanned_files = _iter_scannable_files(input_root)
    extension_semantic_counts = _extension_semantic_counts(scanned_files)
    candidates = [
        path
        for path in scanned_files
        if _is_candidate_file(path)
    ]
    assets = [
        _asset_entry(index, path, input_root, path_policy)
        for index, path in enumerate(candidates, start=1)
    ]

    warnings = sorted(
        {
            warning
            for asset in assets
            for warning in asset["warnings"]
        }
        | (
            {ffprobe_preflight["warning_code"]}
            if ffprobe_preflight["warning_code"]
            else set()
        )
    )
    human_review_required_count = sum(1 for asset in assets if asset["human_review_required"])
    exit_code = 1 if warnings or human_review_required_count else 0
    status = "completed_with_warnings" if exit_code == 1 else "completed"

    if args.dry_run:
        return exit_code, {
            "status": status,
            "project_id": args.project_id,
            "privacy_mode": privacy_mode,
            "files_seen": len(candidates),
            "candidate_media_count": len(candidates),
            "warnings_count": len(warnings),
            "human_review_required_count": human_review_required_count,
            "warnings": warnings,
            "ffprobe_preflight": ffprobe_preflight,
            **extension_semantic_counts,
            "created_outputs": [],
            "planned_outputs": SAFE_OUTPUTS,
            "exit_code": exit_code,
        }

    _write_outputs(
        output_root=output_root,
        project_id=args.project_id,
        project_name=args.project_name,
        privacy_mode=privacy_mode,
        path_policy=path_policy,
        assets=assets,
        warnings=warnings,
        ffprobe_preflight=ffprobe_preflight,
        extension_semantic_counts=extension_semantic_counts,
    )

    return exit_code, {
        "status": status,
        "project_id": args.project_id,
        "privacy_mode": privacy_mode,
        "files_seen": len(candidates),
        "candidate_media_count": len(candidates),
        "warnings_count": len(warnings),
        "human_review_required_count": human_review_required_count,
        "warnings": warnings,
        "ffprobe_preflight": ffprobe_preflight,
        **extension_semantic_counts,
        "created_outputs": SAFE_OUTPUTS,
        "exit_code": exit_code,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cid-media-agent scan")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--project-id", default="synthetic_project")
    parser.add_argument("--project-name", default="Synthetic Project")
    parser.add_argument("--privacy-mode", default="local_only")
    parser.add_argument("--path-policy", default="sanitized_path")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ffprobe-preflight", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--strict-local-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    exit_code, summary = scan(args)

    if args.json_output:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"status={summary['status']}")
        print(f"candidate_media_count={summary['candidate_media_count']}")
        print(f"human_review_required_count={summary['human_review_required_count']}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
