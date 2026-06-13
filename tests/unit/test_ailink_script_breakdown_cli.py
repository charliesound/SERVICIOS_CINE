"""Tests for Script-to-Production Breakdown demo CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure src is in path
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import the CLI main function
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ailink_script_breakdown_demo import main as cli_main

# ---------------------------------------------------------------------------
# Demo script fixture
# ---------------------------------------------------------------------------

DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE

ANA BRUMA (30 años) está sentada en la cocina.
LEO PRADO (25 años) entra con prisa.

LEO: Han llamado del ayuntamiento.

ESCENA 2. EXT. CAMINO RURAL - AMANECER

Ana y Leo caminan por un camino de tierra.

ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA

Ana entra en el BAR DEMO ESTACIÓN.

ESCENA 4. INT. BAR DEMO ESTACIÓN - NOCHE

Reunión de producción.

ESCENA 5. EXT. CAMPO DE LAVANDA - DÍA

Ana camina sola por un campo de lavanda.

ESCENA 6. EXT. CASA DE ANA - DÍA

Leo está reparando una valla.

ESCENA 7. INT. CASA DE ANA - NOCHE

Ana está sola en la cocina.

ESCENA 8. EXT. CAMINO RURAL - NOCHE

Ana y Leo caminan por el camino de noche.
"""


@pytest.fixture
def demo_file(tmp_path):
    """Create a demo script file in tmp_path."""
    demo_path = tmp_path / "demo_script.txt"
    demo_path.write_text(DEMO_SCRIPT, encoding="utf-8")
    return demo_path


def test_cli_generates_both_files(tmp_path, demo_file, monkeypatch):
    """CLI must generate both JSON and Markdown files."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])

    assert exit_code == 0
    assert (output_dir / "breakdown.json").exists()
    assert (output_dir / "breakdown.md").exists()


def test_cli_rejects_missing_input(tmp_path):
    """CLI must reject missing input file."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    exit_code = cli_main([
        "--input-demo", str(tmp_path / "nonexistent.txt"),
        "--output-dir", str(output_dir),
    ])

    assert exit_code == 2


def test_cli_rejects_invalid_input(tmp_path):
    """CLI must reject input that is not the demo script."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("This is not a demo script", encoding="utf-8")

    exit_code = cli_main([
        "--input-demo", str(invalid_file),
        "--output-dir", str(output_dir),
    ])

    assert exit_code == 2


def test_cli_rejects_dangerous_output_dir(tmp_path, demo_file):
    """CLI must reject dangerous output directories."""
    # Test empty-ish path
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", "/",
    ])
    assert exit_code == 2


def test_cli_rejects_mnt_path(tmp_path, demo_file):
    """CLI must reject /mnt/ paths."""
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", "/mnt/something",
    ])
    assert exit_code == 2


def test_cli_respects_force(tmp_path, demo_file, monkeypatch):
    """CLI must respect --force flag."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    # First run
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])
    assert exit_code == 0

    # Second run without --force should fail
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])
    assert exit_code == 2

    # Third run with --force should succeed
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--force",
    ])
    assert exit_code == 0


def test_cli_custom_names(tmp_path, demo_file, monkeypatch):
    """CLI must respect custom file names."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--json-name", "custom.json",
        "--markdown-name", "custom.md",
    ])

    assert exit_code == 0
    assert (output_dir / "custom.json").exists()
    assert (output_dir / "custom.md").exists()


def test_cli_no_xlsx(tmp_path, demo_file):
    """CLI must not generate .xlsx files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])

    xlsx_files = list(output_dir.rglob("*.xlsx"))
    assert xlsx_files == []


def test_cli_no_pdf(tmp_path, demo_file):
    """CLI must not generate .pdf files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])

    pdf_files = list(output_dir.rglob("*.pdf"))
    assert pdf_files == []


def test_cli_no_html(tmp_path, demo_file):
    """CLI must not generate .html files."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])

    html_files = list(output_dir.rglob("*.html"))
    assert html_files == []


def test_cli_with_excel_flag(tmp_path, demo_file, monkeypatch):
    """CLI must generate Excel when --excel-name is provided."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--excel-name", "breakdown.xlsx",
    ])

    assert exit_code == 0
    assert (output_dir / "breakdown.xlsx").exists()


def test_cli_without_excel_flag_no_xlsx(tmp_path, demo_file, monkeypatch):
    """CLI must not generate Excel without --excel-name flag."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
    ])

    assert exit_code == 0
    xlsx_files = list(output_dir.rglob("*.xlsx"))
    assert xlsx_files == []


def test_cli_excel_respects_force(tmp_path, demo_file, monkeypatch):
    """CLI must respect --force for Excel overwrite."""
    monkeypatch.chdir(tmp_path)
    output_dir = Path("output")
    output_dir.mkdir()

    # First run
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--excel-name", "breakdown.xlsx",
    ])
    assert exit_code == 0

    # Second run without --force should fail
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--excel-name", "breakdown.xlsx",
    ])
    assert exit_code == 2

    # Third run with --force should succeed
    exit_code = cli_main([
        "--input-demo", str(demo_file),
        "--output-dir", str(output_dir),
        "--excel-name", "breakdown.xlsx",
        "--force",
    ])
    assert exit_code == 0
