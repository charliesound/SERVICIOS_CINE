from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


SYNTHETIC_ROOT = Path("/tmp/cid-synthetic-folder-e2e-v1")
INSTALLED_CID = Path("/opt/SERVICIOS_CINE/.venv/bin/cid")
OWNERSHIP_MARKER = SYNTHETIC_ROOT / ".cid_test_owned"

SYNTHETIC_DIRECTORIES = (
    "video",
    "audio",
    "image",
    "mixed",
    "empty",
    "nested",
    "nested/level01",
    "nested/level01/level02",
)

SYNTHETIC_FILES = (
    ("video", "shot01.MOV"),
    ("video", "shot02.mp4"),
    ("audio", "recorder01.WAV"),
    ("audio", "ambience.flac"),
    ("image", "still01.JPG"),
    ("image", "raw01.dng"),
    ("mixed", "notes.txt"),
    ("mixed", "project.xml"),
    ("mixed", "no_extension"),
    ("nested/level01/level02", "nested_clip.mxf"),
)

LEAK_FORBIDDEN = (
    "/tmp/cid-synthetic-folder-e2e-v1",
    "shot01.MOV",
    "shot02.mp4",
    "recorder01.WAV",
    "ambience.flac",
    "still01.JPG",
    "raw01.dng",
    "notes.txt",
    "project.xml",
    "no_extension",
    "nested_clip.mxf",
)

EXPECTED_MANIFEST = {
    "schema_version": "cid.local_media_agent.read_only_folder_scanner.v1",
    "status": "READ_ONLY_FOLDER_SCAN_COMPLETED",
    "input_label": "SANITIZED_LOCAL_FOLDER_INPUT",
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
    "scanner_summary": {
        "files_seen": 10,
        "directories_seen": 9,
        "media_candidates": 7,
        "non_media_files": 3,
        "symlinks_rejected": 0,
        "total_bytes": 0,
        "truncated": False,
        "max_files": 5000,
        "max_depth": 8,
        "max_errors": 100,
        "max_observed_depth": 4,
    },
    "extension_summary": {
        ".dng": 1,
        ".flac": 1,
        ".jpg": 1,
        ".mov": 1,
        ".mp4": 1,
        ".mxf": 1,
        ".txt": 1,
        ".wav": 1,
        ".xml": 1,
    },
    "warnings": [],
    "errors": [],
    "depth_summary": {
        "root_depth": 0,
        "direct_child_depth": 1,
        "max_depth": 8,
        "max_observed_depth": 4,
    },
}


def _build_synthetic_tree() -> None:
    for relative_dir in SYNTHETIC_DIRECTORIES:
        (SYNTHETIC_ROOT / relative_dir).mkdir(parents=True, exist_ok=True)
    for relative_dir, filename in SYNTHETIC_FILES:
        (SYNTHETIC_ROOT / relative_dir / filename).touch()
    OWNERSHIP_MARKER.touch()


def _run_installed_cid() -> subprocess.CompletedProcess[bytes]:
    env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "PIP_NO_INDEX": "1",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    }
    return subprocess.run(
        [
            str(INSTALLED_CID),
            "scan",
            "--input-root",
            str(SYNTHETIC_ROOT),
        ],
        shell=False,
        cwd="/tmp",
        check=False,
        capture_output=True,
        text=False,
        timeout=30,
        env=env,
    )


def _remove_synthetic_tree(created_by_test: bool) -> None:
    if not created_by_test:
        return
    if str(SYNTHETIC_ROOT) != "/tmp/cid-synthetic-folder-e2e-v1":
        raise AssertionError("refusing to remove an unexpected path")
    if SYNTHETIC_ROOT.exists():
        shutil.rmtree(SYNTHETIC_ROOT)


def test_installed_cid_scan_runs_end_to_end_on_controlled_synthetic_folder() -> None:
    assert not SYNTHETIC_ROOT.exists(), (
        "pre-existing synthetic root must not be removed"
    )

    created = False
    try:
        _build_synthetic_tree()
        created = True

        assert OWNERSHIP_MARKER.exists()
        OWNERSHIP_MARKER.unlink()

        result = _run_installed_cid()

        assert result.returncode == 0
        assert result.stderr == b""
        assert result.stdout != b""

        stdout_text = result.stdout.decode("utf-8", errors="strict")
        assert stdout_text.count("\n") == 1
        assert stdout_text.endswith("\n")

        payload = json.loads(stdout_text)
        assert payload == EXPECTED_MANIFEST

        expected_bytes = (
            json.dumps(
                EXPECTED_MANIFEST,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        assert result.stdout == expected_bytes

        for secret in LEAK_FORBIDDEN:
            assert secret.encode("utf-8") not in result.stdout
            assert secret.encode("utf-8") not in result.stderr

        print("E2E_STDOUT_BEGIN")
        print(result.stdout.decode("utf-8", errors="strict"), end="")
        print("E2E_STDOUT_END")
    finally:
        _remove_synthetic_tree(created)

    assert not SYNTHETIC_ROOT.exists()
