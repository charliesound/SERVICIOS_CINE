from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md")
RENDERER_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md")
RENDERER_TEST = Path("tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract.py")
ARTIFACT_QA = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_qa_gate_v1.md")
ARTIFACT_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_v1.md")
MAPPING_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_template_fixture_mapping_contract_v1.md")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")

def test_phase_upstream_commit_and_tag():
    text = read(QA_DOC)
    assert "VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1" in text
    assert "VISIBLE.REPORT.RENDERER.CONTRACT.V1" in text
    assert "b112aed" in text
    assert "visible-report-renderer-contract-v1-20260618" in text

def test_required_upstream_files_exist_and_are_referenced():
    text = read(QA_DOC)
    for path in [RENDERER_DOC, RENDERER_TEST, ARTIFACT_QA, ARTIFACT_CONTRACT, MAPPING_CONTRACT, FIXTURE]:
        assert path.exists()
        assert str(path) in text

def test_documentation_only_and_opencode_pending():
    text = read(QA_DOC)
    assert "documentation/test-only" in text
    assert "QA_GATE_READY_FOR_INTERNAL_VALIDATION" in text
    assert "OPENCODE_AUDIT_PASS_RECORDED_BEFORE_FINAL_CLOSURE" in text
    assert "OpenCode is allowed only as a read-only external auditor." in text

def test_opencode_must_not_write_or_implement():
    text = read(QA_DOC)
    for term in [
        "edit files",
        "stage files",
        "commit",
        "tag",
        "push",
        "create artifacts",
        "implement renderer code",
        "implement generator code",
        "implement loader code",
        "implement template engine code",
        "implement runtime code",
    ]:
        assert term in text

def test_blocked_artifacts_runtime_media_and_exports():
    text = read(QA_DOC)
    for term in [
        "create HTML",
        "create PDF",
        "create DOCX",
        "create XLSX",
        "create Markdown report artifact",
        "rendered report",
        "execute ffprobe",
        "execute ffmpeg",
        "inspect real media",
        "process media",
        "create subtitles",
        "create NLE exports",
        "touch backend",
        "touch frontend",
        "touch database",
        "touch Alembic",
        "touch Docker",
    ]:
        assert term in text

def test_audit_brief_preserves_product_safety():
    text = read(QA_DOC)
    for term in [
        "local-only",
        "local-first privacy",
        "Spanish-first stakeholder readability",
        "synthetic-only demonstration",
        "mandatory human review",
        "assistive and not substitutive",
        "no false claims",
        "future renderer inputs are controlled",
        "future renderer outputs are declared only as possible future controlled formats",
    ]:
        assert term in text

def test_internal_qa_blocks_unsafe_progression():
    text = read(QA_DOC)
    for term in [
        "future renderer is defined but not implemented",
        "renderer inputs are controlled",
        "renderer outputs are declared but not created",
        "artifact creation is blocked in this phase",
        "renderer, generator, loader, template engine, and runtime implementation are blocked",
        "scanner changes are blocked",
        "SaaS integration is blocked",
        "ffprobe and ffmpeg execution are blocked",
        "real media processing is blocked",
        "OpenCode audit is required before final closure",
    ]:
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
        "OpenCode did not implement renderer, generator, loader, runtime, or template engine code.",
        "OpenCode did not execute ffprobe or ffmpeg.",
        "OpenCode did not inspect or process real media.",
        "PASS_WITH_OPENCODE_AUDIT",
        "Final closure may proceed only after tests and guards are rerun.",
    ]:
        assert term in text
