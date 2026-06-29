from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as dry_run_cli,
)
from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export import (
    ALLOWED_EXTENSION,
    ARTIFACT_FORMAT,
    ARTIFACT_TYPE,
    DEFAULT_FILENAME,
    PHASE_ID,
    WRITE_AUTHORIZATION,
    export_controlled_visible_report_text_artifact,
)


ROOT = Path(__file__).resolve().parents[2]

IMPLEMENTATION_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_implementation_readiness_gate_v1.md"
)

DRY_RUN_CLI_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

DRY_RUN_BRIDGE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_write_enabled_export_module_exists() -> None:
    assert IMPLEMENTATION_MODULE_PATH.is_file()


def test_controlled_write_enabled_export_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_readiness_document_names_this_implementation() -> None:
    source = _read(READINESS_DOC_PATH)

    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py" in source
    assert "controlled_text_artifact_write_enabled_export_controlled_implementation.py" in source
    assert "export_controlled_visible_report_text_artifact" in source
    assert "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY" in source


def test_accepted_controlled_fixture_owned_write(tmp_path: Path) -> None:
    visible_report_text = "CID controlled visible report\nStatus: OK\n"
    expected_payload = visible_report_text.encode("utf-8")
    expected_hash = hashlib.sha256(expected_payload).hexdigest()

    result = export_controlled_visible_report_text_artifact(
        visible_report_text=visible_report_text,
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    artifact_path = tmp_path / DEFAULT_FILENAME

    assert artifact_path.is_file()
    assert artifact_path.read_bytes() == expected_payload

    assert result["phase"] == PHASE_ID
    assert result["implementation_version"] == "v1"
    assert result["artifact_type"] == ARTIFACT_TYPE
    assert result["artifact_format"] == ARTIFACT_FORMAT
    assert result["filename"] == DEFAULT_FILENAME
    assert result["extension"] == ALLOWED_EXTENSION
    assert result["write_authorization"] == WRITE_AUTHORIZATION
    assert result["write_requested"] is True
    assert result["write_performed"] is True
    assert result["artifact_created_on_disk"] is True
    assert result["bytes_intended"] == len(expected_payload)
    assert result["bytes_written"] == len(expected_payload)
    assert result["content_sha256_before_write"] == expected_hash
    assert result["content_sha256_after_write"] == expected_hash
    assert result["path_boundary"] == "INSIDE_CONTROLLED_OUTPUT_ROOT"
    assert result["overwrite_policy"] == "NO_OVERWRITE"
    assert result["verification_status"] == "VERIFIED"
    assert result["cleanup_expectation"] == "FIXTURE_OWNED_OUTPUT_CLEANUP_BY_TEST_OWNER"
    assert result["warnings"] == []
    assert result["errors"] == []


@pytest.mark.parametrize(
    ("authorization", "expected_error"),
    [
        (None, "write authorization is missing"),
        ("UNKNOWN", "write authorization is unknown"),
        ("DRY_RUN", "write authorization is dry-run-only"),
        ("CONTROLLED_DRY_RUN_ACCEPTED", "write authorization is dry-run-only"),
    ],
)
def test_write_authorization_rejections(
    tmp_path: Path,
    authorization: str | None,
    expected_error: str,
) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization=authorization,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["verification_status"] == "FAILED_CLOSED"
    assert expected_error in result["errors"]
    assert not (tmp_path / DEFAULT_FILENAME).exists()


def test_missing_output_root_rejection() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=None,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root is missing" in result["errors"]


def test_nonexistent_output_root_rejection(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"

    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=missing_root,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root does not exist" in result["errors"]
    assert not missing_root.exists()


def test_non_directory_output_root_rejection(tmp_path: Path) -> None:
    file_root = tmp_path / "not_a_directory"
    file_root.write_text("not a directory", encoding="utf-8")

    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=file_root,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root is not a directory" in result["errors"]


def test_uncontrolled_output_root_rejection() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root is not controlled" in result["errors"]


@pytest.mark.parametrize(
    ("filename", "expected_error"),
    [
        ("../escape.controlled.txt", "filename contains separators"),
        ("folder/escape.controlled.txt", "filename contains separators"),
        (".hidden.controlled.txt", "filename begins with a dot"),
        ("bad name.controlled.txt", "filename contains unsafe characters"),
        ("controlled_visible_report.txt", "extension is unsupported"),
        ("other.controlled.txt", "filename is unsupported"),
        ("", "filename is missing"),
    ],
)
def test_filename_rejections(tmp_path: Path, filename: str, expected_error: str) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        filename=filename,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert expected_error in result["errors"]


def test_target_already_exists_rejection(tmp_path: Path) -> None:
    artifact = tmp_path / DEFAULT_FILENAME
    artifact.write_text("existing", encoding="utf-8")

    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "target artifact already exists" in result["errors"]
    assert artifact.read_text(encoding="utf-8") == "existing"


def test_empty_content_rejection(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "content is empty" in result["errors"]


def test_non_string_content_rejection(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text=b"binary",  # type: ignore[arg-type]
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "content cannot be encoded as UTF-8" in result["errors"]


def test_utf8_byte_count_and_hash_verification(tmp_path: Path) -> None:
    visible_report_text = "Informe controlado con acentos: acción, cámara, producción.\n"
    payload = visible_report_text.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()

    result = export_controlled_visible_report_text_artifact(
        visible_report_text=visible_report_text,
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["bytes_intended"] == len(payload)
    assert result["bytes_written"] == len(payload)
    assert result["content_sha256_before_write"] == digest
    assert result["content_sha256_after_write"] == digest
    assert (tmp_path / DEFAULT_FILENAME).read_bytes() == payload


def test_no_overwrite_behavior(tmp_path: Path) -> None:
    first = export_controlled_visible_report_text_artifact(
        visible_report_text="First report",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )
    second = export_controlled_visible_report_text_artifact(
        visible_report_text="Second report",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert first["verification_status"] == "VERIFIED"
    assert second["verification_status"] == "FAILED_CLOSED"
    assert "target artifact already exists" in second["errors"]
    assert (tmp_path / DEFAULT_FILENAME).read_text(encoding="utf-8") == "First report"


def test_no_directory_creation_behavior(tmp_path: Path) -> None:
    missing_nested_root = tmp_path / "parent" / "child"

    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=missing_nested_root,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root does not exist" in result["errors"]
    assert not missing_nested_root.exists()


def test_success_safety_flags(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    safety_flags = result["safety_flags"]

    assert safety_flags["file_write_performed"] is True
    assert safety_flags["artifact_created_on_disk"] is True
    assert safety_flags["real_media_access_performed"] is False
    assert safety_flags["scanner_execution_performed"] is False
    assert safety_flags["ffprobe_execution_performed"] is False
    assert safety_flags["ffmpeg_execution_performed"] is False
    assert safety_flags["external_process_execution_performed"] is False
    assert safety_flags["network_access_performed"] is False
    assert safety_flags["saas_or_database_access_performed"] is False
    assert safety_flags["directory_creation_performed"] is False
    assert safety_flags["overwrite_performed"] is False
    assert safety_flags["path_boundary_violation_detected"] is False


def test_failure_safety_flags(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization="UNKNOWN",
    )

    safety_flags = result["safety_flags"]

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert safety_flags["file_write_performed"] is False
    assert safety_flags["artifact_created_on_disk"] is False
    assert safety_flags["real_media_access_performed"] is False
    assert safety_flags["scanner_execution_performed"] is False
    assert safety_flags["ffprobe_execution_performed"] is False
    assert safety_flags["ffmpeg_execution_performed"] is False
    assert safety_flags["external_process_execution_performed"] is False
    assert safety_flags["network_access_performed"] is False
    assert safety_flags["saas_or_database_access_performed"] is False
    assert safety_flags["directory_creation_performed"] is False
    assert safety_flags["overwrite_performed"] is False


def test_deterministic_result_shape(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert list(result.keys()) == [
        "phase",
        "implementation_version",
        "artifact_type",
        "artifact_format",
        "controlled_output_root",
        "artifact_path",
        "filename",
        "extension",
        "write_authorization",
        "write_requested",
        "write_performed",
        "artifact_created_on_disk",
        "bytes_intended",
        "bytes_written",
        "content_sha256_before_write",
        "content_sha256_after_write",
        "path_boundary",
        "overwrite_policy",
        "verification_status",
        "cleanup_expectation",
        "safety_flags",
        "warnings",
        "errors",
    ]


def test_existing_dry_run_cli_remains_unchanged() -> None:
    parser = dry_run_cli.build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert "--dry-run" in option_strings
    assert "--visible-report-text" in option_strings
    assert "--planner-result-json" in option_strings
    assert "--caller-context-json" in option_strings

    for forbidden_option in {
        "--write",
        "--write-enabled",
        "--output",
        "--output-path",
        "--create-dir",
        "--mkdir",
        "--overwrite",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
        "--production",
    }:
        assert forbidden_option not in option_strings


def test_existing_dry_run_bridge_remains_unchanged() -> None:
    source = _read(DRY_RUN_BRIDGE_PATH)

    assert "CONTROLLED_DRY_RUN_ACCEPTED" in source
    assert '"write_requested": False' in source
    assert '"write_performed": False' in source
    assert '"artifact_created_on_disk": False' in source
    assert "Only dry-run mode is supported" in source
    assert "write_requested must remain false" in source


def test_current_dry_run_cli_source_has_no_forbidden_runtime_markers() -> None:
    source = _read(DRY_RUN_CLI_PATH)

    for marker in [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        "open(",
        "Popen",
        "socket",
        "requests",
        "urllib",
        "http.client",
    ]:
        assert marker not in source

    assert "sub" + "process" not in source


def test_implementation_source_has_no_prohibited_runtime_integrations() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    for marker in [
        "Popen",
        "socket",
        "requests",
        "urllib",
        "http.client",
        "scanner_execution_performed = True",
        "network_access_performed = True",
        "saas_or_database_access_performed = True",
        "directory_creation_performed = True",
        "overwrite_performed = True",
    ]:
        assert marker not in source

    assert "sub" + "process" not in source


def test_implementation_does_not_create_directories_or_cleanup_arbitrarily() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    for marker in [
        ".mkdir(",
        ".rmdir(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "shutil",
    ]:
        assert marker not in source
