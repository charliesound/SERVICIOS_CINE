from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_READINESS_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTRACT_GATE_WITH_ISOLATED_ENTRYPOINT_BOUNDARIES"
DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate_v1.md"
IMPL = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
FIXTURE_RELATIVE = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
EXPECTED_BYTES = "239"
FUTURE_ENTRYPOINT = "cid-local-media-agent-read-only-single-file-metadata"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_cli_readiness_document_declares_phase_result_and_decision():
    text = _doc_text()
    assert PHASE in text
    assert RESULT in text
    assert DECISION in text
    assert "CLI_READINESS_ONLY_NOT_IMPLEMENTATION" in text


def test_cli_readiness_is_contract_preparation_only():
    text = _doc_text()
    assert "This gate authorizes only a later CLI contract gate" in text
    assert "does not add a new command" in text
    assert "does not change packaging" in text
    assert "does not expose a product CLI yet" in text


def test_cli_readiness_targets_existing_audited_implementation_only():
    text = _doc_text()
    assert "scripts/local_media_agent/read_only_single_file_metadata.py" in text
    assert IMPL.is_file()
    assert "collect_read_only_single_file_metadata" in IMPL.read_text(encoding="utf-8")
    assert "run_cli" in IMPL.read_text(encoding="utf-8")


def test_cli_readiness_keeps_single_controlled_fixture_identity():
    text = _doc_text()
    assert FIXTURE_RELATIVE in text
    assert EXPECTED_BYTES in text
    assert EXPECTED_SHA256 in text
    assert "one controlled file only" in text


def test_cli_readiness_names_future_entrypoint_without_registering_it():
    text = _doc_text()
    assert FUTURE_ENTRYPOINT in text
    assert "no console script registration" in text
    assert "no product CLI integration" in text
    assert "no pyproject modification" in text


def test_cli_readiness_defines_future_arguments_without_implementation_scope():
    text = _doc_text()
    for token in [
        "--target-path",
        "--fixture-root",
        "--expected-sha256",
        "--expected-bytes",
        "--allowed-relative-path",
        "--result-json",
    ]:
        assert token in text
    assert "does not implement that entrypoint" in text


def test_cli_readiness_defines_output_and_exit_contract_preview():
    text = _doc_text()
    assert "JSON result payload" in text
    assert "Plain status output" in text
    assert "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK" in text
    assert "deterministic rejected outcomes" in text


def test_cli_readiness_preserves_private_path_redaction_requirement():
    text = _doc_text()
    assert "<CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt" in text
    assert "must never expose host-private absolute paths" in text
    assert "redacted paths" in text


def test_cli_readiness_keeps_forbidden_runtime_and_product_surfaces_closed():
    text = _doc_text()
    forbidden_scope_markers = [
        "no scanner",
        "no batch processing",
        "no recursion",
        "no external media tool execution",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no customer material",
        "no real media ingest",
        "no service backend",
        "no database access",
        "no frontend",
        "no installer",
        "no fixture modification",
    ]
    for marker in forbidden_scope_markers:
        assert marker in text


def test_existing_implementation_imports_remain_standard_library_only():
    tree = ast.parse(IMPL.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"__future__", "argparse", "hashlib", "json", "pathlib", "typing"}


def test_existing_implementation_source_has_no_external_tool_scanner_or_traversal_patterns():
    source = IMPL.read_text(encoding="utf-8").lower()
    forbidden = [
        "ffprobe",
        "ffmpeg",
        "subprocess",
        "popen",
        "os.system",
        "shell=true",
        "glob(",
        "rglob(",
        "walk(",
        "scandir(",
        "moviepy",
        "cv2",
        "mediainfo",
    ]
    assert not [token for token in forbidden if token in source]


def test_cli_readiness_acceptance_and_next_phase_are_closed():
    text = _doc_text()
    assert "CLI_READINESS_PASS_FOR_SEPARATE_CONTRACT_GATE_ONLY" in text
    assert NEXT_PHASE in text
    assert "The implementation QA gate is already closed" in text
