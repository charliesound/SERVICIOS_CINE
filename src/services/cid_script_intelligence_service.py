from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.production import ProductionBreakdown
from services.cid_screenwriting_theory_service import cid_screenwriting_theory_service


class CIDScriptIntelligenceService:
    def _clamp_score(self, value: int) -> int:
        return max(0, min(100, int(value)))

    def _build_heuristic_scores(self, script_text: str, scenes_count: int, sequence_count: int) -> dict[str, int]:
        length_factor = min(100, max(10, len(script_text) // 60))
        structure = self._clamp_score(40 + (sequence_count * 8))
        conflict = self._clamp_score(30 + (scenes_count * 6))
        pacing = self._clamp_score(35 + (scenes_count * 5))
        return {
            "dramatic_clarity": self._clamp_score((length_factor + structure) // 2),
            "conflict_strength": conflict,
            "character_drive": self._clamp_score(45 + min(25, scenes_count * 3)),
            "structure_strength": structure,
            "pacing": pacing,
            "cinematic_potential": self._clamp_score((structure + conflict + pacing) // 3),
        }

    def _extract_breakdown_data(self, breakdown: ProductionBreakdown | None) -> dict[str, Any]:
        if not breakdown or not breakdown.breakdown_json:
            return {}
        try:
            payload = json.loads(breakdown.breakdown_json)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    async def analyze_project(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        sequence_ids: list[str] | None = None,
        theory_focus: list[str] | None = None,
        include_storyboard_actionables: bool = True,
    ) -> dict[str, Any]:
        project_result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.organization_id == organization_id,
            )
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError("project_not_found")

        script_text = str(project.script_text or "")
        if not script_text.strip():
            raise ValueError("project_script_missing")

        breakdown_result = await db.execute(
            select(ProductionBreakdown).where(ProductionBreakdown.project_id == project_id)
        )
        breakdown = breakdown_result.scalar_one_or_none()
        breakdown_data = self._extract_breakdown_data(breakdown)
        scenes = breakdown_data.get("scenes") or []
        sequences = breakdown_data.get("sequences") or []

        if sequence_ids:
            selected = set(str(item) for item in sequence_ids)
            sequences = [seq for seq in sequences if str(seq.get("sequence_id")) in selected]

        theory_context = await cid_screenwriting_theory_service.fetch_theory_context(topics=theory_focus)
        fallback_used = bool(theory_context.get("fallback_used"))
        scores = self._build_heuristic_scores(script_text, len(scenes), len(sequences))

        seq_hint = ", ".join(str(seq.get("sequence_id")) for seq in sequences[:4]) if sequences else "n/a"
        overview = (
            f"Diagnóstico estructural basado en guion y teoría contextual. "
            f"Escenas detectadas: {len(scenes)}. Secuencias consideradas: {len(sequences)} ({seq_hint})."
        )

        storyboard_actionables: list[str] = []
        if include_storyboard_actionables:
            storyboard_actionables = [
                "Asegurar que cada secuencia tenga objetivo dramático explícito en los primeros planos.",
                "Refinar transiciones de plot points con planos de reacción y contraste de valor.",
                "Agregar beats visuales de conflicto progresivo antes de midpoint y clímax.",
            ]

        theory_snippet = str(theory_context.get("summary") or "")[:320]
        return {
            "project_id": project_id,
            "overall_diagnosis": overview,
            "syd_field": {
                "act_structure": f"Estructura en tres actos inferida con {len(sequences)} secuencias relevantes.",
                "plot_point_1": "Revisar disparador del Acto I al II y su impacto causal.",
                "midpoint": "Verificar punto medio con giro claro de estrategia dramática.",
                "plot_point_2": "Comprobar escalada previa al clímax con consecuencia irreversible.",
                "resolution": "Ajustar resolución para cerrar premisa y arco principal.",
                "issues": [] if len(sequences) >= 2 else ["Posible baja segmentación estructural por secuencias."],
                "recommendations": ["Reforzar hitos de estructura clásica por bloque secuencial."],
            },
            "comparato": {
                "idea": "Validar claridad de idea matriz y su ejecución progresiva.",
                "conflict_matrix": "Mapear conflicto central en niveles interpersonal, interno y contextual.",
                "dramatic_action": "Alinear acciones visibles con el objetivo dramático de cada secuencia.",
                "character_function": "Comprobar función dramática diferenciada por personaje clave.",
                "issues": [] if scores["conflict_strength"] >= 45 else ["Conflicto podría ser insuficiente en desarrollo actual."],
                "recommendations": ["Incrementar oposición activa en secuencias intermedias."],
            },
            "mckee": {
                "scene_value_shifts": ["Evaluar cambios de valor neto al final de cada escena."],
                "conflict_levels": ["interno", "interpersonal", "social"],
                "crisis_climax_resolution": "Revisar progresión crisis->clímax->resolución sin atajos expositivos.",
                "subtext_notes": ["Potenciar subtexto en confrontaciones clave.", theory_snippet] if theory_snippet else ["Potenciar subtexto en confrontaciones clave."],
                "issues": [] if scores["dramatic_clarity"] >= 50 else ["Clarity dramática mejorable en la articulación de beats."],
                "recommendations": ["Ajustar ritmo entre revelaciones y decisiones de alto costo."],
            },
            "scores": scores,
            "storyboard_actionables": storyboard_actionables,
            "theory_sources_used": theory_context.get("sources") or [],
            "fallback_used": fallback_used,
        }


cid_script_intelligence_service = CIDScriptIntelligenceService()
