from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-contract-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)

REQUIRED_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_closure_review_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_closure_review.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract_qa_gate_v1.md"),
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


def test_doc_exists_and_exact_phase_is_declared() -> None:
    assert DOC.exists()
    assert PHASE in read(DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_doc_declares_document_only_implementation_contract() -> None:
    assert_all_present(read(DOC), [
        "document-only implementation contract",
        "does not implement smoke fixture yet",
        "does not implement export yet",
        "does not implement packaging yet",
        "does not write output files",
        "does not create exported files",
        "does not create new fixtures",
        "no runtime implementation",
        "no CLI changes",
        "no renderer changes",
        "no scripts modified",
        "no fixtures modified",
        "does not execute the CLI",
        "does not execute the renderer",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not use subprocess/process execution",
        "does not use real media",
        "does not use arbitrary folders",
        "does not use scanner",
        "does not use network",
        "does not use SaaS/DB",
    ])


def test_doc_does_not_authorize_blocked() -> None:
    assert_all_present(read(DOC), [
        "smoke fixture implementation yet",
        "export implementation yet",
        "packaging implementation yet",
        "file writing yet",
        "artifact generation yet",
        "export CLI command yet",
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_doc_declares_required_sections() -> None:
    assert_all_present(read(DOC), [
        "## Phase",
        "## Objective",
        "## Previous Closed Phase",
        "## Implementation Contract Scope",
        "## Required Existing Artifacts",
        "## Future Implementation Contract",
        "## Allowed Future Controlled Inputs",
        "## Allowed Future Controlled Outputs",
        "## Deterministic Validation Contract",
        "## Privacy and Safety Contract",
        "## Non-Authorization Boundaries",
        "## Functional Result",
        "## Future Target Tag",
        "## Next Microphase",
    ])


def test_required_artifacts_exist() -> None:
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


def test_doc_references_required_artifacts() -> None:
    text = read(DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_doc_declares_future_contract_constraints() -> None:
    assert_all_present(read(DOC), [
        "will use only existing controlled synthetic JSON fixture",
        "will use only existing expected visible text fixture",
        "text/plain or markdown/text compatible",
        "deterministic comparison against expected visible text fixture",
        "output text-only",
        "UTF-8",
        "local-only",
        "non-executable",
        "non-binary",
        "no multimedia",
        "no timeline",
        "no subtitles",
        "no transcription",
        "no real media",
        "no client material",
        "no real shoot names",
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


def test_no_forbidden_authorization_phrases() -> None:
    text = read(DOC).lower()
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
        "smoke fixture implementation is authorized",
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
    assert forbidden_prefix not in read(DOC)
