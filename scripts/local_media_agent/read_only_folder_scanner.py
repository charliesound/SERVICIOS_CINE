from __future__ import annotations

import json
import re
import stat
import sys
from pathlib import Path
from typing import Any, TextIO


SCHEMA_VERSION = "cid.local_media_agent.read_only_folder_scanner.v1"
INPUT_LABEL = "SANITIZED_LOCAL_FOLDER_INPUT"
STATUS_COMPLETED = "READ_ONLY_FOLDER_SCAN_COMPLETED"
STATUS_COMPLETED_WITH_WARNINGS = "READ_ONLY_FOLDER_SCAN_COMPLETED_WITH_WARNINGS"
STATUS_REJECTED = "READ_ONLY_FOLDER_SCAN_REJECTED"
STATUS_TRUNCATED = "READ_ONLY_FOLDER_SCAN_TRUNCATED"

MAX_FILES = 5000
MAX_DEPTH = 8
MAX_ERRORS = 100

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"})
AUDIO_EXTENSIONS = frozenset({".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"})
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf"})
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | IMAGE_EXTENSIONS

REPO_ROOT = Path(__file__).resolve().parents[2]


def scan_read_only_folder(input_root: str | Path) -> dict[str, Any]:
    root_result = _validate_input_root(input_root)
    if root_result[0] is None:
        return _manifest(status=STATUS_REJECTED, errors=[root_result[1] or "INPUT_VALIDATION_FAILED"])

    root = root_result[0]
    counters = {
        "files_seen": 0,
        "directories_seen": 0,
        "media_candidates": 0,
        "non_media_files": 0,
        "symlinks_rejected": 0,
        "total_bytes": 0,
        "truncated": False,
    }
    extension_summary: dict[str, int] = {}
    warnings: list[str] = []
    errors: list[str] = []
    max_observed_depth = 0

    stack: list[tuple[Path, int]] = [(root, 0)]
    while stack:
        directory, depth = stack.pop()
        if depth > MAX_DEPTH:
            warnings.append("MAX_DEPTH_ENTRY_SKIPPED")
            continue

        counters["directories_seen"] += 1
        max_observed_depth = max(max_observed_depth, depth)

        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        except OSError:
            _record_error(errors, counters)
            if counters["truncated"]:
                break
            continue

        for child in children:
            child_depth = depth + 1

            if child_depth > MAX_DEPTH:
                warnings.append("MAX_DEPTH_REACHED_ENTRY_SKIPPED")
                continue

            metadata = _safe_stat(child)
            if metadata is None:
                _record_error(errors, counters)
                if counters["truncated"]:
                    break
                continue

            mode = metadata.st_mode
            if stat.S_ISLNK(mode):
                counters["symlinks_rejected"] += 1
                continue

            if stat.S_ISDIR(mode):
                stack.append((child, child_depth))
                continue

            if stat.S_ISREG(mode):
                counters["files_seen"] += 1
                counters["total_bytes"] += int(metadata.st_size)
                extension = child.suffix.lower()
                if extension:
                    extension_summary[extension] = extension_summary.get(extension, 0) + 1

                if extension in MEDIA_EXTENSIONS:
                    counters["media_candidates"] += 1
                else:
                    counters["non_media_files"] += 1
                max_observed_depth = max(max_observed_depth, child_depth)
                if counters["files_seen"] == MAX_FILES:
                    counters["truncated"] = True
                    warnings.append("MAX_FILES_REACHED")
                    break
                continue

            warnings.append("UNSUPPORTED_ENTRY_TYPE_SKIPPED")

        if counters["truncated"]:
            break

    status = STATUS_TRUNCATED if counters["truncated"] else STATUS_COMPLETED
    if status == STATUS_COMPLETED and (warnings or errors):
        status = STATUS_COMPLETED_WITH_WARNINGS

    return _manifest(
        status=status,
        scanner_summary={
            **counters,
            "max_files": MAX_FILES,
            "max_depth": MAX_DEPTH,
            "max_errors": MAX_ERRORS,
            "max_observed_depth": max_observed_depth,
        },
        extension_summary=dict(sorted(extension_summary.items())),
        warnings=_dedupe(warnings),
        errors=_dedupe(errors),
        depth_summary={
            "root_depth": 0,
            "direct_child_depth": 1,
            "max_depth": MAX_DEPTH,
            "max_observed_depth": max_observed_depth,
        },
    )


def manifest_to_json(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":"))


def emit_manifest_json(manifest: dict[str, Any], stream: TextIO | None = None) -> None:
    target = sys.stdout if stream is None else stream
    target.write(manifest_to_json(manifest) + "\n")


def _validate_input_root(input_root: str | Path) -> tuple[Path | None, str | None]:
    if not isinstance(input_root, (str, Path)):
        return None, "INPUT_TYPE_REJECTED"

    raw = str(input_root).strip()
    if not raw:
        return None, "INPUT_EMPTY_REJECTED"
    if _is_url_like(raw):
        return None, "URL_PATH_REJECTED"
    if _is_windows_drive_path(raw):
        return None, "WINDOWS_DRIVE_PATH_REJECTED"
    if _is_unc_path(raw):
        return None, "UNC_PATH_REJECTED"
    if _is_mnt_path(raw):
        return None, "MOUNT_PATH_REJECTED"
    if "wsl.localhost" in raw.lower():
        return None, "WSL_LOCALHOST_PATH_REJECTED"
    if not raw.startswith("/"):
        return None, "RELATIVE_PATH_REJECTED"

    path = Path(raw)
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        return None, "INPUT_RESOLUTION_REJECTED"

    if _is_repo_path(resolved):
        return None, "REPOSITORY_PATH_REJECTED"
    if path.is_symlink():
        return None, "ROOT_SYMLINK_REJECTED"
    if not path.exists():
        return None, "INPUT_ROOT_NOT_FOUND"
    if path.is_file():
        return None, "FILE_ROOT_REJECTED"
    if not path.is_dir():
        return None, "INPUT_ROOT_NOT_DIRECTORY"

    return resolved, None


def _manifest(
    *,
    status: str,
    scanner_summary: dict[str, Any] | None = None,
    extension_summary: dict[str, int] | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    depth_summary: dict[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "input_label": INPUT_LABEL,
        "privacy": {
            "original_media_modified": False,
            "file_contents_opened": False,
            "content_hashes_computed": False,
            "ffprobe_executed": False,
            "ffmpeg_executed": False,
            "subprocess_used": False,
            "network_used": False,
            "database_used": False,
            "saas_used": False,
            "artifact_written": False,
        },
        "scanner_summary": scanner_summary or _empty_summary(),
        "extension_summary": extension_summary or {},
        "warnings": warnings or [],
        "errors": errors or [],
        "depth_summary": depth_summary or {
            "root_depth": 0,
            "direct_child_depth": 1,
            "max_depth": MAX_DEPTH,
            "max_observed_depth": 0,
        },
    }


def _empty_summary() -> dict[str, Any]:
    return {
        "files_seen": 0,
        "directories_seen": 0,
        "media_candidates": 0,
        "non_media_files": 0,
        "symlinks_rejected": 0,
        "total_bytes": 0,
        "truncated": False,
        "max_files": MAX_FILES,
        "max_depth": MAX_DEPTH,
        "max_errors": MAX_ERRORS,
        "max_observed_depth": 0,
    }


def _safe_stat(path: Path) -> Any | None:
    try:
        return path.lstat()
    except OSError:
        return None


def _record_error(errors: list[str], counters: dict[str, Any]) -> None:
    errors.append("FILESYSTEM_METADATA_UNAVAILABLE")
    if len(errors) >= MAX_ERRORS:
        counters["truncated"] = True
        errors.append("MAX_ERRORS_REACHED")


def _dedupe(values: list[str]) -> list[str]:
    return sorted(set(values))


def _is_repo_path(path: Path) -> bool:
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return False
    return True


def _is_url_like(raw: str) -> bool:
    lowered = raw.lower()
    return "://" in lowered or lowered.startswith(("http:", "https:", "ftp:", "s3:", "gs:"))


def _is_windows_drive_path(raw: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:(?:[\\/].*)?$", raw))


def _is_unc_path(raw: str) -> bool:
    return raw.startswith("\\\\") or raw.startswith("//")


def _is_mnt_path(raw: str) -> bool:
    return raw == "/mnt" or raw.startswith("/mnt/")
