from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-contract-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
CONTRACT_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"
)
CONTRACT_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-contract-v1-20260622"
)
CONTRACT_NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)

REQUIRED_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_closure_review_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_closure_review.py"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_v1.md"),
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


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_qa_gate_declares_documentation_only_no_runtime() -> None:
    assert_all_present(read(QA_DOC), [
        "QA gate documentation",
        "document-only QA gate",
        "validates the previous implementation contract",
        "previous implementation contract is closed conceptually",
        "ready only for future implementation planning",
        "no smoke fixture implementation yet",
        "no export implementation yet",
        "no packaging implementation yet",
        "no file writing yet",
        "no artifact generation yet",
        "no export CLI command yet",
        "no runtime implementation",
        "no CLI changes",
        "no renderer changes",
        "no scripts modified",
        "no fixtures modified",
        "no new fixtures",
        "no exported files",
        "no output file writing",
        "no real media",
        "no arbitrary folders",
        "no scanner execution",
        "no real ffprobe execution",
        "no ffmpeg execution",
        "no subprocess/process execution",
        "no audio extraction",
        "no sync",
        "no transcription",
        "no subtitles",
        "no timeline export",
        "no network",
        "no SaaS/DB",
        "no installer",
        "no public demo",
        "no client demo",
        "no sales demo",
        "no production use",
    ])


def test_qa_gate_declares_required_sections() -> None:
    assert_all_present(read(QA_DOC), [
        "## Phase",
        "## Objective",
        "## Previous Closed Phase",
        "## QA Gate Scope",
        "## Required Existing Artifacts",
        "## Validated Implementation Contract Sections",
        "## Validated Future Implementation Constraints",
        "## Validated Privacy and Safety Boundaries",
        "## Validation of Previous Contract Non-Authorizations",
        "## QA Gate Decision",
        "## Functional Result",
        "## Future Target Tag",
        "## Next Microphase",
    ])


def test_required_artifacts_exist() -> None:
    assert CONTRACT_DOC.exists()
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


def test_qa_gate_references_required_artifacts() -> None:
    text = read(QA_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_contract_doc_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        PREVIOUS_PHASE,
        CONTRACT_FUNCTIONAL_RESULT,
        CONTRACT_TARGET_TAG,
        CONTRACT_NEXT_PHASE,
    ])


def test_contract_doc_declares_required_sections() -> None:
    assert_all_present(read(CONTRACT_DOC), [
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


def test_contract_doc_declares_no_authorization_limits() -> None:
    assert_all_present(read(CONTRACT_DOC), [
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


def test_contract_doc_declares_future_controlled_constraints() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "existing controlled synthetic JSON fixture",
        "existing expected visible text fixture",
        "text/plain or markdown/text compatible only if later authorized",
        "text-only output",
        "UTF-8",
        "local-only",
        "non-executable",
        "non-binary",
        "no multimedia",
        "deterministic comparison against expected visible text fixture",
        "no path leakage",
        "no secrets leakage",
        "no username leakage",
        "no environment leakage",
        "no network leakage",
        "no SaaS/DB leakage",
        "safety flags remain false",
    ])


def test_no_forbidden_authorization_phrases_in_qa_gate() -> None:
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
        "smoke fixture implementation is authorized",
        "client export is authorized",
        "production export is authorized",
    ]:
        assert phrase not in text


def test_no_forbidden_authorization_phrases_in_contract() -> None:
    text = read(CONTRACT_DOC).lower()
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
    for path in [QA_DOC, CONTRACT_DOC]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
