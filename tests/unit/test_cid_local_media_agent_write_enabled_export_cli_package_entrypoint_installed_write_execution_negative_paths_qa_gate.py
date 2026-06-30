from __future__ import annotations

import importlib
import json
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_negative_paths_qa_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
WRITE_AUTHORIZATION = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"
UNKNOWN_AUTHORIZATION = "UNKNOWN_CONTROLLED_WRITE_TOKEN"
VISIBLE_TEXT = "CID Local Media Agent installed entrypoint negative paths controlled fixture visible report."
EXPECTED_FILENAME = "controlled_visible_report.controlled.txt"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_WRITE_EXECUTION_NEGATIVE_PATHS_QA_GATE_V1_CLOSED"


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


def _assert_common_rejection_safety(data: dict) -> None:
    assert data["exit_code"] == 1
    assert data["artifact_created_on_disk"] is False
    assert data["write_performed"] is False
    assert data["write_requested"] is True
    assert data["safety_flags"]["external_process_execution_performed"] is False
    assert data["safety_flags"]["ffmpeg_execution_performed"] is False
    assert data["safety_flags"]["ffprobe_execution_performed"] is False
    assert data["safety_flags"]["network_access_performed"] is False
    assert data["safety_flags"]["scanner_execution_performed"] is False
    assert data["safety_flags"]["saas_or_database_access_performed"] is False


def test_installed_write_negative_paths_qa_doc_exists_and_records_evidence() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.WRITE_EXECUTION.NEGATIVE.PATHS.QA.GATE.V1" in doc
    assert "doc/test-only QA gate" in doc
    assert "rejects unsafe or incomplete write execution requests" in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert WRITE_AUTHORIZATION in doc
    assert DRY_RUN_AUTHORIZATION in doc
    assert "dry-run authorization is not valid for controlled write" in doc
    assert "unknown write authorization" in doc
    assert "controlled output root is not controlled" in doc
    assert "controlled output root does not exist" in doc
    assert "missing controlled output root" in doc
    assert "missing visible report text" in doc
    assert "empty visible report text" in doc
    assert "missing write authorization" in doc
    assert "target artifact already exists" in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_root_pyproject_still_declares_exact_installed_command_target() -> None:
    data = _load_pyproject()
    assert data["project"]["scripts"] == {COMMAND_NAME: EXPECTED_TARGET}


def test_installed_command_is_available_for_negative_path_checks() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_installed_write_rejects_invalid_authorization_tokens_without_artifact(tmp_path: Path) -> None:
    cases = [
        {
            "name": "dry_run_authorization_used_for_write",
            "root": tmp_path / "dry_run_auth",
            "auth": DRY_RUN_AUTHORIZATION,
            "expected_error": "dry-run authorization is not valid for controlled write",
        },
        {
            "name": "unknown_write_authorization",
            "root": tmp_path / "unknown_auth",
            "auth": UNKNOWN_AUTHORIZATION,
            "expected_error": "unknown write authorization",
        },
    ]

    for case in cases:
        case["root"].mkdir(parents=True, exist_ok=True)

        completed = _run_command(
            [
                "--visible-report-text",
                VISIBLE_TEXT,
                "--controlled-output-root",
                str(case["root"]),
                "--write-authorization",
                case["auth"],
                "--result-json",
            ]
        )

        assert completed.returncode == 1, case["name"]
        data = json.loads(completed.stdout)

        _assert_common_rejection_safety(data)
        assert data["verification_status"] == "REJECTED"
        assert data["mode"] == "controlled_write_rejected"
        assert case["expected_error"] in data["errors"]
        assert not any(case["root"].iterdir())


def test_installed_write_rejects_invalid_output_roots_without_artifact(tmp_path: Path) -> None:
    uncontrolled_root = Path("/tmp/cid_lma_installed_write_negative_paths_uncontrolled_pytest_case")
    missing_root = tmp_path / "missing_root_directory"

    if uncontrolled_root.exists():
        for child in uncontrolled_root.rglob("*"):
            if child.is_file():
                child.unlink()
        for child in sorted(uncontrolled_root.rglob("*"), reverse=True):
            if child.is_dir():
                child.rmdir()
        uncontrolled_root.rmdir()

    uncontrolled_root.mkdir(parents=True)

    cases = [
        {
            "name": "uncontrolled_output_root",
            "args": [
                "--visible-report-text",
                VISIBLE_TEXT,
                "--controlled-output-root",
                str(uncontrolled_root),
                "--write-authorization",
                WRITE_AUTHORIZATION,
                "--result-json",
            ],
            "expected_error": "controlled output root is not controlled",
            "expected_status": "FAILED_CLOSED",
            "root_to_check": uncontrolled_root,
        },
        {
            "name": "missing_output_root_directory",
            "args": [
                "--visible-report-text",
                VISIBLE_TEXT,
                "--controlled-output-root",
                str(missing_root),
                "--write-authorization",
                WRITE_AUTHORIZATION,
                "--result-json",
            ],
            "expected_error": "controlled output root does not exist",
            "expected_status": "FAILED_CLOSED",
            "root_to_check": missing_root,
        },
        {
            "name": "missing_output_root_argument",
            "args": [
                "--visible-report-text",
                VISIBLE_TEXT,
                "--write-authorization",
                WRITE_AUTHORIZATION,
                "--result-json",
            ],
            "expected_error": "missing controlled output root",
            "expected_status": "REJECTED",
            "root_to_check": None,
        },
    ]

    for case in cases:
        completed = _run_command(case["args"])

        assert completed.returncode == 1, case["name"]
        data = json.loads(completed.stdout)

        _assert_common_rejection_safety(data)
        assert data["verification_status"] == case["expected_status"]
        assert case["expected_error"] in data["errors"]

        root_to_check = case["root_to_check"]
        if root_to_check is not None and root_to_check.exists():
            assert not any(root_to_check.rglob("*"))

    uncontrolled_root.rmdir()


def test_installed_write_rejects_missing_or_empty_inputs_without_artifact(tmp_path: Path) -> None:
    cases = [
        {
            "name": "missing_visible_report_text",
            "root": tmp_path / "missing_text",
            "args": [
                "--controlled-output-root",
                str(tmp_path / "missing_text"),
                "--write-authorization",
                WRITE_AUTHORIZATION,
                "--result-json",
            ],
            "expected_error": "missing visible report text",
        },
        {
            "name": "empty_visible_report_text",
            "root": tmp_path / "empty_text",
            "args": [
                "--visible-report-text",
                "",
                "--controlled-output-root",
                str(tmp_path / "empty_text"),
                "--write-authorization",
                WRITE_AUTHORIZATION,
                "--result-json",
            ],
            "expected_error": "empty visible report text",
        },
        {
            "name": "missing_write_authorization",
            "root": tmp_path / "missing_auth",
            "args": [
                "--visible-report-text",
                VISIBLE_TEXT,
                "--controlled-output-root",
                str(tmp_path / "missing_auth"),
                "--result-json",
            ],
            "expected_error": "missing write authorization",
        },
    ]

    for case in cases:
        case["root"].mkdir(parents=True, exist_ok=True)

        completed = _run_command(case["args"])

        assert completed.returncode == 1, case["name"]
        data = json.loads(completed.stdout)

        _assert_common_rejection_safety(data)
        assert data["verification_status"] == "REJECTED"
        assert data["mode"] == "controlled_write_rejected"
        assert case["expected_error"] in data["errors"]
        assert not any(case["root"].iterdir())


def test_installed_write_rejects_overwrite_without_mutating_existing_artifact(tmp_path: Path) -> None:
    first = _run_command(
        [
            "--visible-report-text",
            VISIBLE_TEXT,
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    assert first.returncode == 0
    first_data = json.loads(first.stdout)
    artifact_path = Path(first_data["artifact_path"])

    assert first_data["exit_code"] == 0
    assert first_data["verification_status"] == "VERIFIED"
    assert first_data["write_performed"] is True
    assert artifact_path.exists()
    assert artifact_path.name == EXPECTED_FILENAME

    before_content = artifact_path.read_text(encoding="utf-8")

    second = _run_command(
        [
            "--visible-report-text",
            VISIBLE_TEXT,
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    assert second.returncode == 1
    second_data = json.loads(second.stdout)

    _assert_common_rejection_safety(second_data)
    assert second_data["verification_status"] == "FAILED_CLOSED"
    assert second_data["mode"] == "controlled_write"
    assert "target artifact already exists" in second_data["errors"]
    assert second_data["path_boundary"] == "INSIDE_CONTROLLED_OUTPUT_ROOT"
    assert second_data["safety_flags"]["file_write_performed"] is False
    assert second_data["safety_flags"]["overwrite_performed"] is False

    after_content = artifact_path.read_text(encoding="utf-8")
    assert after_content == before_content

    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert files == [artifact_path]


def test_installed_write_negative_paths_leave_no_repo_local_egg_info() -> None:
    assert not EGG_INFO_PATH.exists()


def test_installed_write_negative_paths_keep_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
