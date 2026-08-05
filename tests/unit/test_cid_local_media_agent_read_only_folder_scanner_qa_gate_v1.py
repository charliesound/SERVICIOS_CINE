from __future__ import annotations

import hashlib
import io
import json
import os
import socket
import stat
from pathlib import Path

import pytest

from scripts.local_media_agent import read_only_folder_scanner as scanner

from _cid_historical_contract_snapshot import snapshot_pyproject_text


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py"
RUNTIME = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.RUNTIME_LIMITS.FAIL_CLOSED_FIX.GATE.V1"
IMPLEMENTATION_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.CLOSURE.REVIEW.GATE.V1"
ORIGINAL_RUNTIME_SHA256 = "9a10c9dba6d60b359ac5a4c06901b6c9313450ae727f2fb2cb3d761f707bf2fc"
EXPECTED_RUNTIME_SHA256 = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"

QA_GATE_SOURCE_COMMIT = "fb8b82eb375370d7aca271846ac181cf9736ba9b"

AUTHORIZED_FILES = {
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.md",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_qa_gate_v1.py",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _runtime_source() -> str:
    return _text(RUNTIME)


def _runtime_sha256() -> str:
    return hashlib.sha256(RUNTIME.read_bytes()).hexdigest()


def _manifest_text(manifest: dict[str, object]) -> str:
    return scanner.manifest_to_json(manifest)


def _assert_manifest_shape(manifest: dict[str, object]) -> None:
    assert set(manifest) == {
        "schema_version",
        "status",
        "input_label",
        "privacy",
        "scanner_summary",
        "extension_summary",
        "warnings",
        "errors",
        "depth_summary",
    }
    summary = manifest["scanner_summary"]
    assert isinstance(summary, dict)
    for key in [
        "files_seen",
        "directories_seen",
        "media_candidates",
        "non_media_files",
        "symlinks_rejected",
        "total_bytes",
        "max_files",
        "max_depth",
        "max_errors",
        "max_observed_depth",
    ]:
        assert isinstance(summary[key], int)
        assert summary[key] >= 0
    assert isinstance(summary["truncated"], bool)


def _assert_accepted_invariants(manifest: dict[str, object]) -> None:
    _assert_manifest_shape(manifest)
    summary = manifest["scanner_summary"]
    assert summary["media_candidates"] + summary["non_media_files"] == summary["files_seen"]
    assert summary["total_bytes"] >= 0
    assert summary["directories_seen"] >= 1
    for extension in manifest["extension_summary"]:
        assert extension.startswith(".")
        assert extension == extension.lower()
        assert "/" not in extension
        assert "\\" not in extension


def _assert_no_private_text(manifest: dict[str, object], forbidden: list[str]) -> None:
    payload = _manifest_text(manifest)
    for value in forbidden:
        assert value not in payload


def _assert_rejected(raw_input: object, expected_error: str) -> None:
    manifest = scanner.scan_read_only_folder(raw_input)
    _assert_manifest_shape(manifest)
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == [expected_error]
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["directories_seen"] == 0
    raw_text = str(raw_input)
    if raw_text:
        _assert_no_private_text(manifest, [raw_text])


def test_qa_document_identity_scope_and_next_phase() -> None:
    assert DOC.exists()
    assert TEST.exists()
    text = _text(DOC)
    for value in [
        PHASE,
        PREVIOUS_PHASE,
        IMPLEMENTATION_PHASE,
        NEXT_PHASE,
        ORIGINAL_RUNTIME_SHA256,
        EXPECTED_RUNTIME_SHA256,
    ]:
        assert value in text
    for path in AUTHORIZED_FILES:
        assert path in text
    assert "does not modify the runtime" in text
    assert "does not create a CLI" in text
    assert "does not modify `pyproject.toml`" in text


def test_runtime_sha_constants_preserve_original_and_current_evidence() -> None:
    assert ORIGINAL_RUNTIME_SHA256 == "9a10c9dba6d60b359ac5a4c06901b6c9313450ae727f2fb2cb3d761f707bf2fc"
    assert EXPECTED_RUNTIME_SHA256 == "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
    assert ORIGINAL_RUNTIME_SHA256 != EXPECTED_RUNTIME_SHA256


def test_runtime_integrity_api_stdlib_and_no_entrypoint() -> None:
    assert _runtime_sha256() == EXPECTED_RUNTIME_SHA256
    assert callable(scanner.scan_read_only_folder)
    assert callable(scanner.manifest_to_json)
    assert callable(scanner.emit_manifest_json)

    source = _runtime_source().lower()
    forbidden = [
        "argparse",
        "click",
        "typer",
        "if __name__",
        "import requests",
        "import httpx",
        "import socket",
        "import subprocess",
        "from subprocess",
        "sqlalchemy",
        "psycopg",
        "ffprobe(",
        "ffmpeg(",
        "write_text",
        "write_bytes",
        ".open(",
        "open(",
        "touch(",
    ]
    for value in forbidden:
        assert value not in source
    assert "import stat" in source


def test_pyproject_has_no_cli_packaging_for_scanner() -> None:
    text = snapshot_pyproject_text(QA_GATE_SOURCE_COMMIT)
    assert "read_only_folder_scanner" not in text
    assert "cid scan" not in text
    assert "cid_cli" not in text


def test_input_fail_closed_rejections_are_sanitized(tmp_path: Path) -> None:
    file_root = tmp_path / "private_file.mov"
    file_root.write_text("x", encoding="utf-8")
    symlink_root = tmp_path / "private_link"
    symlink_root.symlink_to(tmp_path, target_is_directory=True)

    cases = [
        (None, "INPUT_TYPE_REJECTED"),
        (123, "INPUT_TYPE_REJECTED"),
        (object(), "INPUT_TYPE_REJECTED"),
        ("", "INPUT_EMPTY_REJECTED"),
        ("   ", "INPUT_EMPTY_REJECTED"),
        ("relative/private", "RELATIVE_PATH_REJECTED"),
        (file_root, "FILE_ROOT_REJECTED"),
        (tmp_path / "missing_private", "INPUT_ROOT_NOT_FOUND"),
        (symlink_root, "ROOT_SYMLINK_REJECTED"),
        ("C:\\Users\\private", "WINDOWS_DRIVE_PATH_REJECTED"),
        ("\\\\private-server\\share", "UNC_PATH_REJECTED"),
        ("https://private.invalid/folder", "URL_PATH_REJECTED"),
        ("/mnt/c/private", "MOUNT_PATH_REJECTED"),
        ("/home/wsl.localhost/private", "WSL_LOCALHOST_PATH_REJECTED"),
        (ROOT, "REPOSITORY_PATH_REJECTED"),
        (RUNTIME, "REPOSITORY_PATH_REJECTED"),
    ]
    for raw_input, expected_error in cases:
        _assert_rejected(raw_input, expected_error)


def test_resolution_failure_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    original_resolve = Path.resolve

    def failing_resolve(self: Path, *args, **kwargs):
        if str(self) == "/tmp/private_ambiguous_root":
            raise OSError("raw /tmp/private_ambiguous_root leaked")
        return original_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", failing_resolve)
    manifest = scanner.scan_read_only_folder("/tmp/private_ambiguous_root")

    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == ["INPUT_RESOLUTION_REJECTED"]
    _assert_no_private_text(manifest, ["private_ambiguous_root", "raw", "/tmp"])


def test_traversal_source_uses_lstat_and_not_path_stat_or_child_helpers() -> None:
    source = _runtime_source()
    traversal = source.split("for child in children:", 1)[1].split("def manifest_to_json", 1)[0]
    assert "metadata = _safe_stat(child)" in traversal
    assert "stat.S_ISLNK" in traversal
    assert "stat.S_ISDIR" in traversal
    assert "stat.S_ISREG" in traversal
    for forbidden in ["child.is_dir(", "child.is_file(", "child.is_symlink(", "child.stat(", "Path.stat"]:
        assert forbidden not in traversal


def test_symlinks_to_file_folder_and_loop_are_not_followed(tmp_path: Path) -> None:
    real_file = tmp_path / "clip.mov"
    real_file.write_text("abcd", encoding="utf-8")
    real_dir = tmp_path / "real_dir"
    real_dir.mkdir()
    (real_dir / "nested.mov").write_text("xx", encoding="utf-8")
    (tmp_path / "file_link").symlink_to(real_file)
    (tmp_path / "dir_link").symlink_to(real_dir, target_is_directory=True)
    (tmp_path / "loop_link").symlink_to(tmp_path, target_is_directory=True)

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == 2
    assert summary["directories_seen"] == 2
    assert summary["total_bytes"] == 6
    assert summary["symlinks_rejected"] == 3
    assert summary["max_observed_depth"] <= 2


def test_depth_boundaries_and_warning_deduplication(tmp_path: Path) -> None:
    current = tmp_path
    for index in range(scanner.MAX_DEPTH - 1):
        current = current / f"level_{index}"
        current.mkdir()
    exactly_at_limit = current / "at_limit.mov"
    exactly_at_limit.write_text("x", encoding="utf-8")
    too_deep_dir = current / "at_limit_dir"
    too_deep_dir.mkdir()
    too_deep_file = too_deep_dir / "too_deep.mov"
    too_deep_file.write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert manifest["depth_summary"]["root_depth"] == 0
    assert manifest["depth_summary"]["direct_child_depth"] == 1
    assert summary["files_seen"] == 1
    assert summary["media_candidates"] == 1
    assert summary["max_observed_depth"] == scanner.MAX_DEPTH
    assert manifest["warnings"].count("MAX_DEPTH_REACHED_ENTRY_SKIPPED") == 1


def test_depth_skip_happens_before_metadata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    current = tmp_path
    for index in range(scanner.MAX_DEPTH):
        current = current / f"level_{index}"
        current.mkdir()
    skipped = current / "skipped.mov"
    skipped.write_text("x", encoding="utf-8")
    original_safe_stat = scanner._safe_stat
    touched: list[str] = []

    def recording_safe_stat(path: Path):
        touched.append(path.name)
        return original_safe_stat(path)

    monkeypatch.setattr(scanner, "_safe_stat", recording_safe_stat)
    manifest = scanner.scan_read_only_folder(tmp_path)

    assert "skipped.mov" not in touched
    assert manifest["scanner_summary"]["files_seen"] == 0


def test_max_files_zero_is_blocked_or_fails_controlled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", 0)
    (tmp_path / "must_not_process.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] in {scanner.STATUS_REJECTED, scanner.STATUS_TRUNCATED}
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["truncated"] is True or manifest["status"] == scanner.STATUS_REJECTED


def test_exactly_max_files_and_more_than_max_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", 3)
    for index in range(5):
        (tmp_path / f"clip_{index}.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert summary["files_seen"] == 3
    assert summary["files_seen"] <= scanner.MAX_FILES
    assert summary["truncated"] is True
    assert "MAX_FILES_REACHED" in manifest["warnings"]


def test_exactly_max_errors_stops_and_sanitizes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scanner, "MAX_ERRORS", 2)
    for index in range(4):
        (tmp_path / f"private_error_{index}.mov").write_text("x", encoding="utf-8")
    calls = {"count": 0}

    def failing_safe_stat(path: Path):
        calls["count"] += 1
        return None

    monkeypatch.setattr(scanner, "_safe_stat", failing_safe_stat)
    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_TRUNCATED
    assert calls["count"] == 2
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["truncated"] is True
    assert manifest["errors"] == ["FILESYSTEM_METADATA_UNAVAILABLE", "MAX_ERRORS_REACHED"]
    _assert_no_private_text(manifest, ["private_error", "OSError"])


def test_directory_iterdir_oserror_is_sanitized(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    original_iterdir = Path.iterdir

    def failing_iterdir(self: Path):
        if self == tmp_path:
            raise OSError("raw private iterdir failure")
        return original_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", failing_iterdir)
    manifest = scanner.scan_read_only_folder(tmp_path)

    _assert_manifest_shape(manifest)
    assert manifest["status"] == scanner.STATUS_COMPLETED_WITH_WARNINGS
    assert manifest["errors"] == ["FILESYSTEM_METADATA_UNAVAILABLE"]
    _assert_no_private_text(manifest, ["raw private", str(tmp_path)])


def test_lstat_oserror_is_sanitized(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "private_lstat.mov").write_text("x", encoding="utf-8")
    original_lstat = Path.lstat

    def failing_lstat(self: Path):
        if self.name == "private_lstat.mov":
            raise OSError("raw private_lstat.mov failure")
        return original_lstat(self)

    monkeypatch.setattr(Path, "lstat", failing_lstat)
    manifest = scanner.scan_read_only_folder(tmp_path)

    _assert_manifest_shape(manifest)
    assert manifest["errors"] == ["FILESYSTEM_METADATA_UNAVAILABLE"]
    _assert_no_private_text(manifest, ["private_lstat", "raw", "failure"])


def test_supported_and_unsupported_entry_types(tmp_path: Path) -> None:
    regular = tmp_path / "UPPER.MOV"
    no_extension = tmp_path / "NOEXTENSION"
    disallowed = tmp_path / "notes.private"
    directory = tmp_path / "folder_private"
    regular.write_text("abcd", encoding="utf-8")
    no_extension.write_text("x", encoding="utf-8")
    disallowed.write_text("xy", encoding="utf-8")
    directory.mkdir()
    (tmp_path / "private_symlink").symlink_to(regular)

    fifo_created = False
    fifo_path = tmp_path / "private_fifo"
    if hasattr(os, "mkfifo"):
        os.mkfifo(fifo_path)
        fifo_created = True

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert summary["files_seen"] == 3
    assert summary["media_candidates"] == 1
    assert summary["non_media_files"] == 2
    assert summary["directories_seen"] == 2
    assert summary["symlinks_rejected"] == 1
    assert summary["total_bytes"] == 7
    assert manifest["extension_summary"] == {".mov": 1, ".private": 1}
    if fifo_created:
        assert "UNSUPPORTED_ENTRY_TYPE_SKIPPED" in manifest["warnings"]


def test_accepted_counter_invariants_across_scenarios(tmp_path: Path) -> None:
    (tmp_path / "a.mov").write_text("x", encoding="utf-8")
    (tmp_path / "b.TXT").write_text("xx", encoding="utf-8")
    (tmp_path / "c").write_text("xxx", encoding="utf-8")
    (tmp_path / "subdir").mkdir()
    manifest = scanner.scan_read_only_folder(tmp_path)

    _assert_accepted_invariants(manifest)
    assert manifest["extension_summary"] == {".mov": 1, ".txt": 1}


def test_privacy_absence_of_paths_names_hosts_and_raw_exceptions(tmp_path: Path) -> None:
    private_dir = tmp_path / "secret_folder_name"
    private_dir.mkdir()
    (private_dir / "secret_clip_name.MOV").write_text("x", encoding="utf-8")
    target = tmp_path / "target.mov"
    target.write_text("x", encoding="utf-8")
    symlink = tmp_path / "secret_symlink_name"
    symlink.symlink_to(target)

    manifest = scanner.scan_read_only_folder(tmp_path)
    private_fragments = [
        str(tmp_path),
        tmp_path.name,
        "secret_folder_name",
        "secret_clip_name",
        "secret_symlink_name",
        "target.mov",
        os.getenv("USER", ""),
        socket.gethostname(),
        "OSError",
        "Traceback",
    ]
    _assert_no_private_text(manifest, [value for value in private_fragments if value])
    assert all(value is False for value in manifest["privacy"].values())


def test_serialization_is_deterministic_stream_based_and_non_mutating(tmp_path: Path) -> None:
    (tmp_path / "clip.mov").write_text("x", encoding="utf-8")
    manifest = scanner.scan_read_only_folder(tmp_path)
    before = json.loads(json.dumps(manifest, sort_keys=True))
    first = scanner.manifest_to_json(manifest)
    second = scanner.manifest_to_json(manifest)

    assert first == second
    assert json.loads(first) == manifest
    stream = io.StringIO()
    scanner.emit_manifest_json(manifest, stream)
    assert stream.getvalue().endswith("\n")
    assert stream.getvalue().count("\n") == 1
    assert json.loads(stream.getvalue()) == manifest
    assert before == manifest
    assert sorted(item.name for item in tmp_path.iterdir()) == ["clip.mov"]
