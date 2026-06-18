from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_implementation_readiness_gate_v1.md"
)

INPUT_OUTPUT_QA = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_qa_gate_v1.md"
)

INPUT_OUTPUT_CONTRACT = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_v1.md"
)

READINESS_GATE = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md"
)

FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_gate_declares_phase_status_and_upstream_baseline():
    text = read(DOC)
    assert "VISIBLE.REPORT.MARKDOWN.RENDERER.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "MARKDOWN_RENDERER_IMPLEMENTATION_READINESS_GATE_READY_FOR_VALIDATION" in text
    assert "ee70ae4" in text
    assert "visible-report-renderer-input-output-contract-qa-gate-v1-20260618" in text
    assert "documentation/test-only" in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(DOC)
    for path in [INPUT_OUTPUT_QA, INPUT_OUTPUT_CONTRACT, READINESS_GATE, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_readiness_decision_authorizes_only_minimal_markdown_with_restrictions():
    text = read(DOC)
    assert "READINESS_DECISION=READY_FOR_MINIMAL_MARKDOWN_RENDERER_IMPLEMENTATION_WITH_RESTRICTIONS" in text
    assert "synthetic-only, local-only, deterministic, and test-controlled" in text


def test_implementation_authorization_boundary_is_safe():
    text = read(DOC)
    for term in [
        "pure Python",
        "standard library first",
        "deterministic output",
        "synthetic fixture only",
        "sanitized fields only",
        "controlled temporary output directory in tests",
        "no overwrite by default",
        "no network calls",
        "no SaaS calls",
        "no source-media scanning",
        "no private workspace access",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no real media probing",
        "no real media processing",
        "no subtitle generation",
        "no NLE export",
        "no backend changes",
        "no frontend changes",
        "no database changes",
        "no Docker changes",
        "no Alembic changes",
    ]:
        assert term in text


def test_next_allowed_phase_is_markdown_renderer_implementation_only():
    text = read(DOC)
    assert "VISIBLE.REPORT.MARKDOWN.RENDERER.IMPLEMENTATION.V1" in text
    for term in [
        "uses the input/output contract",
        "creates deterministic Markdown from synthetic validated data",
        "writes only to a test-controlled output directory",
        "cid_local_media_agent_synthetic_visible_report_v1.md",
        "refuses unsafe output directories",
        "refuses overwrite by default",
        "includes visible synthetic demo disclaimer",
        "includes visible local-first privacy notice",
        "includes visible mandatory human review checklist",
        "presents CID as assistive and not substitutive",
        "avoids raw scanner output",
        "avoids raw ffprobe output",
        "avoids raw ffmpeg logs",
        "avoids absolute paths",
        "avoids usernames",
        "avoids machine names",
        "avoids client identifiers",
        "avoids real project identifiers",
    ]:
        assert term in text


def test_recommended_implementation_shape_avoids_scanner_and_cli_contamination():
    text = read(DOC)
    for term in [
        "small isolated module or script",
        "pure renderer function",
        "validating output directory",
        "deterministic Markdown assembly",
        "unit tests using `tmp_path`",
        "no CLI wiring in the same phase",
        "no packaging in the same phase",
        "should not modify `scripts/cid_media_agent_scan.py`",
    ]:
        assert term in text


def test_minimal_future_test_requirements_are_comprehensive():
    text = read(DOC)
    for term in [
        "output file is created only under controlled temporary directory",
        "output filename is deterministic",
        "safe overwrite defaults to false",
        "existing output causes safe failure by default",
        "fixture is not modified",
        "source media folders are not read",
        "ffprobe is not executed",
        "ffmpeg is not executed",
        "network calls are not made",
        "SaaS calls are not made",
        "rendered Markdown includes all required disclaimers",
        "rendered Markdown includes human review checklist",
        "rendered Markdown does not include absolute paths",
        "rendered Markdown does not include raw scanner dumps",
        "rendered Markdown does not include raw ffprobe dumps",
        "rendered Markdown does not include raw ffmpeg logs",
        "rendered Markdown does not claim real synchronization",
        "rendered Markdown does not claim real transcription",
        "rendered Markdown does not claim real translation",
        "rendered Markdown does not claim real NLE export",
        "rendered Markdown does not claim delivery validation",
    ]:
        assert term in text


def test_human_review_requirement_blocks_final_or_real_claims():
    text = read(DOC)
    for term in [
        "synthetic working demo artifact",
        "a real media analysis",
        "a final technical report",
        "a final postproduction report",
        "a real client deliverable",
        "a delivery validation",
        "a DaVinci Resolve export",
        "an Avid export",
        "a Premiere export",
        "final subtitles",
        "a production-ready installer output",
        "Human review remains mandatory",
    ]:
        assert term in text


def test_not_allowed_next_implementation_blocks_scope_creep():
    text = read(DOC)
    for term in [
        "CLI installation",
        "packaging",
        "entry points",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database integration",
        "Docker integration",
        "Alembic migration",
        "HTML rendering",
        "PDF rendering",
        "DOCX rendering",
        "XLSX rendering",
        "CSV rendering",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "Premiere export",
        "ffprobe execution",
        "ffmpeg execution",
        "real media probing",
        "real media processing",
        "client media upload",
        "network default behavior",
        "licensing behavior",
        "installer behavior",
    ]:
        assert term in text


def test_blocked_scope_for_this_phase_covers_artifacts_runtime_media_and_exports():
    text = read(DOC)
    for term in [
        "renderer code",
        "generator code",
        "loader code",
        "template engine code",
        "runtime code",
        "report artifact",
        "rendered report",
        "Markdown report artifact",
        "HTML report",
        "PDF report",
        "DOCX report",
        "XLSX report",
        "CSV report",
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
