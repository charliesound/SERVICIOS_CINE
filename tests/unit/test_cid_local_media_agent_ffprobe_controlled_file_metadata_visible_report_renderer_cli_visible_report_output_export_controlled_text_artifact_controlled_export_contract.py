from pathlib import Path
import re


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract_v1.md"
)
CLOSURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_closure_review_v1.md"
)
QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_v1.md"
)
MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_CONTRACT_"
    "PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-controlled-"
    "export-contract-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.QA.GATE.V1"
)
CLOSURE_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_NEXT_CONTROLLED_CONTRACT"
)
CLOSURE_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-qa-gate-closure-review-v1-20260622"
)
CLOSURE_NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.V1"
)
QA_GATE_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_QA_GATE_PASS_CLOSED"
)
QA_GATE_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-qa-gate-v1-20260622"
)
QA_GATE_NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)
REQUIRED_ARTIFACTS = [
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_closure_review_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_closure_review.py"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"),
]
RESULT_FIELDS = [
    "phase",
    "previous_phase",
    "functional_result",
    "source_payload_path",
    "visible_report_text_sha256",
    "exported_text_sha256",
    "exported_text_line_count",
    "exported_text_byte_count",
    "text_matches_expected",
    "output_path",
    "output_path_is_relative",
    "real_media_used",
    "scanner_executed",
    "ffprobe_executed",
    "ffmpeg_executed",
    "subprocess_executed",
    "network_used",
    "database_used",
    "output_file_written",
    "export_packaging_performed",
    "artifact_generated",
    "cli_executed",
    "renderer_executed_as_process",
    "client_delivery_enabled",
    "production_use_enabled",
]
PROHIBITED_TOKENS = [
    "import subprocess",
    "from subprocess",
    "subprocess.",
    "requests",
    "httpx",
    "socket",
    "urllib",
    "argparse",
    "print(",
    "logging",
    "__main__",
    "ffprobe -",
    "ffmpeg -",
    "os.environ",
    "expanduser",
    "home()",
    "mkdir",
    "write_text",
    "open(",
    "Path.cwd",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_contract_doc_exists_and_exact_phase_is_declared() -> None:
    assert DOC.exists()
    assert PHASE in read(DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_contract_declares_required_sections_and_boundaries() -> None:
    assert_all_present(read(DOC), [
        "## Phase",
        "## Objective",
        "## Previous Closed Phase",
        "## Contract Scope",
        "## Required Existing Artifacts",
        "## Controlled Export Concept",
        "## Future Implementation Requirements",
        "## Required Future Result Contract",
        "## Required Future Safety Flags",
        "## Required Future Privacy Boundaries",
        "## Non-Authorization Boundaries",
        "## Contract Decision",
        "## Functional Result",
        "## Future Target Tag",
        "## Next Microphase",
        "does not implement export",
        "does not write files",
        "does not create artifacts",
        "does not authorize client delivery, public demo, sales demo, or production use",
        "require a later QA gate before any implementation",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = read(DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact
        assert str(artifact) in text


def test_future_result_fields_are_declared() -> None:
    text = read(DOC)
    for field in RESULT_FIELDS:
        assert f"`{field}`" in text


def test_previous_closure_review_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(CLOSURE_DOC), [
        PREVIOUS_PHASE,
        CLOSURE_FUNCTIONAL_RESULT,
        CLOSURE_TARGET_TAG,
        CLOSURE_NEXT_PHASE,
    ])


def test_previous_qa_gate_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_GATE_DOC), [
        PREVIOUS_PHASE.replace(".QA.GATE.CLOSURE.REVIEW.V1", ".QA.GATE.V1"),
        QA_GATE_FUNCTIONAL_RESULT,
        QA_GATE_TARGET_TAG,
        QA_GATE_NEXT_PHASE,
    ])


def test_module_surface_and_prohibited_tokens() -> None:
    source = read(MODULE_PATH)
    assert_all_present(source, [
        "ControlledTextArtifactSmokeFixtureResult",
        "run_controlled_text_artifact_smoke_fixture",
        "compute_text_sha256",
        "normalize_text",
        "CONTROLLED_PAYLOAD_FIXTURE_PATH",
        "EXPECTED_VISIBLE_TEXT_FIXTURE_PATH",
        "RENDERER_MODULE_PATH",
    ])
    for token in PROHIBITED_TOKENS:
        assert token not in source


def test_module_does_not_touch_disallowed_areas() -> None:
    source = read(MODULE_PATH).lower()
    for token in ["frontend", "backend", "alembic", "docker", "stripe", "credit", "ledger", "ai_jobs"]:
        assert token not in source


def test_no_forbidden_authorization_phrases() -> None:
    for text in [read(DOC).lower(), read(MODULE_PATH).lower(), read(CLOSURE_DOC).lower(), read(QA_GATE_DOC).lower()]:
        for phrase in [
            "authorizes real media",
            "authorizes scanner",
            "authorizes ffprobe",
            "authorizes ffmpeg",
            "authorizes audio extraction",
            "authorizes sync",
            "authorizes transcription",
            "authorizes subtitles",
            "authorizes timeline export",
            "authorizes network",
            "authorizes saas",
            "authorizes db",
            "authorizes installer",
            "authorizes production",
            "ready for client",
            "ready for sales demo",
            "ready for public demo",
            "export implementation is authorized",
            "packaging implementation is authorized",
            "file writing is authorized",
            "artifact generation is authorized",
            "client export is authorized",
            "production export is authorized",
        ]:
            assert phrase not in text


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, CLOSURE_DOC, QA_GATE_DOC, MODULE_PATH]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
