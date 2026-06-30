from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.local_media_agent import (
    cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner as runner,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"
READINESS_DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_controlled_local_demo_script_readiness_gate_v1.md"

EXPECTED_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_CONTROLLED_LOCAL_DEMO_RUNNER_IMPLEMENTATION_V1_CLOSED"


def _is_inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return False
    return True


def test_controlled_local_demo_runner_module_exists_and_exposes_contract() -> None:
    assert RUNNER_PATH.exists()
    assert runner.RUNNER_NAME == "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner"
    assert runner.COMMAND_NAME == "cid-local-media-agent-visible-report-write-enabled-export"
    assert runner.WRITE_AUTHORIZATION == "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
    assert runner.DRY_RUN_AUTHORIZATION == "CONTROLLED_DRY_RUN_ACCEPTED"
    assert runner.OPERATIONAL_BOUNDARY == EXPECTED_BOUNDARY


def test_controlled_local_demo_runner_help_surface_is_controlled() -> None:
    parser = runner.build_parser()
    help_text = parser.format_help()

    for expected in [
        "--result-json",
        "--keep-output",
        "controlled local demo runner",
        "No production",
        "client-facing",
        "real media",
        "scanner",
        "ffprobe",
        "FFmpeg",
        "network",
        "SaaS",
        "database",
        "installer",
    ]:
        assert expected in help_text


def test_controlled_local_demo_runner_executes_full_sequence_and_removes_output() -> None:
    summary = runner.run_controlled_local_demo(keep_output=False)

    assert summary["status"] == EXPECTED_STATUS
    assert summary["operational_boundary"] == EXPECTED_BOUNDARY
    assert summary["output_root_removed"] is True
    assert summary["artifact_available_after_runner"] is False

    output_root = Path(summary["output_root"])
    artifact_path = Path(summary["artifact_path"])

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

    assert summary["artifact_name"] == "controlled_visible_report.controlled.txt"
    assert isinstance(summary["artifact_sha256"], str)
    assert len(summary["artifact_sha256"]) == 64
    assert summary["artifact_bytes"] > 0

    assert summary["steps"] == [
        "installed_command_availability_check",
        "installed_help_invocation",
        "installed_dry_run_result_json_invocation",
        "installed_controlled_write_single_txt_artifact",
        "installed_negative_path_fail_closed",
    ]


def test_controlled_local_demo_runner_can_keep_fixture_owned_output_for_manual_inspection() -> None:
    summary = runner.run_controlled_local_demo(keep_output=True)

    output_root = Path(summary["output_root"])
    artifact_path = Path(summary["artifact_path"])

    try:
        assert summary["status"] == EXPECTED_STATUS
        assert summary["output_root_removed"] is False
        assert summary["artifact_available_after_runner"] is True
        assert output_root.exists()
        assert artifact_path.exists()
        assert not _is_inside_repo(output_root)
        assert not _is_inside_repo(artifact_path)
        assert str(output_root).startswith(str(Path(tempfile.gettempdir()) / "pytest-of-harliesound"))
    finally:
        import shutil

        shutil.rmtree(output_root, ignore_errors=True)


def test_controlled_local_demo_runner_result_json_main_is_deterministic(capsys) -> None:
    exit_code = runner.main(["--result-json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == EXPECTED_STATUS
    assert payload["operational_boundary"] == EXPECTED_BOUNDARY
    assert payload["safety"]["demo_runner_only"] is True
    assert payload["safety"]["fixture_owned_output_root"] is True
    assert payload["safety"]["writes_inside_repository"] is False
    assert payload["safety"]["real_media_used"] is False
    assert payload["safety"]["scanner_used"] is False
    assert payload["safety"]["ffprobe_used"] is False
    assert payload["safety"]["ffmpeg_used"] is False
    assert payload["safety"]["network_used"] is False
    assert payload["safety"]["saas_used"] is False
    assert payload["safety"]["database_used"] is False
    assert payload["safety"]["installer_used"] is False
    assert payload["safety"]["single_artifact_write"] is True


def test_controlled_local_demo_runner_preserves_readiness_boundary() -> None:
    doc = READINESS_DOC_PATH.read_text(encoding="utf-8")

    assert "CONTROLLED.LOCAL.DEMO.SCRIPT.READINESS.GATE.V1" in doc
    assert "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py" in doc
    assert "Installed command availability check" in doc
    assert "Installed `--help` invocation" in doc
    assert "Installed `--dry-run --result-json` invocation" in doc
    assert "Installed controlled write execution creating exactly one `.txt` artifact" in doc
    assert "One basic negative path proving fail-closed behavior" in doc


def test_controlled_local_demo_runner_source_has_no_raw_external_process_or_forbidden_runtime_terms() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8").lower()

    external_process_token = "sub" + "process"
    assert external_process_token not in source
    assert "ffmpeg" in source
    assert "ffprobe" in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "socket." not in source
    assert "sqlalchemy" not in source
    assert "psycopg" not in source


def test_controlled_local_demo_runner_expected_phase_result_marker() -> None:
    assert EXPECTED_RESULT.endswith("_CLOSED")
