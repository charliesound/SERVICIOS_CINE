from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_external_demo_followup_decision_gate_v1.md"
)

RESULT_TOKEN = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_FOLLOWUP_DECISION_GATE_V1_CLOSED"
PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.EXTERNAL.DEMO.FOLLOWUP.DECISION.GATE.V1"


def _text() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_result_token_are_declared():
    text = _text()
    assert PHASE in text
    assert RESULT_TOKEN in text
    assert "documentation and QA only" in text
    assert "controlled follow-up decision readiness" in text


def test_all_followup_decision_outcomes_are_present():
    text = _text()
    required = [
        "Future controlled pilot candidate",
        "Second controlled demo candidate",
        "Hold until real scanner capability exists",
        "Commercial conversation candidate",
        "Low-fit or no-follow-up candidate",
    ]
    for item in required:
        assert item in text


def test_insufficient_feedback_fallback_is_required():
    text = _text()
    assert "INSUFFICIENT_FEEDBACK_REQUIRES_INTERNAL_REVIEW" in text
    assert "If these inputs are missing" in text
    assert "feedback inputs" in text


def test_decision_tokens_are_fixed_and_complete():
    text = _text()
    tokens = [
        "FOLLOWUP_DECISION_FUTURE_CONTROLLED_PILOT_CANDIDATE",
        "FOLLOWUP_DECISION_SECOND_CONTROLLED_DEMO_CANDIDATE",
        "FOLLOWUP_DECISION_HOLD_UNTIL_REAL_SCANNER_CAPABILITY",
        "FOLLOWUP_DECISION_COMMERCIAL_DISCOVERY_CANDIDATE",
        "FOLLOWUP_DECISION_LOW_FIT_NO_FOLLOWUP",
        "FOLLOWUP_DECISION_INSUFFICIENT_FEEDBACK_REQUIRES_INTERNAL_REVIEW",
    ]
    for token in tokens:
        assert token in text
    assert "No other decision token is allowed" in text


def test_each_outcome_defines_allowed_and_forbidden_actions():
    text = _text()
    assert text.count("Allowed next action") >= 5
    assert text.count("Forbidden next action") >= 5
    assert "Recommended wording" in text


def test_stop_conditions_are_explicit():
    text = _text()
    assert "Red flags requiring stop" in text
    stop_items = [
        "process real material immediately",
        "production-ready",
        "public download",
        "installer access",
        "firm delivery date",
        "overstate the current capability",
    ]
    for item in stop_items:
        assert item in text


def test_non_negotiable_boundaries_remain_in_place():
    text = _text()
    boundaries = [
        "No production claim",
        "No public demo claim",
        "No final product claim",
        "No real client media processing",
        "No scanner execution claim",
        "No ffprobe or FFmpeg execution claim",
        "No SaaS integration claim",
        "No database access claim",
        "No installer claim",
        "No pricing commitment",
        "No delivery date commitment",
        "No pilot commitment without a separate future gate",
    ]
    for boundary in boundaries:
        assert boundary in text


def test_followup_record_fields_are_defined():
    text = _text()
    fields = [
        "Demo date",
        "Stakeholder category",
        "Pain statement",
        "Main objection",
        "Buying-context signal",
        "Decision outcome",
        "Reason for outcome",
        "Forbidden actions explicitly avoided",
        "Review date",
    ]
    for field in fields:
        assert field in text


def test_record_excludes_sensitive_or_confidential_material():
    text = _text()
    forbidden_record_items = [
        "confidential client material",
        "real media paths",
        "private script content",
        "production secrets",
        "credentials",
    ]
    for item in forbidden_record_items:
        assert item in text


def test_allowed_and_forbidden_gate_outputs_are_clear():
    text = _text()
    allowed = [
        "A decision classification",
        "A conservative next-step recommendation",
        "A list of risks",
        "A list of missing evidence",
        "A future-gate recommendation",
    ]
    forbidden = [
        "Product roadmap commitment",
        "Pilot agreement",
        "Installation instruction for external users",
        "Real media intake instruction",
        "Commercial pricing",
        "Public launch statement",
    ]
    for item in allowed + forbidden:
        assert item in text


def test_acceptance_criteria_are_complete():
    text = _text()
    criteria = [
        "The five main follow-up outcomes are present",
        "The insufficient-feedback outcome is present",
        "Each outcome has allowed and forbidden next actions",
        "Stop conditions are explicit",
        "Decision tokens are fixed",
        "Scope remains documentation and QA only",
    ]
    for item in criteria:
        assert item in text


def test_closure_statement_does_not_authorize_pilot_or_product_readiness():
    text = _text()
    assert RESULT_TOKEN in text
    assert "does not mean that a pilot is authorized" in text
    assert "commercial offer is ready" in text
    assert "production-ready" in text
