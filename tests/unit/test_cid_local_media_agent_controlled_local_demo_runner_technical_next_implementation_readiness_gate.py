from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "product"
    / "local_media_agent"
    / "cid_local_media_agent_controlled_local_demo_runner_technical_next_implementation_readiness_gate_v1.md"
)

DOC_TEXT = DOC_PATH.read_text(encoding="utf-8")


def test_document_exists_and_declares_phase_identity():
    assert DOC_PATH.exists()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.TECHNICAL.NEXT.IMPLEMENTATION.READINESS.GATE.V1" in DOC_TEXT
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_TECHNICAL_NEXT_IMPLEMENTATION_READINESS_GATE_V1_CLOSED" in DOC_TEXT


def test_gate_is_documentation_and_qa_only():
    required = [
        "documentation and QA test only",
        "does not implement that next direction",
        "runtime code",
        "package entrypoints",
        "pyproject configuration",
    ]
    for item in required:
        assert item in DOC_TEXT


def test_non_negotiable_boundary_blocks_real_usage():
    blocked_items = [
        "real customer media",
        "real production project folders",
        "client installation",
        "public demo",
        "paid pilot",
        "customer-facing promise",
        "scanner over arbitrary folders",
        "batch processing",
        "SaaS or database access",
    ]
    for item in blocked_items:
        assert item in DOC_TEXT


def test_current_technical_position_is_captured():
    current_items = [
        "installed export command",
        "installed controlled demo runner",
        "--help",
        "--result-json",
        "--result-json --keep-output",
        "deterministic artifact name, byte count, and SHA evidence",
        "automatic cleanup by default",
        "no write inside the repository",
        "no overwrite",
    ]
    for item in current_items:
        assert item in DOC_TEXT


def test_technical_gap_summary_contains_required_layers():
    gap_items = [
        "controlled non-customer media fixtures",
        "fixture manifest with expected properties",
        "read-only media metadata extraction",
        "safe external command wrapper policy",
        "timeout and error redaction behavior",
        "deterministic visible report over fixture evidence",
        "minimal scanner behavior limited to fixture roots",
        "privacy and data-handling checks",
    ]
    for item in gap_items:
        assert item in DOC_TEXT


def test_candidate_options_are_ordered_and_scanner_is_deferred():
    assert "Option 1 — Controlled non-customer fixture pack" in DOC_TEXT
    assert "Status: suitable as first technical step." in DOC_TEXT
    assert "Option 2 — Read-only single-file metadata extraction over fixture" in DOC_TEXT
    assert "Option 4 — Minimal fixture-root scanner" in DOC_TEXT
    assert "defer until fixture and single-file read-only extraction are stable" in DOC_TEXT


def test_decision_selects_fixture_first_read_only_chain():
    assert "CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_THEN_READ_ONLY_SINGLE_FILE_METADATA_CHAIN" in DOC_TEXT
    assert "begin with a controlled fixture pack" in DOC_TEXT
    assert "read-only single-file metadata extraction chain" in DOC_TEXT
    assert "must not jump directly to a scanner" in DOC_TEXT


def test_recommended_next_gate_is_fixture_pack_readiness():
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.READINESS.GATE.V1" in DOC_TEXT
    assert "controlled, non-customer fixture pack" in DOC_TEXT
    assert "manifest schema" in DOC_TEXT
    assert "must not use customer media" in DOC_TEXT


def test_implementation_order_is_conservative():
    ordered_items = [
        "1. Controlled non-customer fixture pack readiness.",
        "2. Controlled fixture manifest contract.",
        "3. Read-only single-file metadata command wrapper readiness.",
        "4. Read-only single-file metadata implementation over fixture.",
        "5. Visible metadata report over fixture.",
        "6. Minimal fixture-root scanner readiness.",
        "7. Minimal fixture-root scanner implementation.",
        "8. Packaging readiness.",
        "9. External pilot readiness review.",
    ]
    for item in ordered_items:
        assert item in DOC_TEXT


def test_constraints_preserve_project_boundaries():
    constraints = [
        "WSL Ubuntu execution only",
        "canonical repository only",
        "`.venv` activated",
        "PostgreSQL-only project policy remains untouched",
        "no `.env` changes",
        "no database or SaaS access",
        "no backend or frontend work",
        "no broad folder traversal",
        "no network",
        "no writes outside controlled output roots",
    ]
    for item in constraints:
        assert item in DOC_TEXT


def test_blocked_shortcuts_prevent_premature_product_or_pilot_claims():
    shortcuts = [
        "using a real shoot folder as the first test",
        "demonstrating over customer assets",
        "adding scanner traversal before single-file behavior is proven",
        "adding transcription before metadata extraction is safe",
        "adding synchronization before metadata extraction is safe",
        "creating public marketing claims",
        "treating the current demo runner as a product release",
        "treating a candidate as an approved pilot",
    ]
    for item in shortcuts:
        assert item in DOC_TEXT


def test_readiness_checklist_and_close_result_are_present():
    checklist_items = [
        "the next technical target is explicitly named",
        "the target is smaller than a scanner",
        "customer material remains blocked",
        "runtime implementation remains blocked in this gate",
        "pilot execution remains blocked",
        "packaging remains deferred",
        "fixture-first ordering is present",
        "read-only single-file extraction is present as a later step",
        "output boundaries remain controlled",
        "No implementation permission is granted by this gate",
    ]
    for item in checklist_items:
        assert item in DOC_TEXT
