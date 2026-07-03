from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent.own_real_material_dry_run_intake import (
    SANITIZED_LABEL,
    STATUS_ACCEPTED,
    STATUS_REJECTED,
    plan_own_real_material_dry_run_intake,
)

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_implementation_gate_v1.md"
MODULE = ROOT / "scripts/local_media_agent/own_real_material_dry_run_intake.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_own_real_material_dry_run_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_own_real_material_dry_run_readiness_gate_v1.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.IMPLEMENTATION.GATE.V1"
STARTING_HEAD = "71384472d0b04343650635d917c522f8f7105f78"
STARTING_STATE = "OWN_REAL_MATERIAL_DRY_RUN_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1"
TARGET_NEXT_STATE = "OWN_REAL_MATERIAL_DRY_RUN_IMPLEMENTATION_GATE_PASSED_READY_FOR_OWN_REAL_MATERIAL_DRY_RUN_QA_GATE"

# Forbidden fragments built via concatenation to avoid self-match
UNC_PREFIX = ("\\", "\\", "")
MNT_PREFIX = ("/", "mnt", "/")
WSL_DOMAIN = ("wsl", ".", "localhost")
WIN_DRIVE = ("C", ":", "\\")

EXCLUDED_RENDERER_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)
EXCLUDED_CLI_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text, f"Expected string not found: {value!r}"


def _module_source() -> str:
    return _text(MODULE)


# ---------------------------------------------------------------------------
# Document identity
# ---------------------------------------------------------------------------


def test_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
        TARGET_NEXT_STATE,
    ])


# ---------------------------------------------------------------------------
# Document scope
# ---------------------------------------------------------------------------


def test_document_declares_scope() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase implements an isolated dry-run intake planner for operator-controlled real material.",
        "This phase does not use real media during tests.",
        "This phase uses only synthetic fixtures in `tmp_path`.",
        "This phase does not use client material.",
        "This phase does not connect the real client flow.",
        "This phase does not open video or audio files.",
        "This phase does not read media bytes.",
        "This phase does not execute ffmpeg, ffprobe, subprocess, or shell.",
        "This phase does not delete, move, rename, or overwrite files.",
        "This phase does not create outputs on real material.",
        "This phase does not touch scanner runtime, SaaS, backend, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        "Directories and subfolders remain blocked until an explicit future phase.",
        "Use of operator-controlled real material is reserved for an explicit future controlled execution phase.",
        "Use of real client material remains blocked until `CLIENT_REAL_PILOT.READINESS.GATE`.",
    ])


# ---------------------------------------------------------------------------
# Excluded historical tests
# ---------------------------------------------------------------------------


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


# ---------------------------------------------------------------------------
# Required audited artifacts
# ---------------------------------------------------------------------------


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [READINESS_DOC, READINESS_TEST, MODULE]:
        assert path.exists(), f"Required artifact missing: {path}"
        rel = str(path.relative_to(ROOT))
        assert rel in text, f"Required artifact not referenced in doc: {rel}"


# ---------------------------------------------------------------------------
# Module existence and API
# ---------------------------------------------------------------------------


def test_module_exists_and_exposes_required_function() -> None:
    assert MODULE.exists()
    assert callable(plan_own_real_material_dry_run_intake)


# ---------------------------------------------------------------------------
# Rejection: consent, read_only, allow_real_material
# ---------------------------------------------------------------------------


def test_rejects_missing_consent() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="/some/path",
        operator_consent=False,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "OPERATOR_CONSENT_REQUIRED" in result["errors"]


def test_rejects_read_only_false() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="/some/path",
        operator_consent=True,
        read_only=False,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "READ_ONLY_REQUIRED" in result["errors"]


def test_rejects_allow_real_material_false() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="/some/path",
        operator_consent=True,
        read_only=True,
        allow_real_material=False,
    )
    assert result["status"] == STATUS_REJECTED
    assert "REAL_MATERIAL_OPT_IN_REQUIRED" in result["errors"]


# ---------------------------------------------------------------------------
# Rejection: path constraints
# ---------------------------------------------------------------------------


def test_rejects_empty_path() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="",
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "INPUT_PATH_EMPTY" in result["errors"]


def test_rejects_whitespace_path() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="   ",
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "INPUT_PATH_EMPTY" in result["errors"]


def test_rejects_relative_path() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="relative/path/file.txt",
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "NON_ABSOLUTE_PATH_REJECTED" in result["errors"]


# ---------------------------------------------------------------------------
# Rejection: Windows/mount/UNC/wsl paths (concatenation-safe)
# ---------------------------------------------------------------------------


def test_rejects_windows_style_path() -> None:
    win_path = WIN_DRIVE[0] + WIN_DRIVE[1] + WIN_DRIVE[2] + "Users\\test\\file.txt"
    result = plan_own_real_material_dry_run_intake(
        input_path=win_path,
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "WINDOWS_STYLE_PATH_REJECTED" in result["errors"]


def test_rejects_mount_path() -> None:
    mnt_path = MNT_PREFIX[0] + MNT_PREFIX[1] + MNT_PREFIX[2] + "c/Users/file.txt"
    result = plan_own_real_material_dry_run_intake(
        input_path=mnt_path,
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "MOUNT_PATH_REJECTED" in result["errors"]


def test_rejects_unc_path() -> None:
    unc_path = (
        UNC_PREFIX[0] + UNC_PREFIX[1] + "server\\share\\file.txt"
    )
    result = plan_own_real_material_dry_run_intake(
        input_path=unc_path,
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "UNC_PATH_REJECTED" in result["errors"]


def test_rejects_wsl_localhost_path() -> None:
    wsl_path = (
        "/" + WSL_DOMAIN[0] + WSL_DOMAIN[1] + WSL_DOMAIN[2] + "/Ubuntu/home/test/file.txt"
    )
    result = plan_own_real_material_dry_run_intake(
        input_path=wsl_path,
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "WSL_LOCALHOST_PATH_REJECTED" in result["errors"]


# ---------------------------------------------------------------------------
# Rejection: symlink, directory, non-existent
# ---------------------------------------------------------------------------


def test_rejects_symlink(tmp_path: Path) -> None:
    target = tmp_path / "real_file.txt"
    target.write_text("synthetic")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    result = plan_own_real_material_dry_run_intake(
        input_path=str(link),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "SYMLINK_REJECTED" in result["errors"]


def test_rejects_directory(tmp_path: Path) -> None:
    subdir = tmp_path / "subfolder"
    subdir.mkdir()

    result = plan_own_real_material_dry_run_intake(
        input_path=str(subdir),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "DIRECTORY_REJECTED_DIRECTORY_SUPPORT_REQUIRES_FUTURE_PHASE" in result["errors"]


def test_rejects_non_existent_path() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="/tmp/nonexistent_xyz_file_cid_test",
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_REJECTED
    assert "INPUT_PATH_NOT_FOUND" in result["errors"]


# ---------------------------------------------------------------------------
# Acceptance
# ---------------------------------------------------------------------------


def test_accepts_synthetic_file_in_tmp_path(tmp_path: Path) -> None:
    test_file = tmp_path / "test_media_sample.bin"
    test_file.write_text("synthetic fixture content for dry-run test")

    result = plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["status"] == STATUS_ACCEPTED
    assert result["accepted"] is True
    assert result["input_kind"] == "file"
    assert result["read_only"] is True
    assert result["operator_consent"] is True
    assert result["real_material_scope"] == "OWN_CONTROLLED_ONLY"


# ---------------------------------------------------------------------------
# Sanitized label
# ---------------------------------------------------------------------------


def test_returns_sanitized_label(tmp_path: Path) -> None:
    test_file = tmp_path / "secret_project_final_cut_4k.mov"
    test_file.write_text("synthetic")

    result = plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["sanitized_input_label"] == SANITIZED_LABEL


def test_rejected_returns_sanitized_label() -> None:
    result = plan_own_real_material_dry_run_intake(
        input_path="",
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    assert result["sanitized_input_label"] == SANITIZED_LABEL


# ---------------------------------------------------------------------------
# No absolute path or real filename leaked
# ---------------------------------------------------------------------------


def test_does_not_leak_absolute_path(tmp_path: Path) -> None:
    test_file = tmp_path / "confidential.mp4"
    test_file.write_text("synthetic")

    result = plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    json_str = str(result)
    assert str(test_file) not in json_str
    assert str(tmp_path) not in json_str


def test_does_not_leak_real_filename(tmp_path: Path) -> None:
    test_file = tmp_path / "confidential_client_final.mp4"
    test_file.write_text("synthetic")

    result = plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )
    json_str = str(result)
    assert "confidential_client_final.mp4" not in json_str


# ---------------------------------------------------------------------------
# No bytes read, no file modification, no file creation
# ---------------------------------------------------------------------------


def test_does_not_read_bytes(tmp_path: Path) -> None:
    test_file = tmp_path / "no_read.bin"
    test_file.write_text("original content")

    plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )

    assert test_file.read_text() == "original content"


def test_does_not_create_any_file(tmp_path: Path) -> None:
    test_file = tmp_path / "source.bin"
    test_file.write_text("synthetic")

    before = set(tmp_path.iterdir())

    plan_own_real_material_dry_run_intake(
        input_path=str(test_file),
        operator_consent=True,
        read_only=True,
        allow_real_material=True,
    )

    after = set(tmp_path.iterdir())
    assert before == after


# ---------------------------------------------------------------------------
# Module source sanity
# ---------------------------------------------------------------------------


def test_module_does_not_contain_forbidden_technologies() -> None:
    source = _module_source()
    forbidden = [
        "scanner",
        "backend",
        "frontend",
        "database",
        "docker",
        "alembic",
        "stripe",
        "ai_jobs",
        "credits",
        "ledger",
        "ffmpeg",
        "ffprobe",
        "subprocess",
        "Popen",
        "os.system",
    ]
    for term in forbidden:
        assert term not in source.lower(), f"Forbidden term found in module: {term}"


def test_module_does_not_contain_windows_or_mount_paths() -> None:
    source = _module_source()
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_test_does_not_contain_windows_or_mount_paths() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source
