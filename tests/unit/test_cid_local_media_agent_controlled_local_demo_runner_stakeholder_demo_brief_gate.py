from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_stakeholder_demo_brief_gate_v1.md"
)

EXPECTED_GATE = (
    "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER."
    "STAKEHOLDER.DEMO.BRIEF.GATE.V1"
)

EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_"
    "STAKEHOLDER_DEMO_BRIEF_GATE_V1_CLOSED"
)

REQUIRED_STAKEHOLDERS = [
    "Producer",
    "Executive producer managing multiple productions",
    "Jefe/a de producción",
    "Film school or training center",
    "Postproduction company",
    "Sound department or post sound team",
    "Distributor, exhibitor, or institutional stakeholder",
]

REQUIRED_SECTIONS = [
    "## Gate identity",
    "## Purpose",
    "## Non-goals",
    "## Universal demo framing",
    "## Stakeholder profiles",
    "## Demo order by stakeholder type",
    "## Universal feedback capture",
    "## Stop conditions during stakeholder conversations",
    "## Approved next-step asks",
    "## Acceptance checklist for this brief",
    "## Closure statement",
]

FORBIDDEN_CLAIMS = [
    "the full product is finished",
    "real camera files are being scanned",
    "real metadata extraction is active in this demo",
    "real video or audio analysis is happening in this demo",
    "the demo is ready for unattended client use",
    "public launch",
]

PROFILE_REQUIRED_TERMS = [
    "Primary concern:",
    "Recommended opening:",
    "Show first:",
    "Useful question to ask:",
    "Likely objection:",
    "Answer:",
]


def _read_doc() -> str:
    assert DOC_PATH.exists(), f"Missing document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_document_exists_and_declares_gate_identity():
    text = _read_doc()
    assert EXPECTED_GATE in text
    assert EXPECTED_RESULT in text
    assert "controlled technical demo only" in text
    assert "documentation and QA only" in text


def test_required_sections_are_present():
    text = _read_doc()
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_all_required_stakeholder_profiles_are_present():
    text = _read_doc()
    for stakeholder in REQUIRED_STAKEHOLDERS:
        assert stakeholder in text


def test_each_profile_has_operational_brief_elements():
    text = _read_doc()
    for term in PROFILE_REQUIRED_TERMS:
        assert text.count(term) >= len(REQUIRED_STAKEHOLDERS)


def test_profile_specific_focus_is_not_generic_marketing():
    text = _read_doc()
    required_focus_terms = [
        "portfolio visibility",
        "practical handoff pain",
        "teaching professional discipline",
        "ingest discipline",
        "audio file organization",
        "delivery reliability",
    ]
    for term in required_focus_terms:
        assert term in text


def test_demo_boundary_is_repeated_clearly():
    text = _read_doc()
    assert "not yet the full product" in text
    assert "not processing real client footage" in text
    assert "not a scanner" in text
    assert "does not authorize real material" in text
    assert "does not authorize public demo status" in text
    assert "does not authorize production readiness claims" in text


def test_forbidden_claims_are_present_only_as_explicit_non_promises():
    text = _read_doc()
    non_promise_block_start = text.index("The operator must not say:")
    non_promise_block_end = text.index("## Stakeholder profiles")
    non_promise_block = text[non_promise_block_start:non_promise_block_end]
    for claim in FORBIDDEN_CLAIMS:
        assert claim in non_promise_block


def test_universal_feedback_capture_is_actionable():
    text = _read_doc()
    required_feedback_terms = [
        "Stakeholder type.",
        "Their strongest pain point.",
        "Which missing feature they asked for first.",
        "Whether they accepted the controlled-demo boundary.",
        "What proof they would need before a second meeting.",
        "future buyer, tester, advisor",
    ]
    for term in required_feedback_terms:
        assert term in text


def test_stop_conditions_protect_against_overselling():
    text = _read_doc()
    required_stop_terms = [
        "finished product",
        "real client material",
        "production installation",
        "pricing or delivery commitments",
        "public marketing claims",
        "without speculation",
    ]
    for term in required_stop_terms:
        assert term in text


def test_approved_next_steps_do_not_request_sensitive_material_or_payment():
    text = _read_doc()
    assert "feedback on workflow pain" in text
    assert "non-sensitive workflow examples" in text
    assert "private validation conversation" in text
    assert "real client files" in text
    assert "payment commitment" in text
    assert "public endorsement" in text


def test_scope_exclusions_remain_doc_only_and_do_not_add_implementation():
    text = _read_doc()
    excluded_terms = [
        "runtime code",
        "package entrypoints",
        "project configuration",
        "scanner behavior",
        "real media processing",
        "backend services",
        "frontend screens",
        "SaaS integration",
        "deployment configuration",
    ]
    for term in excluded_terms:
        assert term in text


def test_document_does_not_contain_runtime_implementation_snippets():
    text = _read_doc()
    forbidden_runtime_tokens = [
        "subprocess.run(",
        "os.system(",
        "CREATE TABLE",
        "ALTER TABLE",
        "docker compose",
        "stripe",
        "uvicorn",
    ]
    for token in forbidden_runtime_tokens:
        assert token not in text
