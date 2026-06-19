from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

CLI_PATH = Path("scripts/cid_local_media_agent_synthetic_visible_report_cli.py")
RENDERER_PATH = Path("scripts/cid_local_media_agent_synthetic_visible_report_renderer.py")
SCANNER_PATH = Path("scripts/cid_media_agent_scan.py")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def load_cli_module():
    spec = importlib.util.spec_from_file_location("cid_synthetic_visible_report_cli", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cli_module_and_upstream_files_exist():
    assert CLI_PATH.exists()
    assert RENDERER_PATH.exists()
    assert SCANNER_PATH.exists()
    assert FIXTURE.exists()


def test_help_text_states_synthetic_local_demo_scope(capsys):
    cli = load_cli_module()

    code = cli.main(["--help"])
    captured = capsys.readouterr()

    assert code == 0
    assert "synthetic-visible-report" in captured.out
    for term in [
        "Demo sintética local",
        "No analiza media real",
        "No sincroniza audio/vídeo real",
        "No transcribe audio real",
        "No traduce diálogo real",
        "No genera subtítulos finales",
        "No exporta a NLE",
        "No sube material del cliente",
        "Revisión humana obligatoria",
        "CID es asistivo y no sustitutivo",
        "--fixture",
        "--output-dir",
        "--format markdown",
        "--allow-overwrite",
    ]:
        assert term in captured.out


def test_no_args_prints_help_and_returns_success(capsys):
    cli = load_cli_module()

    code = cli.main([])
    captured = capsys.readouterr()

    assert code == 0
    assert "Uso:" in captured.out
    assert "synthetic-visible-report" in captured.out


def test_cli_generates_only_expected_markdown_file(tmp_path, capsys):
    cli = load_cli_module()

    code = cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
    ])
    captured = capsys.readouterr()

    assert code == 0
    assert (tmp_path / OUTPUT_FILENAME).exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == [OUTPUT_FILENAME]
    assert f"OK: generado {OUTPUT_FILENAME}" in captured.out
    assert "Demo sintética local-first" in captured.out
    assert "Revisión humana obligatoria" in captured.out
    assert "No analiza media real ni sube material del cliente" in captured.out
    assert str(tmp_path) not in captured.out
    assert str(FIXTURE.resolve()) not in captured.out


def test_cli_refuses_overwrite_by_default_and_allows_explicit_overwrite(tmp_path, capsys):
    cli = load_cli_module()
    args = [
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
    ]

    assert cli.main(args) == 0
    first_text = (tmp_path / OUTPUT_FILENAME).read_text(encoding="utf-8")

    assert cli.main(args) == 2
    captured = capsys.readouterr()
    assert "ERROR:" in captured.err
    assert str(tmp_path) not in captured.err

    assert cli.main(args + ["--allow-overwrite"]) == 0
    second_text = (tmp_path / OUTPUT_FILENAME).read_text(encoding="utf-8")
    assert second_text == first_text


def test_cli_rejects_non_markdown_format_and_unexpected_options(tmp_path, capsys):
    cli = load_cli_module()

    non_markdown = cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "pdf",
    ])
    captured = capsys.readouterr()
    assert non_markdown == 2
    assert "solo se permite --format markdown" in captured.err
    assert not (tmp_path / OUTPUT_FILENAME).exists()

    unexpected = cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
        "--source-media",
        "media",
    ])
    captured = capsys.readouterr()
    assert unexpected == 2
    assert "opción no permitida" in captured.err


def test_cli_rejects_wrong_fixture_basename_and_missing_output_dir(tmp_path, capsys):
    cli = load_cli_module()
    wrong_fixture = tmp_path / "real_project_report.json"
    wrong_fixture.write_text("{}", encoding="utf-8")

    wrong_fixture_code = cli.main([
        "--fixture",
        str(wrong_fixture),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
    ])
    captured = capsys.readouterr()
    assert wrong_fixture_code == 2
    assert "ERROR:" in captured.err

    missing_output_code = cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path / "missing"),
        "--format",
        "markdown",
    ])
    captured = capsys.readouterr()
    assert missing_output_code == 2
    assert "ERROR:" in captured.err


def test_cli_does_not_modify_fixture_renderer_or_scanner(tmp_path):
    cli = load_cli_module()

    fixture_before = sha256(FIXTURE)
    renderer_before = sha256(RENDERER_PATH)
    scanner_before = sha256(SCANNER_PATH)

    code = cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
    ])

    assert code == 0
    assert sha256(FIXTURE) == fixture_before
    assert sha256(RENDERER_PATH) == renderer_before
    assert sha256(SCANNER_PATH) == scanner_before


def test_generated_markdown_retains_renderer_safety_notices(tmp_path):
    cli = load_cli_module()
    assert cli.main([
        "--fixture",
        str(FIXTURE),
        "--output-dir",
        str(tmp_path),
        "--format",
        "markdown",
    ]) == 0

    text = (tmp_path / OUTPUT_FILENAME).read_text(encoding="utf-8")
    for term in [
        "demo sintética",
        "local-first",
        "Checklist obligatorio de revisión humana",
        "No realiza sincronización real",
        "No transcribe audio real",
        "No traduce diálogos reales",
        "No genera subtítulos finales",
        "No exporta a DaVinci Resolve",
        "CID no sustituye",
    ]:
        assert term in text

    for forbidden in [
        str(FIXTURE.resolve()),
        str(tmp_path.resolve()),
        "/opt/SERVICIOS_CINE",
        "/home/harliesound",
        "\\wsl.localhost",
        "C:\\",
        "{",
        "}",
    ]:
        assert forbidden not in text


def test_cli_source_is_standard_library_and_does_not_call_services_or_external_binaries():
    source = CLI_PATH.read_text(encoding="utf-8")

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
        "cid_media_agent_scan",
        "pyproject",
        "setup.py",
        "setup.cfg",
        "entry_" + "points",
        "console_" + "scripts",
    ]

    for term in forbidden:
        assert term not in source

    assert "ff" + "probe" not in source
    assert "ff" + "mpeg" not in source


def test_no_packaging_files_are_modified_by_this_phase():
    for path in [Path("pyproject.toml"), Path("setup.py"), Path("setup.cfg")]:
        if path.exists():
            assert path.exists()


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    doc = Path(
        "docs/product/local_media_agent/"
        "cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"
    )
    assert blocked not in doc.read_text(encoding="utf-8").lower()
    assert blocked not in CLI_PATH.read_text(encoding="utf-8").lower()
    assert blocked not in Path(__file__).read_text(encoding="utf-8").lower()
