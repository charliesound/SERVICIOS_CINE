from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_integration_readiness_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_integration_readiness_contract_v1.md"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.INTEGRATION.READINESS.CONTRACT.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.INTEGRATION.READINESS.CONTRACT.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_INTEGRATION_READINESS_CONTRACT_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-integration-readiness-contract-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.READINESS.CONTRACT.V1"
)

REQUIRED_ARTIFACTS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_qa_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_qa_gate_v1.md"),
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
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
        "new runtime integration",
        "new CLI integration",
        "report packaging",
        "export",
    ])


def test_contract_doc_exists_and_declares_phase_and_result() -> None:
    assert CONTRACT_DOC.exists()
    content = read(CONTRACT_DOC)
    assert_all_present(content, [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
        "VISIBLE_REPORT_OUTPUT_INTEGRATION_READINESS_CONTRACT_PASS_READY_FOR_QA_GATE",
    ])


def test_contract_doc_declares_required_sections() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "## Integration Readiness Scope",
        "## Required Previous Closed Phases",
        "## Required Existing Artifacts",
        "## Readiness Conditions",
        "## Non-Authorization Boundaries",
        "## Functional Result",
        "## Next Microphase",
    ])


def test_contract_doc_declares_readiness_conditions() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "visible output contract is closed",
        "visible output QA gate is closed",
        "controlled smoke fixture is closed",
        "controlled smoke fixture QA gate is closed",
        "expected visible text fixture exists",
        "controlled JSON fixture exists",
        "safety flags remain false",
        "no path leakage",
        "no secrets leakage",
        "no real media",
        "no real ffprobe",
        "no ffmpeg",
        "no network",
        "no SaaS/DB",
    ])


def test_contract_doc_references_required_artifacts() -> None:
    text = read(CONTRACT_DOC)
    for artifact in REQUIRED_ARTIFACTS:
        assert str(artifact) in text


def test_required_artifacts_exist() -> None:
    for artifact in REQUIRED_ARTIFACTS:
        assert artifact.exists(), artifact


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
