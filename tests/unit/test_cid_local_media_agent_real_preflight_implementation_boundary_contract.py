import ast
from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_implementation_boundary_contract_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_implementation_boundary_contract.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1"


def _doc_text() -> str:
    assert DOC.exists(), f"Missing contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_contract_document_exists():
    assert DOC.exists()


def test_contract_contains_phase_identifier():
    assert PHASE in _doc_text()


def test_contract_is_documentation_test_only():
    text = _doc_text().lower()
    assert "documentation/test-only" in text
    assert "does not implement real preflight runtime behavior" in text


def test_contract_depends_on_previous_real_preflight_qa_gate():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1" in text


def test_contract_limits_future_implementation_to_filesystem_metadata():
    text = _doc_text().lower()
    assert "local filesystem validation" in text
    assert "filesystem metadata only" in text
    assert "must not read media bytes" in text


def test_contract_enumerates_allowed_future_checks():
    text = _doc_text()
    required = [
        "INPUT_FOLDER_EXISTS",
        "INPUT_FOLDER_IS_DIRECTORY",
        "INPUT_FOLDER_LOCAL_ONLY",
        "OUTPUT_FOLDER_PREPARABLE",
        "INPUT_OUTPUT_SEPARATED",
        "SCAN_DEPTH_WITHIN_LIMIT",
        "MEDIA_FILE_COUNT_WITHIN_LIMIT",
        "TOTAL_MEDIA_SIZE_WITHIN_LIMIT",
        "SYMLINKS_NOT_FOLLOWED",
        "PRIVATE_PATHS_NOT_REPORTED",
        "SANITIZED_PAYLOAD_READY",
    ]
    for item in required:
        assert item in text


def test_contract_preserves_conservative_default_limits():
    text = _doc_text().lower()
    assert "maximum selected media files: 25" in text
    assert "maximum total selected media size: 10 gb" in text
    assert "maximum scan depth: 3" in text
    for ext in [".mov", ".mp4", ".mxf", ".wav", ".aif", ".aiff"]:
        assert ext in text


def test_contract_requires_symlink_and_traversal_blocking():
    text = _doc_text().lower()
    assert "symlink following: disabled by default" in text
    assert "traversal outside selected folder: blocked by default" in text
    assert "symlinks would need to be followed" in text


def test_contract_requires_output_separation():
    text = _doc_text().lower()
    assert "input and output locations overlap" in text
    assert "must not write reports" in text
    assert "inside the selected input media folder" in text
    assert "separated from the selected input folder" in text


def test_contract_defines_exact_result_states():
    text = _doc_text()
    assert "`PREFLIGHT_PASS`" in text
    assert "`PREFLIGHT_FAIL`" in text
    assert "`PREFLIGHT_BLOCKED`" in text


def test_contract_defines_result_state_meanings():
    text = _doc_text().lower()
    assert "safe enough for the next human-approved phase" in text
    assert "did not satisfy one or more validation checks" in text
    assert "safety, privacy, locality, traversal, permission, symlink, or scope boundary" in text


def test_contract_enumerates_sanitized_payload_fields():
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


def test_contract_enumerates_prohibited_payload_fields():
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
        "transcript text",
        "subtitle text",
        "waveform data",
        "frame data",
        "thumbnail data",
    ]
    for item in required:
        assert item in text


def test_contract_blocks_media_processing_operations():
    text = _doc_text().lower()
    required = [
        "media decoding",
        "stream probing",
        "codec probing",
        "container probing",
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


def test_contract_blocks_export_upload_and_integration_operations():
    text = _doc_text().lower()
    required = [
        "nle export",
        "edl, xml, aaf, otio, or timeline generation",
        "upload",
        "cloud transfer",
        "scanner integration",
        "real report generation",
        "packaging implementation",
        "installer implementation",
        "desktop application implementation",
        "license activation",
        "saas integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "billing changes",
    ]
    for item in required:
        assert item in text


def test_contract_enumerates_fail_closed_conditions():
    text = _doc_text().lower()
    required = [
        "selected input folder is missing",
        "selected input folder is not a directory",
        "output folder overlaps with the input folder",
        "traversal escapes the selected input folder",
        "scan depth limit is exceeded",
        "file count limit is exceeded",
        "total selected media size limit is exceeded",
        "privacy-safe reporting cannot be guaranteed",
        "sanitized output cannot be produced",
        "filesystem error cannot be classified safely",
    ]
    for item in required:
        assert item in text


def test_contract_defines_privacy_safe_logging_boundary():
    text = _doc_text().lower()
    assert "future logs must remain privacy-safe" in text
    assert "failed check identifiers" in text
    assert "numeric counts" in text
    assert "size buckets" in text
    assert "must not include" in text
    assert "raw filenames" in text
    assert "full folder paths" in text


def test_contract_non_goals_keep_runtime_closed():
    text = _doc_text().lower()
    required = [
        "runtime implementation",
        "modifying existing cli behavior",
        "modifying scanner behavior",
        "integrating with synthetic visible report generation",
        "processing real media",
        "invoking media tools",
        "creating app packaging",
        "creating shell launchers",
        "creating a desktop app",
        "creating installers",
        "adding licensing",
        "connecting to saas systems",
    ]
    for item in required:
        assert item in text


def test_contract_acceptance_criteria_are_contractual():
    text = _doc_text().lower()
    required = [
        "the contract file exists",
        "the contract states that the phase is documentation/test-only",
        "future implementation boundary is limited to filesystem metadata",
        "allowed future checks are enumerated",
        "blocked operations are enumerated",
        "sanitized payload fields are enumerated",
        "prohibited payload fields are enumerated",
        "fail-closed conditions are enumerated",
        "output separation is required",
        "no runtime source file is changed by this phase",
    ]
    for item in required:
        assert item in text


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


def test_next_phase_remains_conservative():
    text = _doc_text().lower()
    assert "real preflight implementation readiness gate" in text
    assert "must still remain conservative" in text
    assert "must not automatically authorize media decoding" in text
