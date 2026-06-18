from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md"
)

RENDERER_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md"
)

RENDERER_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md"
)

ARTIFACT_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_qa_gate_v1.md"
)

ARTIFACT_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_artifact_contract_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_gate_declares_phase_status_and_upstream_baseline():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "RENDERER_IMPLEMENTATION_READINESS_GATE_READY_FOR_VALIDATION" in text
    assert "ea5b555" in text
    assert "visible-report-renderer-contract-qa-gate-v1-20260618" in text
    assert "documentation/test-only" in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(DOC)
    for path in [RENDERER_QA, RENDERER_CONTRACT, ARTIFACT_QA, ARTIFACT_CONTRACT, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_readiness_decision_blocks_direct_implementation():
    text = read(DOC)
    assert "READINESS_DECISION=NOT_READY_FOR_RENDERER_IMPLEMENTATION_YET" in text
    assert "The next phase should define the renderer input/output contract before any renderer implementation." in text
    assert "This is intentional." in text


def test_required_before_implementation_list_is_complete():
    text = read(DOC)
    for term in [
        "exact input schema",
        "exact render plan",
        "exact output format for the first implementation",
        "output path policy",
        "artifact naming policy",
        "safe overwrite policy",
        "redaction policy",
        "fixture integrity policy",
        "no real media policy",
        "no ffprobe execution policy",
        "no ffmpeg execution policy",
        "no network default policy",
        "no SaaS integration policy",
        "deterministic rendering policy",
        "human review policy",
        "no false claims policy",
        "manual approval before creating any visible artifact",
    ]:
        assert term in text


def test_allowed_next_phase_is_input_output_contract_only():
    text = read(DOC)
    assert "VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.V1" in text
    assert "That phase must remain documentation/test-only." in text
    assert "It must not implement renderer code." in text
    assert "It must not create a report artifact." in text


def test_not_allowed_next_blocks_implementation_artifacts_and_media():
    text = read(DOC)
    for term in [
        "renderer implementation",
        "renderer runtime implementation",
        "HTML report creation",
        "PDF report creation",
        "DOCX report creation",
        "XLSX report creation",
        "Markdown report artifact creation",
        "generator implementation",
        "loader implementation",
        "template engine implementation",
        "scanner changes",
        "SaaS integration",
        "ffprobe execution",
        "ffmpeg execution",
        "real media probing",
        "real media processing",
        "subtitle generation",
        "NLE export",
    ]:
        assert term in text


def test_future_implementation_checks_are_safe_and_deterministic():
    text = read(DOC)
    for term in [
        "input schema is locked",
        "render plan is locked",
        "first output format is locked",
        "output directory is controlled",
        "output path is deterministic",
        "output path cannot target source media folders",
        "output path cannot target private workspace folders",
        "artifact naming avoids real project identifiers",
        "rendered content uses sanitized synthetic fields only",
        "fixture file remains immutable",
        "no real media is read",
        "no disk scan is performed",
        "no ffprobe execution is performed",
        "no ffmpeg execution is performed",
        "no network call is performed by default",
        "no SaaS upload is performed",
        "no client media is uploaded",
    ]:
        assert term in text


def test_future_implementation_checks_preserve_disclaimers_and_no_claims():
    text = read(DOC)
    for term in [
        "human review disclaimer is visible",
        "synthetic demo disclaimer is visible",
        "no real synchronization claim is made",
        "no real transcription claim is made",
        "no real translation claim is made",
        "no real NLE export claim is made",
        "no delivery validation claim is made",
    ]:
        assert term in text


def test_product_position_is_stakeholder_readable_and_assistive():
    text = read(DOC)
    for term in [
        "synthetic local demo",
        "producción",
        "productor",
        "montaje",
        "ayudante de montaje",
        "DIT",
        "sonido",
        "subtítulos",
        "dirección",
        "postproducción",
        "without pretending that real media has been analyzed",
        "CID remains assistive, not substitutive",
    ]:
        assert term in text


def test_blocked_scope_covers_runtime_media_exports_and_systems():
    text = read(DOC)
    for term in [
        "renderer code",
        "generator code",
        "loader code",
        "template engine code",
        "runtime code",
        "report artifact",
        "rendered report",
        "HTML report",
        "PDF report",
        "DOCX report",
        "XLSX report",
        "CSV report",
        "Markdown report artifact",
        "scanner runtime",
        "SaaS runtime",
        "backend",
        "frontend",
        "database",
        "Alembic migration",
        "Docker configuration",
        "ffprobe execution",
        "ffmpeg execution",
        "media probing",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "Premiere export",
        "client media",
        "real media",
        "private media",
        "source media",
    ]:
        assert term in text


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(DOC).lower()
    assert blocked not in read(Path(__file__)).lower()
