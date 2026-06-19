import ast
from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_implementation_readiness_gate_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_implementation_readiness_gate.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.READINESS.GATE.V1"

PREREQUISITE_DOCS = [
    Path("docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_contract_v1.md"),
    Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_implementation_boundary_contract_v1.md"),
]

PREREQUISITE_TESTS = [
    Path("tests/unit/test_cid_local_media_agent_real_test_scope_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_real_test_scope_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_real_media_privacy_safety_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_real_input_folder_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_real_input_folder_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_contract.py"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_contract_qa_gate.py"),
    Path("tests/unit/test_cid_local_media_agent_real_preflight_implementation_boundary_contract.py"),
]


def _doc_text() -> str:
    assert DOC.exists(), f"Missing readiness gate document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_readiness_gate_document_exists():
    assert DOC.exists()


def test_readiness_gate_contains_phase_identifier():
    assert PHASE in _doc_text()


def test_readiness_gate_is_documentation_test_only():
    text = _doc_text().lower()
    assert "documentation/test-only" in text
    assert "does not implement runtime behavior" in text
    assert "does not create a real preflight function" in text


def test_readiness_gate_depends_on_boundary_contract():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1" in text
    assert "The boundary contract remains authoritative." in text


def test_readiness_gate_defines_exact_decision_states():
    text = _doc_text()
    states = [
        "`IMPLEMENTATION_READY`",
        "`IMPLEMENTATION_NOT_READY`",
        "`IMPLEMENTATION_BLOCKED`",
    ]
    for state in states:
        assert state in text


def test_readiness_gate_defines_decision_state_meanings():
    text = _doc_text().lower()
    assert "strictly limited to the approved filesystem-metadata boundary" in text
    assert "prerequisite contracts, tests, guardrails, or review conditions are missing" in text
    assert "privacy, safety, runtime, scope, saas, billing, media-processing, or repository boundary" in text


def test_prerequisite_phase_chain_is_enumerated():
    text = _doc_text()
    phases = [
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.SCOPE.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.MEDIA.PRIVACY.SAFETY.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1",
    ]
    for phase in phases:
        assert phase in text


def test_prerequisite_documents_exist():
    missing = [str(path) for path in PREREQUISITE_DOCS if not path.exists()]
    assert not missing, f"Missing prerequisite docs: {missing}"


def test_prerequisite_tests_exist():
    missing = [str(path) for path in PREREQUISITE_TESTS if not path.exists()]
    assert not missing, f"Missing prerequisite tests: {missing}"


def test_repository_conditions_are_enumerated():
    text = _doc_text().lower()
    required = [
        "repository is clean before implementation work starts",
        "current branch is `main`",
        "working directory is `/opt/servicios_cine`",
        "wsl ubuntu",
        ".venv is active",
        "no windows path is used",
        "no protected file is modified",
        "postgresql-only guardrails remain intact",
        "wsl repo guard passes",
        "postgresql-only regression guard passes",
    ]
    for item in required:
        assert item in text


def test_protected_areas_remain_closed():
    text = _doc_text().lower()
    required = [
        ".env",
        "real databases",
        "backups",
        "docker",
        "alembic",
        "frontend",
        "backend",
        "saas runtime",
        "stripe",
        "ai jobs",
        "credits",
        "ledger",
        "billing",
        "licensing",
        "installer",
        "desktop app",
        "shell launcher",
        "packaging",
        "upload flows",
        "cloud transfer flows",
    ]
    for item in required:
        assert item in text


def test_future_scope_is_limited_to_filesystem_metadata():
    text = _doc_text().lower()
    assert "minimal real preflight implementation" in text
    assert "limited to local filesystem metadata" in text
    required = [
        "check whether selected input folder exists",
        "check whether selected input folder is a directory",
        "check whether selected input folder is locally accessible",
        "check input and output separation",
        "count selected media files",
        "count accepted extensions",
        "count ignored extensions",
        "count rejected extensions",
        "calculate coarse total size bucket",
        "calculate maximum detected scan depth",
        "detect symlink presence without following symlinks",
    ]
    for item in required:
        assert item in text


def test_future_hard_limits_are_preserved():
    text = _doc_text().lower()
    assert "maximum selected media files: 25" in text
    assert "maximum total selected media size: 10 gb" in text
    assert "maximum scan depth: 3" in text
    assert "symlink following: disabled" in text
    assert "traversal outside selected folder: blocked" in text
    assert "output inside input folder: blocked" in text
    for ext in [".mov", ".mp4", ".mxf", ".wav", ".aif", ".aiff"]:
        assert ext in text


def test_future_preflight_result_states_are_preserved():
    text = _doc_text()
    for state in ["`PREFLIGHT_PASS`", "`PREFLIGHT_FAIL`", "`PREFLIGHT_BLOCKED`"]:
        assert state in text


def test_future_allowed_payload_fields_are_enumerated():
    text = _doc_text().lower()
    required = [
        "sanitized input folder label",
        "sanitized output folder label",
        "media file count",
        "total selected media size bucket",
        "maximum detected scan depth",
        "accepted extension counts",
        "ignored extension counts",
        "rejected extension counts",
        "failed check identifiers",
        "remediation guidance without private full paths",
    ]
    for item in required:
        assert item in text


def test_future_prohibited_payload_fields_are_enumerated():
    text = _doc_text().lower()
    required = [
        "full private paths",
        "raw filenames",
        "client names",
        "project names",
        "media hashes",
        "media content",
        "stream metadata",
        "codec metadata",
        "timecode metadata",
        "embedded metadata",
        "transcript text",
        "subtitle text",
        "waveform data",
        "frame data",
        "thumbnail data",
    ]
    for item in required:
        assert item in text


def test_media_processing_remains_blocked():
    text = _doc_text().lower()
    required = [
        "media decoding",
        "stream probing",
        "codec probing",
        "container probing",
        "ffprobe on real files",
        "ffmpeg on real files",
        "frame extraction",
        "thumbnail generation",
        "waveform generation",
        "audio analysis",
        "speech recognition",
        "transcription",
        "translation",
        "subtitle generation",
        "sync analysis",
        "clap detection",
        "timecode extraction",
    ]
    for item in required:
        assert item in text


def test_integration_export_upload_and_saas_remain_blocked():
    text = _doc_text().lower()
    required = [
        "scanner integration",
        "real report generation",
        "synthetic visible report integration",
        "nle export",
        "edl generation",
        "xml generation",
        "aaf generation",
        "otio generation",
        "timeline generation",
        "upload",
        "cloud transfer",
        "desktop packaging",
        "installer creation",
        "licensing activation",
        "saas integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "billing changes",
    ]
    for item in required:
        assert item in text


def test_implementation_opening_criteria_are_enumerated():
    text = _doc_text().lower()
    required = [
        "prerequisite contracts are present",
        "prerequisite qa gates are present",
        "implementation boundary contract is present",
        "this readiness gate is present",
        "this readiness gate test passes",
        "previous real preflight contract tests pass",
        "boundary contract tests pass",
        "wsl repo guard passes",
        "postgresql-only guard passes",
        "staged diff contains only files authorized by the current phase",
        "human operator intentionally opens the next implementation phase",
    ]
    for item in required:
        assert item in text


def test_next_implementation_constraints_are_enumerated():
    text = _doc_text().lower()
    required = [
        "be named explicitly",
        "identify exact target runtime file or files before editing",
        "start with a clean repo precheck",
        "include tests before or with implementation",
        "remain fail-closed",
        "avoid importing scanner code",
        "avoid invoking ffprobe or ffmpeg",
        "avoid reading media bytes",
        "avoid exposing raw filenames or full paths",
        "avoid writing output inside selected input media folders",
        "avoid saas/backend/frontend/database/billing changes",
    ]
    for item in required:
        assert item in text


def test_blocker_conditions_are_enumerated():
    text = _doc_text().lower()
    required = [
        "any prerequisite contract is missing",
        "any prerequisite test is failing",
        "boundary contract is not present",
        "privacy-safe reporting cannot be guaranteed",
        "output separation is unclear",
        "symlink behavior is unclear",
        "traversal blocking is unclear",
        "size and count limits are unclear",
        "sanitized payload fields are unclear",
        "prohibited payload fields are unclear",
        "blocked media operations are unclear",
        "protected repo areas would be touched",
        "runtime scope would expand beyond filesystem metadata",
    ]
    for item in required:
        assert item in text


def test_non_goals_keep_runtime_closed():
    text = _doc_text().lower()
    required = [
        "implement real preflight",
        "modify cli behavior",
        "modify scanner behavior",
        "generate real reports",
        "process real media",
        "invoke media tools",
        "connect to davinci resolve",
        "create nle exports",
        "create subtitles",
        "create transcripts",
        "translate media",
        "sync audio and video",
        "package an app",
        "create a desktop app",
        "create an installer",
        "add licensing",
        "connect to saas",
        "change backend",
        "change frontend",
        "change databases",
        "change billing",
    ]
    for item in required:
        assert item in text


def test_acceptance_criteria_are_contractual():
    text = _doc_text().lower()
    required = [
        "the readiness gate document exists",
        "the readiness gate states that it is documentation/test-only",
        "the readiness gate depends on the implementation boundary contract",
        "the readiness gate defines exactly three decision states",
        "the prerequisite chain is enumerated",
        "repository conditions are enumerated",
        "future implementation scope is limited to filesystem metadata",
        "future hard limits are preserved",
        "future payload boundaries are enumerated",
        "blocked operations remain blocked",
        "next implementation constraints are enumerated",
        "no runtime source file is changed by this phase",
    ]
    for item in required:
        assert item in text


def test_recommended_next_phase_is_minimal_runtime_contract_not_implementation():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1" in text
    lowered = text.lower()
    assert "define the exact target file, function name, data shape, test fixtures, and fail-closed expectations" in lowered


def test_this_test_file_does_not_import_runtime_modules():
    tree = ast.parse(TEST.read_text(encoding="utf-8"))
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    forbidden_imports = {
        ".".join(["scripts", "cid_media_agent_scan"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_cli"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_preflight_check"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_renderer"]),
    }

    assert imported_modules.isdisjoint(forbidden_imports)
