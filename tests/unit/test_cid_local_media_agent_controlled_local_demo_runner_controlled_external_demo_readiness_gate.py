from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "product" / "local_media_agent" / "cid_local_media_agent_controlled_local_demo_runner_controlled_external_demo_readiness_gate_v1.md"
TEXT = DOC.read_text(encoding="utf-8")


def test_document_exists_and_has_closure_result():
    assert DOC.exists()
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_EXTERNAL_DEMO_READINESS_GATE_V1_CLOSED" in TEXT


def test_phase_identifier_and_baseline_are_present():
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.CONTROLLED.EXTERNAL.DEMO.READINESS.GATE.V1" in TEXT
    assert "c92457018da79085127031e3a4720c9e1c6feaa2" in TEXT
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_STAKEHOLDER_DEMO_BRIEF_GATE_V1_CLOSED" in TEXT


def test_scope_remains_documentation_and_qa_only():
    assert "This phase is documentation and QA only" in TEXT
    for forbidden in [
        "runtime changes",
        "pyproject changes",
        "command changes",
        "scanner changes",
        "ffprobe or FFmpeg invocation changes",
        "real media material",
        "real client material",
        "SaaS changes",
        "database changes",
        "installer changes",
        "backend changes",
        "frontend changes",
    ]:
        assert forbidden in TEXT


def test_demo_status_is_controlled_not_public_or_final():
    assert "A controlled technical local demo" in TEXT
    assert "a finished product" in TEXT
    assert "a public demo" in TEXT
    assert "a production workflow" in TEXT
    assert "not a final product" in TEXT


def test_pre_demo_checklist_includes_runner_and_evidence():
    for token in [
        "cid-local-media-agent-controlled-local-demo-runner --help",
        "cid-local-media-agent-controlled-local-demo-runner --result-json",
        "cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output",
        "controlled_visible_report.controlled.txt",
        "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f",
        "controlled artifact byte size is `167`",
        "default cleanup removes temporary output",
        "preserved output can be manually cleaned",
    ]:
        assert token in TEXT


def test_safe_opening_and_safe_closing_are_defined():
    assert "Safe opening statement" in TEXT
    assert "What I am going to show is a controlled technical demo" in TEXT
    assert "Safe closing statement" in TEXT
    assert "not that this is already the finished product" in TEXT


def test_operator_allowed_and_forbidden_language_is_explicit():
    assert "What the operator may say" in TEXT
    assert "What the operator must not say" in TEXT
    assert "This is ready for your production" in TEXT
    assert "It already scans your media folders" in TEXT
    assert "Delivery date is guaranteed" in TEXT
    assert "We can process your real material now" in TEXT


def test_stakeholder_specific_framing_is_present():
    for profile in [
        "Producer",
        "Executive producer with several productions",
        "Head of production",
        "Film school",
        "Postproduction supervisor",
        "Sound/post professional",
        "Institutional or distribution contact",
    ]:
        assert profile in TEXT


def test_feedback_capture_protocol_is_structured():
    assert "Feedback capture protocol" in TEXT
    for item in [
        "Pain point",
        "Value signal",
        "Trust signal",
        "Objection",
        "Priority",
        "What part of this would save someone time?",
        "Which evidence would you need before trusting it?",
    ]:
        assert item in TEXT


def test_no_show_and_stop_conditions_are_defined():
    assert "No-show conditions" in TEXT
    assert "Stop conditions during the meeting" in TEXT
    assert "worktree is dirty before the demo" in TEXT
    assert "SHA does not match the approved controlled value" in TEXT
    assert "Do not improvise a workaround" in TEXT
    assert "fail closed" in TEXT


def test_external_follow_up_is_limited_and_non_binding():
    assert "External follow-up boundary" in TEXT
    assert "non-binding pilot exploration" in TEXT
    assert "paid deployment" in TEXT
    assert "guaranteed dates" in TEXT
    assert "real-media ingestion without a future approved phase" in TEXT


def test_acceptance_criteria_cover_external_readiness():
    assert "Acceptance criteria" in TEXT
    for criterion in [
        "phase identifier is present",
        "external showing is limited",
        "public demo is forbidden",
        "real material processing is forbidden",
        "SHA and byte values are present",
        "stakeholder-specific framing is present",
        "next steps are limited and non-binding",
    ]:
        assert criterion in TEXT
