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

    def _sanitize_text(self, value: Any, *, max_len: int = 180) -> str:
        text = " ".join(str(value or "").split())
        if len(text) > max_len:
            return text[: max_len - 3].rstrip() + "..."
        return text

    def _collect_scene_signals(self, scenes: list[dict[str, Any]]) -> dict[str, Any]:
        conflict_terms = ("conflicto", "pelea", "discute", "amenaza", "crisis", "riesgo", "tension", "tensión")
        action_terms = ("corre", "entra", "sale", "dispara", "persigue", "golpea", "escapa", "confronta")
        conflict_hits = 0
        action_hits = 0
        character_names: set[str] = set()
        for scene in scenes:
            text = " ".join(str(item) for item in (scene.get("action_blocks") or []))
            lower = text.lower()
            if any(term in lower for term in conflict_terms):
                conflict_hits += 1
            if any(term in lower for term in action_terms):
                action_hits += 1
            for name in scene.get("characters_detected") or []:
                value = self._sanitize_text(name, max_len=40)
                if value:
                    character_names.add(value)
        return {
            "conflict_hits": conflict_hits,
            "action_hits": action_hits,
            "characters": sorted(character_names),
        }

    def _infer_act_stage(self, sequence_count: int, scenes_count: int) -> str:
        if sequence_count <= 1 or scenes_count <= 3:
            return "planteamiento"
        if sequence_count <= 3 or scenes_count <= 10:
            return "confrontación"
        return "resolución"

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
        signals = self._collect_scene_signals(scenes)
        act_stage = self._infer_act_stage(len(sequences), len(scenes))

        seq_hint = ", ".join(str(seq.get("sequence_id")) for seq in sequences[:4]) if sequences else "n/a"
        sequence_scope = f"secuencias solicitadas {', '.join(sequence_ids)}" if sequence_ids else "todo el proyecto"
        overview = (
            f"Diagnóstico estructural basado en guion y teoría contextual. "
            f"Ámbito: {sequence_scope}. Escenas detectadas: {len(scenes)}. "
            f"Secuencias consideradas: {len(sequences)} ({seq_hint})."
        )

        storyboard_actionables: list[str] = []
        if include_storyboard_actionables:
            storyboard_actionables = [
                f"Priorizar objetivo dramático explícito en aperturas de secuencia ({len(sequences)} secuencias).",
                f"Diseñar escalada visual de conflicto en al menos {max(1, signals['conflict_hits'])} escenas clave.",
                f"Ajustar ritmo con beats de acción visibles ({signals['action_hits']} escenas con acción detectada).",
            ]

        key_characters = ", ".join(signals["characters"][:4]) if signals["characters"] else "sin personajes destacados"
        conflict_matrix = (
            f"Conflicto matriz estimado: {max(1, signals['conflict_hits'])} escenas con fricción dramática, "
            f"{signals['action_hits']} con acción visible; personajes foco: {key_characters}."
        )
        return {
            "project_id": project_id,
            "overall_diagnosis": overview,
            "syd_field": {
                "act_structure": f"Con {len(scenes)} escenas y {len(sequences)} secuencias, el tramo actual encaja mejor como {act_stage}.",
                "plot_point_1": f"Hipótesis: ubicar primer punto de giro al cerrar la primera secuencia útil ({seq_hint.split(',')[0] if seq_hint != 'n/a' else 'sin secuencia clara'}).",
                "midpoint": f"Hipótesis: midpoint alrededor de la escena {max(1, len(scenes)//2)} con cambio de estrategia o riesgo.",
                "plot_point_2": f"Hipótesis: segundo giro en la última secuencia analizada para empujar al clímax ({len(sequences)} secuencias).",
                "resolution": "La resolución debe cerrar la pregunta dramática principal y costo del protagonista.",
                "issues": [] if len(sequences) >= 2 else ["Posible baja segmentación estructural por secuencias."],
                "recommendations": ["Definir objetivo y obstáculo por secuencia para clarificar progresión de actos."],
            },
            "comparato": {
                "idea": f"La idea matriz debe sostener {len(scenes)} escenas sin perder causalidad dramática.",
                "conflict_matrix": conflict_matrix,
                "dramatic_action": f"Acción dramática visible en {signals['action_hits']} escenas; reforzar decisión-consecuencia en cada bloque.",
                "character_function": f"Funciones dramáticas detectables: {key_characters}.",
                "issues": [] if scores["conflict_strength"] >= 45 else ["Conflicto podría ser insuficiente en desarrollo actual."],
                "recommendations": ["Aumentar oposición activa en secuencias intermedias y elevar costo de decisión."],
            },
            "mckee": {
                "scene_value_shifts": [
                    f"Escena 1->{min(2, len(scenes))}: pasar de expectativa a presión.",
                    f"Bloque medio (escena {max(1, len(scenes)//2)}): giro de valor hacia riesgo/urgencia.",
                ] if scenes else ["Sin escenas suficientes para inferir cambios de valor."],
                "conflict_levels": ["interno", "interpersonal", "social"],
                "crisis_climax_resolution": f"Escalonar crisis->clímax->resolución sobre {len(sequences)} secuencias, evitando resolución abrupta.",
                "subtext_notes": [
                    "En confrontaciones clave, sustituir explicación explícita por intención contradictoria en diálogo y acción.",
                    f"Priorizar subtexto en escenas con mayor fricción (detectadas: {signals['conflict_hits']}).",
                ],
                "issues": [] if scores["dramatic_clarity"] >= 50 else ["Clarity dramática mejorable en la articulación de beats."],
                "recommendations": ["Ajustar ritmo entre revelaciones y decisiones de alto costo en escenas puente."],
            },
            "scores": scores,
            "storyboard_actionables": storyboard_actionables,
            "theory_sources_used": theory_context.get("sources") or [],
            "fallback_used": fallback_used,
        }


cid_script_intelligence_service = CIDScriptIntelligenceService()
