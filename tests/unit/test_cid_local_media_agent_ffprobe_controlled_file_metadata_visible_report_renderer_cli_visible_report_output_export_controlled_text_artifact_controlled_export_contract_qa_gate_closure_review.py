from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract_qa_gate_closure_review_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract_v1.md"
)
CONTRACT_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract.py"
)
QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract_qa_gate_v1.md"
)
QA_GATE_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_contract_qa_gate.py"
)
SMOKE_CLOSURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_closure_review_v1.md"
)
SMOKE_CLOSURE_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_qa_gate_closure_review.py"
)
MODULE_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py"
)
SMOKE_IMPLEMENTATION_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation.py"
)
PAYLOAD_FIXTURE = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"
)
EXPECTED_TEXT_FIXTURE = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"
)
RENDERER_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer.py"
)
CLI_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_CONTRACT_"
    "QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-controlled-export-"
    "contract-qa-gate-closure-review-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.V1"
)
CONTRACT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.V1"
)
CONTRACT_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_CONTRACT_"
    "PASS_READY_FOR_QA_GATE"
)
CONTRACT_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-controlled-"
    "export-contract-v1-20260622"
)
CONTRACT_NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "CONTROLLED.EXPORT.CONTRACT.QA.GATE.V1"
)
QA_GATE_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_CONTRACT_"
    "QA_GATE_PASS_CLOSED"
)
QA_GATE_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-controlled-"
    "export-contract-qa-gate-v1-20260622"
)
QA_GATE_NEXT_PHASE = PHASE

REQUIRED_ARTIFACTS = [
    CONTRACT_DOC,
    CONTRACT_TEST,
    QA_GATE_DOC,
    QA_GATE_TEST,
    SMOKE_CLOSURE_DOC,
    SMOKE_CLOSURE_TEST,
    MODULE_PATH,
    SMOKE_IMPLEMENTATION_TEST,
    PAYLOAD_FIXTURE,
    EXPECTED_TEXT_FIXTURE,
    RENDERER_PATH,
    CLI_PATH,
]
DOC_SECTIONS = [
    "## Phase",
    "## Objective",
    "## Previous Closed Phase",
    "## Closure Review Scope",
    "## Required Existing Artifacts",
    "## Reviewed Contract Closure",
    "## Reviewed QA Gate Closure",
    "## Reviewed Safety Boundaries",
    "## Reviewed Privacy Boundaries",
    "## Reviewed Non-Authorization Boundaries",
    "## Closure Review Decision",
    "## Functional Result",
    "## Future Target Tag",
    "## Next Microphase",
]
CONTRACT_SECTIONS = [
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
]
QA_GATE_SECTIONS = [
    "## Phase",
    "## Objective",
    "## Previous Closed Phase",
    "## QA Gate Scope",
    "## Required Existing Artifacts",
    "## Validated Contract Completeness",
    "## Validated Controlled Export Concept",
    "## Validated Future Implementation Requirements",
    "## Validated Future Result Contract",
    "## Validated Future Safety Flags",
    "## Validated Future Privacy Boundaries",
    "## Validated Non-Authorization Boundaries",
    "## QA Gate Decision",
    "## Functional Result",
    "## Future Target Tag",
    "## Next Microphase",
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
MODULE_SURFACE = [
    "ControlledTextArtifactSmokeFixtureResult",
    "run_controlled_text_artifact_smoke_fixture",
    "compute_text_sha256",
    "normalize_text",
    "CONTROLLED_PAYLOAD_FIXTURE_PATH",
    "EXPECTED_VISIBLE_TEXT_FIXTURE_PATH",
    "RENDERER_MODULE_PATH",
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
DISALLOWED_AREAS = [
    "saas",
    "db",
    "frontend",
    "backend",
    "alembic",
    "docker",
    "stripe",
    "credit",
    "ledger",
    "ai_jobs",
]
FORBIDDEN_AUTHORIZATION_PHRASES = [
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
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_closure_review_doc_exists_and_exact_phase_is_declared() -> None:
    assert DOC.exists()
    assert PHASE in read(DOC)


def test_exact_previous_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_closure_review_declares_required_sections() -> None:
    assert_all_present(read(DOC), DOC_SECTIONS)


def test_closure_review_references_and_requires_existing_artifacts() -> None:
    text = read(DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact
        assert str(artifact) in text


def test_closure_review_declares_contract_and_qa_gate_closure() -> None:
    assert_all_present(read(DOC), [
        "The controlled export contract is closed conceptually",
        "The controlled export contract QA gate is closed conceptually",
        "the chain is ready only for a future explicit controlled export implementation readiness contract",
        "document-only and test-only",
    ])


def test_closure_review_declares_non_authorization_boundaries() -> None:
    assert_all_present(read(DOC), [
        "does not authorize:",
        "export implementation",
        "real export",
        "packaging",
        "file writing",
        "artifact generation",
        "arbitrary path input",
        "real media",
        "scanner execution",
        "real ffprobe execution",
        "ffmpeg execution",
        "subprocess/process execution",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "network",
        "SaaS/DB",
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_contract_doc_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        CONTRACT_PHASE,
        CONTRACT_FUNCTIONAL_RESULT,
        CONTRACT_TARGET_TAG,
        CONTRACT_NEXT_PHASE,
    ])


def test_contract_doc_declares_complete_sections_and_future_result_fields() -> None:
    text = read(CONTRACT_DOC)
    assert_all_present(text, CONTRACT_SECTIONS)
    for field in RESULT_FIELDS:
        assert f"`{field}`" in text


def test_contract_doc_declares_no_export_implementation_or_writing() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "does not implement export",
        "does not write files",
        "does not create artifacts",
        "does not create exported files",
        "does not create output directories",
        "does not authorize client delivery, public demo, sales demo, or production use",
        "does not authorize export implementation, real export, packaging, file writing, artifact generation",
    ])


def test_contract_doc_declares_no_real_export_packaging_or_demos() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "real export",
        "packaging",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
        "require a later QA gate before any implementation",
    ])


def test_qa_gate_doc_phase_previous_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_GATE_DOC), [
        PREVIOUS_PHASE,
        CONTRACT_PHASE,
        QA_GATE_FUNCTIONAL_RESULT,
        QA_GATE_TARGET_TAG,
        QA_GATE_NEXT_PHASE,
    ])


def test_qa_gate_doc_is_document_only_and_validates_contract() -> None:
    assert_all_present(read(QA_GATE_DOC), [
        "document-only QA gate",
        "validates the previous controlled export contract",
        "The previous controlled export contract is closed conceptually",
        "does not implement export",
    ])


def test_qa_gate_doc_declares_complete_sections_and_non_authorization() -> None:
    text = read(QA_GATE_DOC)
    assert_all_present(text, QA_GATE_SECTIONS)
    assert_all_present(text, [
        "does not authorize export implementation, real export, packaging, file writing, artifact generation, client delivery, public demo, sales demo, or production use",
        "does not authorize:",
        "export implementation",
        "real export",
        "packaging",
        "file writing",
        "artifact generation",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_module_surface_and_prohibited_tokens_are_stable() -> None:
    source = read(MODULE_PATH)
    assert_all_present(source, MODULE_SURFACE)
    for token in PROHIBITED_TOKENS:
        assert token not in source


def test_module_does_not_touch_disallowed_areas() -> None:
    source = read(MODULE_PATH).lower()
    for token in DISALLOWED_AREAS:
        assert token not in source


def test_no_forbidden_authorization_phrases() -> None:
    texts = [
        read(DOC).lower(),
        read(CONTRACT_DOC).lower(),
        read(QA_GATE_DOC).lower(),
        read(MODULE_PATH).lower(),
    ]
    for text in texts:
        for phrase in FORBIDDEN_AUTHORIZATION_PHRASES:
            assert phrase not in text


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, CONTRACT_DOC, QA_GATE_DOC, MODULE_PATH]:
        assert forbidden_prefix not in read(path)
