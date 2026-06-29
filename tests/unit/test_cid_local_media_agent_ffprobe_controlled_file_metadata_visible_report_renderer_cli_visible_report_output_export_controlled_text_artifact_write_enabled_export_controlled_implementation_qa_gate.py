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
    PHASE_ID as IMPLEMENTATION_PHASE_ID,
    WRITE_AUTHORIZATION,
    export_controlled_visible_report_text_artifact,
)


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate.py"
)

IMPLEMENTATION_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
)

IMPLEMENTATION_TEST_PATH = ROOT / (
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

QA_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTROLLED."
    "IMPLEMENTATION.QA.GATE.V1"
)

QA_RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CONTROLLED_IMPLEMENTATION_QA_GATE_PASS"
)

PREVIOUS_COMMIT = "75caff738b481f793d6df0eddea9425cf44f3164"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-controlled-impl-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-controlled-impl-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTROLLED."
    "IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        IMPLEMENTATION_MODULE_PATH,
        IMPLEMENTATION_TEST_PATH,
        READINESS_DOC_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_qa_exist(path: Path) -> None:
    assert path.is_file()


@pytest.mark.parametrize(
    "required_text",
    [
        QA_PHASE_ID,
        QA_RESULT_ID,
        PREVIOUS_COMMIT,
        PREVIOUS_TAG,
        TARGET_TAG,
        NEXT_PHASE_ID,
        "This is a doc/test-only QA gate.",
        "This QA gate audits the controlled write-enabled export implementation.",
        "This QA gate does not add runtime implementation.",
        "This QA gate does not modify the controlled write-enabled export implementation.",
        "This QA gate does not modify the current dry-run CLI.",
        "This QA gate does not modify the current dry-run bridge.",
        "This QA gate does not authorize CLI usage.",
        "This QA gate does not authorize client-facing usage.",
        "This QA gate does not authorize production usage.",
    ],
)
def test_qa_gate_declares_scope_lineage_and_result(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target controlled implementation test passed with 33 checks.",
        "current dry-run CLI forbidden marker check passed.",
        "corrected write-enabled implementation safety check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target controlled implementation tag absent locally before tagging.",
        "target controlled implementation tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target controlled implementation test passed with 33 checks.",
        "final implementation readiness gate test passed with 322 checks.",
        "final contract QA closure review test passed with 266 checks.",
        "final contract QA gate test passed with 244 checks.",
        "final contract test passed with 251 checks.",
        "final current dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the implementation exposes `export_controlled_visible_report_text_artifact`.",
        "the implementation uses explicit authorization `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.",
        "the implementation creates only `controlled_visible_report.controlled.txt`.",
        "the implementation accepts controlled visible report text from memory only.",
        "the implementation requires an explicit controlled output root.",
        "the implementation accepts fixture-owned output roots only.",
        "the implementation rejects missing authorization.",
        "the implementation rejects unknown authorization.",
        "the implementation rejects dry-run authorization.",
        "the implementation rejects missing output root.",
        "the implementation rejects nonexistent output root.",
        "the implementation rejects non-directory output root.",
        "the implementation rejects uncontrolled output root.",
        "the implementation rejects unsafe filenames.",
        "the implementation rejects unsupported filenames.",
        "the implementation rejects existing target artifact.",
        "the implementation rejects empty content.",
        "the implementation rejects non-string content.",
        "the implementation writes UTF-8 bytes.",
        "the implementation records intended bytes.",
        "the implementation records written bytes.",
        "the implementation records SHA256 before write.",
        "the implementation records SHA256 after write.",
        "the implementation verifies byte count.",
        "the implementation verifies content hash.",
        "the implementation uses no-overwrite semantics.",
        "the implementation creates no directories.",
        "the implementation performs no arbitrary cleanup.",
        "the implementation performs no scanner execution.",
        "the implementation performs no ffprobe execution.",
        "the implementation performs no FFmpeg execution.",
        "the implementation performs no external process execution.",
        "the implementation performs no network access.",
        "the implementation performs no SaaS or database access.",
        "the implementation does not modify the current dry-run CLI.",
        "the implementation does not modify the current dry-run bridge.",
        "the implementation result shape is deterministic.",
        "the implementation safety flags are explicit and conservative.",
    ],
)
def test_qa_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "phase.",
        "implementation_version.",
        "artifact_type.",
        "artifact_format.",
        "controlled_output_root.",
        "artifact_path.",
        "filename.",
        "extension.",
        "write_authorization.",
        "write_requested.",
        "write_performed.",
        "artifact_created_on_disk.",
        "bytes_intended.",
        "bytes_written.",
        "content_sha256_before_write.",
        "content_sha256_after_write.",
        "path_boundary.",
        "overwrite_policy.",
        "verification_status.",
        "cleanup_expectation.",
        "safety_flags.",
        "warnings.",
        "errors.",
        "`write_performed=True`.",
        "`artifact_created_on_disk=True`.",
        "`file_write_performed=True`.",
        "Those values are accepted only for the single controlled fixture-owned text artifact.",
        "All other operational safety flags must remain false on success.",
    ],
)
def test_qa_result_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "removes explicit authorization.",
        "weakens fixture-owned output root enforcement.",
        "permits uncontrolled output roots.",
        "permits arbitrary paths.",
        "permits path traversal.",
        "permits unsupported filenames.",
        "permits overwrite.",
        "creates directories.",
        "deletes files.",
        "renames files.",
        "replaces files.",
        "performs arbitrary cleanup.",
        "reads real media.",
        "executes scanner code.",
        "executes ffprobe.",
        "executes FFmpeg.",
        "executes external processes.",
        "accesses network.",
        "accesses SaaS or database state.",
        "modifies the dry-run CLI.",
        "modifies the dry-run bridge.",
        "adds client-facing behavior.",
        "adds production behavior.",
        "removes SHA256 verification.",
        "removes byte count verification.",
        "removes deterministic result shape.",
        "removes conservative safety flags.",
    ],
)
def test_qa_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize CLI integration.",
        "This QA gate does not authorize command-line write flags.",
        "This QA gate does not authorize writing outside fixture-owned roots.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize overwrite.",
        "This QA gate does not authorize multiple artifacts.",
        "This QA gate does not authorize arbitrary cleanup.",
        "This QA gate does not authorize real media access.",
        "This QA gate does not authorize scanner execution.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize external process execution.",
        "This QA gate does not authorize network access.",
        "This QA gate does not authorize SaaS integration.",
        "This QA gate does not authorize database integration.",
        "This QA gate does not authorize backend changes.",
        "This QA gate does not authorize frontend changes.",
        "This QA gate does not authorize installer work.",
        "This QA gate does not authorize client-facing demo work.",
        "This QA gate does not authorize public demo work.",
        "This QA gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export implementation is accepted by QA gate." in doc
    assert "The current project now has a controlled fixture-owned write-enabled export primitive." in doc
    assert "The current project remains not ready for CLI write-enabled export." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc


def test_implementation_accepts_single_controlled_fixture_owned_write(tmp_path: Path) -> None:
    content = "QA gate controlled visible report\n"
    payload = content.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()

    result = export_controlled_visible_report_text_artifact(
        visible_report_text=content,
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    artifact_path = tmp_path / DEFAULT_FILENAME

    assert artifact_path.is_file()
    assert artifact_path.read_bytes() == payload

    assert result["phase"] == IMPLEMENTATION_PHASE_ID
    assert result["artifact_type"] == ARTIFACT_TYPE
    assert result["artifact_format"] == ARTIFACT_FORMAT
    assert result["filename"] == DEFAULT_FILENAME
    assert result["extension"] == ALLOWED_EXTENSION
    assert result["write_authorization"] == WRITE_AUTHORIZATION
    assert result["write_requested"] is True
    assert result["write_performed"] is True
    assert result["artifact_created_on_disk"] is True
    assert result["bytes_intended"] == len(payload)
    assert result["bytes_written"] == len(payload)
    assert result["content_sha256_before_write"] == digest
    assert result["content_sha256_after_write"] == digest
    assert result["path_boundary"] == "INSIDE_CONTROLLED_OUTPUT_ROOT"
    assert result["overwrite_policy"] == "NO_OVERWRITE"
    assert result["verification_status"] == "VERIFIED"
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
def test_qa_gate_authorization_rejections(
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
def test_qa_gate_filename_rejections(tmp_path: Path, filename: str, expected_error: str) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        filename=filename,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert expected_error in result["errors"]


def test_qa_gate_rejects_existing_artifact_and_preserves_content(tmp_path: Path) -> None:
    artifact = tmp_path / DEFAULT_FILENAME
    artifact.write_text("existing", encoding="utf-8")

    result = export_controlled_visible_report_text_artifact(
        visible_report_text="new",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "target artifact already exists" in result["errors"]
    assert artifact.read_text(encoding="utf-8") == "existing"


def test_qa_gate_rejects_uncontrolled_output_root() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert "controlled output root is not controlled" in result["errors"]


@pytest.mark.parametrize(
    ("content", "expected_error"),
    [
        ("", "content is empty"),
        (b"binary", "content cannot be encoded as UTF-8"),
    ],
)
def test_qa_gate_content_rejections(
    tmp_path: Path,
    content: object,
    expected_error: str,
) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text=content,  # type: ignore[arg-type]
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert expected_error in result["errors"]


def test_qa_gate_result_shape_is_deterministic(tmp_path: Path) -> None:
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


def test_qa_gate_success_safety_flags_are_conservative(tmp_path: Path) -> None:
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


def test_qa_gate_current_dry_run_cli_still_has_no_write_options() -> None:
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


def test_qa_gate_current_dry_run_bridge_remains_dry_run_only() -> None:
    source = _read(DRY_RUN_BRIDGE_PATH)

    assert "CONTROLLED_DRY_RUN_ACCEPTED" in source
    assert '"write_requested": False' in source
    assert '"write_performed": False' in source
    assert '"artifact_created_on_disk": False' in source
    assert "Only dry-run mode is supported" in source
    assert "write_requested must remain false" in source


def test_qa_gate_current_dry_run_cli_source_has_no_forbidden_runtime_markers() -> None:
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


def test_qa_gate_implementation_source_has_no_prohibited_runtime_integrations() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    for marker in [
        ".mkdir(",
        ".rmdir(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "shutil",
        "Popen",
        "os.system",
        "import subprocess",
        "subprocess.",
        "socket.",
        "requests.",
        "urllib.",
        "http.client",
        "scanner_execution_performed = True",
        "ffprobe_execution_performed = True",
        "ffmpeg_execution_performed = True",
        "external_process_execution_performed = True",
        "network_access_performed = True",
        "saas_or_database_access_performed = True",
        "directory_creation_performed = True",
        "overwrite_performed = True",
    ]:
        assert marker not in source


def test_qa_gate_implementation_source_declares_required_safe_false_flags() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    for marker in [
        '"scanner_execution_performed": False',
        '"ffprobe_execution_performed": False',
        '"ffmpeg_execution_performed": False',
        '"external_process_execution_performed": False',
        '"network_access_performed": False',
        '"saas_or_database_access_performed": False',
        '"directory_creation_performed": False',
        '"overwrite_performed": False',
    ]:
        assert marker in source
