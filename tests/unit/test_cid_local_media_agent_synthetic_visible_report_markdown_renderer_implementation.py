from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path("scripts/cid_local_media_agent_synthetic_visible_report_renderer.py")
FIXTURE = Path("tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json")
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def load_module():
    spec = importlib.util.spec_from_file_location("cid_synthetic_visible_report_renderer", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_module_and_fixture_exist():
    assert MODULE_PATH.exists()
    assert FIXTURE.exists()


def test_renderer_creates_deterministic_markdown_under_tmp_path(tmp_path):
    module = load_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)

    assert output == tmp_path / OUTPUT_FILENAME
    assert output.exists()
    assert output.read_text(encoding="utf-8") == module.build_synthetic_visible_report_markdown(
        module._load_fixture(FIXTURE)
    )


def test_renderer_refuses_overwrite_by_default(tmp_path):
    module = load_module()
    module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)

    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)


def test_renderer_allows_explicit_overwrite_with_same_deterministic_content(tmp_path):
    module = load_module()
    first = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    first_text = first.read_text(encoding="utf-8")

    second = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path, allow_overwrite=True)
    assert second == first
    assert second.read_text(encoding="utf-8") == first_text


def test_renderer_refuses_non_controlled_fixture_name(tmp_path):
    module = load_module()
    bad_fixture = tmp_path / "real_client_media_report.json"
    bad_fixture.write_text("{}", encoding="utf-8")

    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(bad_fixture, tmp_path)


def test_renderer_refuses_repository_output_directory():
    module = load_module()

    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(FIXTURE, Path.cwd())


def test_renderer_refuses_missing_output_directory(tmp_path):
    module = load_module()

    with pytest.raises(module.SyntheticVisibleReportRendererError):
        module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path / "missing")


def test_fixture_is_not_modified(tmp_path):
    module = load_module()
    before = file_sha256(FIXTURE)
    module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    after = file_sha256(FIXTURE)
    assert before == after


def test_rendered_markdown_contains_required_visible_safety_notices(tmp_path):
    module = load_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    text = output.read_text(encoding="utf-8")

    for term in [
        "demo sintética",
        "No procede de material real de cliente",
        "local-first",
        "no salen del disco por defecto",
        "No realiza sincronización real",
        "No ejecuta ffprobe",
        "No ejecuta ffmpeg",
        "No transcribe audio real",
        "No traduce diálogos reales",
        "No genera subtítulos finales",
        "No exporta a DaVinci Resolve",
        "No valida delivery final",
        "Checklist obligatorio de revisión humana",
        "CID no sustituye",
        "Informe Markdown sintético generado de forma determinista",
    ]:
        assert term in text


def test_rendered_markdown_does_not_include_absolute_paths_or_raw_json(tmp_path):
    module = load_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    text = output.read_text(encoding="utf-8")

    assert str(FIXTURE.resolve()) not in text
    assert str(tmp_path.resolve()) not in text
    assert "/opt/SERVICIOS_CINE" not in text
    assert "/home/harliesound" not in text
    assert "\\wsl.localhost" not in text
    assert "C:\\" not in text
    assert "{" not in text
    assert "}" not in text


def test_rendered_markdown_does_not_make_false_real_capability_claims(tmp_path):
    module = load_module()
    output = module.render_synthetic_visible_report_markdown(FIXTURE, tmp_path)
    text = output.read_text(encoding="utf-8").lower()

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
        assert claim not in text


def test_implementation_uses_standard_library_and_no_external_execution_or_network():
    source = MODULE_PATH.read_text(encoding="utf-8")

    forbidden_imports_or_calls = [
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "os.system",
        "Popen(",
        "run(",
        "check_output(",
        "check_call(",
    ]

    for forbidden in forbidden_imports_or_calls:
        assert forbidden not in source


def test_implementation_does_not_modify_scanner_or_define_cli_entry_point():
    source = MODULE_PATH.read_text(encoding="utf-8")
    scanner = Path("scripts/cid_media_agent_scan.py")

    assert scanner.exists()
    assert "argparse" not in source
    assert "click" not in source
    assert "typer" not in source
    assert "if __name__" not in source


def test_no_blocked_database_engine_label_in_new_files():
    blocked = "sqli" + "te"
    assert blocked not in Path("docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_markdown_renderer_implementation_v1.md").read_text(encoding="utf-8").lower()
    assert blocked not in MODULE_PATH.read_text(encoding="utf-8").lower()
    assert blocked not in Path(__file__).read_text(encoding="utf-8").lower()
