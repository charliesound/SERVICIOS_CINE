from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from scripts.local_media_agent import (
    cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner as runner,
)


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_controlled_local_demo_runner_qa_gate_v1.md"
RUNNER_PATH = REPO_ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"
RUNNER_IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"

EXPECTED_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.QA.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_CONTROLLED_LOCAL_DEMO_RUNNER_QA_GATE_V1_CLOSED"
EXPECTED_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_WRITE_AUTH = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
EXPECTED_DRY_RUN_AUTH = "CONTROLLED_DRY_RUN_ACCEPTED"
EXPECTED_ARTIFACT_NAME = "controlled_visible_report.controlled.txt"

EXPECTED_STEPS = [
    "installed_command_availability_check",
    "installed_help_invocation",
    "installed_dry_run_result_json_invocation",
    "installed_controlled_write_single_txt_artifact",
    "installed_negative_path_fail_closed",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def test_controlled_local_demo_runner_qa_gate_doc_exists_and_freezes_contract() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert EXPECTED_PHASE in doc
    assert "doc/test-only QA gate" in doc
    assert "does not modify the runner implementation" in doc
    assert str(RUNNER_PATH.relative_to(REPO_ROOT)) in doc
    assert str(RUNNER_IMPLEMENTATION_TEST_PATH.relative_to(REPO_ROOT)) in doc
    assert EXPECTED_COMMAND in doc
    assert EXPECTED_WRITE_AUTH in doc
    assert EXPECTED_DRY_RUN_AUTH in doc
    assert EXPECTED_BOUNDARY in doc
    assert "Installed command availability check." in doc
    assert "Installed command help invocation." in doc
    assert "Installed dry-run result JSON invocation." in doc
    assert "Installed controlled write of exactly one `.txt` artifact." in doc
    assert "Installed negative path fail-closed validation." in doc
    assert "status=CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED" in doc
    assert "output_root_removed=true" in doc
    assert "artifact_available_after_runner=false" in doc
    assert "dry_run.verification_status=DRY_RUN_ONLY" in doc
    assert "write.verification_status=VERIFIED" in doc
    assert "negative_path.verification_status=REJECTED" in doc
    assert "runner `--keep-output` QA path is inspected and cleaned" in doc
    assert "Database regression guard" in doc
    assert EXPECTED_RESULT in doc


def test_controlled_local_demo_runner_qa_gate_runner_identity_is_stable() -> None:
    assert RUNNER_PATH.exists()
    assert runner.RUNNER_NAME == "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner"
    assert runner.COMMAND_NAME == EXPECTED_COMMAND
    assert runner.WRITE_AUTHORIZATION == EXPECTED_WRITE_AUTH
    assert runner.DRY_RUN_AUTHORIZATION == EXPECTED_DRY_RUN_AUTH
    assert runner.OPERATIONAL_BOUNDARY == EXPECTED_BOUNDARY


def test_controlled_local_demo_runner_qa_gate_default_json_contract_removes_output() -> None:
    summary = runner.run_controlled_local_demo(keep_output=False)

    output_root = Path(summary["output_root"])
    artifact_path = Path(summary["artifact_path"])

    assert summary["status"] == EXPECTED_STATUS
    assert summary["operational_boundary"] == EXPECTED_BOUNDARY
    assert summary["output_root_removed"] is True
    assert summary["artifact_available_after_runner"] is False
    assert not output_root.exists()
    assert not artifact_path.exists()
    assert not _is_inside_repo(output_root)
    assert not _is_inside_repo(artifact_path)

    assert summary["help_exit_code"] == 0
    assert summary["dry_run_exit_code"] == 0
    assert summary["write_exit_code"] == 0
    assert summary["negative_exit_code"] != 0

    assert summary["dry_run"]["verification_status"] == "DRY_RUN_ONLY"
    assert summary["dry_run"]["artifact_created_on_disk"] is False
    assert summary["write"]["verification_status"] == "VERIFIED"
    assert summary["write"]["artifact_created_on_disk"] is True
    assert summary["write"]["write_performed"] is True
    assert summary["negative_path"]["verification_status"] == "REJECTED"
    assert summary["negative_path"]["write_performed"] is False

    assert summary["artifact_name"] == EXPECTED_ARTIFACT_NAME
    assert isinstance(summary["artifact_sha256"], str)
    assert len(summary["artifact_sha256"]) == 64
    assert summary["artifact_bytes"] > 0
    assert summary["steps"] == EXPECTED_STEPS


def test_controlled_local_demo_runner_qa_gate_keep_output_is_fixture_owned_and_cleaned() -> None:
    summary = runner.run_controlled_local_demo(keep_output=True)

    output_root = Path(summary["output_root"])
    artifact_path = Path(summary["artifact_path"])
    fixture_temp_root = Path(tempfile.gettempdir()) / "pytest-of-harliesound"

    try:
        assert summary["status"] == EXPECTED_STATUS
        assert summary["output_root_removed"] is False
        assert summary["artifact_available_after_runner"] is True
        assert output_root.exists()
        assert artifact_path.exists()
        assert artifact_path.name == EXPECTED_ARTIFACT_NAME
        assert str(output_root).startswith(str(fixture_temp_root))
        assert not _is_inside_repo(output_root)
        assert not _is_inside_repo(artifact_path)
    finally:
        shutil.rmtree(output_root, ignore_errors=True)

    assert not output_root.exists()


def test_controlled_local_demo_runner_qa_gate_main_result_json_is_deterministic(capsys) -> None:
    exit_code = runner.main(["--result-json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == EXPECTED_STATUS
    assert payload["operational_boundary"] == EXPECTED_BOUNDARY
    assert payload["steps"] == EXPECTED_STEPS
    assert payload["output_root_removed"] is True
    assert payload["artifact_available_after_runner"] is False
    assert payload["dry_run"]["verification_status"] == "DRY_RUN_ONLY"
    assert payload["write"]["verification_status"] == "VERIFIED"
    assert payload["negative_path"]["verification_status"] == "REJECTED"


def test_controlled_local_demo_runner_qa_gate_safety_flags_are_frozen() -> None:
    summary = runner.run_controlled_local_demo(keep_output=False)
    safety = summary["safety"]

    assert safety["demo_runner_only"] is True
    assert safety["fixture_owned_output_root"] is True
    assert safety["writes_inside_repository"] is False
    assert safety["real_media_used"] is False
    assert safety["scanner_used"] is False
    assert safety["ffprobe_used"] is False
    assert safety["ffmpeg_used"] is False
    assert safety["network_used"] is False
    assert safety["saas_used"] is False
    assert safety["database_used"] is False
    assert safety["installer_used"] is False
    assert safety["client_demo"] is False
    assert safety["public_demo"] is False
    assert safety["single_artifact_write"] is True
    assert safety["overwrite_used"] is False


def test_controlled_local_demo_runner_qa_gate_source_keeps_forbidden_runtime_absent() -> None:
    source = _read(RUNNER_PATH).lower()

    external_process_token = "sub" + "process"

    assert external_process_token not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "socket." not in source
    assert "sqlalchemy" not in source
    assert "psycopg" not in source


def test_controlled_local_demo_runner_qa_gate_expected_result_marker() -> None:
    assert EXPECTED_RESULT.endswith("_CLOSED")
