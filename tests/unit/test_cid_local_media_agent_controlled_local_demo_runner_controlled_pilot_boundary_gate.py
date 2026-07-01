from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_boundary_gate_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER."
    "CONTROLLED.PILOT.BOUNDARY.GATE.V1"
)

RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_BOUNDARY_GATE_V1_CLOSED"


def _text() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_phase_and_closure_result_are_declared():
    text = _text()
    assert PHASE in text
    assert RESULT in text


def test_candidate_and_real_pilot_are_separated():
    text = _text()
    assert "candidate" in text.lower()
    assert "real pilot" in text.lower()
    assert "A candidate can be interesting without being ready for a pilot." in text
    assert "this state is still not a pilot" in text


def test_real_pilot_is_not_authorized():
    text = _text()
    required = [
        "real pilot execution",
        "Real pilot authorized",
        "explicitly out of scope",
        "not authorizing a pilot yet",
    ]
    for phrase in required:
        assert phrase in text


def test_real_material_and_external_installation_are_blocked():
    text = _text()
    required = [
        "No real client file should be accepted at this stage.",
        "client material intake",
        "external installation",
        "client workstation setup",
        "copying material",
        "downloading material",
        "opening client files",
    ]
    for phrase in required:
        assert phrase in text


def test_commercial_promises_are_blocked():
    text = _text()
    required = [
        "commercial pricing commitment",
        "binding delivery date",
        "promise of final product behavior",
        "This is ready for production use.",
        "Send me your material and I will test it.",
    ]
    for phrase in required:
        assert phrase in text


def test_required_future_gates_are_named():
    text = _text()
    required = [
        "pilot scope gate",
        "real material intake policy gate",
        "privacy and confidentiality gate",
        "technical execution readiness gate",
        "support and rollback gate",
        "success criteria gate",
        "pilot approval record gate",
    ]
    for phrase in required:
        assert phrase in text


def test_allowed_classifications_are_defined():
    text = _text()
    required = [
        "DEMO_ONLY_CONTACT",
        "PILOT_CANDIDATE_EARLY",
        "PILOT_CANDIDATE_BLOCKED",
        "PILOT_CANDIDATE_READY_FOR_SCOPE_DISCUSSION",
        "NOT_A_PILOT_CANDIDATE",
    ]
    for phrase in required:
        assert phrase in text


def test_blocked_classifications_are_defined():
    text = _text()
    blocked = [
        "PILOT_APPROVED",
        "REAL_MEDIA_APPROVED",
        "INSTALLATION_APPROVED",
        "PRODUCTION_USE_APPROVED",
        "CLIENT_PROCESSING_APPROVED",
    ]
    for phrase in blocked:
        assert phrase in text


def test_stop_conditions_are_present():
    text = _text()
    required = [
        "Stop the pilot conversation immediately",
        "the prospect asks to send material now",
        "the prospect asks for production use",
        "the prospect wants installation before readiness gates",
        "I want to keep this accurate.",
    ]
    for phrase in required:
        assert phrase in text


def test_current_demo_chain_is_limited():
    text = _text()
    proven = [
        "controlled runner invocation",
        "deterministic controlled artifact",
        "stable artifact byte count",
        "stable artifact digest",
        "negative path fail-closed behavior",
        "no real media access",
        "no scanner execution",
    ]
    not_proven = [
        "real folder scanning",
        "real metadata extraction",
        "waveform sync",
        "transcription",
        "subtitle generation",
        "installer readiness",
        "legal readiness",
    ]
    for phrase in proven + not_proven:
        assert phrase in text


def test_scope_lock_blocks_implementation_runtime_and_product_surface_changes():
    text = _text()
    required = [
        "This phase is documentation and QA only.",
        "runtime code",
        "package entrypoints",
        "command behavior",
        "scanner behavior",
        "media processing",
        "ffprobe behavior",
        "FFmpeg behavior",
        "SaaS code",
        "database code",
        "installer code",
        "backend code",
        "frontend code",
        "pyproject configuration",
    ]
    for phrase in required:
        assert phrase in text


def test_no_runtime_implementation_terms_are_introduced_as_actions():
    text = _text().lower()
    forbidden_action_phrases = [
        "implement scanner",
        "run ffprobe over client media",
        "run ffmpeg over client media",
        "create installer",
        "modify pyproject",
        "alter backend",
        "alter frontend",
        "connect to saas",
        "use database",
        "process real media now",
    ]
    for phrase in forbidden_action_phrases:
        assert phrase not in text
