from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.production_advisor_reference_service import ProductionAdvisorReferenceService  # noqa: E402


def test_load_reference_if_exists() -> None:
    service = ProductionAdvisorReferenceService()
    loaded = service.load_production_advisor_reference()

    assert loaded["available"] is True
    assert loaded["content"]
    assert loaded["missing_files"] == []


def test_load_reference_missing_file_does_not_fail(tmp_path: Path) -> None:
    service = ProductionAdvisorReferenceService(reference_dir=tmp_path)
    loaded = service.load_production_advisor_reference()

    assert loaded["available"] is False
    assert loaded["missing_files"] == ["asesor_produccion_cinematografico.md"]


def test_build_script_production_analysis_prompt() -> None:
    service = ProductionAdvisorReferenceService()
    prompt = service.build_script_production_analysis_prompt(
        project_name="Proyecto Demo",
        script_excerpt="INT. CASA - NOCHE. Marta revisa documentos de rodaje.",
    )

    lowered = prompt.lower()
    assert "analisis de guion" in lowered
    assert "marta revisa documentos" in lowered
    assert "imprimibles/editables" in lowered


def test_build_budget_prompt() -> None:
    service = ProductionAdvisorReferenceService()
    prompt = service.build_budget_prompt(
        project_name="Proyecto Demo",
        script_excerpt="EXT. CALLE - DIA. Rodaje con extras y vehiculos.",
        budget_level="high",
    )

    lowered = prompt.lower()
    assert "presupuesto" in lowered
    assert "por partidas" in lowered
    assert "imprimible/editable" in lowered or "imprimibles/editables" in lowered


def test_build_paperwork_and_permits_prompt() -> None:
    service = ProductionAdvisorReferenceService()
    paperwork = service.build_paperwork_prompt(
        project_name="Proyecto Demo",
        script_excerpt="INT. TEATRO - NOCHE. Ensayo general.",
    )
    permit = service.build_location_permit_prompt(
        project_name="Proyecto Demo",
        location_name="Teatro Principal",
        script_excerpt="EXT. PLAZA - NOCHE. Multitud reunida.",
    )

    paperwork_lower = paperwork.lower()
    permit_lower = permit.lower()
    assert "documentacion" in paperwork_lower
    assert "contratos" in paperwork_lower
    assert "editables" in paperwork_lower
    assert "permisos" in permit_lower
    assert "teatro principal" in permit_lower


def test_build_subsidy_search_prompt() -> None:
    service = ProductionAdvisorReferenceService()
    prompt = service.build_subsidy_search_prompt(
        project_name="Proyecto Demo",
        project_type="feature film",
        territory="España",
    )

    lowered = prompt.lower()
    assert "subvenciones" in lowered
    assert "tabla" in lowered
    assert "cronograma" in lowered
