import ast
from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_contract_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_contract.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1"

FUTURE_RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
FUTURE_IMPLEMENTATION_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime.py")


def _doc_text() -> str:
    assert DOC.exists(), f"Missing minimal runtime contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_minimal_runtime_contract_document_exists():
    assert DOC.exists()


def test_minimal_runtime_contract_contains_phase_identifier():
    assert PHASE in _doc_text()


def test_minimal_runtime_contract_is_documentation_test_only():
    text = _doc_text().lower()
    assert "documentation/test-only" in text
    assert "does not create runtime code" in text
    assert "does not create a real preflight module" in text
    assert "does not create a real preflight function" in text


def test_prerequisite_readiness_gate_is_declared_with_valid_recovery_tag():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-implementation-readiness-gate-v1-postgresql-only-recovery-20260619" in text
    assert "The earlier non-recovery readiness tag must not be used as stable" in text


def test_future_target_runtime_file_is_named_but_not_created_by_this_phase():
    text = _doc_text()
    assert "scripts/cid_local_media_agent_real_preflight.py" in text
    assert "This current phase must not create that file." in text
    assert not FUTURE_RUNTIME_FILE.exists()


def test_future_implementation_test_file_is_named_but_not_created_by_this_phase():
    text = _doc_text()
    assert "tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime.py" in text
    assert "This current phase must not create that file." in text
    assert not FUTURE_IMPLEMENTATION_TEST.exists()


def test_future_public_function_is_named_and_single_entry_point():
    text = _doc_text()
    assert "run_real_preflight_check(request: RealPreflightRequest) -> RealPreflightResult" in text
    lowered = text.lower()
    assert "no other public runtime entry point is authorized" in lowered
    assert "local-only" in lowered
    assert "fail-closed" in lowered


def test_future_request_shape_is_enumerated():
    text = _doc_text()
    required = [
        "`input_folder_path`",
        "`output_folder_path`",
        "`max_file_count`",
        "`max_total_size_bytes`",
        "`max_scan_depth`",
        "`accepted_extensions`",
        "`follow_symlinks`",
    ]
    for item in required:
        assert item in text


def test_future_request_defaults_are_conservative():
    text = _doc_text().lower()
    assert "`max_file_count`: 25" in text
    assert "`max_total_size_bytes`: 10737418240" in text
    assert "`max_scan_depth`: 3" in text
    assert "`follow_symlinks`: false" in text
    for ext in [".mov", ".mp4", ".mxf", ".wav", ".aif", ".aiff"]:
        assert ext in text


def test_request_paths_are_memory_only_not_reported():
    text = _doc_text().lower()
    assert "may hold local private paths in memory only" in text
    assert "must never be copied into logs" in text
    assert "serialized result payloads" in text
    assert "user-visible diagnostic text" in text


def test_future_result_shape_is_enumerated():
    text = _doc_text()
    required = [
        "`status`",
        "`sanitized_input_folder_label`",
        "`sanitized_output_folder_label`",
        "`media_file_count`",
        "`total_selected_media_size_bucket`",
        "`maximum_detected_scan_depth`",
        "`accepted_extension_counts`",
        "`ignored_extension_counts`",
        "`rejected_extension_counts`",
        "`failed_check_identifiers`",
        "`remediation_items`",
    ]
    for item in required:
        assert item in text


def test_future_result_shape_prohibits_private_and_media_derived_fields():
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


def test_future_result_states_are_preserved():
    text = _doc_text()
    for state in ["`PREFLIGHT_PASS`", "`PREFLIGHT_FAIL`", "`PREFLIGHT_BLOCKED`"]:
        assert state in text


def test_future_check_identifiers_are_enumerated():
    text = _doc_text()
    required = [
        "INPUT_FOLDER_EXISTS",
        "INPUT_FOLDER_IS_DIRECTORY",
        "INPUT_FOLDER_LOCAL_ONLY",
        "INPUT_FOLDER_ACCESSIBLE",
        "OUTPUT_FOLDER_PREPARABLE",
        "INPUT_OUTPUT_SEPARATED",
        "SCAN_DEPTH_WITHIN_LIMIT",
        "MEDIA_FILE_COUNT_WITHIN_LIMIT",
        "TOTAL_MEDIA_SIZE_WITHIN_LIMIT",
        "ACCEPTED_EXTENSIONS_PRESENT",
        "REJECTED_EXTENSIONS_REPORTED",
        "SYMLINKS_NOT_FOLLOWED",
        "TRAVERSAL_DID_NOT_ESCAPE_INPUT",
        "PRIVATE_PATHS_NOT_REPORTED",
        "SANITIZED_PAYLOAD_READY",
    ]
    for item in required:
        assert item in text


def test_unknown_filesystem_conditions_are_blocked():
    text = _doc_text().lower()
    assert "unknown filesystem condition" in text
    assert "blocked rather than inventing a permissive result" in text


def test_future_allowed_behavior_is_filesystem_metadata_only():
    text = _doc_text().lower()
    required = [
        "directory existence",
        "directory type",
        "directory entries",
        "extension strings",
        "file sizes",
        "traversal depth",
        "permission availability",
        "basic stat-like availability",
        "symlink detection without following symlinks",
    ]
    for item in required:
        assert item in text


def test_future_runtime_must_not_read_or_parse_media():
    text = _doc_text().lower()
    required = [
        "must not read media bytes",
        "must not parse media headers",
        "must not derive media fingerprints",
        "must not open media streams",
        "must not inspect codecs",
        "must not infer audiovisual content",
    ]
    for item in required:
        assert item in text


def test_future_fixture_boundary_is_synthetic_local_only():
    text = _doc_text().lower()
    required = [
        "synthetic local fixtures",
        "temporary input folders",
        "temporary output folders",
        "empty placeholder files",
        "tiny text placeholder files with accepted media-like extensions",
        "generic synthetic filenames",
        "nested synthetic folders",
        "symlink fixtures only when the platform supports them safely",
    ]
    for item in required:
        assert item in text


def test_future_fixture_boundary_forbids_real_media_and_real_names():
    text = _doc_text().lower()
    required = [
        "real client media",
        "real production media",
        "real project folders",
        "real camera files",
        "real sound files",
        "real location folders",
        "real person names",
        "real client names",
        "real project names",
        "copied user filenames",
        "media samples from external sources",
        "cloud-mounted media",
        "network-mounted media",
    ]
    for item in required:
        assert item in text


def test_fail_closed_behavior_is_enumerated():
    text = _doc_text().lower()
    required = [
        "input folder path is missing",
        "input folder is not a directory",
        "input folder cannot be accessed safely",
        "selected folder is not local",
        "output folder cannot be prepared safely",
        "input and output folders overlap",
        "traversal escapes the selected input folder",
        "symlink following would be required",
        "scan depth exceeds the configured limit",
        "file count exceeds the configured limit",
        "total selected media size exceeds the configured limit",
        "sanitized result payload cannot be produced",
        "privacy-safe reporting cannot be guaranteed",
        "unknown filesystem error cannot be classified safely",
    ]
    for item in required:
        assert item in text


def test_preflight_state_meanings_are_fail_closed():
    text = _doc_text().lower()
    assert "may return `preflight_fail` only when the filesystem is reachable and safely classified" in text
    assert "may return `preflight_pass` only when every required check passes" in text
    assert "result payload remains sanitized" in text


def test_output_separation_rule_is_required():
    text = _doc_text().lower()
    required = [
        "must not write inside the selected input folder",
        "must not create reports",
        "temporary files inside the selected input folder",
        "output folder only when it is separated from the input folder",
    ]
    for item in required:
        assert item in text


def test_logging_rule_is_privacy_safe():
    text = _doc_text().lower()
    required_allowed = [
        "phase identifier",
        "result status",
        "failed check identifiers",
        "numeric counts",
        "size buckets",
        "generic remediation identifiers",
    ]
    for item in required_allowed:
        assert item in text

    required_forbidden = [
        "full private paths",
        "raw filenames",
        "client names",
        "project names",
        "media-derived metadata",
        "media-derived content",
    ]
    for item in required_forbidden:
        assert item in text


def test_import_boundaries_are_enumerated():
    text = _doc_text().lower()
    required = [
        "scanner modules",
        "synthetic visible report modules",
        "media probing wrappers",
        "transcription modules",
        "translation modules",
        "sync modules",
        "subtitle modules",
        "nle export modules",
        "saas modules",
        "database modules",
        "billing modules",
        "licensing modules",
        "upload modules",
    ]
    for item in required:
        assert item in text


def test_future_runtime_dependency_boundary_is_standard_library_only():
    text = _doc_text().lower()
    assert "standard library filesystem/path utilities" in text
    assert "unless a later contract explicitly authorizes another dependency" in text


def test_blocked_operations_remain_blocked():
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
        "scanner integration",
        "real report generation",
        "synthetic visible report integration",
        "davinci resolve integration",
        "avid integration",
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


def test_required_later_implementation_phase_is_named():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.IMPLEMENTATION.V1" in text
    lowered = text.lower()
    assert "must start from a clean repository precheck" in lowered
    assert "must include tests before or with implementation" in lowered


def test_acceptance_criteria_are_contractual():
    text = _doc_text().lower()
    required = [
        "the minimal runtime contract document exists",
        "the phase is documentation/test-only",
        "the future target runtime file is named",
        "the future implementation test file is named",
        "the future public function is named",
        "the future request shape is enumerated",
        "the future result shape is enumerated",
        "the future result states are preserved",
        "the future check identifiers are enumerated",
        "local filesystem metadata is the only allowed inspection source",
        "future fixtures are synthetic and local-only",
        "fail-closed behavior is enumerated",
        "output separation is required",
        "logging remains privacy-safe",
        "import boundaries are enumerated",
        "blocked operations remain blocked",
        "no runtime source file is created by this phase",
    ]
    for item in required:
        assert item in text


def test_contract_test_file_does_not_import_future_runtime_or_existing_runtime_modules():
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
        ".".join(["scripts", "cid_local_media_agent_real_preflight"]),
        ".".join(["scripts", "cid_media_agent_scan"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_cli"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_preflight_check"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_renderer"]),
    }

    assert imported_modules.isdisjoint(forbidden_imports)
