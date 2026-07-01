from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_evidence_plan_template_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.EVIDENCE.PLAN.TEMPLATE.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_EVIDENCE_PLAN_TEMPLATE_GATE_V1_CLOSED"


def read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_document_exists_and_declares_gate_identity():
    text = read_doc()
    assert PHASE in text
    assert RESULT in text
    assert "Controlled Pilot Evidence Plan Template Gate V1" in text


def test_document_is_template_only_and_denies_real_pilot_authorization():
    text = read_doc()
    assert "planning artifact only" in text
    assert "does not approve a pilot" in text
    assert "does not authorize a pilot" in text


def test_document_blocks_real_material_and_external_installation():
    text = read_doc()
    assert "real client media" in text
    assert "external installation" in text
    assert "production media" in text
    assert "material ingestion" in text


def test_document_preserves_controlled_runner_reference_evidence():
    text = read_doc()
    assert "controlled_visible_report.controlled.txt" in text
    assert "167" in text
    assert "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f" in text
    assert "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED" in text
    assert "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY" in text


def test_document_defines_required_evidence_categories():
    text = read_doc()
    for phrase in [
        "Technical execution evidence",
        "Workflow value evidence",
        "Feedback evidence",
        "Risk evidence",
        "Privacy and data handling evidence",
        "Operator evidence",
        "Commercial evidence",
    ]:
        assert phrase in text


def test_document_defines_evidence_capture_matrix():
    text = read_doc()
    assert "Evidence capture matrix" in text
    for token in [
        "EVID-TECH-001",
        "EVID-TECH-002",
        "EVID-OPS-001",
        "EVID-VALUE-001",
        "EVID-RISK-001",
        "EVID-STOP-001",
    ]:
        assert token in text


def test_document_distinguishes_evidence_quality_levels():
    text = read_doc()
    for phrase in [
        "Level 0 — Not evidence",
        "Level 1 — Weak evidence",
        "Level 2 — Useful controlled evidence",
        "Level 3 — Pilot-grade evidence",
    ]:
        assert phrase in text


def test_document_includes_success_failure_and_stop_conditions():
    text = read_doc()
    assert "Success evidence placeholders" in text
    assert "Failure evidence placeholders" in text
    assert "Stop conditions" in text
    assert "evidence package is complete" in text
    assert "operator needed to improvise" in text
    assert "success criteria are vague" in text


def test_document_requires_anonymization_and_retention_rules():
    text = read_doc()
    assert "anonymization rule" in text
    assert "retention rule" in text
    assert "deletion rule" in text
    assert "redacted summaries" in text


def test_document_links_to_scope_and_risk_templates_without_replacing_them():
    text = read_doc()
    assert "approved scope reference" in text
    assert "approved risk register reference" in text
    assert "Risk evidence must reference the pilot risk register template instead of replacing it." in text


def test_document_keeps_scope_doc_and_test_only():
    text = read_doc()
    for phrase in [
        "only this document and its QA test are staged",
        "no runtime files are changed",
        "no package entrypoints are changed",
        "no scanner code is changed",
        "no ffprobe or FFmpeg integration is changed",
        "no SaaS, database, backend, frontend, installer, or pyproject file is changed",
    ]:
        assert phrase in text


def test_document_contains_no_customer_specific_fields():
    text = read_doc().lower()
    for forbidden in [
        "customer name;",
        "project title;",
        "real production title;",
        "real file names;",
        "actual media paths;",
        "actual client feedback;",
        "real pilot dates.",
    ]:
        assert forbidden in text
