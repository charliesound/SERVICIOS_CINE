from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent import read_only_folder_scanner as scanner


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.md"
MODULE = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.RUNTIME_LIMITS.FAIL_CLOSED_FIX.GATE.V1"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1"
BASE_SHA = "9a10c9dba6d60b359ac5a4c06901b6c9313450ae727f2fb2cb3d761f707bf2fc"

AUTHORIZED_FILES = {
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.md",
    "scripts/local_media_agent/read_only_folder_scanner.py",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_runtime_limits_fail_closed_fix_gate_v1.py",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_doc_contains(values: list[str]) -> None:
    text = _text(DOC)
    for value in values:
        assert value in text


def _assert_runtime_limit_rejected(manifest: dict[str, object], forbidden: list[str]) -> None:
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == [scanner.ERROR_RUNTIME_LIMIT_CONFIGURATION_REJECTED]
    assert manifest["scanner_summary"] == {
        "files_seen": 0,
        "directories_seen": 0,
        "media_candidates": 0,
        "non_media_files": 0,
        "symlinks_rejected": 0,
        "total_bytes": 0,
        "truncated": False,
    }
    payload = scanner.manifest_to_json(manifest)
    assert json.loads(payload) == manifest
    for value in forbidden:
        assert value not in payload


def _forbid_input_and_filesystem(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_input_validation(input_root):
        raise AssertionError("input validation must not run for invalid runtime limits")

    def forbidden_stat(path):
        raise AssertionError("lstat must not run for invalid runtime limits")

    monkeypatch.setattr(scanner, "_validate_input_root", forbidden_input_validation)
    monkeypatch.setattr(scanner, "_safe_stat", forbidden_stat)


def _forbidden_value_fragments(value: object) -> list[str]:
    if value == 0:
        return []
    return [repr(value), str(value)]


def test_document_declares_fix_identity_scope_and_next_phase() -> None:
    assert DOC.exists()
    assert MODULE.exists()
    assert TEST.exists()
    _assert_doc_contains([
        PHASE,
        BASE_SHA,
        "The adversarial QA gate found that monkeypatching `MAX_FILES=0`",
        "before input root validation, path resolution, or filesystem traversal",
        "`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1`",
    ])
    for path in AUTHORIZED_FILES:
        assert path in _text(DOC)
    assert NEXT_PHASE in _text(DOC)


@pytest.mark.parametrize("value", [0, -1, True, None, "5000"])
def test_invalid_max_files_rejects_before_input_or_traversal(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
) -> None:
    monkeypatch.setattr(scanner, "MAX_FILES", value)
    _forbid_input_and_filesystem(monkeypatch)

    manifest = scanner.scan_read_only_folder("/private/input/that/must/not/be/touched")

    _assert_runtime_limit_rejected(manifest, ["/private", "MAX_FILES", *_forbidden_value_fragments(value)])


@pytest.mark.parametrize("value", [0, -1, True, None, "100"])
def test_invalid_max_errors_rejects_before_input_or_traversal(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
) -> None:
    monkeypatch.setattr(scanner, "MAX_ERRORS", value)
    _forbid_input_and_filesystem(monkeypatch)

    manifest = scanner.scan_read_only_folder("/private/input/that/must/not/be/touched")

    _assert_runtime_limit_rejected(manifest, ["/private", "MAX_ERRORS", *_forbidden_value_fragments(value)])


@pytest.mark.parametrize("value", [-1, True, None, "8"])
def test_invalid_max_depth_rejects_before_input_or_traversal(
    monkeypatch: pytest.MonkeyPatch,
    value: object,
) -> None:
    monkeypatch.setattr(scanner, "MAX_DEPTH", value)
    _forbid_input_and_filesystem(monkeypatch)

    manifest = scanner.scan_read_only_folder("/private/input/that/must/not/be/touched")

    _assert_runtime_limit_rejected(manifest, ["/private", "MAX_DEPTH", *_forbidden_value_fragments(value)])


def test_max_depth_zero_is_valid_and_blocks_depth_one_before_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(scanner, "MAX_DEPTH", 0)
    (tmp_path / "clip.mov").write_text("x", encoding="utf-8")
    touched: list[str] = []
    original_safe_stat = scanner._safe_stat

    def recording_safe_stat(path: Path):
        touched.append(path.name)
        return original_safe_stat(path)

    monkeypatch.setattr(scanner, "_safe_stat", recording_safe_stat)

    manifest = scanner.scan_read_only_folder(tmp_path)

    assert manifest["status"] == scanner.STATUS_COMPLETED_WITH_WARNINGS
    assert manifest["scanner_summary"]["directories_seen"] == 1
    assert manifest["scanner_summary"]["files_seen"] == 0
    assert manifest["scanner_summary"]["total_bytes"] == 0
    assert touched == []
    assert manifest["warnings"] == ["MAX_DEPTH_REACHED_ENTRY_SKIPPED"]


def test_normal_runtime_limits_preserve_scanner_behavior(tmp_path: Path) -> None:
    (tmp_path / "clip.MOV").write_text("abcd", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("xy", encoding="utf-8")
    (tmp_path / "NOEXT").write_text("z", encoding="utf-8")

    manifest = scanner.scan_read_only_folder(tmp_path)
    summary = manifest["scanner_summary"]

    assert manifest["status"] == scanner.STATUS_COMPLETED
    assert summary["files_seen"] == 3
    assert summary["media_candidates"] == 1
    assert summary["non_media_files"] == 2
    assert summary["media_candidates"] + summary["non_media_files"] == summary["files_seen"]
    assert summary["total_bytes"] == 7
    assert manifest["extension_summary"] == {".mov": 1, ".txt": 1}


def test_runtime_source_contains_limit_guard_and_no_forbidden_additions() -> None:
    source = _text(MODULE)
    assert "def _runtime_limits_are_valid()" in source
    assert "def _valid_limit" in source
    assert "ERROR_RUNTIME_LIMIT_CONFIGURATION_REJECTED" in source
    assert "_runtime_limits_are_valid()" in source.split("root_result = _validate_input_root", 1)[0]
    for forbidden in [
        "argparse",
        "subprocess.",
        "import subprocess",
        "ffprobe(",
        "ffmpeg(",
        "requests",
        "httpx",
        "socket",
    ]:
        assert forbidden not in source
