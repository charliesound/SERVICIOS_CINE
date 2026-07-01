from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_risk_register_template_gate_v1.md"
)


def _doc() -> str:
    assert DOC_PATH.exists(), f"missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_gate_identity_and_closure_result_are_declared() -> None:
    text = _doc()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.RISK.REGISTER.TEMPLATE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_RISK_REGISTER_TEMPLATE_GATE_V1_CLOSED" in text
    assert "controlled planning artifact for a future pilot" in text


def test_gate_is_documentation_and_qa_only() -> None:
    text = _doc()
    required = [
        "documentation and QA only",
        "creates no runtime code",
        "creates no scanner behavior",
        "performs no media probing",
        "accepts no customer material",
    ]
    for item in required:
        assert item in text


def test_non_authorization_boundaries_are_explicit() -> None:
    text = _doc()
    blocked = [
        "real customer media",
        "real production material",
        "external installation",
        "processing client files",
        "scanner execution",
        "ffprobe execution",
        "FFmpeg execution",
        "SaaS/database access",
        "pricing commitment",
        "product-final claims",
    ]
    for item in blocked:
        assert item in text


def test_upstream_gate_dependencies_are_listed() -> None:
    text = _doc()
    dependencies = [
        "Controlled local demo runner operator evidence pack gate",
        "Demo narrative gate",
        "Operator runbook gate",
        "Failure modes and recovery gate",
        "Demo acceptance checklist gate",
        "Stakeholder demo brief gate",
        "Controlled external demo readiness gate",
        "External demo feedback capture gate",
        "External demo follow-up decision gate",
        "Controlled pilot candidate gate",
        "Controlled pilot boundary gate",
        "Controlled pilot prerequisites gate",
        "Controlled pilot scope template gate",
    ]
    for dependency in dependencies:
        assert dependency in text


def test_status_severity_and_probability_values_are_controlled() -> None:
    text = _doc()
    for status in [
        "OPEN",
        "MITIGATED",
        "ACCEPTED_WITH_RESERVATION",
        "BLOCKING",
        "REJECTED",
        "NOT_APPLICABLE",
    ]:
        assert status in text
    for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        assert severity in text
    for probability in ["LOW", "MEDIUM", "HIGH", "UNKNOWN"]:
        assert probability in text
    assert "`UNKNOWN` probability must not be treated as safe" in text


def test_risk_ownership_fields_are_complete() -> None:
    text = _doc()
    fields = [
        "risk id",
        "risk title",
        "category",
        "description",
        "trigger condition",
        "severity",
        "probability",
        "owner",
        "mitigation",
        "stop condition",
        "evidence required",
        "current status",
        "decision date",
        "follow-up action",
    ]
    for field in fields:
        assert field in text


def test_required_risk_categories_are_present() -> None:
    text = _doc()
    categories = [
        "Customer data and material risk",
        "Technical readiness risk",
        "Operator and workflow risk",
        "Expectation and commercial risk",
        "Legal, confidentiality, and permission risk",
        "Support and operational risk",
        "Security and local boundary risk",
        "Success criteria and evidence risk",
    ]
    for category in categories:
        assert category in text


def test_minimum_risks_cover_customer_material_and_permissions() -> None:
    text = _doc()
    required_risks = [
        "material ownership unclear",
        "consent incomplete",
        "customer provides more material than allowed",
        "confidential filenames or paths become visible",
        "operator accidentally opens material outside the pilot folder",
        "permission to use material is incomplete",
    ]
    for risk in required_risks:
        assert risk in text


def test_minimum_risks_cover_technical_and_operational_limits() -> None:
    text = _doc()
    required_risks = [
        "scanner real execution not yet authorized",
        "media probing not yet authorized for client material",
        "unsupported codec/container expectations",
        "hardware mismatch between internal demo and customer environment",
        "no signed installer available yet",
        "operator skips preflight",
        "operator fails to clean temporary output",
    ]
    for risk in required_risks:
        assert risk in text


def test_minimum_risks_cover_commercial_legal_and_support_expectations() -> None:
    text = _doc()
    required_risks = [
        "stakeholder interprets controlled demo as finished product",
        "price is discussed before scope and risk acceptance",
        "confidentiality terms not approved",
        "data-processing responsibility unclear",
        "stakeholder lacks authority to approve pilot",
        "no support window approved",
        "rollback process undefined",
    ]
    for risk in required_risks:
        assert risk in text


def test_template_table_and_examples_are_present() -> None:
    text = _doc()
    assert "| Field | Required value |" in text
    assert "RISK-XXX" in text
    assert "Example RISK-001" in text
    assert "Example RISK-002" in text
    assert "Example RISK-003" in text
    assert "The following examples are placeholders" in text


def test_blocking_criteria_prevent_premature_pilot_authorization() -> None:
    text = _doc()
    blocking = [
        "any `CRITICAL` risk remains `OPEN`",
        "any data/material risk is `BLOCKING`",
        "stakeholder authority is unclear",
        "pilot scope is not approved",
        "support boundary is not approved",
        "local-only boundary cannot be preserved",
        "commercial expectations exceed current technical maturity",
        "product-final claims are required by the stakeholder",
    ]
    for item in blocking:
        assert item in text
