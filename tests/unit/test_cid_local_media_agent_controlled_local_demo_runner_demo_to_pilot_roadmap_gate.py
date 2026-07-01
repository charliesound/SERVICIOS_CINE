"""QA gate for CID Local Media Agent demo-to-pilot roadmap gate V1."""

from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_demo_to_pilot_roadmap_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.TO.PILOT.ROADMAP.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_TO_PILOT_ROADMAP_GATE_V1_CLOSED"


def _read_doc() -> str:
    assert DOC_PATH.exists(), f"missing roadmap document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_result_are_declared() -> None:
    text = _read_doc()
    assert PHASE in text
    assert RESULT in text
    assert "documentation and QA only" in text


def test_current_capability_is_limited_to_controlled_demo() -> None:
    text = _read_doc()
    required = [
        "Installed export command is available",
        "Installed controlled local demo runner is available",
        "Runner can emit structured JSON evidence",
        "Runner remains demo-only",
        "Runner does not process real media",
    ]
    for item in required:
        assert item in text


def test_roadmap_stages_are_ordered_and_present() -> None:
    text = _read_doc()
    stages = [
        "Stage 1 — Controlled synthetic-to-controlled-media readiness",
        "Stage 2 — Real media preflight architecture",
        "Stage 3 — ffprobe and FFmpeg capability gates",
        "Stage 4 — Scanner capability gates",
        "Stage 5 — Human-visible report maturity",
        "Stage 6 — Packaging and local installation readiness",
        "Stage 7 — Privacy, legal, and pilot agreement readiness",
        "Stage 8 — Pilot execution readiness",
    ]
    positions = [text.index(stage) for stage in stages]
    assert positions == sorted(positions)


def test_technical_gaps_before_pilot_are_explicit() -> None:
    text = _read_doc()
    required = [
        "Real media fixture policy",
        "Safe media probing implementation",
        "External tool execution safety",
        "Scanner runtime readiness",
        "Human-readable report maturity",
        "Packaging readiness",
        "Local installation readiness",
        "Privacy boundary implementation",
        "Pilot evidence automation",
        "Regression coverage for controlled media fixtures",
    ]
    for item in required:
        assert item in text


def test_product_gaps_before_pilot_are_explicit() -> None:
    text = _read_doc()
    required = [
        "Pilot value hypothesis per stakeholder",
        "Pilot success metric",
        "Pilot stop condition",
        "Client-side responsible person",
        "Stakeholder feedback loop",
        "Scope approval",
        "Risk approval",
        "Evidence approval",
        "Exit decision approval",
        "Commercial non-promise wording",
    ]
    for item in required:
        assert item in text


def test_non_authorizations_block_real_pilot_and_client_material() -> None:
    text = _read_doc()
    blocked = [
        "Real pilot.",
        "Real client material.",
        "Public demo.",
        "External installation.",
        "Client device deployment.",
        "Scanner runtime.",
        "ffprobe runtime against real client media.",
        "FFmpeg runtime against real client media.",
        "Network transfer.",
        "SaaS integration.",
        "Database access.",
        "Installer work.",
        "Pricing.",
        "Contracting.",
        "Support obligations.",
        "Production delivery.",
    ]
    for item in blocked:
        assert item in text


def test_ordered_next_gates_are_declared() -> None:
    text = _read_doc()
    required = [
        "Controlled media fixture policy gate",
        "Controlled real-media preflight contract gate",
        "Controlled external tool execution readiness gate",
        "Controlled scanner runtime readiness gate",
        "Controlled human-visible report maturity gate",
        "Controlled packaging readiness gate",
        "Controlled privacy and pilot agreement readiness gate",
        "Controlled pilot execution gate",
    ]
    for item in required:
        assert item in text


def test_operator_language_prevents_overpromising() -> None:
    text = _read_doc()
    assert "The current demo proves a controlled local evidence chain" in text
    assert "It does not yet process your real material" in text
    assert "We can run this on your production folders now" in text
    assert "This is ready as a finished product" in text
    assert "Send me your material and I will test it" in text


def test_acceptance_checklist_preserves_boundaries() -> None:
    text = _read_doc()
    required = [
        "It preserves the current demo boundary",
        "It lists technical gaps before pilot",
        "It lists product gaps before pilot",
        "It defines ordered future gates",
        "It blocks real client material",
        "It blocks external installation",
        "It blocks scanner and external media tooling until dedicated gates exist",
        "It blocks support, pricing, contract, and public claims",
        "It remains documentation and QA only",
    ]
    for item in required:
        assert item in text


def test_document_does_not_authorize_forbidden_actions() -> None:
    text = _read_doc()
    forbidden_claims = [
        "real pilot is approved",
        "real client material is approved",
        "external installation is approved",
        "product is final",
        "production use is approved",
    ]
    lowered = text.lower()
    for claim in forbidden_claims:
        assert claim not in lowered


def test_next_recommended_phase_is_not_real_pilot() -> None:
    text = _read_doc()
    assert "The next recommended phase is a controlled media fixture policy gate, not a real pilot." in text


def test_scope_mentions_only_documentation_and_qa() -> None:
    text = _read_doc()
    assert "documentation and QA only" in text
    assert "repository scope limited to this document and its QA test" in text
