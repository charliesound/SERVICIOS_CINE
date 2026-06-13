"""Gating audit tests for Script-to-Production Breakdown demo prototype.

Phase: AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.PROTOTYPE.GATING.AUDIT.PHASE3.1

Tests-only. No runtime modifications.
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ailink_tools.script_breakdown.demo_parser import (
    DEMO_MARKERS,
    parse_demo_script,
)
from ailink_tools.script_breakdown.exports import (
    export_json,
    export_markdown,
)
from ailink_tools.script_breakdown.schemas import BreakdownResult

from ailink_script_breakdown_demo import main as cli_main

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_DEMO_SCRIPT = """
ESCENA 1. INT. CASA DE ANA - NOCHE

ANA BRUMA (30 anos) esta sentada en la cocina.
LEO PRADO (25 anos) entra con prisa.

LEO: Han llamado del ayuntamiento.

ESCENA 2. EXT. CAMINO RURAL - AMANECER

Ana y Leo caminan por un camino de tierra.

ANA: El informe dice que necesitamos tres permisos.

ESCENA 3. EXT. PUEBLO DEMO BRUMA - DÍA

Ana entra en el BAR DEMO ESTACIÓN.

MARA: Ana, ya has hablado con el alcalde?

ESCENA 4. INT. BAR DEMO ESTACIÓN - NOCHE

Reunion de produccion.

BRUNO: El sonido va a ser complicado.

ESCENA 5. EXT. CAMPO DE LAVANDA - DÍA

Ana camina sola por un campo de lavanda.

ESCENA 6. EXT. CASA DE ANA - DÍA

Leo esta reparando una valla.

LEO: Y si el alcalde dice que no?

ESCENA 7. INT. CASA DE ANA - NOCHE

Ana esta sola en la cocina.

ANA: (al telefono) Necesito hablar sobre los permisos.

ESCENA 8. EXT. CAMINO RURAL - NOCHE

Ana y Leo caminan por el camino de noche.

ANA: Manana tenemos que decidir.
"""


@pytest.fixture
def valid_demo_file(tmp_path):
    """Create a valid demo script file."""
    demo_path = tmp_path / "demo_script.txt"
    demo_path.write_text(VALID_DEMO_SCRIPT, encoding="utf-8")
    return demo_path


@pytest.fixture
def breakdown_result():
    """Parse valid demo and return result."""
    return parse_demo_script(VALID_DEMO_SCRIPT)


# ===========================================================================
# CATEGORY A — Input demo strictness (5 tests)
# ===========================================================================


class TestInputDemoStrictness:
    """A1-A5: Verify parser rejects all non-controlled demo inputs."""

    def test_rejects_text_without_demo_markers(self):
        """A1: Text with no ESCENA markers must be rejected."""
        with pytest.raises(ValueError, match="no soportado"):
            parse_demo_script("Este es un guion cualquiera sin marcadores.")

    def test_rejects_generic_scene_text(self):
        """A2: Text with generic scenes not in DEMO_MARKERS must be rejected."""
        text = (
            "ESCENA 1. INT. OFICINA - DIA\n"
            "Un empleado trabaja en un escritorio.\n"
            "ESCENA 2. EXT. CALLE - NOCHE\n"
            "La calle esta vacia.\n"
            "ESCENA 3. INT. OFICINA - DIA\n"
            "El empleado habla por telefono.\n"
            "ESCENA 4. EXT. CALLE - AMANECER\n"
            "El empleado sale a caminar.\n"
            "ESCENA 5. INT. OFICINA - NOCHE\n"
            "El empleado duerme en el escritorio.\n"
            "ESCENA 6. EXT. CALLE - DIA\n"
            "La calle tiene gente.\n"
            "ESCENA 7. INT. OFICINA - AMANECER\n"
            "El empleado se despierta.\n"
            "ESCENA 8. EXT. CALLE - NOCHE\n"
            "La calle esta cerrada.\n"
        )
        with pytest.raises(ValueError, match="no soportado"):
            parse_demo_script(text)

    def test_rejects_real_script_without_markers(self):
        """A3: Real-script-like text without DEMO_MARKERS must be rejected."""
        text = (
            "FADE IN:\n"
            "INT. COFFEE SHOP - DAY\n"
            "A BARISTA wipes the counter. A CUSTOMER enters.\n\n"
            "BARISTA\n"
            "Good morning! The usual?\n\n"
            "CUSTOMER\n"
            "Please. Extra shot today.\n\n"
            "EXT. CITY STREET - NIGHT\n"
            "Rain falls on empty sidewalks.\n"
            "A CAR passes slowly.\n\n"
            "INT. APARTMENT - DAWN\n"
            "The CUSTOMER sits at a desk, tired.\n"
            "They open a LAPTOP.\n\n"
            "EXT. PARK - DAY\n"
            "Children play. The CUSTOMER watches.\n\n"
            "INT. OFFICE - NIGHT\n"
            "Fluorescent lights hum.\n"
            "The CUSTOMER types furiously.\n\n"
            "EXT. BRIDGE - DAWN\n"
            "Fog rolls in.\n"
            "The CUSTOMER stands alone.\n\n"
            "INT. BEDROOM - NIGHT\n"
            "The CUSTOMER sleeps.\n"
            "FADE OUT.\n"
        )
        with pytest.raises(ValueError, match="no soportado"):
            parse_demo_script(text)

    def test_rejects_single_scene_input(self):
        """A4: Input with only one valid marker must be rejected."""
        text = (
            "ESCENA 1. INT. CASA DE ANA - NOCHE\n"
            "Ana esta cocinando.\n"
            "Leo entra.\n"
        )
        with pytest.raises(ValueError, match="no soportado"):
            parse_demo_script(text)

    def test_all_eight_markers_required(self):
        """A5: Removing any single marker from valid input causes rejection."""
        for i in range(len(DEMO_MARKERS)):
            incomplete = VALID_DEMO_SCRIPT.replace(DEMO_MARKERS[i], "ESCENA X. INT. LUGAR - DIA")
            with pytest.raises(ValueError, match="no soportado"):
                parse_demo_script(incomplete)


# ===========================================================================
# CATEGORY B — Isolation productora/pelicula (4 tests)
# ===========================================================================


class TestIsolationIds:
    """B1-B4: Verify multi-client/multi-project isolation in all outputs."""

    def test_metadata_contains_all_four_ids(self, breakdown_result):
        """B1: metadata must have organization_id, tenant_id, project_id, film_id."""
        meta = breakdown_result.metadata
        assert "organization_id" in meta
        assert "tenant_id" in meta
        assert "project_id" in meta
        assert "film_id" in meta
        assert meta["organization_id"].startswith("ORG-DEMO-")
        assert meta["tenant_id"].startswith("TENANT-DEMO-")
        assert meta["project_id"].startswith("PROJECT-DEMO-")
        assert meta["film_id"].startswith("FILM-DEMO-")

    def test_json_preserves_isolation_ids(self, breakdown_result):
        """B2: JSON round-trip preserves all 4 isolation IDs."""
        json_str = breakdown_result.to_json()
        parsed = json.loads(json_str)
        meta = parsed["metadata"]
        assert meta["organization_id"] == "ORG-DEMO-001"
        assert meta["tenant_id"] == "TENANT-DEMO-001"
        assert meta["project_id"] == "PROJECT-DEMO-001"
        assert meta["film_id"] == "FILM-DEMO-001"

    def test_markdown_contains_isolation_section(self, breakdown_result, tmp_path):
        """B3: Markdown must have 'Metadata de Aislamiento' with all 4 IDs."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8")
        assert "Metadata de Aislamiento" in content
        assert "organization_id" in content
        assert "tenant_id" in content
        assert "project_id" in content
        assert "film_id" in content

    def test_no_output_without_project_scope(self):
        """B4: BreakdownResult without IDs in metadata violates contract."""
        result = parse_demo_script(VALID_DEMO_SCRIPT)
        meta = result.metadata
        required = ["organization_id", "tenant_id", "project_id", "film_id"]
        for field in required:
            assert field in meta, f"Missing {field} in metadata"
            assert len(meta[field]) > 0, f"Empty {field} in metadata"


# ===========================================================================
# CATEGORY C — Dangerous paths (5 tests)
# ===========================================================================


class TestDangerousPaths:
    """C1-C5: Verify CLI and exports reject dangerous output paths."""

    def test_cli_rejects_root_slash(self, valid_demo_file):
        """C1: CLI must reject --output-dir /."""
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", "/",
        ])
        assert exit_code == 2

    def test_cli_rejects_windows_c_drive(self, valid_demo_file):
        """C2: CLI must reject all Windows-like paths with drive letter."""
        dangerous_paths = [
            "C:\\",
            "C:\\Users\\test",
            "D:\\demo\\salida",
            "C:/Users/test",
            "D:/demo/salida",
        ]
        for bad_path in dangerous_paths:
            exit_code = cli_main([
                "--input-demo", str(valid_demo_file),
                "--output-dir", bad_path,
            ])
            assert exit_code == 2, f"Expected exit 2 for path: {bad_path}"

    def test_cli_rejects_mnt_path(self, valid_demo_file):
        """C3: CLI must reject /mnt/... paths."""
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", "/mnt/something",
        ])
        assert exit_code == 2

    def test_cli_rejects_empty_output_dir(self, valid_demo_file):
        """C4: CLI must reject empty --output-dir."""
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", "",
        ])
        assert exit_code == 2

    def test_exports_do_not_write_outside_dir(self, breakdown_result, tmp_path):
        """C5: Exports must not create files outside the target directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        json_path = output_dir / "breakdown.json"
        md_path = output_dir / "breakdown.md"
        export_json(breakdown_result, json_path)
        export_markdown(breakdown_result, md_path)

        all_files = list(tmp_path.rglob("*"))
        output_files = list(output_dir.rglob("*"))
        outside = [f for f in all_files if f not in output_files and f.is_file()]
        # Filter out tmp_path itself
        outside = [f for f in outside if f.parent != tmp_path]
        assert outside == [], f"Files found outside output dir: {outside}"


# ===========================================================================
# CATEGORY D — Forbidden formats (5 tests)
# ===========================================================================


class TestForbiddenFormats:
    """D1-D5: Verify no forbidden file formats are generated."""

    def test_no_xlsx_generated(self, valid_demo_file, tmp_path, monkeypatch):
        """D1: CLI must not generate .xlsx files."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert list(output_dir.rglob("*.xlsx")) == []

    def test_no_pdf_generated(self, valid_demo_file, tmp_path, monkeypatch):
        """D2: CLI must not generate .pdf files."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert list(output_dir.rglob("*.pdf")) == []

    def test_no_html_generated(self, valid_demo_file, tmp_path, monkeypatch):
        """D3: CLI must not generate .html files."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert list(output_dir.rglob("*.html")) == []

    def test_no_csv_generated(self, valid_demo_file, tmp_path, monkeypatch):
        """D4: CLI must not generate .csv files."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert list(output_dir.rglob("*.csv")) == []

    def test_no_public_export_functions_for_xlsx_pdf_html_csv(self):
        """D5: exports module must not expose functions for xlsx/pdf/html/csv."""
        public = [name for name, _ in inspect.getmembers(
            __import__("ailink_tools.script_breakdown.exports", fromlist=["exports"]),
            inspect.isfunction,
        )]
        forbidden_patterns = ["xlsx", "pdf", "html", "csv"]
        for func_name in public:
            lower = func_name.lower()
            for pattern in forbidden_patterns:
                assert pattern not in lower, (
                    f"Public function '{func_name}' contains forbidden pattern '{pattern}'"
                )


# ===========================================================================
# CATEGORY E — Forbidden imports (4 tests)
# ===========================================================================


class TestForbiddenImports:
    """E1-E4: Verify no forbidden imports exist in runtime modules."""

    def _get_all_source(self) -> str:
        """Concatenate source of all runtime modules."""
        files = [
            SRC_DIR / "ailink_tools" / "script_breakdown" / "demo_parser.py",
            SRC_DIR / "ailink_tools" / "script_breakdown" / "exports.py",
            SRC_DIR / "ailink_tools" / "script_breakdown" / "schemas.py",
            SCRIPTS_DIR / "ailink_script_breakdown_demo.py",
        ]
        parts = []
        for f in files:
            if f.exists():
                parts.append(f.read_text(encoding="utf-8"))
        return "\n".join(parts)

    def test_no_backend_saas_imports(self):
        """E1: No from app/routes/services imports in runtime modules."""
        source = self._get_all_source()
        forbidden = ["from app ", "from routes", "from services"]
        for term in forbidden:
            assert term not in source, f"Forbidden import found: {term}"

    def test_no_sqlalchemy_alembic_imports(self):
        """E2: No sqlalchemy or alembic imports."""
        source = self._get_all_source()
        forbidden = [
            "import sqlalchemy", "from sqlalchemy",
            "import alembic", "from alembic",
        ]
        for term in forbidden:
            assert term not in source, f"Forbidden import found: {term}"

    def test_no_docker_config_imports(self):
        """E3: No docker or compose imports."""
        source = self._get_all_source()
        forbidden = ["import docker", "from docker", "import compose"]
        for term in forbidden:
            assert term not in source, f"Forbidden import found: {term}"

    def test_no_ocr_pdf_finaldraft_fountain_ai_imports(self):
        """E4: No OCR/PDF/FinalDraft/Fountain/AI imports."""
        source = self._get_all_source()
        forbidden = [
            "import pytesseract", "import fitz",
            "import fountain", "import final_draft",
            "import openai", "import anthropic",
        ]
        for term in forbidden:
            assert term not in source, f"Forbidden import found: {term}"


# ===========================================================================
# CATEGORY F — CLI behavior (5 tests)
# ===========================================================================


class TestCLIBehavior:
    """F1-F5: Verify CLI exit codes and overwrite semantics."""

    def test_cli_without_force_does_not_overwrite(self, valid_demo_file, tmp_path, monkeypatch):
        """F1: Without --force, second run must fail (exit 2)."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        # First run
        exit1 = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert exit1 == 0
        # Second run without --force
        exit2 = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert exit2 == 2

    def test_cli_with_force_overwrites_only_expected(self, valid_demo_file, tmp_path, monkeypatch):
        """F2: With --force, only .json and .md exist."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        # First run
        cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        # Second run with --force
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
            "--force",
        ])
        assert exit_code == 0
        # Only .json and .md should exist
        all_files = list(output_dir.iterdir())
        for f in all_files:
            assert f.suffix in (".json", ".md"), f"Unexpected file: {f}"

    def test_cli_exit_code_zero_on_success(self, valid_demo_file, tmp_path, monkeypatch):
        """F3: Valid run returns exit 0."""
        monkeypatch.chdir(tmp_path)
        output_dir = Path("output")
        output_dir.mkdir()
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert exit_code == 0

    def test_cli_exit_code_two_on_dangerous_args(self, valid_demo_file, tmp_path):
        """F4: Invalid input and dangerous paths return exit 2."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        # Missing input
        exit1 = cli_main([
            "--input-demo", str(tmp_path / "nonexistent.txt"),
            "--output-dir", str(output_dir),
        ])
        assert exit1 == 2
        # Dangerous path
        exit2 = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", "/",
        ])
        assert exit2 == 2

    def test_cli_exit_code_three_on_unexpected_error(self, valid_demo_file, tmp_path, monkeypatch):
        """F5: Unexpected RuntimeError triggers exit 3."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        def bad_parse(text):
            raise RuntimeError("simulated failure")

        monkeypatch.setattr(
            "ailink_script_breakdown_demo.parse_demo_script",
            bad_parse,
        )
        exit_code = cli_main([
            "--input-demo", str(valid_demo_file),
            "--output-dir", str(output_dir),
        ])
        assert exit_code == 3


# ===========================================================================
# CATEGORY G — Markdown readability (6 tests)
# ===========================================================================


class TestMarkdownReadability:
    """G1-G6: Verify Markdown output is human-readable with required sections."""

    def test_markdown_contains_project_title(self, breakdown_result, tmp_path):
        """G1: Markdown must contain 'Proyecto Demo Bruma'."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8")
        assert "Proyecto Demo Bruma" in content

    def test_markdown_contains_human_review(self, breakdown_result, tmp_path):
        """G2: Markdown must contain 'revisión humana'."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8").lower()
        assert "revisión humana" in content

    def test_markdown_contains_preliminary_budget(self, breakdown_result, tmp_path):
        """G3: Markdown must contain 'presupuesto preliminar'."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8").lower()
        assert "presupuesto preliminar" in content

    def test_markdown_contains_viability(self, breakdown_result, tmp_path):
        """G4: Markdown must contain 'viabilidad'."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8").lower()
        assert "viabilidad" in content

    def test_markdown_contains_disclaimer(self, breakdown_result, tmp_path):
        """G5: Markdown must contain a disclaimer about human review."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8").lower()
        has_disclaimer = (
            "requiere revisión humana" in content
            or "no presupuesto definitivo" in content
            or "desglose orientativo" in content
        )
        assert has_disclaimer, "Missing disclaimer about human review or provisional nature"

    def test_markdown_has_all_sections(self, breakdown_result, tmp_path):
        """G6: Markdown must have all required sections."""
        md_path = tmp_path / "breakdown.md"
        export_markdown(breakdown_result, md_path)
        content = md_path.read_text(encoding="utf-8")
        required_sections = [
            "Escenas",
            "Personajes",
            "Localizaciones",
            "Riesgos",
            "Viabilidad",
            "Presupuesto",
            "Recomendaciones",
        ]
        for section in required_sections:
            assert section in content, f"Missing section: {section}"


# ===========================================================================
# CATEGORY H — No unsafe claims (2 tests)
# ===========================================================================


class TestNoUnsafeClaims:
    """H1-H2: Verify no unsafe marketing claims in runtime source."""

    def test_no_unsafe_claims_in_parser_source(self):
        """H1: demo_parser.py must not contain unsafe claims."""
        source_file = SRC_DIR / "ailink_tools" / "script_breakdown" / "demo_parser.py"
        source = source_file.read_text(encoding="utf-8").lower()
        forbidden = [
            "presupuesto exacto",
            "sustituye al productor",
            "sustituye al director",
            "garantiza viabilidad",
        ]
        for claim in forbidden:
            assert claim not in source, f"Unsafe claim found in demo_parser.py: '{claim}'"

    def test_no_unsafe_claims_in_exports_source(self):
        """H2: exports.py must not contain unsafe claims."""
        source_file = SRC_DIR / "ailink_tools" / "script_breakdown" / "exports.py"
        source = source_file.read_text(encoding="utf-8").lower()
        forbidden = [
            "producto disponible",
            "funcionalidad final",
        ]
        for claim in forbidden:
            assert claim not in source, f"Unsafe claim found in exports.py: '{claim}'"
