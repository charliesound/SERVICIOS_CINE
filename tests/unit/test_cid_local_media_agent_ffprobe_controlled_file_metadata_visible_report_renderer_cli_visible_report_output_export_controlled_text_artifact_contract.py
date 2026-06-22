from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_contract_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTRACT.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.READINESS.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTRACT_PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-contract-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTRACT.QA.GATE.V1"
)

REQUIRED_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_integration_readiness_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_integration_readiness_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_readiness_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_readiness_contract_qa_gate_v1.md"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"),
    Path("tests/fixtures/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py"),
    Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_markdown_exists_and_declares_exact_phase() -> None:
    assert QA_DOC.exists()
    assert PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_document_is_contract_only_no_runtime() -> None:
    assert_all_present(read(QA_DOC), [
        "document-contract only",
        "no runtime implementation",
        "no CLI changes",
        "no renderer changes",
        "does not modify existing scripts",
        "does not modify existing fixtures",
        "does not execute the CLI",
        "does not execute the renderer",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not use subprocess/process execution",
        "does not use real media",
        "does not use scanner",
        "does not use arbitrary folders",
        "does not use network",
        "does not use SaaS/DB",
    ])


def test_document_declares_no_export_no_packaging_no_files() -> None:
    assert_all_present(read(QA_DOC), [
        "does not implement export",
        "does not implement packaging",
        "does not create exported files",
        "does not write new output files",
    ])


def test_document_does_not_authorize_blocked() -> None:
    assert_all_present(read(QA_DOC), [
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
        "export implementation",
        "export CLI command",
        "report packaging implementation",
        "file writing",
        "artifact generation",
    ])


def test_required_sections_are_present() -> None:
    assert_all_present(read(QA_DOC), [
        "## Controlled Text Artifact Scope",
        "## Required Previous Closed Phases",
        "## Required Existing Artifacts",
        "## Controlled Text Artifact Definition",
        "## Controlled Text Artifact Criteria",
        "## Future Controlled Export Constraints",
        "## Non-Authorization Boundaries",
        "## Functional Result",
        "## Next Microphase",
    ])


def test_document_references_required_artifacts() -> None:
    text = read(QA_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_required_artifacts_exist() -> None:
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


def test_controlled_text_artifact_definition_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "text-only artifact",
        "controlled synthetic JSON",
        "pure renderer",
        "semantically equivalent",
        "UTF-8",
        "deterministic",
        "human-readable",
        "local-only",
        "non-executable",
        "non-binary",
        "non-multimedia",
        "non-timeline",
        "non-subtitles",
        "non-transcription",
        "without real media",
        "without client material",
        "without real shoot names",
        "no path leakage",
        "no secrets leakage",
        "no username leakage",
        "no environment leakage",
        "no network leakage",
        "no SaaS/DB leakage",
        "safety flags remain false",
        "no external process",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no scanner execution",
        "no media processing",
    ])


def test_future_export_constraints_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "controlled JSON fixture",
        "only produce text",
        "controlled test/fixture",
        "not read real media",
        "not execute ffprobe/ffmpeg",
        "not make network calls",
        "not write to DB/SaaS",
        "not produce client deliverables",
    ])


def test_document_does_not_authorize_forbidden_phrases() -> None:
    text = read(QA_DOC).lower()
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


def test_test_file_does_not_import_or_execute_runtime() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "scripts",
        "from " + "scripts",
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process.",
        "request" + "s",
        "sock" + "et",
        "htt" + "px",
        "url" + "lib",
        "ff" + "probe -",
        "ff" + "mpeg -",
    ]
    for token in forbidden:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    assert forbidden_prefix not in read(QA_DOC)
