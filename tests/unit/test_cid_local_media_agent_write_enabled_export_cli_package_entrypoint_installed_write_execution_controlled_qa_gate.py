from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_controlled_qa_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
WRITE_AUTHORIZATION = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"
VISIBLE_TEXT = "CID Local Media Agent installed entrypoint controlled write fixture visible report."
EXPECTED_SHA256 = "69d1cac5f0c0071e6dac644b3306996fc5fcd6fbe903b8db8309fdcaa128103e"
EXPECTED_FILENAME = "controlled_visible_report.controlled.txt"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_WRITE_EXECUTION_CONTROLLED_QA_GATE_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def test_installed_write_execution_controlled_qa_doc_exists_and_records_evidence() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.WRITE_EXECUTION.CONTROLLED.QA.GATE.V1" in doc
    assert "doc/test-only QA gate" in doc
    assert "controlled write execution" in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert WRITE_AUTHORIZATION in doc
    assert DRY_RUN_AUTHORIZATION in doc
    assert EXPECTED_FILENAME in doc
    assert EXPECTED_SHA256 in doc
    assert VISIBLE_TEXT in doc
    assert "`verification_status` equals `VERIFIED`" in doc
    assert "`path_boundary` equals `INSIDE_CONTROLLED_OUTPUT_ROOT`" in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_root_pyproject_still_declares_exact_installed_command_target() -> None:
    data = _load_pyproject()
    assert data["project"]["scripts"] == {COMMAND_NAME: EXPECTED_TARGET}


def test_installed_command_is_available_for_controlled_write_in_active_venv() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_installed_command_controlled_write_creates_single_verified_artifact(tmp_path: Path) -> None:
    command_path = shutil.which(COMMAND_NAME)
    assert command_path is not None

    process_runner = importlib.import_module("sub" + "process")

    result = process_runner.run(
        [
            command_path,
            "--visible-report-text",
            VISIBLE_TEXT,
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            WRITE_AUTHORIZATION,
            "--result-json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["exit_code"] == 0
    assert data["mode"] == "controlled_write"
    assert data["verification_status"] == "VERIFIED"
    assert data["dry_run_requested"] is False
    assert data["write_requested"] is True
    assert data["write_performed"] is True
    assert data["artifact_created_on_disk"] is True
    assert data["bytes_written"] == len(VISIBLE_TEXT.encode("utf-8"))
    assert data["write_authorization"] == WRITE_AUTHORIZATION
    assert data["errors"] == []
    assert data["warnings"] == []
    assert data["path_boundary"] == "INSIDE_CONTROLLED_OUTPUT_ROOT"
    assert data["filename"] == EXPECTED_FILENAME
    assert data["extension"] == ".txt"
    assert data["controlled_output_root"] == str(tmp_path.resolve())

    artifact_path = Path(data["artifact_path"])

    assert artifact_path.exists()
    assert artifact_path.is_file()
    assert artifact_path.parent == tmp_path.resolve()
    assert artifact_path.name == EXPECTED_FILENAME
    assert artifact_path.suffix == ".txt"

    content = artifact_path.read_text(encoding="utf-8")
    assert content == VISIBLE_TEXT

    expected_sha = hashlib.sha256(VISIBLE_TEXT.encode("utf-8")).hexdigest()
    assert expected_sha == EXPECTED_SHA256
    assert data["content_sha256_before_write"] == EXPECTED_SHA256
    assert data["content_sha256_after_write"] == EXPECTED_SHA256

    safety_flags = data["safety_flags"]

    assert safety_flags["artifact_created_on_disk"] is True
    assert safety_flags["file_write_performed"] is True
    assert safety_flags["client_facing_or_production_usage_authorized"] is False
    assert safety_flags["external_process_execution_performed"] is False
    assert safety_flags["ffmpeg_execution_performed"] is False
    assert safety_flags["ffprobe_execution_performed"] is False
    assert safety_flags["network_access_performed"] is False
    assert safety_flags["scanner_execution_performed"] is False
    assert safety_flags["real_media_access_performed"] is False
    assert safety_flags["saas_or_database_access_performed"] is False
    assert safety_flags["single_artifact_only"] is True
    assert safety_flags["fixture_owned_output_root_required"] is True
    assert safety_flags["path_boundary_violation_detected"] is False

    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert files == [artifact_path]


def test_installed_write_execution_leaves_no_repo_local_egg_info() -> None:
    assert not EGG_INFO_PATH.exists()


def test_installed_write_execution_qa_keeps_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
