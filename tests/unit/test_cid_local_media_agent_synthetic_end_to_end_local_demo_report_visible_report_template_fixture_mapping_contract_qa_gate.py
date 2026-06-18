from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_qa_gate_v1.md")
MAPPING_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md")
MAPPING_TEST = Path("tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract.py")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")
TEMPLATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_v1.md")
TEMPLATE_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_contract_qa_gate_v1.md")

def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")

def test_phase_upstream_commit_and_tag():
    text = read(QA_DOC)
    assert "VISIBLE.REPORT.TEMPLATE.FIXTURE.MAPPING.CONTRACT.QA.GATE.V1" in text
    assert "3b0d58e" in text
    assert "visible-report-template-fixture-mapping-contract-v1-20260618" in text

def test_required_upstream_files_exist_and_are_referenced():
    text = read(QA_DOC)
    for path in [MAPPING_DOC, MAPPING_TEST, FIXTURE, TEMPLATE_DOC, TEMPLATE_QA_DOC]:
        assert path.exists()
        assert str(path) in text

def test_opencode_audit_required_and_read_only():
    text = read(QA_DOC)
    assert "OPENCODE_AUDIT_PASS_RECORDED_BEFORE_FINAL_CLOSURE" in text
    assert "OpenCode is allowed only as a read-only external auditor." in text
    for term in ["must not edit files", "stage files", "commit", "tag", "push", "create artifacts"]:
        assert term in text

def test_blocked_runtime_artifact_and_media_scope():
    text = read(QA_DOC)
    for term in ["renderer code", "generator code", "loader code", "runtime code", "modify fixtures", "modify scanner code", "modify SaaS code", "execute ffprobe", "execute ffmpeg", "inspect real media", "process media", "create PDF", "create DOCX", "create XLSX", "create Markdown report artifact", "touch backend", "touch frontend", "touch database", "touch Alembic", "touch Docker"]:
        assert term in text

def test_audit_brief_preserves_product_safety():
    text = read(QA_DOC)
    for term in ["documentation/test-only", "fixture JSON not modified", "local-first privacy", "Spanish-first stakeholder readability", "production, editing, assistant editing, DIT, sound, subtitles, and postproduction", "no false claims", "mandatory human review", "assistive and not substitutive"]:
        assert term in text

def test_fixture_integrity_and_final_closure_gate():
    text = read(QA_DOC)
    assert str(FIXTURE) in text
    assert "Any staged change to that fixture is a failure." in text
    assert "Final closure is blocked until OpenCode audit is run" in text

def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(QA_DOC).lower()
    assert blocked not in read(Path(__file__)).lower()

def test_opencode_audit_pass_is_recorded():
    text = read(QA_DOC)
    for term in [
        "OPENCODE_AUDIT_RESULT=PASS",
        "READ_ONLY_EXTERNAL_AUDITOR",
        "Required fixes:",
        "NONE",
        "OpenCode did not edit files.",
        "OpenCode did not stage files.",
        "OpenCode did not commit, tag, or push.",
        "OpenCode did not create artifacts.",
        "OpenCode did not implement runtime.",
        "OpenCode did not modify fixtures.",
        "OpenCode did not execute ffprobe or ffmpeg.",
        "OpenCode did not inspect or process real media.",
        "PASS_WITH_OPENCODE_AUDIT",
        "Final closure may proceed only after tests and guards are rerun.",
    ]:
        assert term in text
