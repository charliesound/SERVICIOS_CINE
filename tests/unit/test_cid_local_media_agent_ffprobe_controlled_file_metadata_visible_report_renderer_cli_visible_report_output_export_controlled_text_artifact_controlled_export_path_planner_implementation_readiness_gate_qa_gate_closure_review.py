from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_closure_review_v1.md"
)

QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_qa_gate.py"
)

READINESS_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate_v1.md"
)

READINESS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_readiness_gate.py"
)

PREVIOUS_CONTRACT_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CONTRACT_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_closure_review.py"
)

PLANNER_CONTRACT_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_qa_gate_v1.md"
)

PLANNER_CONTRACT_QA_GATE_TEST_PATH = Path(
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

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_PASS_CLOSED"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_PATH_PLANNER_IMPLEMENTATION_PHASE"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_files_exist():
    assert DOC_PATH.exists()
    assert QA_GATE_DOC_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert READINESS_DOC_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert PREVIOUS_CONTRACT_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CONTRACT_CLOSURE_TEST_PATH.exists()
    assert PLANNER_CONTRACT_QA_GATE_DOC_PATH.exists()
    assert PLANNER_CONTRACT_QA_GATE_TEST_PATH.exists()
    assert PLANNER_CONTRACT_DOC_PATH.exists()
    assert PLANNER_CONTRACT_TEST_PATH.exists()
    assert PATH_CONTRACT_DOC_PATH.exists()
    assert PATH_CONTRACT_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_references_previous_chain():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(QA_GATE_DOC_PATH) in text
    assert str(QA_GATE_TEST_PATH) in text
    assert str(READINESS_DOC_PATH) in text
    assert str(READINESS_TEST_PATH) in text
    assert str(PREVIOUS_CONTRACT_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CONTRACT_CLOSURE_TEST_PATH) in text
    assert str(PLANNER_CONTRACT_QA_GATE_DOC_PATH) in text
    assert str(PLANNER_CONTRACT_QA_GATE_TEST_PATH) in text
    assert str(PLANNER_CONTRACT_DOC_PATH) in text
    assert str(PLANNER_CONTRACT_TEST_PATH) in text
    assert str(PATH_CONTRACT_DOC_PATH) in text
    assert str(PATH_CONTRACT_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_is_doc_and_test_only():
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_summarizes_qa_gate_findings():
    text = _read(DOC_PATH)

    required_phrases = [
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
        "Requires validation evidence before closure.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_decision_is_limited():
    text = _read(DOC_PATH)

    required_phrases = [
        "The controlled export path planner implementation readiness gate QA gate is closed.",
        "The chain is ready only for a future controlled path planner implementation phase.",
        "That future phase must remain limited to the planner implementation boundary already defined by the contract.",
        "This closure review does not itself implement the planner.",
        "This closure review does not authorize path resolver code beyond the already defined pure planner boundary.",
        "This closure review does not authorize file writing.",
        "This closure review does not authorize directory creation.",
        "This closure review does not authorize artifact generation on disk.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_defines_future_boundary():
    text = _read(DOC_PATH)

    required_phrases = [
        "A future controlled implementation phase may add only a pure path planner.",
        "That future planner must be deterministic.",
        "That future planner must be local-only.",
        "That future planner must be side-effect free.",
        "That future planner must be importable without side effects.",
        "That future planner must not perform import-time work.",
        "That future planner must not parse CLI arguments.",
        "That future planner must not read environment variables.",
        "That future planner must not read configuration files.",
        "That future planner must accept only `controlled_export_root` and a controlled descriptor.",
        "That future planner must return only a planned path descriptor.",
        "That future planner must reject unsafe roots and filenames.",
        "That future planner must reject traversal, path separators, drive prefixes, UNC paths, hidden dotfiles, and wrong suffixes.",
        "That future planner must set `write_performed` as false.",
        "That future planner must set `artifact_created_on_disk` as false.",
        "That future planner must not write files.",
        "That future planner must not create directories.",
        "That future planner must not create artifacts on disk.",
        "That future planner must not scan folders.",
        "That future planner must not access real media.",
        "That future planner must not execute ffprobe or FFmpeg.",
        "That future planner must not execute subprocesses or external processes.",
        "That future planner must not access the network.",
        "That future planner must not touch SaaS, database, installer, or client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_non_authorization_is_complete():
    text = _read(DOC_PATH)
    lowered = text.lower()

    required_phrases = [
        "does not authorize broad path planner implementation",
        "does not authorize path resolver implementation beyond the contracted pure planner boundary",
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_previous_qa_gate_supports_closure():
    text = _read(QA_GATE_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "This QA gate validates the controlled export path planner implementation readiness gate." in text
    assert "This phase is documentation and test-only." in text
    assert "Closing this QA gate means only that the readiness decision has been validated." in text
    assert "PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_QA_GATE_PASS_CLOSED" in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_previous_qa_gate_evidence_is_complete():
    text = _read(QA_GATE_DOC_PATH)

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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_readiness_gate_supports_scope():
    text = _read(READINESS_DOC_PATH)

    required_phrases = [
        "This readiness gate validates whether the repository is ready to accept a future controlled pure path planner implementation phase.",
        "This readiness gate confirms only that the controlled path planner implementation chain has enough contractual evidence to proceed to a QA gate for this readiness decision.",
        "It does not approve implementation.",
        "It does not approve runtime execution.",
        "It does not approve file writing.",
        "It does not approve artifact creation on disk.",
        "It does not approve use with real media or arbitrary folders.",
        "PATH_PLANNER_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_QA_GATE",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_readiness_gate_defines_future_boundary():
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_planner_contract_supports_future_limits():
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_planner_contract_supports_rejections():
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_current_implementation_remains_pathless():
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_test_sources_have_no_external_execution_or_network_imports():
    for path in [
        TEST_PATH,
        QA_GATE_TEST_PATH,
        READINESS_TEST_PATH,
        PREVIOUS_CONTRACT_CLOSURE_TEST_PATH,
        PLANNER_CONTRACT_QA_GATE_TEST_PATH,
        PLANNER_CONTRACT_TEST_PATH,
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


def test_controlled_export_path_planner_readiness_gate_qa_gate_closure_review_does_not_claim_runtime_or_client_readiness():
    combined = "\n".join(
        [
            _read(DOC_PATH),
            _read(QA_GATE_DOC_PATH),
            _read(READINESS_DOC_PATH),
            _read(PREVIOUS_CONTRACT_CLOSURE_DOC_PATH),
            _read(PLANNER_CONTRACT_QA_GATE_DOC_PATH),
            _read(PLANNER_CONTRACT_DOC_PATH),
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
