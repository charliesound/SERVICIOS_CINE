from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_prerequisites_gate_v1.md"


def _doc() -> str:
    assert DOC.exists(), f"missing doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_phase_and_result_are_declared():
    text = _doc()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.PREREQUISITES.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PREREQUISITES_GATE_V1_CLOSED" in text


def test_scope_is_documentation_and_qa_only():
    text = _doc()
    assert "Scope: documentation and QA test only." in text
    assert "This gate does not authorize a real pilot." in text


def test_real_pilot_and_real_media_remain_blocked():
    text = _doc()
    required = [
        "real client media",
        "production media",
        "external installation",
        "pilot start",
        "product readiness claim",
    ]
    for token in required:
        assert token in text


def test_human_consent_and_authorization_are_required():
    text = _doc()
    required = [
        "written authorization from the client-side decision maker",
        "named internal CID owner",
        "named client owner",
        "named technical contact",
    ]
    for token in required:
        assert token in text


def test_scope_and_data_boundaries_are_defined():
    text = _doc()
    required = [
        "exact use case",
        "exact allowed inputs",
        "exact disallowed inputs",
        "maximum duration",
        "whether media is synthetic",
        "real client material remains blocked",
    ]
    for token in required:
        assert token in text


def test_technical_prerequisites_are_required_before_future_pilot():
    text = _doc()
    required = [
        "real scanner readiness",
        "real media preflight readiness",
        "FFmpeg/ffprobe execution policy",
        "timeout policy",
        "cleanup policy",
        "QA coverage for every enabled path",
    ]
    for token in required:
        assert token in text


def test_legal_confidentiality_and_success_criteria_are_required():
    text = _doc()
    required = [
        "NDA or written confidentiality terms",
        "retention/deletion policy",
        "permitted evidence collection",
        "Success criteria must be measurable",
        "does not create legal approval",
    ]
    for token in required:
        assert token in text


def test_support_rollback_and_commercial_boundaries_are_preserved():
    text = _doc()
    required = [
        "pilot stop procedure",
        "cleanup procedure",
        "rollback path",
        "No support obligation is created by this gate.",
        "pilot candidate does not equal paid customer",
        "pricing remains separate",
    ]
    for token in required:
        assert token in text


def test_decision_statuses_include_ready_and_blocked_paths():
    text = _doc()
    required = [
        "PILOT_PREREQUISITES_NOT_READY",
        "PILOT_PREREQUISITES_PARTIAL",
        "PILOT_PREREQUISITES_READY_FOR_PLANNING_GATE",
        "PILOT_BLOCKED_BY_DATA_RISK",
        "PILOT_BLOCKED_BY_TECHNICAL_READINESS",
        "PILOT_BLOCKED_BY_COMMERCIAL_AMBIGUITY",
    ]
    for token in required:
        assert token in text


def test_operator_language_blocks_overpromising():
    text = _doc()
    required = [
        "This is a prerequisite review for a possible future controlled pilot.",
        "If the prerequisites are unclear, the correct decision is to pause",
        "We can start the pilot now.",
        "Send me your production media.",
        "This is the final product.",
    ]
    for token in required:
        assert token in text


def test_stop_conditions_protect_scope():
    text = _doc()
    required = [
        "the client wants to send real media immediately",
        "the client requests installation",
        "confidentiality terms are absent",
        "success criteria are vague",
        "the client expects production reliability",
    ]
    for token in required:
        assert token in text


def test_prior_gate_dependencies_are_listed():
    text = _doc()
    required = [
        "operator evidence pack gate",
        "demo narrative gate",
        "operator runbook gate",
        "failure modes recovery gate",
        "demo acceptance checklist gate",
        "stakeholder demo brief gate",
        "controlled external demo readiness gate",
        "external demo feedback capture gate",
        "external demo follow-up decision gate",
        "controlled pilot candidate gate",
        "controlled pilot boundary gate",
    ]
    for token in required:
        assert token in text
