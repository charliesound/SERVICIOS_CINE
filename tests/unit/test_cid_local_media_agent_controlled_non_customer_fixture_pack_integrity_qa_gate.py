from __future__ import annotations

import hashlib
import json
from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_non_customer_fixture_pack_integrity_qa_gate_v1.md"
)
FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1")
README_PATH = FIXTURE_ROOT / "README.md"
MANIFEST_PATH = FIXTURE_ROOT / "manifest.controlled.json"
MARKER_PATH = FIXTURE_ROOT / "media" / "controlled_plain_text_marker.txt"

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_INTEGRITY_QA_GATE_V1_CLOSED"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CREATION_GATE_V1_CLOSED"
EXPECTED_SCHEMA = "cid.local_media_agent.controlled_non_customer_fixture_pack.v1"
EXPECTED_PACK_ID = "controlled_non_customer_fixture_pack_v1"
EXPECTED_FIXTURE_ID = "controlled_plain_text_marker_v1"
EXPECTED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
CLOSURE_DECISION = "FIXTURE_PACK_INTEGRITY_VERIFIED_FOR_READ_ONLY_SINGLE_FILE_METADATA_PREP"


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_integrity_gate_document_exists_and_declares_phase_result() -> None:
    text = _doc()
    assert DOC_PATH.exists()
    assert PHASE in text
    assert RESULT in text
    assert PREVIOUS_RESULT in text
    assert CLOSURE_DECISION in text


def test_integrity_gate_document_declares_fixture_pack_under_audit() -> None:
    text = _doc()
    assert EXPECTED_PACK_ID in text
    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "manifest.controlled.json" in text
    assert EXPECTED_RELATIVE_PATH in text


def test_integrity_gate_document_declares_exact_hash_and_byte_requirements() -> None:
    text = _doc()
    assert f"Expected bytes: `{EXPECTED_BYTES}`" in text
    assert EXPECTED_SHA256 in text
    assert EXPECTED_FIXTURE_ID in text
    assert "SHA256" in text


def test_integrity_gate_document_preserves_explicit_non_goals() -> None:
    text = _doc()
    required_non_goals = [
        "create new fixtures",
        "run ffprobe",
        "run FFmpeg",
        "run a scanner",
        "inspect real production material",
        "inspect customer material",
        "touch runtime product behavior",
        "touch backend or frontend surfaces",
    ]
    for phrase in required_non_goals:
        assert phrase in text


def test_fixture_pack_root_and_expected_files_exist() -> None:
    assert FIXTURE_ROOT.is_dir()
    assert README_PATH.is_file()
    assert MANIFEST_PATH.is_file()
    assert MARKER_PATH.is_file()


def test_fixture_pack_contains_only_approved_file_set() -> None:
    files = sorted(path.relative_to(FIXTURE_ROOT).as_posix() for path in FIXTURE_ROOT.rglob("*") if path.is_file())
    assert files == ["README.md", "manifest.controlled.json", EXPECTED_RELATIVE_PATH]


def test_marker_fixture_has_exact_byte_count_and_sha256() -> None:
    payload = MARKER_PATH.read_bytes()
    assert len(payload) == EXPECTED_BYTES
    assert hashlib.sha256(payload).hexdigest() == EXPECTED_SHA256


def test_marker_fixture_is_plain_text_boundary_marker_only() -> None:
    text = MARKER_PATH.read_text(encoding="utf-8")
    assert "CID Local Media Agent controlled non-customer fixture pack v1" in text
    assert "Fixture: controlled_plain_text_marker_v1" in text
    assert "no customer media" in text
    assert "no audio" in text
    assert "no video" in text


def test_manifest_schema_pack_identity_and_status_are_stable() -> None:
    manifest = _manifest()
    assert manifest["schema_version"] == EXPECTED_SCHEMA
    assert manifest["pack_id"] == EXPECTED_PACK_ID
    assert manifest["fixture_root"] == FIXTURE_ROOT.as_posix()
    assert manifest["status"] == "CREATED_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK"
    assert manifest["created_by_gate"] is True


def test_manifest_single_fixture_entry_matches_marker_file() -> None:
    manifest = _manifest()
    fixtures = manifest["fixtures"]
    assert len(fixtures) == 1
    entry = fixtures[0]
    assert entry["fixture_id"] == EXPECTED_FIXTURE_ID
    assert entry["relative_path"] == EXPECTED_RELATIVE_PATH
    assert entry["expected_bytes"] == EXPECTED_BYTES
    assert entry["expected_sha256"] == EXPECTED_SHA256
    assert entry["encoding"] == "utf-8"
    assert entry["mime_type"] == "text/plain"


def test_manifest_boundary_flags_remain_closed() -> None:
    boundary = _manifest()["non_customer_boundary"]
    expected_false_flags = [
        "customer_material_allowed",
        "external_tool_execution_allowed",
        "network_access_allowed",
        "personal_data_allowed",
        "real_production_assets_allowed",
        "runtime_behavior_allowed",
        "saas_or_database_coupling_allowed",
        "scanner_execution_allowed",
        "video_or_audio_fixture_allowed",
    ]
    for flag in expected_false_flags:
        assert boundary[flag] is False


def test_integrity_gate_points_to_metadata_readiness_not_scanner_execution() -> None:
    text = _doc()
    manifest = _manifest()
    assert "READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1" in text
    assert "read_only_single_file_metadata_chain" in manifest["blocked_until_later_gate"]
    assert "minimal_scanner_limited_to_fixture_root" in manifest["blocked_until_later_gate"]
    assert "must still avoid external tool execution" in text
