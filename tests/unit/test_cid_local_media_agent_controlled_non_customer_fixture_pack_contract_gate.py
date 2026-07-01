from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/product/local_media_agent/cid_local_media_agent_controlled_non_customer_fixture_pack_contract_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CONTRACT.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_CONTRACT_GATE_V1_CLOSED"


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_contract_document_exists() -> None:
    assert DOC_PATH.exists()


def test_phase_and_result_are_declared() -> None:
    text = _doc()
    assert PHASE in text
    assert RESULT in text


def test_decision_selects_controlled_fixture_first_path() -> None:
    text = _doc()
    assert "CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN" in text
    assert "Define fixture pack contract" in text
    assert "Create fixture pack in a later explicit gate" in text
    assert "read-only single-file metadata" in text


def test_gate_is_documentation_and_qa_only() -> None:
    text = _doc()
    assert "documentation and QA test only" in text
    assert "This gate does not create the path" in text
    assert "does **not** implement it" in text


def test_fixture_creation_and_binary_assets_remain_blocked() -> None:
    text = _doc()
    assert "Creating media fixtures" in text
    assert "Adding binary assets" in text
    assert "Downloading sample media" in text
    assert "Closure does not mean fixtures exist" in text


def test_customer_and_production_material_are_forbidden() -> None:
    text = _doc()
    required = [
        "Using customer footage",
        "Using production footage",
        "Using real rushes",
        "footage from a client",
        "material from a real production",
        "customer material is authorized",
    ]
    for item in required:
        assert item in text


def test_media_tooling_and_scanner_execution_remain_blocked() -> None:
    text = _doc()
    required = [
        "Executing media tooling",
        "Executing a scanner",
        "media tooling is authorized",
        "scanner execution is authorized",
        "No broad scan of user folders",
    ]
    for item in required:
        assert item in text


def test_allowed_and_forbidden_fixture_categories_are_defined() -> None:
    text = _doc()
    assert "Allowed future fixture categories" in text
    assert "Forbidden future fixture categories" in text
    assert "Tiny silent video fixture" in text
    assert "Tiny audio fixture" in text
    assert "copyrighted clips" in text
    assert "private documents" in text


def test_future_manifest_and_checksum_policy_are_required() -> None:
    text = _doc()
    assert "Required future manifest" in text
    assert "Required future checksum policy" in text
    assert "fixture id" in text
    assert "byte size" in text
    assert "checksum" in text
    assert "must fail closed" in text


def test_metadata_and_report_boundaries_preserve_sequence() -> None:
    text = _doc()
    assert "one controlled fixture" in text
    assert "single file only" in text
    assert "controlled fixture only" in text
    assert "visible report gate may consume controlled fixture metadata only" in text
    assert "fixture-root scanner sequencing" in text


def test_commercial_and_operator_boundaries_prevent_overclaiming() -> None:
    text = _doc()
    assert "must not be used to tell a producer" in text
    assert "can already process their material" in text
    assert "operator must stop" in text
    assert "must not substitute personal footage" in text


def test_approved_next_gate_is_planning_not_creation() -> None:
    text = _doc()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.PLAN.GATE.V1" in text
    assert "should still be documentation/test-only" in text
    assert "should still not create binary fixtures" in text
