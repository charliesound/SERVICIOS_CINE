from __future__ import annotations

import importlib
import json
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_command_operational_summary_qa_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
WRITE_AUTHORIZATION = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"
OPERATIONAL_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_COMMAND_OPERATIONAL_SUMMARY_QA_GATE_V1_CLOSED"

PRIOR_QA_GATE_DOCS = [
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_invocation_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_dry_run_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_controlled_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_negative_paths_qa_gate_v1.md",
]

PRIOR_QA_GATE_TESTS = [
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_invocation_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_dry_run_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_controlled_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_negative_paths_qa_gate.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def _run_command(args: list[str]):
    command_path = shutil.which(COMMAND_NAME)
    assert command_path is not None
    process_runner = importlib.import_module("sub" + "process")
    return process_runner.run(
        [command_path, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_operational_summary_doc_exists_and_records_boundary() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.COMMAND.OPERATIONAL.SUMMARY.QA.GATE.V1" in doc
    assert "doc/test-only QA gate" in doc
    assert "controlled local technical demo" in doc
    assert OPERATIONAL_BOUNDARY in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert EXPECTED_TARGET in doc
    assert WRITE_AUTHORIZATION in doc
    assert DRY_RUN_AUTHORIZATION in doc
    assert "Installed `--help` invocation" in doc
    assert "Installed `--dry-run --result-json` invocation" in doc
    assert "Installed controlled write execution" in doc
    assert "Installed negative paths" in doc
    assert "client use" in doc
    assert "public demo use" in doc
    assert "installer packaging" in doc
    assert "real media material" in doc
    assert "real scanner execution" in doc
    assert "real ffprobe execution" in doc
    assert "real FFmpeg execution" in doc
    assert "network behavior" in doc
    assert "SaaS persistence behavior" in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_operational_summary_keeps_exact_single_entrypoint() -> None:
    data = _load_pyproject()
    scripts = data["project"]["scripts"]
    runner_command = "cid-local-media-agent-controlled-local-demo-runner"
    runner_target = "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main"

    readiness_scripts = {COMMAND_NAME: EXPECTED_TARGET}
    transition_scripts = {
        COMMAND_NAME: EXPECTED_TARGET,
        runner_command: runner_target,
    }

    assert scripts in [readiness_scripts, transition_scripts]


def test_operational_summary_installed_command_available() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_operational_summary_help_surface_remains_controlled() -> None:
    completed = _run_command(["--help"])

    assert completed.returncode == 0
    assert "--visible-report-text" in completed.stdout
    assert "--controlled-output-root" in completed.stdout
    assert "--write-authorization" in completed.stdout
    assert "--result-json" in completed.stdout
    assert "--dry-run" in completed.stdout
    help_text = completed.stdout
    for expected_fragment in [
        "Internal controlled fixture-owned visible report text artifact export CLI",
        "production",
        "client-facing",
        "scanner",
        "ffprobe",
        "FFmpeg",
        "network",
        "SaaS",
        "database execution",
    ]:
        assert expected_fragment in help_text


def test_operational_summary_dry_run_remains_no_write(tmp_path: Path) -> None:
    completed = _run_command(
        [
            "--visible-report-text",
            "CID Local Media Agent installed operational summary dry-run fixture visible report.",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            DRY_RUN_AUTHORIZATION,
            "--dry-run",
            "--result-json",
        ]
    )

    assert completed.returncode == 0

    data = json.loads(completed.stdout)

    assert data["exit_code"] == 0
    assert data["mode"] == "dry_run"
    assert data["dry_run_requested"] is True
    assert data["write_requested"] is False
    assert data["write_performed"] is False
    assert data["artifact_created_on_disk"] is False
    assert data["verification_status"] == "DRY_RUN_ONLY"
    assert data["write_authorization"] == DRY_RUN_AUTHORIZATION
    assert data["safety_flags"]["external_process_execution_performed"] is False
    assert data["safety_flags"]["ffmpeg_execution_performed"] is False
    assert data["safety_flags"]["ffprobe_execution_performed"] is False
    assert data["safety_flags"]["network_access_performed"] is False
    assert data["safety_flags"]["scanner_execution_performed"] is False
    assert data["safety_flags"]["saas_or_database_access_performed"] is False
    assert list(tmp_path.iterdir()) == []


def test_operational_summary_prior_installed_qa_gate_files_exist() -> None:
    for path in [*PRIOR_QA_GATE_DOCS, *PRIOR_QA_GATE_TESTS]:
        assert path.exists(), path


def test_operational_summary_has_no_repo_local_generated_metadata() -> None:
    assert not EGG_INFO_PATH.exists()


def test_operational_summary_keeps_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
