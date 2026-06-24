from pathlib import Path


CLOSURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_closure_review_v1.md"
)
QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_IMPLEMENTATION"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-contract-qa-gate-closure-review-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.V1"
)
QA_GATE_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED"
)
QA_GATE_TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-contract-qa-gate-v1-20260622"
)
QA_GATE_NEXT_PHASE = (
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
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_contract_qa_gate.py"),
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


def test_closure_review_doc_exists_and_exact_phase_is_declared() -> None:
    assert CLOSURE_DOC.exists()
    assert PHASE in read(CLOSURE_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
    assert_all_present(read(CLOSURE_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_closure_review_declares_documentation_only_no_runtime() -> None:
    assert_all_present(read(CLOSURE_DOC), [
        "closure review documentation",
        "document-only closure review",
        "validates the previous implementation contract QA gate",
        "previous implementation contract QA gate is closed conceptually",
        "previous implementation contract is validated",
        "ready only for future controlled implementation phase",
        "this phase does not implement anything",
        "does not authorize implementation yet by itself",
        "no smoke fixture implementation in this phase",
        "no export implementation in this phase",
        "no packaging implementation in this phase",
        "no file writing in this phase",
        "no artifact generation in this phase",
        "no export CLI command in this phase",
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


def test_closure_review_declares_required_sections() -> None:
    assert_all_present(read(CLOSURE_DOC), [
        "## Phase",
        "## Objective",
        "## Previous Closed Phase",
        "## Closure Review Scope",
        "## Required Existing Artifacts",
        "## Validated QA Gate Closure",
        "## Validated Implementation Contract Closure",
        "## Validated Future Implementation Readiness",
        "## Non-Authorization Boundaries",
        "## Closure Review Decision",
        "## Functional Result",
        "## Future Target Tag",
        "## Next Microphase",
    ])


def test_required_artifacts_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert CONTRACT_DOC.exists()
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


def test_closure_review_references_required_artifacts() -> None:
    text = read(CLOSURE_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_previous_qa_gate_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(QA_GATE_DOC), [
        PREVIOUS_PHASE,
        QA_GATE_FUNCTIONAL_RESULT,
        QA_GATE_TARGET_TAG,
        QA_GATE_NEXT_PHASE,
    ])


def test_previous_qa_gate_declares_required_sections() -> None:
    assert_all_present(read(QA_GATE_DOC), [
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


def test_previous_contract_phase_result_tag_and_next_are_declared() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        PREVIOUS_PHASE.replace(".QA.GATE.V1", ".V1"),
        CONTRACT_FUNCTIONAL_RESULT,
        CONTRACT_TARGET_TAG,
        CONTRACT_NEXT_PHASE,
    ])


def test_previous_contract_declares_required_sections() -> None:
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


def test_previous_chain_declares_no_authorization_limits() -> None:
    qa_text = read(QA_GATE_DOC)
    contract_text = read(CONTRACT_DOC)
    for item in [
        "document-only implementation contract",
        "document-only QA gate",
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
    ]:
        assert item in qa_text or item in contract_text


def test_no_forbidden_authorization_phrases_in_closure_review() -> None:
    text = read(CLOSURE_DOC).lower()
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


def test_no_forbidden_authorization_phrases_in_previous_qa_gate_and_contract() -> None:
    for text in [read(QA_GATE_DOC).lower(), read(CONTRACT_DOC).lower()]:
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
    for path in [CLOSURE_DOC, QA_GATE_DOC, CONTRACT_DOC]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
