from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_v1.md"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.READINESS.CONTRACT.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-export-controlled-text-artifact-smoke-controlled-"
    "fixture-implementation-readiness-contract-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT."
    "SMOKE.CONTROLLED.FIXTURE.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)

CONTRACT_FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_SMOKE_CONTROLLED_FIXTURE_"
    "IMPLEMENTATION_READINESS_CONTRACT_PASS_READY_FOR_QA_GATE"
)

REQUIRED_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_v1.md"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract.py"),
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
        "does not implement smoke fixture",
        "does not implement export",
        "does not implement packaging",
        "does not create exported files",
        "does not create new fixtures",
        "does not write new output files",
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


def test_qa_gate_does_not_authorize_blocked() -> None:
    assert_all_present(read(QA_DOC), [
        "does not authorize installer",
        "does not authorize public demo",
        "does not authorize client demo",
        "does not authorize sales demo",
        "does not authorize production use",
        "does not authorize export implementation",
        "does not authorize export CLI command",
        "does not authorize report packaging implementation",
        "does not authorize file writing",
        "does not authorize artifact generation",
        "does not authorize smoke fixture implementation",
    ])


def test_qa_gate_declares_validated_items() -> None:
    assert_all_present(read(QA_DOC), [
        "Implementation Readiness Scope",
        "Required Previous Closed Phases",
        "Required Existing Artifacts",
        "Implementation Readiness Definition",
        "Implementation Readiness Criteria",
        "Future Implementation Constraints",
        "Non-Authorization Boundaries",
        "Functional Result",
        "Next Microphase",
    ])


def test_contract_doc_exists_and_declares_phase_and_result() -> None:
    assert CONTRACT_DOC.exists()
    assert_all_present(read(CONTRACT_DOC), [
        PREVIOUS_PHASE,
        CONTRACT_FUNCTIONAL_RESULT,
        "Implementation Readiness Scope",
        "Required Previous Closed Phases",
        "Required Existing Artifacts",
        "Implementation Readiness Definition",
        "Implementation Readiness Criteria",
        "Future Implementation Constraints",
        "Non-Authorization Boundaries",
        "Functional Result",
        "Next Microphase",
    ])


def test_contract_doc_declares_implementation_readiness_definition() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "document-only pre-implementation contract",
        "readiness for a future controlled implementation",
        "existing controlled synthetic JSON fixture only",
        "existing expected visible text fixture only",
        "text/plain or markdown/text compatible output only if later authorized",
        "deterministic text comparison",
        "semantic equivalence to safe visible report",
        "text-only output",
        "UTF-8",
        "deterministic output",
        "human-readable output",
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


def test_contract_doc_declares_future_constraints() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "only existing controlled JSON fixture",
        "only existing expected visible text fixture",
        "only deterministic text comparison",
        "only text/plain or markdown/text compatible output",
        "no real media read",
        "no ffprobe/ffmpeg execution",
        "no scanner",
        "no subprocess/process execution",
        "no network",
        "no DB/SaaS",
        "no client deliverables",
        "no packaging",
        "no installer",
        "no public/client/sales demo",
        "no production use",
        "no implementation until later explicit QA gate",
    ])


def test_required_artifacts_exist() -> None:
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


def test_qa_gate_references_required_artifacts() -> None:
    text = read(QA_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_contract_doc_references_required_artifacts() -> None:
    text = read(CONTRACT_DOC)
    referenced = [
        artifact
        for artifact in REQUIRED_ARTIFACTS
        if artifact
        not in {
            Path(
                "docs/product/local_media_agent/"
                "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract_v1.md"
            ),
            Path(
                "tests/unit/"
                "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture_implementation_readiness_contract.py"
            ),
        }
    ]
    for artifact in referenced:
        assert str(artifact) in text


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
