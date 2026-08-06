"""Validate the installed CID entrypoint on a native Windows runner."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXPECTED_ERROR = "WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED"
EXPECTED_SCHEMA = "cid.local_media_agent.read_only_folder_scanner.v1"
EXPECTED_STATUS = "READ_ONLY_FOLDER_SCAN_COMPLETED"
EXPECTED_INPUT_LABEL = "SANITIZED_LOCAL_FOLDER_INPUT"
EXPECTED_PRIVACY_KEYS = (
    "artifact_written",
    "content_hashes_computed",
    "database_used",
    "ffmpeg_executed",
    "ffprobe_executed",
    "file_contents_opened",
    "network_used",
    "original_media_modified",
    "saas_used",
    "subprocess_used",
)
EXPECTED_FILES = (
    "video-one.mp4",
    "video-two.mp4",
    "audio-one.wav",
    "audio-two.wav",
    "audio-three.wav",
    "image-one.jpg",
    "image-two.jpg",
    "notes.txt",
    "metadata.xml",
)
EXPECTED_MEDIA_EXTENSIONS = {".mp4": 2, ".wav": 3, ".jpg": 2}
EXPECTED_OTHER_EXTENSIONS = {".txt": 1, ".xml": 1}
COMMAND_TIMEOUT_SECONDS = 30


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_SECONDS,
        check=False,
        shell=False,
    )


def _assert(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def _snapshot(root: Path) -> dict[str, tuple[str, int, int]]:
    entries: dict[str, tuple[str, int, int]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        metadata = path.stat()
        kind = "directory" if path.is_dir() else "file"
        entries[relative] = (kind, metadata.st_size, metadata.st_mtime_ns)
    return entries


def _create_fixture(root: Path) -> None:
    nested = root / "nested"
    nested.mkdir()
    for name in EXPECTED_FILES[:7]:
        (root / name).touch()
    for name in EXPECTED_FILES[7:]:
        (nested / name).touch()


def _assert_help(cid: str, args: list[str]) -> None:
    result = _run([cid, *args])
    _assert(result.returncode == 0, "WINDOWS_CI_HELP_COMMAND_FAILED")
    _assert(result.stderr == "", "WINDOWS_CI_HELP_STDERR_NOT_EMPTY")


def _validate_success_output(
    output: str,
    root: Path,
    before: dict[str, tuple[str, int, int]],
    after: dict[str, tuple[str, int, int]],
) -> None:
    _assert(str(root) not in output, "SUCCESS_OUTPUT_SYNTHETIC_ROOT_LEAK")
    _assert(not any(name in output for name in EXPECTED_FILES), "SUCCESS_OUTPUT_SYNTHETIC_FILENAME_LEAK")
    payload = json.loads(output)
    _assert(payload["status"] == EXPECTED_STATUS, "WINDOWS_NATIVE_SCAN_STATUS_INVALID")
    _assert(payload["schema_version"] == EXPECTED_SCHEMA, "WINDOWS_NATIVE_SCAN_SCHEMA_INVALID")
    _assert(payload["input_label"] == EXPECTED_INPUT_LABEL, "WINDOWS_NATIVE_SCAN_INPUT_LABEL_INVALID")
    summary = payload["scanner_summary"]
    _assert(summary["files_seen"] == 9, "WINDOWS_NATIVE_SCAN_FILE_COUNT_INVALID")
    _assert(summary["media_candidates"] == 7, "WINDOWS_NATIVE_SCAN_MEDIA_COUNT_INVALID")
    _assert(summary["non_media_files"] == 2, "WINDOWS_NATIVE_SCAN_NON_MEDIA_COUNT_INVALID")
    _assert(summary["total_bytes"] == 0, "WINDOWS_NATIVE_SCAN_TOTAL_BYTES_INVALID")
    _assert(summary["truncated"] is False, "WINDOWS_NATIVE_SCAN_TRUNCATED")
    _assert(payload["errors"] == [], "WINDOWS_NATIVE_SCAN_ERRORS_PRESENT")
    _assert(payload["warnings"] == [], "WINDOWS_NATIVE_SCAN_WARNINGS_PRESENT")
    extensions = payload["extension_summary"]
    _assert(all(extensions.get(key) == value for key, value in EXPECTED_MEDIA_EXTENSIONS.items()), "WINDOWS_NATIVE_SCAN_MEDIA_EXTENSIONS_INVALID")
    _assert(all(extensions.get(key) == value for key, value in EXPECTED_OTHER_EXTENSIONS.items()), "WINDOWS_NATIVE_SCAN_OTHER_EXTENSIONS_INVALID")
    privacy = payload["privacy"]
    _assert(all(privacy.get(key) is False for key in EXPECTED_PRIVACY_KEYS), "WINDOWS_CI_PRIVACY_ASSERTION_FAILED")
    _assert(before == after, "FIXTURE_READ_ONLY_VALIDATION_FAILED")


def _validate_wsl_rejection(cid: str, root: Path) -> None:
    drive, _ = os.path.splitdrive(str(root))
    _assert(drive, "WINDOWS_CI_SYNTHETIC_DRIVE_UNAVAILABLE")
    marker = "CID-Synthetic-Rejection-Path"
    nonexistent = f"{drive}\\{marker}"
    _assert(not Path(nonexistent).exists(), "NONEXISTENT_REJECTION_PATH_ALREADY_EXISTS")
    result = _run(
        [
            cid,
            "scan",
            "--input-root",
            nonexistent,
            "--development-wsl-host-drive",
            drive.rstrip(":"),
        ]
    )
    _assert(result.returncode != 0, "WINDOWS_WSL_FLAG_REJECTION_ACCEPTED")
    _assert(result.stderr == "", "WINDOWS_WSL_FLAG_REJECTION_STDERR_NOT_EMPTY")
    payload = json.loads(result.stdout)
    _assert(payload["errors"] == [EXPECTED_ERROR], "WINDOWS_WSL_FLAG_REJECTION_ERROR_INVALID")
    _assert("INPUT_ROOT_NOT_FOUND" not in result.stdout, "WINDOWS_WSL_FLAG_REJECTION_USED_FILESYSTEM_ERROR")
    _assert(nonexistent not in result.stdout, "WINDOWS_WSL_FLAG_REJECTION_PATH_LEAK")
    _assert(marker not in result.stdout, "WINDOWS_WSL_FLAG_REJECTION_FOLDER_LEAK")
    _assert(drive not in result.stdout, "WINDOWS_WSL_FLAG_REJECTION_DRIVE_LEAK")
    _assert(not Path(nonexistent).exists(), "NONEXISTENT_REJECTION_PATH_CREATED")


def main() -> int:
    if os.name != "nt":
        print("WINDOWS_CI_VALIDATOR_REQUIRES_NATIVE_WINDOWS", file=sys.stderr)
        return 2

    try:
        cid_path = shutil.which("cid")
        _assert(cid_path is not None, "WINDOWS_CID_ENTRYPOINT_NOT_FOUND")
        cid = Path(cid_path)
        _assert(cid.is_file(), "WINDOWS_CID_ENTRYPOINT_NOT_A_FILE")
        _assert(cid.name.lower() == "cid.exe", "WINDOWS_CID_ENTRYPOINT_SUFFIX_INVALID")
        _assert_help(cid_path, ["--help"])
        _assert_help(cid_path, ["scan", "--help"])

        with tempfile.TemporaryDirectory(prefix="CID Synthetic Media Root ") as temporary_root:
            root = Path(temporary_root)
            _create_fixture(root)
            before = _snapshot(root)
            _assert(len(before) == 10, "SYNTHETIC_ENTRY_COUNT_INVALID")
            result = _run([cid_path, "scan", "--input-root", str(root)])
            _assert(result.returncode == 0, "WINDOWS_NATIVE_SCAN_FAILED")
            _assert(result.stderr == "", "WINDOWS_NATIVE_SCAN_STDERR_NOT_EMPTY")
            after = _snapshot(root)
            _validate_success_output(result.stdout, root, before, after)
            _validate_wsl_rejection(cid_path, root)

        print("WINDOWS_CID_ENTRYPOINT_DISCOVERED=True")
        print("WINDOWS_CID_HELP_VALID=True")
        print("WINDOWS_CID_SCAN_HELP_VALID=True")
        print("WINDOWS_NATIVE_SYNTHETIC_SCAN_VALID=True")
        print("WINDOWS_NATIVE_WSL_FLAG_REJECTION_VALID=True")
        print("WINDOWS_NATIVE_READ_ONLY_VALID=True")
        print("WINDOWS_CI_VALIDATION_COMPLETED=True")
        return 0
    except (AssertionError, json.JSONDecodeError, OSError, subprocess.SubprocessError) as exc:
        print(f"WINDOWS_CI_VALIDATION_FAILED:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
