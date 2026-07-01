from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_non_customer_fixture_pack_creation_gate_v1.md"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
README_PATH = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/README.md"
MANIFEST_PATH = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/manifest.controlled.json"
MARKER_PATH = REPO_ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_GATE_V1_CLOSED"
EXPECTED_MARKER_BYTES = 239
EXPECTED_MARKER_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
EXPECTED_PACK_STATUS = "CREATED_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK"
EXPECTED_DECISION = "CONTROLLED_FIXTURE_PACK_CREATED_WITH_TEXT_ONLY_DETERMINISTIC_BOUNDARIES"
EXPECTED_NEXT_GATE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1"

EXPECTED_FIXTURE_FILES = {
    Path("README.md"),
    Path("manifest.controlled.json"),
    Path("media/controlled_plain_text_marker.txt"),
}

FORBIDDEN_SUFFIXES = {
    ".mov",
    ".mp4",
    ".mxf",
    ".wav",
    ".aif",
    ".aiff",
    ".mp3",
    ".flac",
    ".mkv",
    ".avi",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _manifest() -> dict:
    return json.loads(_read_text(MANIFEST_PATH))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_creation_gate_document_exists_and_declares_identity() -> None:
    text = _read_text(DOC_PATH)
    assert PHASE in text
    assert RESULT in text
    assert EXPECTED_PACK_STATUS in text
    assert EXPECTED_DECISION in text
    assert EXPECTED_NEXT_GATE in text


def test_fixture_root_exists_with_exact_file_set() -> None:
    assert FIXTURE_ROOT.is_dir()
    actual = {p.relative_to(FIXTURE_ROOT) for p in FIXTURE_ROOT.rglob("*") if p.is_file()}
    assert actual == EXPECTED_FIXTURE_FILES


def test_manifest_is_valid_and_has_required_identity() -> None:
    manifest = _manifest()
    assert manifest["schema_version"] == "cid.local_media_agent.controlled_non_customer_fixture_pack.v1"
    assert manifest["pack_id"] == "controlled_non_customer_fixture_pack_v1"
    assert manifest["status"] == EXPECTED_PACK_STATUS
    assert manifest["phase"] == PHASE
    assert manifest["result_when_closed"] == RESULT
    assert manifest["fixture_root"] == "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
    assert manifest["allowed_next_gate"] == EXPECTED_NEXT_GATE


def test_manifest_boundary_flags_are_closed() -> None:
    boundary = _manifest()["non_customer_boundary"]
    expected_false_flags = [
        "customer_material_allowed",
        "personal_data_allowed",
        "real_production_assets_allowed",
        "video_or_audio_fixture_allowed",
        "external_tool_execution_allowed",
        "network_access_allowed",
        "runtime_behavior_allowed",
        "scanner_execution_allowed",
        "saas_or_database_coupling_allowed",
    ]
    assert sorted(boundary) == sorted(expected_false_flags)
    assert all(boundary[key] is False for key in expected_false_flags)


def test_manifest_contains_single_controlled_marker_fixture() -> None:
    fixtures = _manifest()["fixtures"]
    assert len(fixtures) == 1
    fixture = fixtures[0]
    assert fixture["fixture_id"] == "controlled_plain_text_marker_v1"
    assert fixture["relative_path"] == "media/controlled_plain_text_marker.txt"
    assert fixture["mime_type"] == "text/plain"
    assert fixture["encoding"] == "utf-8"
    assert fixture["purpose"] == "deterministic fixture integrity marker"


def test_marker_fixture_has_expected_bytes_and_hash() -> None:
    assert MARKER_PATH.is_file()
    assert MARKER_PATH.stat().st_size == EXPECTED_MARKER_BYTES
    assert _sha256(MARKER_PATH) == EXPECTED_MARKER_SHA256


def test_manifest_marker_integrity_matches_actual_file() -> None:
    fixture = _manifest()["fixtures"][0]
    assert fixture["expected_bytes"] == MARKER_PATH.stat().st_size
    assert fixture["expected_sha256"] == _sha256(MARKER_PATH)


def test_marker_text_declares_non_customer_boundary() -> None:
    text = _read_text(MARKER_PATH)
    assert "CID Local Media Agent controlled non-customer fixture pack v1" in text
    assert "controlled_plain_text_marker_v1" in text
    assert "no customer media" in text
    assert "no personal data" in text
    assert "no audio" in text
    assert "no video" in text


def test_readme_documents_fixture_boundary_and_next_gate() -> None:
    text = _read_text(README_PATH)
    assert EXPECTED_PACK_STATUS in text
    assert PHASE in text
    assert EXPECTED_NEXT_GATE in text
    assert "not a media sample pack" in text
    assert "customer material" in text
    assert "personal data" in text
    assert "external tool execution" in text


def test_fixture_pack_contains_no_video_or_audio_extensions() -> None:
    files = [p for p in FIXTURE_ROOT.rglob("*") if p.is_file()]
    assert files
    assert all(p.suffix.lower() not in FORBIDDEN_SUFFIXES for p in files)


def test_document_records_exact_created_files_and_acceptance_criteria() -> None:
    text = _read_text(DOC_PATH)
    for rel in ["tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/README.md", "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/manifest.controlled.json", "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"]:
        assert rel in text
    for required in [
        "exactly the expected five files",
        "manifest is valid JSON",
        "marker fixture byte count",
        "marker fixture SHA256",
        "no video or audio extensions",
        "repository guards pass before commit",
    ]:
        assert required in text


def test_gate_blocks_later_metadata_scanner_and_runtime_actions() -> None:
    text = _read_text(DOC_PATH)
    manifest = _manifest()
    for token in [
        "metadata extraction",
        "external tool usage",
        "scanner execution",
        "customer material",
        "pilot usage",
        "product runtime behavior",
    ]:
        assert token in text
    assert manifest["blocked_until_later_gate"] == [
        "read_only_single_file_metadata_chain",
        "visible_report_over_fixture",
        "minimal_scanner_limited_to_fixture_root",
    ]
