from __future__ import annotations

import builtins
import io
import json
from pathlib import Path

import pytest

from scripts.local_media_agent import read_only_folder_scanner as scanner

from _cid_historical_contract_snapshot import snapshot_pyproject_text


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.md"
MODULE = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_IMPLEMENTATION_GATE_V1_CLOSED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.READINESS.GATE.V1"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1"

IMPLEMENTATION_SOURCE_COMMIT = "d53da68a49c853a343b2f5ba41aa7408944bd4e7"

AUTHORIZED_FILES = {
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.md",
    "scripts/local_media_agent/read_only_folder_scanner.py",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py",
}

ALL_MEDIA_EXTENSIONS = (
    scanner.VIDEO_EXTENSIONS | scanner.AUDIO_EXTENSIONS | scanner.IMAGE_EXTENSIONS
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text, f"Expected string not found: {value!r}"


def test_document_exists_and_declares_implementation_gate_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [PHASE, EXPECTED_RESULT, PREVIOUS_PHASE, NEXT_PHASE])


def test_exactly_three_authorized_files_are_declared() -> None:
    text = _text(DOC)
    for path in AUTHORIZED_FILES:
        assert path in text
    assert DOC.exists()
    assert MODULE.exists()
    assert TEST.exists()


def test_document_blocks_cli_entrypoint_packaging_and_product_areas() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "does not create a public CLI",
        "does not create `cid scan`",
        "does not create `cid_cli.py`",
        "does not modify `pyproject.toml`",
        "does not create package entrypoints",
        "does not create installed commands",
        "does not touch backend, frontend, DB, SaaS, Docker, Alembic, Stripe, auth, AI Jobs, or ledger",
    ])


def test_document_records_lstat_stat_mode_and_limit_corrections() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "through `path.lstat()`",
        "`stat.S_ISLNK(st_mode)`",
        "`stat.S_ISDIR(st_mode)`",
        "`stat.S_ISREG(st_mode)`",
        "does not use `child.is_symlink()`, `child.is_dir()`, or `child.is_file()` during traversal",
        "When `files_seen` reaches exactly `max_files`",
        "`MAX_FILES_REACHED` is added",
        "When more than `max_files` files exist, `files_seen` never exceeds `max_files`.",
        "depth greater than `max_depth`, it is rejected before metadata is obtained",
    ])


def test_pyproject_is_not_modified_with_read_only_folder_scanner_entrypoint() -> None:
    text = snapshot_pyproject_text(IMPLEMENTATION_SOURCE_COMMIT)
    assert "read_only_folder_scanner" not in text
    assert "cid scan" not in text
    assert "cid_cli" not in text


def test_public_api_exists_without_argparse_or_entrypoint() -> None:
    assert callable(scanner.scan_read_only_folder)
    assert callable(scanner.manifest_to_json)
    assert callable(scanner.emit_manifest_json)
    source = _text(MODULE)
    assert "argparse" not in source
    assert "if __name__" not in source


def test_valid_empty_folder_returns_sanitized_manifest(tmp_path: Path) -> None:
    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["schema_version"] == scanner.SCHEMA_VERSION
    assert manifest["status"] == scanner.STATUS_COMPLETED
    assert manifest["input_label"] == scanner.INPUT_LABEL
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["directories_seen"] == 1
    assert manifest["scanner_summary"]["media_candidates"] == 0
    assert manifest["scanner_summary"]["non_media_files"] == 0
    assert manifest["scanner_summary"]["total_bytes"] == 0
    assert manifest["extension_summary"] == {}
    assert manifest["warnings"] == []
    assert manifest["errors"] == []


def test_media_non_media_extension_summary_and_case_insensitive_classification(tmp_path: Path) -> None:
    media_upper = tmp_path / "UPPER.MP4"
    media_lower = tmp_path / "sound.wav"
    non_media = tmp_path / "notes.txt"
    no_extension = tmp_path / "README"
    media_upper.write_text("abc", encoding="utf-8")
    media_lower.write_text("abcd", encoding="utf-8")
    non_media.write_text("ab", encoding="utf-8")
    no_extension.write_text("a", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == 4
    assert summary["media_candidates"] == 2
    assert summary["non_media_files"] == 2
    assert summary["media_candidates"] + summary["non_media_files"] == summary["files_seen"]
    assert summary["total_bytes"] == 10
    assert manifest["extension_summary"] == {".mp4": 1, ".txt": 1, ".wav": 1}


def test_v1_allowlist_is_complete() -> None:
    assert scanner.VIDEO_EXTENSIONS == {
        ".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm",
    }
    assert scanner.AUDIO_EXTENSIONS == {
        ".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg",
    }
    assert scanner.IMAGE_EXTENSIONS == {
        ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf",
    }


def test_all_allowlisted_extensions_count_as_media_case_insensitive(tmp_path: Path) -> None:
    for index, extension in enumerate(sorted(ALL_MEDIA_EXTENSIONS)):
        suffix = extension.upper() if index % 2 == 0 else extension
        (tmp_path / f"synthetic_{index}{suffix}").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == len(ALL_MEDIA_EXTENSIONS)
    assert summary["media_candidates"] == len(ALL_MEDIA_EXTENSIONS)
    assert summary["non_media_files"] == 0


def test_directories_seen_depth_and_total_bytes_semantics(tmp_path: Path) -> None:
    child = tmp_path / "child"
    grandchild = child / "grandchild"
    grandchild.mkdir(parents=True)
    (grandchild / "clip.mov").write_text("12345", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]


    assert manifest["depth_summary"]["root_depth"] == 0
    assert manifest["depth_summary"]["direct_child_depth"] == 1
    assert summary["directories_seen"] == 3
    assert summary["files_seen"] == 1
    assert summary["total_bytes"] == 5
    assert summary["max_observed_depth"] == 3


def test_max_depth_does_not_descend_past_limit(tmp_path: Path) -> None:
    current = tmp_path
    for level in range(scanner.MAX_DEPTH + 2):
        current = current / f"level_{level}"
        current.mkdir()
    (current / "too_deep.mp4").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == 0
    assert summary["media_candidates"] == 0
    assert summary["directories_seen"] == scanner.MAX_DEPTH + 1
    assert "MAX_DEPTH_REACHED_ENTRY_SKIPPED" in manifest["warnings"]


def test_file_at_max_depth_plus_one_is_not_processed(tmp_path: Path) -> None:
    current = tmp_path
    for level in range(scanner.MAX_DEPTH):
        current = current / f"level_{level}"
        current.mkdir()
    (current / "too_deep.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["media_candidates"] == 0
    assert manifest["scanner_summary"]["total_bytes"] == 0
    assert "MAX_DEPTH_REACHED_ENTRY_SKIPPED" in manifest["warnings"]


def test_max_files_truncates_controlled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", 2)
    for index in range(4):
        (tmp_path / f"clip_{index}.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert manifest["scanner_summary"]["files_seen"] == 2
    assert manifest["scanner_summary"]["truncated"] is True
    assert "MAX_FILES_REACHED" in manifest["warnings"]


def test_exactly_max_files_truncates_immediately(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", 3)
    for index in range(3):
        (tmp_path / f"clip_{index}.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert manifest["scanner_summary"]["files_seen"] == 3
    assert manifest["scanner_summary"]["truncated"] is True
    assert "MAX_FILES_REACHED" in manifest["warnings"]


def test_more_than_max_files_never_exceeds_limit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", 3)
    for index in range(7):
        (tmp_path / f"clip_{index}.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert manifest["scanner_summary"]["files_seen"] == 3
    assert manifest["scanner_summary"]["files_seen"] <= scanner.MAX_FILES
    assert manifest["scanner_summary"]["media_candidates"] == 3


def test_max_errors_truncates_controlled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_ERRORS", 2)
    for index in range(3):
        (tmp_path / f"broken_{index}.mov").write_text("x", encoding="utf-8")

    def always_fail(path: Path) -> None:
        return None

    monkeypatch.setattr(scanner, "_safe_stat", always_fail)

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["total_bytes"] == 0
    assert manifest["scanner_summary"]["truncated"] is True
    assert "FILESYSTEM_METADATA_UNAVAILABLE" in manifest["errors"]
    assert "MAX_ERRORS_REACHED" in manifest["errors"]


def test_root_symlink_and_internal_symlink_are_rejected(tmp_path: Path) -> None:
    real_root = tmp_path / "real"
    real_root.mkdir()
    (real_root / "clip.mov").write_text("x", encoding="utf-8")
    root_link = tmp_path / "root_link"
    root_link.symlink_to(real_root, target_is_directory=True)

    rejected = scanner.scan_read_only_folder(root_link)
    assert rejected["status"] == scanner.STATUS_REJECTED
    assert rejected["errors"] == ["ROOT_SYMLINK_REJECTED"]

    internal_link = real_root / "internal_link"
    internal_link.symlink_to(real_root / "clip.mov")
    manifest = scanner.scan_read_only_folder(real_root)
    assert manifest["scanner_summary"]["files_seen"] == 1
    assert manifest["scanner_summary"]["symlinks_rejected"] == 1
    assert manifest["scanner_summary"]["total_bytes"] == 1


def test_internal_symlinks_do_not_change_file_directory_or_byte_counts(tmp_path: Path) -> None:
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    real_file = tmp_path / "clip.mov"
    real_file.write_text("abcd", encoding="utf-8")
    (tmp_path / "file_link").symlink_to(real_file)
    (tmp_path / "dir_link").symlink_to(real_dir, target_is_directory=True)

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == 1
    assert summary["directories_seen"] == 2
    assert summary["total_bytes"] == 4
    assert summary["symlinks_rejected"] == 2


def test_invalid_roots_are_rejected_fail_closed(tmp_path: Path) -> None:
    file_root = tmp_path / "file.txt"
    file_root.write_text("x", encoding="utf-8")

    cases = [
        (file_root, "FILE_ROOT_REJECTED"),
        (tmp_path / "missing", "INPUT_ROOT_NOT_FOUND"),
        ("relative/path", "RELATIVE_PATH_REJECTED"),
        ("C:\\Users\\example", "WINDOWS_DRIVE_PATH_REJECTED"),
        ("\\\\server\\share", "UNC_PATH_REJECTED"),
        ("https://example.invalid/folder", "URL_PATH_REJECTED"),
        ("/mnt/c/example", "MOUNT_PATH_REJECTED"),
        ("/home/wsl.localhost/example", "WSL_LOCALHOST_PATH_REJECTED"),
        (ROOT, "REPOSITORY_PATH_REJECTED"),
        (MODULE, "REPOSITORY_PATH_REJECTED"),
    ]
    for raw_path, expected_error in cases:
        manifest = scanner.scan_read_only_folder(raw_path)
        assert manifest["status"] == scanner.STATUS_REJECTED
        assert manifest["errors"] == [expected_error]
        assert manifest["scanner_summary"]["files_seen"] == 0
        assert manifest["scanner_summary"]["directories_seen"] == 0


def test_manifest_is_sanitized_and_contains_no_paths_or_filenames(tmp_path: Path) -> None:
    (tmp_path / "private_name.MOV").write_text("x", encoding="utf-8")
    manifest = scanner.scan_read_only_folder(tmp_path)
    payload = scanner.manifest_to_json(manifest)

    forbidden = [
        str(tmp_path),
        "private_name",
        "private_name.MOV",
        "absolute_path",
        "relative_path",
        "filename",
        "file_name",
        "folder_name",
        "hostname",
        "username",
        "machine_name",
        "symlink_target",
    ]
    for value in forbidden:
        assert value not in payload


def test_privacy_flags_are_false(tmp_path: Path) -> None:
    manifest = scanner.scan_read_only_folder(tmp_path)
    assert manifest["privacy"] == {
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
    }


def test_no_content_opening_is_performed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "clip.mov").write_text("x", encoding="utf-8")

    def forbidden_open(*args, **kwargs):
        raise AssertionError("content opening is forbidden")

    monkeypatch.setattr(builtins, "open", forbidden_open)
    manifest = scanner.scan_read_only_folder(tmp_path)
    assert manifest["scanner_summary"]["files_seen"] == 1


def test_no_artifacts_are_written_and_json_serialization_is_valid(tmp_path: Path) -> None:
    before = sorted(item.name for item in tmp_path.iterdir())
    manifest = scanner.scan_read_only_folder(tmp_path)
    after = sorted(item.name for item in tmp_path.iterdir())

    assert after == before
    payload = scanner.manifest_to_json(manifest)
    assert json.loads(payload) == manifest

    stream = io.StringIO()
    scanner.emit_manifest_json(manifest, stream)
    assert json.loads(stream.getvalue()) == manifest


def test_safe_stat_uses_lstat_and_not_path_stat() -> None:
    class FakePath:
        def __init__(self) -> None:
            self.lstat_called = False

        def lstat(self):
            self.lstat_called = True
            return "LSTAT_RESULT"

        def stat(self):
            raise AssertionError("Path.stat must not be used by _safe_stat")

    fake_path = FakePath()

    assert scanner._safe_stat(fake_path) == "LSTAT_RESULT"
    assert fake_path.lstat_called is True


def test_source_has_no_forbidden_dependencies_or_operations() -> None:
    source = _text(MODULE).lower()
    forbidden = [
        "import argparse",
        "import subprocess",
        "from subprocess",
        "subprocess.",
        "ffprobe(",
        "ffmpeg(",
        "import requests",
        "import httpx",
        "import socket",
        "import sqlalchemy",
        "import psycopg",
        "import magic",
        "import mimetypes",
        "import hashlib",
        ".open(",
        "open(",
        "write_text",
        "write_bytes",
        "touch(",
        "child.is_dir(",
        "child.is_file(",
        "child.is_symlink(",
        "path.stat(",
    ]
    for value in forbidden:
        assert value not in source
    assert "import stat" in source
    assert "path.lstat()" in source
    assert "stat.s_islnk" in source
    assert "stat.s_isdir" in source
    assert "stat.s_isreg" in source


def test_media_candidate_invariant_holds_for_mixed_folder(tmp_path: Path) -> None:
    (tmp_path / "a.mov").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")
    (tmp_path / "c").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["media_candidates"] + summary["non_media_files"] == summary["files_seen"]
