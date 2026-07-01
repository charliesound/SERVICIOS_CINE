from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_candidate_gate_v1.md"
)


def _read_doc() -> str:
    assert DOC_PATH.exists(), f"Missing gate document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_closure_token_are_present() -> None:
    text = _read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.CANDIDATE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_CANDIDATE_GATE_V1_CLOSED" in text
    assert "documentation and QA only" in text


def test_gate_does_not_authorize_real_pilot_or_customer_material() -> None:
    text = _read_doc()
    required_boundaries = [
        "does not authorize a real pilot",
        "real client material processing",
        "customer-side installation",
        "public demo usage",
        "production usage",
        "pilot start date",
        "product-final claim",
    ]
    for boundary in required_boundaries:
        assert boundary in text


def test_inputs_required_before_classification_are_defined() -> None:
    text = _read_doc()
    required_inputs = [
        "controlled external demo",
        "Feedback was captured",
        "follow-up decision",
        "stakeholder profile",
        "operational pain",
        "not a finished product",
    ]
    for item in required_inputs:
        assert item in text


def test_all_candidate_categories_are_defined() -> None:
    text = _read_doc()
    categories = [
        "STRONG_FUTURE_PILOT_CANDIDATE",
        "POSSIBLE_FUTURE_PILOT_CANDIDATE",
        "WAIT_UNTIL_REAL_SCANNER_CAPABILITY",
        "COMMERCIAL_CONVERSATION_ONLY",
        "NOT_A_FIT_NOW",
    ]
    for category in categories:
        assert category in text


def test_mandatory_classification_fields_are_present() -> None:
    text = _read_doc()
    fields = [
        "contact role category",
        "organization type",
        "stated operational pain",
        "requested workflow",
        "candidate category",
        "confidence level",
        "next safe action",
        "forbidden action",
        "expectation risk level",
        "review date",
    ]
    for field in fields:
        assert field in text


def test_scoring_rubric_is_internal_and_non_binding() -> None:
    text = _read_doc()
    assert "Use this scoring model only as internal guidance" in text
    assert "not a sales qualification score" in text
    assert "Operational pain clarity" in text
    assert "Workflow fit" in text
    assert "Boundary acceptance" in text
    assert "Pilot safety" in text


def test_safe_next_actions_are_paired_with_forbidden_actions() -> None:
    text = _read_doc()
    assert "Safe next action" in text
    assert "Forbidden action" in text
    assert "add to controlled pilot candidate backlog" in text
    assert "start pilot" in text
    assert "process real folders" in text
    assert "offer price or contract" in text


def test_red_flags_and_positive_signals_are_documented() -> None:
    text = _read_doc()
    red_flags = [
        "confidential client material immediately",
        "production-ready",
        "unsupported media processing claims",
        "uncontrolled devices",
    ]
    positive_signals = [
        "chaotic folders",
        "production teams lose time",
        "post supervisor or production coordinator",
        "safe pilot would look like later",
    ]
    for item in red_flags + positive_signals:
        assert item in text


def test_candidate_note_template_contains_required_keys() -> None:
    text = _read_doc()
    keys = [
        "CONTACT_ROLE_CATEGORY:",
        "ORGANIZATION_TYPE:",
        "STATED_OPERATIONAL_PAIN:",
        "MISSING_CAPABILITY_BLOCKING_REAL_PILOT:",
        "CANDIDATE_CATEGORY:",
        "NEXT_SAFE_ACTION:",
        "FORBIDDEN_ACTION:",
        "REVIEW_DATE:",
    ]
    for key in keys:
        assert key in text


def test_operator_language_blocks_overpromising() -> None:
    text = _read_doc()
    assert "I am not marking this as a pilot yet" in text
    assert "possible pilot candidate" in text
    assert "We can start a pilot with your material" in text
    assert "This is ready for your production" in text
    assert "We can install this for your team now" in text


def test_decision_examples_cover_key_stakeholders() -> None:
    text = _read_doc()
    examples = [
        "Productora with multiple active productions",
        "Escuela de cine",
        "Postproduction supervisor",
        "Generic AI-curious contact",
    ]
    for example in examples:
        assert example in text


def test_closure_criteria_preserve_controlled_scope() -> None:
    text = _read_doc()
    criteria = [
        "pilot candidacy is classification only",
        "real pilot start remains blocked",
        "real customer material remains blocked",
        "installation remains blocked",
        "unsupported media processing remains blocked",
        "scoring is internal and non-binding",
    ]
    for criterion in criteria:
        assert criterion in text
