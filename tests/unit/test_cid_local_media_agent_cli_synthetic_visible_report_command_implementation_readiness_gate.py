from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_cli_synthetic_visible_report_command_implementation_readiness_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_cli_synthetic_visible_report_command_contract_v1.md"
)
CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_cli_synthetic_visible_report_command_contract.py")
RENDERER = Path("scripts/cid_local_media_agent_synthetic_visible_report_renderer.py")
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


def test_gate_declares_phase_status_and_baseline():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "CLI_SYNTHETIC_VISIBLE_REPORT_COMMAND_IMPLEMENTATION_READINESS_GATE_READY_FOR_VALIDATION" in text
    assert "dd13871" in text
    assert "cli-synthetic-visible-report-command-contract-v1-20260618" in text
    assert "documentation/test-only" in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(DOC)
    for path in [CONTRACT_DOC, CONTRACT_TEST, RENDERER, RENDERER_IMPL_TEST, RENDERER_QA_TEST, FIXTURE]:
        assert path.exists()
        assert str(path) in text


def test_readiness_decision_authorizes_only_minimal_cli_wiring_with_restrictions():
    text = read(DOC)
    assert "READINESS_DECISION=READY_FOR_MINIMAL_CLI_WIRING_IMPLEMENTATION_WITH_RESTRICTIONS" in text
    for term in [
        "local",
        "synthetic-only",
        "development-scoped",
        "non-installable",
        "non-packaged",
        "does not modify scanner behavior",
    ]:
        assert term in text


def test_this_phase_does_not_implement_or_integrate_runtime_scope():
    text = read(DOC)
    for term in [
        "does not implement CLI wiring",
        "command registration",
        "packaging",
        "installable entry points",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database integration",
        "Docker integration",
        "Alembic migration",
        "external binary execution",
        "media probing",
        "media processing",
        "real media processing",
        "installer behavior",
        "licensing behavior",
    ]:
        assert term in text


def test_implementation_authorization_boundary_is_strict():
    text = read(DOC)
    for term in [
        "minimal development CLI wrapper",
        "pure Python",
        "standard library only",
        "isolated script or module",
        "calls the existing synthetic Markdown renderer",
        "synthetic-visible-report",
        "--fixture",
        "--output-dir",
        "--allow-overwrite",
        "--format markdown",
        "cid_local_media_agent_synthetic_visible_report_v1.md",
        "no overwrite by default",
        "deterministic exit behavior",
        "no media input arguments",
        "no source-media scanning",
        "no scanner integration",
        "no network calls",
        "no SaaS calls",
        "no database calls",
        "no external binary execution",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no real media probing",
        "no real media processing",
        "no subtitle generation",
        "no NLE export",
        "no packaging",
        "no installable entry point",
    ]:
        assert term in text


def test_recommended_future_shape_keeps_scanner_and_packaging_untouched():
    text = read(DOC)
    for term in [
        "scripts/cid_local_media_agent_synthetic_visible_report_cli.py",
        "should not modify:",
        "scripts/cid_media_agent_scan.py",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "package entry point configuration",
        "backend files",
        "frontend files",
        "database files",
        "Docker files",
        "Alembic files",
    ]:
        assert term in text


def test_future_cli_behavior_accepts_only_contract_inputs_and_rejects_scope_creep():
    text = read(DOC)
    for term in [
        "missing fixture",
        "wrong fixture basename",
        "missing output directory",
        "unsafe output directory",
        "existing output without explicit overwrite",
        "non-Markdown format",
        "source media paths",
        "scan paths",
        "upload endpoints",
        "tokens",
        "database URLs",
        "sync options",
        "transcription options",
        "translation options",
        "subtitle options",
        "NLE export options",
        "installer options",
        "licensing options",
    ]:
        assert term in text


def test_future_required_test_coverage_is_complete():
    text = read(DOC)
    for term in [
        "help text states synthetic local demo scope",
        "help text states no real media analysis",
        "help text states no sync, transcription, translation, final subtitles, NLE export, or upload",
        "command accepts only the contract inputs",
        "command rejects non-Markdown format",
        "command rejects wrong fixture basename",
        "command rejects missing output directory",
        "command rejects unsafe output directory",
        "command refuses overwrite by default",
        "command allows overwrite only with `--allow-overwrite`",
        "command creates only the deterministic Markdown filename",
        "command output remains inside the caller-supplied controlled output directory",
        "command does not modify the fixture",
        "command does not modify the renderer",
        "command does not modify scanner code",
        "command does not call scanner code",
        "command does not call network libraries",
        "command does not call SaaS services",
        "command does not call database services",
        "command does not execute external binaries",
        "command does not execute ffprobe",
        "command does not execute ffmpeg",
        "command does not process real media",
        "command does not create HTML, PDF, DOCX, XLSX, CSV, SRT, VTT, XML, FCPXML, EDL, OTIO, MOV, MP4, or WAV",
        "command messages avoid private paths, usernames, machine names, client identifiers, and real project identifiers",
        "generated Markdown still includes synthetic demo, local-first, human review, no-real-media, no-sync, no-transcription, no-translation, no-NLE-export, and assistive-CID notices",
    ]:
        assert term in text


def test_still_blocked_after_readiness_gate():
    text = read(DOC)
    for term in [
        "packaging",
        "installable entry point",
        "production CLI distribution",
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
        "Windows/macOS/Linux installer",
        "signed binaries",
        "updater behavior",
        "activation behavior",
        "iLok/PACE behavior",
    ]:
        assert term in text


def test_next_phase_is_minimal_cli_implementation_only():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.V1" in text
    assert "minimal development CLI wrapper only" in text


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(DOC).lower()
    assert blocked not in read(Path(__file__)).lower()
