from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


REFERENCE_FILENAME = "asesor_produccion_cinematografico.md"


class ProductionAdvisorReferenceService:
    def __init__(self, reference_dir: Optional[Path] = None) -> None:
        self.reference_dir = reference_dir or Path(__file__).resolve().parents[2] / "directivas" / "production_references"

    def load_production_advisor_reference(self) -> dict[str, Any]:
        file_path = self.reference_dir / REFERENCE_FILENAME
        if not file_path.is_file():
            return {
                "available": False,
                "path": str(file_path),
                "content": "",
                "missing_files": [REFERENCE_FILENAME],
            }
        return {
            "available": True,
            "path": str(file_path),
            "content": file_path.read_text(encoding="utf-8"),
            "missing_files": [],
        }

    def build_script_production_analysis_prompt(
        self,
        *,
        project_name: str,
        script_excerpt: str,
        production_scope: str = "feature film development",
    ) -> str:
        return self._compose_prompt(
            title="Analisis de guion para produccion cinematografica",
            body=[
                f"Proyecto: {project_name}",
                f"Scope: {production_scope}",
                f"Script excerpt: {script_excerpt}",
                "Entrega un analisis profesional con riesgos de produccion, necesidades clave, optimizacion narrativa y visual, checklist operativo y recomendaciones imprimibles/editables.",
            ],
        )

    def build_budget_prompt(
        self,
        *,
        project_name: str,
        script_excerpt: str,
        budget_level: str = "medium",
        currency: str = "EUR",
    ) -> str:
        return self._compose_prompt(
            title="Presupuesto cinematografico por partidas",
            body=[
                f"Proyecto: {project_name}",
                f"Budget level: {budget_level}",
                f"Currency: {currency}",
                f"Script excerpt: {script_excerpt}",
                "Genera presupuesto por partidas, tabla de costes, supuestos, cronograma financiero y version imprimible/editable.",
            ],
        )

    def build_paperwork_prompt(
        self,
        *,
        project_name: str,
        script_excerpt: str,
        paperwork_scope: str = "documentacion de rodaje",
    ) -> str:
        return self._compose_prompt(
            title="Documentacion y papeleo de produccion",
            body=[
                f"Proyecto: {project_name}",
                f"Paperwork scope: {paperwork_scope}",
                f"Script excerpt: {script_excerpt}",
                "Genera checklist, formularios, documentos editables, contratos base y avisos legales/practicos listos para impresion o edicion.",
            ],
        )

    def build_location_permit_prompt(
        self,
        *,
        project_name: str,
        location_name: str,
        script_excerpt: str,
    ) -> str:
        return self._compose_prompt(
            title="Permisos de rodaje y localizaciones",
            body=[
                f"Proyecto: {project_name}",
                f"Location: {location_name}",
                f"Script excerpt: {script_excerpt}",
                "Prepara requisitos de permiso, checklist documental, riesgos practicos, necesidades municipales y formularios imprimibles/editables.",
            ],
        )

    def build_subsidy_search_prompt(
        self,
        *,
        project_name: str,
        project_type: str,
        territory: str,
    ) -> str:
        return self._compose_prompt(
            title="Busqueda de subvenciones cinematograficas",
            body=[
                f"Proyecto: {project_name}",
                f"Project type: {project_type}",
                f"Territory: {territory}",
                "Genera tabla de subvenciones potenciales, criterios de elegibilidad, documentos requeridos, cronograma y respuesta imprimible/editable.",
            ],
        )

    def _compose_prompt(self, *, title: str, body: list[str]) -> str:
        reference = self.load_production_advisor_reference()
        reference_block = reference["content"][:2000] if reference["content"] else "Asesor de Produccion Cinematografico reference unavailable. Keep output professional and editable."
        parts = [
            title,
            reference_block,
            *body,
            "Formato de salida: respuestas profesionales, tablas, checklist, documentos editables, presupuestos por partidas, cronogramas, formularios y avisos legales/practicos.",
        ]
        return "\n\n".join(part for part in parts if part)


production_advisor_reference_service = ProductionAdvisorReferenceService()


def load_production_advisor_reference() -> dict[str, Any]:
    return production_advisor_reference_service.load_production_advisor_reference()


def build_script_production_analysis_prompt(**kwargs: Any) -> str:
    return production_advisor_reference_service.build_script_production_analysis_prompt(**kwargs)


def build_budget_prompt(**kwargs: Any) -> str:
    return production_advisor_reference_service.build_budget_prompt(**kwargs)


def build_paperwork_prompt(**kwargs: Any) -> str:
    return production_advisor_reference_service.build_paperwork_prompt(**kwargs)


def build_location_permit_prompt(**kwargs: Any) -> str:
    return production_advisor_reference_service.build_location_permit_prompt(**kwargs)


def build_subsidy_search_prompt(**kwargs: Any) -> str:
    return production_advisor_reference_service.build_subsidy_search_prompt(**kwargs)
