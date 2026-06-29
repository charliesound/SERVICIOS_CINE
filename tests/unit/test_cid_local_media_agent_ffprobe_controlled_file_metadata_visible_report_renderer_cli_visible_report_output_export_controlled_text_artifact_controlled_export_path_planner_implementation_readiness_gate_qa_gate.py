from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_v1.md"
)

READINESS_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_v1.md"
)

READINESS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate.py"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_closure_review.py"
)

PLANNER_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_v1.md"
)

PLANNER_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate.py"
)

PLANNER_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_v1.md"
)

PLANNER_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract.py"
)

READINESS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review_v1.md"
)

READINESS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review.py"
)

PATH_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_v1.md"
)

PATH_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract.py"
)

IMPLEMENTATION_SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_QA_GATE"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_PASS_CLOSED"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_files_exist():
    assert DOC_PATH.exists()
    assert READINESS_DOC_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PLANNER_QA_GATE_DOC_PATH.exists()
    assert PLANNER_QA_GATE_TEST_PATH.exists()
    assert PLANNER_CONTRACT_DOC_PATH.exists()
    assert PLANNER_CONTRACT_TEST_PATH.exists()
    assert READINESS_CLOSURE_DOC_PATH.exists()
    assert READINESS_CLOSURE_TEST_PATH.exists()
    assert PATH_CONTRACT_DOC_PATH.exists()
    assert PATH_CONTRACT_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_references_previous_chain():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(READINESS_DOC_PATH) in text
    assert str(READINESS_TEST_PATH) in text
    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert str(PLANNER_QA_GATE_DOC_PATH) in text
    assert str(PLANNER_QA_GATE_TEST_PATH) in text
    assert str(PLANNER_CONTRACT_DOC_PATH) in text
    assert str(PLANNER_CONTRACT_TEST_PATH) in text
    assert str(READINESS_CLOSURE_DOC_PATH) in text
    assert str(READINESS_CLOSURE_TEST_PATH) in text
    assert str(PATH_CONTRACT_DOC_PATH) in text
    assert str(PATH_CONTRACT_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_is_doc_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add runtime behavior.",
        "It does not implement a path planner.",
        "It does not implement a path resolver.",
        "It does not modify the controlled export implementation.",
        "It does not write files.",
        "It does not create directories.",
        "It does not create artifacts on disk.",
        "It does not authorize filesystem export implementation.",
        "It does not authorize any real media workflow.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_scope_validates_readiness_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This QA gate validates the controlled export path planner implementation readiness gate.",
        "Exists at the expected document path.",
        "Is paired with a unit test.",
        "References the previous planner implementation contract QA gate closure review.",
        "Preserves the previous functional result.",
        "Defines readiness only for a future QA gate decision.",
        "Does not approve implementation.",
        "Does not approve runtime execution.",
        "Does not approve file writing.",
        "Does not approve artifact creation on disk.",
        "Does not approve real media use.",
        "Does not approve arbitrary folder use.",
        "Keeps the current in-memory descriptor builder pathless.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_requires_future_planner_limits():
    text = _read(DOC_PATH)

    required_phrases = [
        "Requires a future planner to be pure.",
        "Requires a future planner to be deterministic.",
        "Requires a future planner to be local-only.",
        "Requires a future planner to be side-effect free.",
        "Requires a future planner to return only a planned path descriptor.",
        "Requires a future planner to avoid file writing.",
        "Requires a future planner to avoid directory creation.",
        "Requires a future planner to avoid artifact generation on disk.",
        "Requires a future planner to avoid real media access.",
        "Requires a future planner to avoid process execution.",
        "Requires a future planner to avoid network access.",
        "Requires a future planner to avoid SaaS, database, installer, and client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_defines_validation_evidence():
    text = _read(DOC_PATH)

    required_phrases = [
        "Python compile check for this QA gate test.",
        "This QA gate unit test.",
        "Previous planner implementation readiness gate unit test.",
        "Previous planner implementation contract QA gate closure review unit test.",
        "Previous planner implementation contract QA gate unit test.",
        "Previous planner implementation contract unit test.",
        "Earlier implementation readiness QA gate closure review unit test.",
        "Previous path contract unit test.",
        "WSL repository guard.",
        "Database backend regression guard.",
        "Diff check.",
        "Protected files check.",
        "Target tag absence check locally and remotely.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_closure_decision_is_limited():
    text = _read(DOC_PATH)

    required_phrases = [
        "If all QA evidence passes, the controlled export path planner implementation readiness gate QA gate may be closed.",
        "Closing this QA gate means only that the readiness decision has been validated.",
        "Closing this QA gate does not authorize a path planner implementation.",
        "Closing this QA gate does not authorize path resolver code.",
        "Closing this QA gate does not authorize file writing.",
        "Closing this QA gate does not authorize directory creation.",
        "Closing this QA gate does not authorize artifact generation on disk.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_non_authorization_is_complete():
    text = _read(DOC_PATH)
    lowered = text.lower()

    required_phrases = [
        "does not authorize path planner implementation",
        "does not authorize path resolver implementation",
        "does not authorize file writing",
        "does not authorize directory creation",
        "does not authorize artifact generation on disk",
        "does not authorize real media",
        "does not authorize arbitrary folders",
        "does not authorize scanner execution",
        "does not authorize ffprobe or ffmpeg execution",
        "does not authorize subprocess or process execution",
        "does not authorize audio extraction",
        "does not authorize sync",
        "does not authorize transcription",
        "does not authorize subtitles",
        "does not authorize timeline export",
        "does not authorize network access",
        "does not authorize saas or database integration",
        "does not authorize installer work",
        "does not authorize public demo, client demo, sales demo, or production use",
    ]

    for phrase in required_phrases:
        assert phrase in lowered


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_previous_readiness_gate_supports_qa_gate():
    text = _read(READINESS_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "This readiness gate validates whether the repository is ready to accept a future controlled pure path planner implementation phase." in text
    assert "This phase is documentation and test-only." in text
    assert "This readiness gate confirms only that the controlled path planner implementation chain has enough contractual evidence to proceed to a QA gate for this readiness decision." in text
    assert "PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_QA_GATE" in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_previous_readiness_gate_defines_preconditions():
    text = _read(READINESS_DOC_PATH)

    required_phrases = [
        "The previous planner implementation contract QA gate closure review exists.",
        "The previous planner implementation contract QA gate exists.",
        "The planner implementation contract exists.",
        "The planner implementation contract defines a pure deterministic local-only side-effect-free planner.",
        "The planner implementation contract restricts the future module location to `scripts/local_media_agent/`.",
        "The planner implementation contract forbids import-time work.",
        "The planner implementation contract forbids CLI parsing.",
        "The planner implementation contract forbids environment reads.",
        "The planner implementation contract forbids configuration file reads.",
        "The planner implementation contract forbids real media access.",
        "The planner implementation contract forbids arbitrary folder access.",
        "The planner implementation contract forbids file open, read, write, and delete operations.",
        "The planner implementation contract restricts future inputs to `controlled_export_root` and a controlled descriptor.",
        "The existing in-memory descriptor builder remains pathless.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_previous_readiness_gate_defines_future_boundary():
    text = _read(READINESS_DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may be considered only after this readiness gate and its QA gate are closed.",
        "That later implementation phase may add only a pure path planner.",
        "That later implementation phase must not write files.",
        "That later implementation phase must not create directories.",
        "That later implementation phase must not create artifacts on disk.",
        "That later implementation phase must not scan folders.",
        "That later implementation phase must not execute ffprobe or FFmpeg.",
        "That later implementation phase must not execute subprocesses or external processes.",
        "That later implementation phase must not access the network.",
        "That later implementation phase must not touch SaaS, database, installer, or client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_planner_contract_supports_scope():
    text = _read(PLANNER_CONTRACT_DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may add only a pure path planner.",
        "That future planner must be deterministic.",
        "That future planner must be local-only.",
        "That future planner must be side-effect free.",
        "That future planner must only calculate and return a planned path descriptor.",
        "That future planner must not write files.",
        "That future planner must not create directories.",
        "That future planner must not create artifacts on disk.",
        "That future planner must not scan folders.",
        "That future planner must not execute ffprobe or FFmpeg.",
        "That future planner must not execute subprocesses or external processes.",
        "That future planner must not access the network.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_planner_contract_supports_path_rejection():
    text = _read(PLANNER_CONTRACT_DOC_PATH)

    required_phrases = [
        "Missing controlled export root.",
        "Empty controlled export root.",
        "Whitespace-only controlled export root.",
        "Missing descriptor.",
        "Descriptor without `suggested_filename`.",
        "Empty suggested filename.",
        "Whitespace-only suggested filename.",
        "Absolute suggested filename.",
        "Parent traversal segments.",
        "Path separators in the suggested filename.",
        "Windows drive prefixes.",
        "UNC path forms.",
        "Hidden dotfile names.",
        "Suggested filename without the `.controlled_visible_report.txt` suffix.",
        "Any final resolved path outside the controlled export root.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_current_implementation_remains_pathless():
    source = _read(IMPLEMENTATION_SCRIPT_PATH).lower()

    required_phrases = [
        "build_controlled_text_artifact_descriptor",
        "suggested_filename",
        "write_performed",
        "artifact_created_on_disk",
    ]

    forbidden_phrases = [
        "resolve_export_path",
        "planned_artifact_path",
        "controlled_export_root",
        "output_path",
        "input_path",
        "media_folder",
        "folder_path",
        "ffprobe command",
        "ffmpeg command",
        "upload",
        "download",
    ]

    for phrase in required_phrases:
        assert phrase in source

    for phrase in forbidden_phrases:
        assert phrase not in source


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_test_sources_have_no_external_execution_or_network_imports():
    for path in [
        TEST_PATH,
        READINESS_TEST_PATH,
        PREVIOUS_CLOSURE_TEST_PATH,
        PLANNER_QA_GATE_TEST_PATH,
        PLANNER_CONTRACT_TEST_PATH,
        READINESS_CLOSURE_TEST_PATH,
        PATH_CONTRACT_TEST_PATH,
    ]:
        tree = ast.parse(_read(path))

        forbidden_import_roots = {
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "urllib",
            "ftplib",
            "smtplib",
        }

        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_roots.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        assert imported_roots.isdisjoint(forbidden_import_roots)


def test_controlled_export_path_planner_implementation_readiness_gate_qa_gate_does_not_claim_runtime_or_client_readiness():
    combined = "\n".join(
        [
            _read(DOC_PATH),
            _read(READINESS_DOC_PATH),
            _read(PREVIOUS_CLOSURE_DOC_PATH),
            _read(PLANNER_QA_GATE_DOC_PATH),
            _read(PLANNER_CONTRACT_DOC_PATH),
            _read(READINESS_CLOSURE_DOC_PATH),
            _read(PATH_CONTRACT_DOC_PATH),
        ]
    ).lower()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "disk export ready",
        "export file created",
        "runtime exporter writes files",
        "users can export",
        "installer ready",
    ]

    for claim in forbidden_claims:
        assert claim not in combined
