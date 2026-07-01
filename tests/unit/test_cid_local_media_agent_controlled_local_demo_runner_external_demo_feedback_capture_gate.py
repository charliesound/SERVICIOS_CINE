from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_external_demo_feedback_capture_gate_v1.md"
)

EXPECTED_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER."
    "EXTERNAL.DEMO.FEEDBACK.CAPTURE.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_"
    "EXTERNAL_DEMO_FEEDBACK_CAPTURE_GATE_V1_CLOSED"
)

FORBIDDEN_AUTHORIZATIONS = [
    "This gate authorizes a real client pilot",
    "This gate authorizes a paid pilot",
    "This gate authorizes a public demo",
    "This gate authorizes processing client media",
    "This gate authorizes installing on an uncontrolled client machine",
    "This gate authorizes product launch claims",
    "This gate authorizes pricing offers",
    "This gate authorizes SaaS integration claims",
    "This gate authorizes scanner availability claims",
]


def _doc_text() -> str:
    assert DOC_PATH.exists(), f"missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_feedback_capture_gate_identity_and_closure_token_are_present():
    text = _doc_text()
    assert EXPECTED_PHASE in text
    assert EXPECTED_RESULT in text
    assert "Gate identity" in text
    assert "External Demo Feedback Capture Gate V1" in text


def test_scope_is_documentation_and_qa_only():
    text = _doc_text()
    assert "documentation and QA only" in text
    assert "No runtime implementation" in text
    assert "No command implementation" in text
    assert "No pyproject change" in text
    assert "No backend change" in text
    assert "No frontend change" in text


def test_feedback_capture_timing_is_defined():
    text = _doc_text()
    assert "Immediate verbal feedback" in text
    assert "Operator notes" in text
    assert "Internal classification" in text
    assert "within 30 minutes" in text


def test_stakeholder_profile_fields_are_defined():
    text = _doc_text()
    for required in [
        "Stakeholder type",
        "Role in buying decision",
        "Production context",
        "Urgency level",
        "Data sensitivity level",
        "Demo context",
    ]:
        assert required in text


def test_core_feedback_questions_cover_understanding_workflow_value_trust_buying_and_objections():
    text = _doc_text()
    for section in [
        "### Understanding",
        "### Workflow pain",
        "### Value perception",
        "### Trust and boundary",
        "### Buying and adoption",
        "### Objections",
    ]:
        assert section in text


def test_feedback_classification_states_are_conservative():
    text = _doc_text()
    for state in [
        "EXPLORATORY_ONLY",
        "PAIN_CONFIRMED",
        "TECHNICAL_INTEREST_CONFIRMED",
        "COMMERCIAL_INTEREST_CONFIRMED",
        "NOT_A_FIT",
        "WAITLIST_CANDIDATE",
        "PILOT_DISCOVERY_CANDIDATE",
    ]:
        assert state in text
    assert "not an immediate pilot promise" in text


def test_evidence_quality_levels_prevent_overweighting_polite_interest():
    text = _doc_text()
    assert "LOW_EVIDENCE" in text
    assert "MEDIUM_EVIDENCE" in text
    assert "HIGH_EVIDENCE" in text
    assert "vague praise" in text
    assert "Only `HIGH_EVIDENCE` should influence roadmap priority strongly." in text


def test_red_flags_are_captured_before_next_step():
    text = _doc_text()
    for red_flag in [
        "Stakeholder believes the demo is already the full product.",
        "Stakeholder assumes real media scanning is already available.",
        "Stakeholder asks to process confidential material immediately.",
        "Stakeholder asks for a public promise, date, price, or contractual commitment.",
        "Stakeholder asks for a live installation on an uncontrolled machine.",
    ]:
        assert red_flag in text
    assert "Any red flag requires internal review before a next step." in text


def test_feedback_note_template_contains_required_fields():
    text = _doc_text()
    for field in [
        "Feedback record ID:",
        "Demo date:",
        "Operator:",
        "Stakeholder type:",
        "Controlled boundary restated: yes/no",
        "Main pain described:",
        "Current workaround:",
        "Most valuable future output:",
        "Objections:",
        "Red flags:",
        "Evidence quality:",
        "Primary classification:",
        "Recommended next step:",
        "Commitments made:",
        "Internal reviewer:",
    ]:
        assert field in text


def test_commitments_policy_distinguishes_allowed_and_forbidden_wording():
    text = _doc_text()
    assert "Allowed wording" in text
    assert "Forbidden wording" in text
    assert "We are collecting feedback." in text
    assert "This is not yet the final product." in text
    assert "The product is production-ready." in text
    assert "We can process confidential material today." in text


def test_next_step_model_is_not_a_sales_close():
    text = _doc_text()
    for recommendation in [
        "NO_FOLLOW_UP",
        "SEND_SUMMARY_ONLY",
        "ASK_ONE_FOLLOW_UP_QUESTION",
        "SCHEDULE_PRODUCT_DISCOVERY",
        "HOLD_FOR_LATER",
        "INTERNAL_REVIEW_REQUIRED",
    ]:
        assert recommendation in text
    assert "not a sales close" in text


def test_gate_does_not_authorize_forbidden_product_or_client_actions():
    text = _doc_text()
    assert "This gate does not authorize:" in text
    assert "A real client pilot." in text
    assert "A paid pilot." in text
    assert "A public demo." in text
    assert "Processing client media." in text
    assert "Installing on an uncontrolled client machine." in text
    assert "SaaS integration claims." in text
    assert "Scanner availability claims." in text
    assert "Real ffprobe or FFmpeg execution claims." in text
    for forbidden in FORBIDDEN_AUTHORIZATIONS:
        assert forbidden not in text
