from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_scope_template_gate_v1.md"


def _doc() -> str:
    assert DOC.exists(), f"missing doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_phase_and_result_are_declared():
    text = _doc()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.SCOPE.TEMPLATE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_SCOPE_TEMPLATE_GATE_V1_CLOSED" in text


def test_scope_is_documentation_and_qa_only():
    text = _doc()
    assert "Scope: documentation and QA test only." in text
    assert "This gate does not authorize" in text


def test_template_is_blank_and_reusable():
    text = _doc()
    required = [
        "The template is intentionally blank",
        "candidate organization placeholder",
        "stakeholder role placeholder",
        "scope version placeholder",
        "status label placeholder",
    ]
    for token in required:
        assert token in text


def test_real_execution_and_real_media_remain_blocked():
    text = _doc()
    required = [
        "real client media",
        "production media",
        "real pilot start",
        "product readiness claim",
        "client workstation installation",
    ]
    for token in required:
        assert token in text


def test_status_labels_include_ready_and_blocked_paths():
    text = _doc()
    required = [
        "PILOT_SCOPE_TEMPLATE_BLANK",
        "PILOT_SCOPE_DRAFT_INCOMPLETE",
        "PILOT_SCOPE_READY_FOR_APPROVAL_GATE",
        "PILOT_SCOPE_BLOCKED_BY_UNCLEAR_DATA",
        "PILOT_SCOPE_BLOCKED_BY_TECHNICAL_GAP",
        "PILOT_SCOPE_BLOCKED_BY_COMMERCIAL_AMBIGUITY",
        "PILOT_SCOPE_BLOCKED_BY_LEGAL_OR_CONFIDENTIALITY_GAP",
    ]
    for token in required:
        assert token in text


def test_business_problem_and_objective_placeholders_exist():
    text = _doc()
    required = [
        "operational pain statement",
        "current workflow description",
        "expected learning from the pilot",
        "primary pilot objective",
        "explicit non-objectives",
        "minimum observable evidence",
        "stop condition",
    ]
    for token in required:
        assert token in text


def test_allowed_and_disallowed_input_placeholders_are_defined():
    text = _doc()
    required = [
        "synthetic fixture only",
        "sanitized sample only",
        "client-approved non-production sample",
        "full production folders",
        "camera cards",
        "sound rolls",
        "rushes from active productions",
    ]
    for token in required:
        assert token in text


def test_technical_environment_duration_and_evidence_boundaries_exist():
    text = _doc()
    required = [
        "no real scanner execution",
        "no real FFmpeg execution",
        "no real ffprobe execution",
        "execution machine placeholder",
        "pilot duration placeholder",
        "operator notes",
        "pass/fail checklist",
    ]
    for token in required:
        assert token in text


def test_success_support_legal_and_commercial_placeholders_exist():
    text = _doc()
    required = [
        "time saved hypothesis",
        "support contact",
        "incident stop condition",
        "written approval exists",
        "confidentiality terms exist",
        "price",
        "roadmap commitment",
    ]
    for token in required:
        assert token in text


def test_exit_decisions_do_not_start_real_pilot():
    text = _doc()
    required = [
        "PILOT_SCOPE_NOT_READY",
        "PILOT_SCOPE_NEEDS_REVISION",
        "PILOT_SCOPE_READY_FOR_APPROVAL_GATE",
        "PILOT_SCOPE_DEFERRED_UNTIL_REAL_SCANNER",
        "PILOT_SCOPE_DEFERRED_UNTIL_INSTALLER",
        "No exit decision in this template starts a real pilot.",
    ]
    for token in required:
        assert token in text


def test_stop_conditions_protect_scope():
    text = _doc()
    required = [
        "the client wants to send real media immediately",
        "the client asks for installation before approval",
        "success criteria are vague",
        "confidentiality terms are absent",
        "the requested workflow requires SaaS or database integration",
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
        "controlled pilot prerequisites gate",
    ]
    for token in required:
        assert token in text
