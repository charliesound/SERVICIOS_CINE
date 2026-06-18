from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_qa_gate_v1.md")
INPUT_OUTPUT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_v1.md")
INPUT_OUTPUT_TEST = Path("tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract.py")
READINESS_GATE = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md")
RENDERER_QA = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md")
RENDERER_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")

def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")

def test_phase_upstream_commit_and_tag():
    text = read(QA_DOC)
    assert "VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.QA.GATE.V1" in text
    assert "VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.V1" in text
    assert "a5de7cb" in text
    assert "visible-report-renderer-input-output-contract-v1-20260618" in text

def test_required_upstream_files_exist_and_are_referenced():
    text = read(QA_DOC)
    for path in [INPUT_OUTPUT_DOC, INPUT_OUTPUT_TEST, READINESS_GATE, RENDERER_QA, RENDERER_CONTRACT, FIXTURE]:
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
        "create filesystem write behavior",
    ]:
        assert term in text

def test_blocked_artifacts_runtime_media_and_exports():
    text = read(QA_DOC)
    for term in [
        "create HTML",
        "create PDF",
        "create DOCX",
        "create XLSX",
        "create CSV",
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

def test_audit_brief_preserves_input_output_contract_safety():
    text = read(QA_DOC)
    for term in [
        "Markdown is selected only as the first future controlled output format",
        "no Markdown artifact is created",
        "exact input sections and required fields are defined",
        "render order is locked",
        "output path policy is safe",
        "artifact naming policy avoids real identifiers",
        "redaction policy blocks sensitive values",
        "safe overwrite is false by default",
        "render options are allowlisted",
        "unsafe render options are blocked",
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
    ]:
        assert term in text

def test_internal_qa_requirements_are_complete():
    text = read(QA_DOC)
    for term in [
        "input/output contract exists",
        "input/output contract references commit a5de7cb",
        "Markdown future output is selected but not created",
        "exact future input sections are defined",
        "required input fields are defined",
        "input must be synthetic, sanitized, and validated",
        "render order is locked",
        "output path policy blocks unsafe targets",
        "artifact naming avoids real identifiers",
        "redaction policy blocks sensitive values",
        "safe overwrite is false by default",
        "allowed render options are defined",
        "blocked render options are defined",
        "claims policy blocks unsafe real-capability claims",
        "human review policy is visible",
        "renderer implementation is blocked in this phase",
        "artifact creation is blocked in this phase",
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
        "OpenCode did not create artifacts or reports.",
        "OpenCode did not implement renderer, generator, loader, runtime, or template engine code.",
        "OpenCode did not create filesystem write behavior.",
        "OpenCode did not execute ffprobe or ffmpeg.",
        "OpenCode did not inspect or process real media.",
        "PASS_WITH_OPENCODE_AUDIT",
        "Final closure may proceed only after tests and guards are rerun.",
    ]:
        assert term in text
