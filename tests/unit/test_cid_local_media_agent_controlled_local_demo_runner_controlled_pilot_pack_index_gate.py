from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_pack_index_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_result_token_are_present() -> None:
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.PACK.INDEX.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PACK_INDEX_GATE_V1_CLOSED" in text


def test_gate_is_documentation_and_qa_only() -> None:
    text = _doc_text()
    assert "Gate type: documentation and QA only" in text
    assert "This gate is documentation and QA only." in text
    assert "No runtime implementation." in text
    assert "No command implementation." in text
    assert "No pyproject change." in text


def test_all_pilot_pack_templates_are_indexed() -> None:
    text = _doc_text()
    required = [
        "Pilot prerequisites template",
        "Pilot scope template",
        "Pilot risk register template",
        "Pilot evidence plan template",
        "Pilot exit criteria template",
    ]
    for item in required:
        assert item in text


def test_required_usage_order_is_explicit() -> None:
    text = _doc_text()
    expected_order = [
        "1. Prerequisites.",
        "2. Scope.",
        "3. Risk register.",
        "4. Evidence plan.",
        "5. Exit criteria.",
        "6. Pilot authorization review gate, not included in this gate.",
    ]
    for line in expected_order:
        assert line in text


def test_dependency_map_is_present() -> None:
    text = _doc_text()
    assert "Prerequisites" in text
    assert "-> Scope" in text
    assert "-> Risk Register" in text
    assert "-> Evidence Plan" in text
    assert "-> Exit Criteria" in text
    assert "-> Future Pilot Authorization Review Gate" in text


def test_decision_states_are_bounded_and_do_not_authorize_pilot() -> None:
    text = _doc_text()
    allowed_states = [
        "PACK_NOT_STARTED",
        "PACK_INCOMPLETE",
        "PACK_BLOCKED_BY_PREREQUISITES",
        "PACK_BLOCKED_BY_SCOPE",
        "PACK_BLOCKED_BY_RISK",
        "PACK_BLOCKED_BY_EVIDENCE_PLAN",
        "PACK_BLOCKED_BY_EXIT_CRITERIA",
        "PACK_READY_FOR_FUTURE_AUTHORIZATION_REVIEW",
    ]
    for state in allowed_states:
        assert state in text
    blocked_states = [
        "PILOT_AUTHORIZED",
        "CLIENT_MATERIAL_ALLOWED",
        "EXTERNAL_INSTALLATION_ALLOWED",
        "REAL_PROCESSING_ALLOWED",
        "COMMERCIAL_OFFER_APPROVED",
    ]
    for state in blocked_states:
        assert state in text


def test_completeness_checklist_blocks_real_work() -> None:
    text = _doc_text()
    required = [
        "No real media is accepted.",
        "No external installation is authorized.",
        "No production workflow is promised.",
        "No price is committed.",
        "No legal agreement is implied.",
        "No support obligation is created.",
    ]
    for item in required:
        assert item in text


def test_required_operator_language_is_present() -> None:
    text = _doc_text()
    assert "This is a preparation index for a possible future controlled pilot." in text
    assert "It does not authorize a real pilot" in text
    assert "client material, installation, processing, price, support, or product commitment" in text


def test_blocked_transitions_are_explicit() -> None:
    text = _doc_text()
    required = [
        "Demo feedback directly to real pilot.",
        "Pilot candidate directly to client material.",
        "Scope template directly to installation.",
        "Risk register directly to client processing.",
        "Evidence plan directly to commercial claim.",
        "Exit criteria directly to sales commitment.",
        "Pack index directly to real pilot authorization.",
    ]
    for item in required:
        assert item in text


def test_future_authorization_gate_remains_required() -> None:
    text = _doc_text()
    assert "A future pilot authorization review gate is required" in text
    required = [
        "Accepting real client material.",
        "Running against real media.",
        "Installing on an external client machine.",
        "Providing client support.",
        "Defining pilot dates.",
        "Defining pricing.",
        "Signing any commitment.",
        "Treating outputs as production evidence.",
    ]
    for item in required:
        assert item in text


def test_forbidden_technical_and_commercial_scope_is_present() -> None:
    text = _doc_text()
    required = [
        "No scanner execution.",
        "No ffprobe execution.",
        "No FFmpeg execution.",
        "No real media access.",
        "No client material.",
        "No external installation.",
        "No SaaS access.",
        "No database access.",
        "No backend change.",
        "No frontend change.",
        "No pricing commitment.",
        "No contract commitment.",
        "No support commitment.",
        "No real pilot authorization.",
    ]
    for item in required:
        assert item in text


def test_closure_statement_preserves_boundary() -> None:
    text = _doc_text()
    assert "Closure does not authorize real client work." in text
    assert "without authorizing a real pilot" in text
