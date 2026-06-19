from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_contract_v1.md")

RENDERER = Path("scripts/cid_local_media_agent_synthetic_visible_report_renderer.py")
RENDERER_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_qa_gate_v1.md"
)
RENDERER_IMPL_TEST = Path(
    "tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_implementation.py"
)
RENDERER_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_qa_gate.py"
)
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def test_contract_declares_phase_status_and_baseline():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.CONTRACT.V1" in text
    assert "CLI_SYNTHETIC_VISIBLE_REPORT_COMMAND_CONTRACT_READY_FOR_VALIDATION" in text
    assert "0d4e322" in text
    assert "visible-report-markdown-renderer-qa-gate-v1-20260618" in text
    assert "documentation/test-only" in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(DOC)
    for path in [RENDERER, RENDERER_QA_DOC, RENDERER_IMPL_TEST, RENDERER_QA_TEST, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_contract_does_not_authorize_cli_or_packaging_implementation():
    text = read(DOC)
    for term in [
        "does not implement CLI wiring",
        "command registration",
        "packaging",
        "entry points",
        "installer behavior",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database integration",
        "Docker integration",
        "Alembic migration",
    ]:
        assert term in text


def test_future_command_name_and_purpose_are_defined():
    text = read(DOC)
    assert "synthetic-visible-report" in text
    assert "cid-local-media-agent synthetic-visible-report" in text
    for term in [
        "synthetic-only",
        "local-only",
        "deterministic",
        "human-review gated",
        "non-destructive",
        "no-overwrite by default",
        "no network by default",
        "no media-processing by default",
        "no scanner integration by default",
        "no SaaS integration by default",
    ]:
        assert term in text


def test_future_allowed_inputs_are_strictly_limited():
    text = read(DOC)
    for term in [
        "--fixture",
        "--output-dir",
        "--allow-overwrite",
        "--format markdown",
        "synthetic_demo_report_fixture_v1.json",
        "The output directory must already exist",
    ]:
        assert term in text

    for term in [
        "source media directory",
        "client media directory",
        "private workspace directory",
        "recursive scan directory",
        "upload URL",
        "SaaS endpoint",
        "API token",
        "database URL",
        "installer flags",
        "licensing flags",
        "sync flags",
        "transcription flags",
        "translation flags",
        "NLE export flags",
    ]:
        assert term in text


def test_future_allowed_output_is_single_markdown_file():
    text = read(DOC)
    assert "cid_local_media_agent_synthetic_visible_report_v1.md" in text
    for term in [
        "HTML",
        "PDF",
        "DOCX",
        "XLSX",
        "CSV",
        "SRT",
        "VTT",
        "XML",
        "FCPXML",
        "EDL",
        "OTIO",
        "MOV",
        "MP4",
        "WAV",
        "database records",
        "SaaS records",
        "reports committed to the repository",
    ]:
        assert term in text


def test_future_exit_behavior_is_deterministic_and_safe():
    text = read(DOC)
    for term in [
        "exit success when the Markdown report is created safely",
        "exit failure when fixture basename is not allowed",
        "exit failure when fixture file does not exist",
        "exit failure when output directory does not exist",
        "exit failure when output directory is unsafe",
        "exit failure when output file already exists and overwrite is not explicitly allowed",
        "exit failure when requested format is not Markdown",
        "exit failure when any network, SaaS, scanner, media, subtitle, or NLE operation is requested",
    ]:
        assert term in text


def test_future_user_facing_messages_preserve_privacy():
    text = read(DOC)
    for term in [
        "generated filename",
        "synthetic demo status",
        "local-first privacy reminder",
        "human review reminder",
        "stack traces by default",
        "absolute paths when not needed",
        "usernames",
        "machine names",
        "client identifiers",
        "real project identifiers",
        "raw JSON dumps",
        "scanner dumps",
        "external binary logs",
    ]:
        assert term in text


def test_future_safety_requirements_keep_media_and_services_blocked():
    text = read(DOC)
    for term in [
        "no source-media scanning",
        "no real media probing",
        "no real media processing",
        "no waveform sync",
        "no timecode sync",
        "no clap sync",
        "no transcription",
        "no translation",
        "no subtitle generation",
        "no DaVinci Resolve export",
        "no Avid export",
        "no Premiere export",
        "no OTIO export",
        "no EDL export",
        "no XML export",
        "no FCPXML export",
        "no external binary execution",
        "no network calls",
        "no SaaS calls",
        "no backend calls",
        "no frontend calls",
        "no database calls",
        "no Docker use",
        "no Alembic use",
        "no installer behavior",
        "no licensing behavior",
    ]:
        assert term in text


def test_future_help_text_requirements_block_false_claims():
    text = read(DOC)
    for term in [
        "this is a synthetic local demo command",
        "it does not analyze real media",
        "it does not synchronize real audio/video",
        "it does not transcribe real audio",
        "it does not translate real dialogue",
        "it does not generate final subtitles",
        "it does not export to NLE",
        "it does not upload client material",
        "human review is mandatory",
        "CID is assistive and not substitutive",
    ]:
        assert term in text


def test_future_implementation_remains_separately_gated():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "That phase should still be documentation/test-only" in text
    assert "Only after that should a real implementation phase be considered." in text


def test_still_blocked_scope_is_explicit():
    text = read(DOC)
    for term in [
        "CLI implementation",
        "packaging",
        "installable entry point",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database integration",
        "Docker integration",
        "Alembic migration",
        "installer behavior",
        "licensing behavior",
        "real media processing",
        "external binary execution",
        "subtitle generation",
        "NLE export",
        "committed report artifacts",
    ]:
        assert term in text


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(DOC).lower()
    assert blocked not in read(Path(__file__)).lower()
