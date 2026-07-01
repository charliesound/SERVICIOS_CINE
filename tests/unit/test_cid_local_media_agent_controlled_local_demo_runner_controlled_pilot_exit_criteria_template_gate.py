"""QA gate for CID Local Media Agent controlled pilot exit criteria template."""

from pathlib import Path


DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_exit_criteria_template_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.EXIT.CRITERIA.TEMPLATE.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_EXIT_CRITERIA_TEMPLATE_GATE_V1_CLOSED"


def _doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_document_exists_and_names_phase() -> None:
    text = _doc()
    assert PHASE in text
    assert EXPECTED_RESULT in text


def test_final_exit_classifications_are_complete() -> None:
    text = _doc()
    for token in (
        "PILOT_SUCCESS",
        "PILOT_SUCCESS_WITH_RESERVATIONS",
        "PILOT_INCONCLUSIVE",
        "PILOT_STOPPED_FOR_RISK",
        "PILOT_NO_COMMERCIAL_FIT",
        "PILOT_PENDING_TECHNICAL_DEVELOPMENT",
    ):
        assert token in text


def test_template_requires_scope_evidence_value_and_risk_status() -> None:
    text = _doc()
    for token in (
        "scope_status",
        "evidence_status",
        "value_signal",
        "technical_readiness",
        "operational_readiness",
        "commercial_fit",
        "risk_status",
        "final_classification",
    ):
        assert token in text


def test_hard_stop_conditions_are_present() -> None:
    text = _doc()
    for phrase in (
        "Hard stop conditions",
        "material outside the authorized scope",
        "confidentiality or consent is unclear",
        "critical risk has no mitigation",
        "product capability is missing",
    ):
        assert phrase in text


def test_conservative_next_steps_are_present() -> None:
    text = _doc()
    for token in (
        "PROCEED_TO_NEXT_CONTROLLED_STAGE",
        "REPEAT_WITH_REVISED_SCOPE",
        "PAUSE_UNTIL_TECHNICAL_CAPABILITY_EXISTS",
        "REJECT_PILOT_ESCALATION",
        "REQUIRE_RISK_MITIGATION_FIRST",
        "REQUIRE_COMMERCIAL_CLARIFICATION_FIRST",
    ):
        assert token in text


def test_automatic_escalations_are_blocked() -> None:
    text = _doc()
    for phrase in (
        "automatic production rollout",
        "automatic paid subscription",
        "automatic external installation",
        "automatic processing of real media",
        "automatic SaaS integration",
        "automatic support commitment",
    ):
        assert phrase in text


def test_exit_narrative_sections_are_required() -> None:
    text = _doc()
    for phrase in (
        "What was tested",
        "What was demonstrated",
        "What was not demonstrated",
        "What risk remains",
        "Recommended next controlled step",
    ):
        assert phrase in text


def test_evidence_boundaries_are_explicit() -> None:
    text = _doc()
    for phrase in (
        "evidence produced by the tool",
        "evidence observed by the operator",
        "feedback from the stakeholder",
        "assumptions made by the internal team",
        "items that remain unverified",
    ):
        assert phrase in text


def test_template_blocks_real_pilot_authorization() -> None:
    text = _doc()
    for phrase in (
        "does not authorize a real pilot",
        "customer media ingestion",
        "external installation",
        "customer processing",
        "product-final promises",
    ):
        assert phrase in text


def test_scope_remains_documentation_and_qa_only() -> None:
    text = _doc()
    for phrase in (
        "documentation and QA only",
        "runtime modification",
        "backend changes",
        "frontend changes",
        "installer packaging",
    ):
        assert phrase in text


def test_operator_wording_prevents_overclaiming() -> None:
    text = _doc()
    assert "does not turn the current demo into a finished product" in text
    assert "The pilot proved the product is ready for production use" in text
    assert "We can now process all your real material" in text
    assert "ready for a paid rollout" in text


def test_qa_expectations_cover_required_boundaries() -> None:
    text = _doc()
    for phrase in (
        "includes all six final exit classifications",
        "blocks automatic production rollout",
        "blocks real customer media processing",
        "blocks external installation",
        "requires evidence completeness",
        "requires residual risk classification",
        "requires a written exit narrative",
    ):
        assert phrase in text
