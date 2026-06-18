from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_qa_gate_v1.md"
)
IMPLEMENTATION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_implementation_v1.md"
)
IMPLEMENTATION_TEST = Path(
    "tests/unit/test_cid_local_media_agent_synthetic_visible_report_markdown_renderer_implementation.py"
)
MODULE_PATH = Path("scripts/cid_local_media_agent_synthetic_visible_report_renderer.py")
SCANNER_PATH = Path("scripts/cid_media_agent_scan.py")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def read(path: Path) -> str:
    assert path.exists(), f"Missing expected file: {path}"
    return path.read_text(encoding="utf-8")


def load_renderer_module():
    spec = importlib.util.spec_from_file_location(
        "cid_synthetic_visible_report_renderer_qa_gate",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_qa_gate_declares_phase_upstream_and_status():
    text = read(QA_DOC)
    assert "VISIBLE.REPORT.MARKDOWN.RENDERER.QA.GATE.V1" in text
    assert "MARKDOWN_RENDERER_QA_GATE_READY_FOR_VALIDATION" in text
    assert "b166f51" in text
    assert "visible-report-markdown-renderer-implementation-v1-20260618" in text
    assert "documentation/test-only" in text
    assert "It does not modify the renderer implementation." in text


def test_required_upstream_files_exist_and_are_referenced():
    text = read(QA_DOC)
    for path in [IMPLEMENTATION_DOC, IMPLEMENTATION_TEST, MODULE_PATH, SCANNER_PATH, FIXTURE]:
        assert path.exists()
    for path in [IMPLEMENTATION_TEST, MODULE_PATH, FIXTURE]:
        assert str(path) in text


def test_qa_gate_decision_and_validation_requirements_are_recorded():
    text = read(QA_DOC)
    assert "QA_GATE_DECISION=READY_FOR_INTERNAL_VALIDATION" in text
    for term in [
        "target QA tests pass",
        "implementation tests pass",
        "related contract/readiness tests pass",
        "staged scope safety check passes",
        "fixture integrity check passes",
        "runtime safety static check passes",
        "scanner not modified check passes",
        "WSL guard passes",
        "PostgreSQL-only regression guard passes",
    ]:
        assert term in text


def test_required_qa_coverage_is_complete():
    text = read(QA_DOC)
    for term in [
        "remains a small isolated script",
        "uses standard library only",
        "remains fixture-only",
        "accepts only the controlled synthetic fixture filename",
        "writes only the deterministic Markdown filename",
        "writes only to a caller-supplied controlled output directory",
        "refuses repository output",
        "refuses missing output directories",
        "refuses overwrite by default",
        "allows overwrite only when explicitly requested",
        "produces deterministic content",
        "does not modify the fixture",
        "does not modify scanner code",
        "does not define CLI wiring",
        "does not define packaging or entry points",
        "does not call network libraries",
        "does not call SaaS services",
        "does not call subprocess or external binary execution",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not read source-media folders",
        "does not process real media",
        "does not generate subtitles",
        "does not export NLE files",
        "does not include absolute paths in the rendered Markdown",
        "does not dump raw JSON in the rendered Markdown",
        "includes synthetic demo disclaimer",
        "includes local-first privacy notice",
        "includes mandatory human review checklist",
        "presents CID as assistive and not substitutive",
    ]:
        assert term in text


def test_scope_remains_blocked_after_qa_gate():
    text = read(QA_DOC)
    for term in [
        "CLI command wiring",
        "packaging",
        "installable entry point",
        "scanner integration",
        "report generator CLI",
        "report artifact committed to repository",
        "HTML/PDF/DOCX/XLSX/CSV output",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "Premiere export",
        "OTIO export",
        "EDL export",
        "XML export",
        "FCPXML export",
        "ffprobe execution",
        "ffmpeg execution",
        "real media probing",
        "real media processing",
        "SaaS upload",
        "SaaS metadata sync",
        "backend integration",
        "frontend integration",
        "database integration",
        "Docker integration",
        "Alembic migration",
        "licensing behavior",
        "installer behavior",
    ]:
        assert term in text


def test_next_phase_is_cli_contract_not_cli_implementation():
    text = read(QA_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.CONTRACT.V1" in text
    assert "documentation/test-only" in text
    assert "before any CLI wiring is implemented" in text


def test_renderer_source_has_no_cli_network_subprocess_or_external_binary_execution_terms():
    source = read(MODULE_PATH)
    forbidden = [
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import httpx",
        "from httpx",
        "import ftplib",
        "import smtplib",
        "os.system",
        "Popen(",
        "check_output(",
        "check_call(",
        "argparse",
        "click",
        "typer",
        "if __name__",
        "DaVinci Resolve export",
        "Avid export",
        "Premiere export",
    ]
    for term in forbidden:
        assert term not in source

    assert "ff" + "probe" not in source
    assert "ff" + "mpeg" not in source


def test_renderer_creates_expected_markdown_and_does_not_modify_fixture(tmp_path):
    module = load_renderer_module()
    before = file_sha256(FIXTURE)

    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)

    after = file_sha256(FIXTURE)
    assert before == after
    assert output == tmp_path / OUTPUT_FILENAME
    assert output.exists()


def test_renderer_output_is_deterministic_with_explicit_overwrite(tmp_path):
    module = load_renderer_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    first = output.read_text(encoding="utf-8")

    output_again = module.render_synthetic_visible_report_markdown(
        FIXTURE,
        tmp_path,
        allow_overwrite=True,
    )
    second = output_again.read_text(encoding="utf-8")

    assert output_again == output
    assert first == second


def test_renderer_refuses_overwrite_repository_output_and_bad_fixture(tmp_path):
    module = load_renderer_module()

    module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)

    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(FIXTURE, Path.cwd())

    bad_fixture = tmp_path / "real_project_report.json"
    bad_fixture.write_text("{}", encoding="utf-8")
    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(bad_fixture, tmp_path, allow_overwrite=True)


def test_rendered_markdown_contains_safety_notices_and_no_false_real_claims(tmp_path):
    module = load_renderer_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    text = output.read_text(encoding="utf-8")
    lowered = text.lower()

    required = [
        "demo sintética",
        "No procede de material real de cliente",
        "local-first",
        "no salen del disco por defecto",
        "No realiza sincronización real",
        "No ejecuta " + "ff" + "probe",
        "No ejecuta " + "ff" + "mpeg",
        "No transcribe audio real",
        "No traduce diálogos reales",
        "No genera subtítulos finales",
        "No exporta a DaVinci Resolve",
        "No valida delivery final",
        "Checklist obligatorio de revisión humana",
        "CID no sustituye",
    ]
    for term in required:
        assert term in text

    forbidden_claims = [
        "sincronización real completada",
        "transcripción real completada",
        "traducción real completada",
        "exportación real completada",
        "delivery validado",
        "material real procesado",
        "subtítulos finales generados",
    ]
    for claim in forbidden_claims:
        assert claim not in lowered


def test_rendered_markdown_does_not_leak_paths_raw_json_or_sensitive_markers(tmp_path):
    module = load_renderer_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    text = output.read_text(encoding="utf-8")

    forbidden = [
        str(FIXTURE.resolve()),
        str(tmp_path.resolve()),
        "/opt/SERVICIOS_CINE",
        "/home/harliesound",
        "\\wsl.localhost",
        "C:\\",
        "{",
        "}",
        "CID_PRIVATE_WORKSPACE",
        "real_project",
        "token",
        "password",
    ]
    for term in forbidden:
        assert term not in text


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in read(QA_DOC).lower()
    assert blocked not in read(Path(__file__)).lower()
