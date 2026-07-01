from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_controlled_pilot_pack_readiness_review_gate_v1.md"
)


def _text() -> str:
    assert DOC.exists(), f"missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_gate_identity_and_result_token_are_present() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.PILOT.PACK.READINESS.REVIEW.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_PILOT_PACK_READINESS_REVIEW_GATE_V1_CLOSED" in text
    assert "documentation and QA only" in text


def test_purpose_keeps_review_internal_and_non_authorizing() -> None:
    text = _text()
    assert "internal preparation package" in text
    assert "does not create a real pilot" in text
    assert "authorize external installation" in text
    assert "customer-facing production workflow" in text


def test_prior_pack_documents_are_referenced() -> None:
    text = _text()
    required = [
        "controlled_pilot_candidate_gate_v1.md",
        "controlled_pilot_boundary_gate_v1.md",
        "controlled_pilot_prerequisites_gate_v1.md",
        "controlled_pilot_scope_template_gate_v1.md",
        "controlled_pilot_risk_register_template_gate_v1.md",
        "controlled_pilot_evidence_plan_template_gate_v1.md",
        "controlled_pilot_exit_criteria_template_gate_v1.md",
        "controlled_pilot_pack_index_gate_v1.md",
    ]
    for item in required:
        assert item in text


def test_non_authorizations_are_explicit() -> None:
    text = _text()
    required = [
        "a real pilot",
        "external installation",
        "customer media processing",
        "customer data intake",
        "customer environment execution",
        "scanner execution",
        "ffprobe or FFmpeg execution against real media",
        "SaaS or database integration",
        "installer packaging",
        "pricing commitment",
        "legal commitment",
        "support obligation",
        "public demo",
        "production use",
    ]
    for item in required:
        assert item in text


def test_readiness_dimensions_are_complete() -> None:
    text = _text()
    required = [
        "### 1. Completeness",
        "### 2. Consistency",
        "### 3. Decision traceability",
        "### 4. Commercial restraint",
        "### 5. Operational restraint",
        "### 6. Risk posture",
    ]
    for item in required:
        assert item in text


def test_decision_traceability_path_is_present() -> None:
    text = _text()
    required = [
        "External controlled demo seen",
        "Feedback captured",
        "Follow-up decision made",
        "Candidate status considered",
        "Pilot boundary checked",
        "Prerequisites reviewed",
        "Scope drafted",
        "Risks listed",
        "Evidence plan drafted",
        "Exit criteria drafted",
        "Pack index reviewed",
        "Real pilot still blocked",
    ]
    for item in required:
        assert item in text


def test_review_outcome_categories_are_controlled() -> None:
    text = _text()
    required = [
        "READY_FOR_INTERNAL_PILOT_PREPARATION_USE",
        "READY_WITH_RESERVATIONS",
        "NOT_READY_REQUIRES_DOC_FIX",
        "BLOCKED_BY_SCOPE_RISK",
    ]
    for item in required:
        assert item in text


def test_mandatory_closing_position_keeps_real_pilot_blocked() -> None:
    text = _text()
    assert "real pilot still requires a later explicit authorization gate" in text
    assert "internal preparation review only" in text


def test_operator_boundaries_are_present() -> None:
    text = _text()
    allowed = [
        "check whether the pilot preparation documents are complete",
        "explain internally what documents exist",
        "identify missing or conflicting pilot preparation language",
        "decide whether a future pilot conversation can be prepared",
        "keep the next step conservative",
    ]
    blocked = [
        "invite a client into a pilot",
        "request real footage",
        "install anything on a client machine",
        "ask for credentials",
        "process customer media",
        "quote price or delivery dates",
        "present the pack as a signed pilot agreement",
    ]
    for item in allowed + blocked:
        assert item in text


def test_stop_conditions_block_accidental_real_pilot() -> None:
    text = _text()
    required = [
        "suggests a real pilot can start immediately",
        "implies customer material may be accepted",
        "implies installation is ready",
        "implies scanner or media analysis is live for customer use",
        "implies ffprobe or FFmpeg will run against real client media",
        "implies support or service-level commitments exist",
        "implies price or legal terms are final",
        "removes the need for a later explicit real pilot authorization gate",
    ]
    for item in required:
        assert item in text


def test_validation_posture_keeps_scope_to_two_files_and_guards() -> None:
    text = _text()
    assert "this document" in text
    assert "its QA test" in text
    assert "WSL/repo/secrets guard" in text
    assert "PostgreSQL-only regression guard" in text
    assert "HEAD, origin/main, and tag match" in text


def test_document_does_not_contain_forbidden_authorization_language() -> None:
    text = _text().lower()
    forbidden = [
        "real pilot is authorized",
        "customer material is authorized",
        "external installation is authorized",
        "production use is authorized",
        "pricing is final",
        "support is guaranteed",
        "finished product",
    ]
    for item in forbidden:
        assert item not in text
