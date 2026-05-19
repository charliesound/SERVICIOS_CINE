from __future__ import annotations

import json
import re
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

    def _sequence_aliases(self, sequence_id: Any) -> set[str]:
        raw = str(sequence_id or "").strip().lower()
        if not raw:
            return set()
        aliases = {raw}
        match = re.search(r"(\d+)$", raw)
        if not match:
            return aliases
        number = int(match.group(1))
        aliases.update(
            {
                str(number),
                f"seq_{number}",
                f"seq_{number:02d}",
                f"seq_{number:03d}",
                f"sequence_{number}",
                f"sequence_{number:02d}",
                f"sequence_{number:03d}",
            }
        )
        return aliases

    def _scene_number(self, scene: dict[str, Any], fallback_index: int) -> int:
        value = scene.get("scene_number")
        try:
            if value is not None:
                return int(value)
        except Exception:
            pass
        return fallback_index + 1

    def _filter_sequences_and_scenes(
        self,
        *,
        scenes: list[dict[str, Any]],
        sequences: list[dict[str, Any]],
        sequence_ids: list[str] | None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[int], list[str]]:
        if not sequence_ids:
            scene_numbers = [self._scene_number(scene, idx) for idx, scene in enumerate(scenes)]
            sequence_list = [str(seq.get("sequence_id") or "") for seq in sequences if seq.get("sequence_id")]
            return scenes, sequences, scene_numbers, sequence_list

        requested_aliases: set[str] = set()
        for seq in sequence_ids:
            requested_aliases.update(self._sequence_aliases(seq))

        matched_sequences = []
        matched_sequence_ids: list[str] = []
        included_scene_numbers: set[int] = set()
        for seq in sequences:
            seq_id = str(seq.get("sequence_id") or "")
            aliases = self._sequence_aliases(seq_id)
            if aliases.intersection(requested_aliases):
                matched_sequences.append(seq)
                if seq_id:
                    matched_sequence_ids.append(seq_id)
                for number in seq.get("included_scenes") or []:
                    try:
                        included_scene_numbers.add(int(number))
                    except Exception:
                        continue

        if included_scene_numbers:
            filtered_scenes = [
                scene for idx, scene in enumerate(scenes)
                if self._scene_number(scene, idx) in included_scene_numbers
            ]
            ordered_numbers = sorted(included_scene_numbers)
            return filtered_scenes, matched_sequences, ordered_numbers, matched_sequence_ids

        # Fallback when there is no explicit scene mapping in breakdown.
        if matched_sequences and scenes:
            sorted_scenes = sorted(
                [dict(scene, _scene_number=self._scene_number(scene, idx)) for idx, scene in enumerate(scenes)],
                key=lambda s: int(s.get("_scene_number") or 0),
            )
            chunk_size = max(1, len(sorted_scenes) // max(1, len(sequences) or 1))
            scoped: list[dict[str, Any]] = []
            scoped_numbers: list[int] = []
            for seq in matched_sequences:
                seq_id = str(seq.get("sequence_id") or "")
                aliases = self._sequence_aliases(seq_id)
                number_match = [a for a in aliases if a.isdigit()]
                if not number_match:
                    continue
                seq_number = int(sorted(number_match, key=len)[0])
                start = max(0, (seq_number - 1) * chunk_size)
                end = min(len(sorted_scenes), start + chunk_size)
                if start >= len(sorted_scenes):
                    continue
                for scene in sorted_scenes[start:end]:
                    scoped.append({k: v for k, v in scene.items() if k != "_scene_number"})
                    scoped_numbers.append(int(scene.get("_scene_number") or 0))
            return scoped, matched_sequences, sorted(set(scoped_numbers)), matched_sequence_ids

        return [], [], [], []

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

        scoped_scenes, scoped_sequences, scoped_scene_numbers, scoped_sequence_ids = self._filter_sequences_and_scenes(
            scenes=scenes,
            sequences=sequences,
            sequence_ids=sequence_ids,
        )

        theory_context = await cid_screenwriting_theory_service.fetch_theory_context(topics=theory_focus)
        fallback_used = bool(theory_context.get("fallback_used"))
        scores = self._build_heuristic_scores(script_text, len(scoped_scenes), len(scoped_sequences))
        signals = self._collect_scene_signals(scoped_scenes)
        act_stage = self._infer_act_stage(len(scoped_sequences), len(scoped_scenes))

        if sequence_ids and not scoped_scenes:
            scores = {
                "dramatic_clarity": 10,
                "conflict_strength": 0,
                "character_drive": 10,
                "structure_strength": 0,
                "pacing": 0,
                "cinematic_potential": 5,
            }

        seq_hint = ", ".join(str(seq.get("sequence_id")) for seq in scoped_sequences[:4]) if scoped_sequences else "n/a"
        sequence_scope = f"secuencias solicitadas {', '.join(sequence_ids)}" if sequence_ids else "todo el proyecto"
        overview = (
            f"Diagnóstico estructural basado en guion y teoría contextual. "
            f"Ámbito: {sequence_scope}. Escenas analizadas: {len(scoped_scenes)} {scoped_scene_numbers[:8] if scoped_scene_numbers else []}. "
            f"Secuencias consideradas: {len(scoped_sequences)} ({', '.join(scoped_sequence_ids) if scoped_sequence_ids else seq_hint})."
        )

        storyboard_actionables: list[str] = []
        if include_storyboard_actionables:
            if sequence_ids and not scoped_scenes:
                storyboard_actionables = [
                    "No hay material analizable para la secuencia solicitada; verifica sequence_id y reintenta.",
                    "Confirma que el mapa de secuencias del proyecto incluya escenas para esa secuencia.",
                ]
            else:
                storyboard_actionables = [
                    f"Priorizar objetivo dramático explícito en aperturas de secuencia ({len(scoped_sequences)} secuencias).",
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
                "act_structure": f"Con {len(scoped_scenes)} escenas y {len(scoped_sequences)} secuencias, el tramo actual encaja mejor como {act_stage}.",
                "plot_point_1": f"Hipótesis: ubicar primer punto de giro al cerrar la primera secuencia útil ({seq_hint.split(',')[0] if seq_hint != 'n/a' else 'sin secuencia clara'}).",
                "midpoint": f"Hipótesis: midpoint alrededor de la escena {max(1, len(scoped_scenes)//2)} con cambio de estrategia o riesgo.",
                "plot_point_2": f"Hipótesis: segundo giro en la última secuencia analizada para empujar al clímax ({len(scoped_sequences)} secuencias).",
                "resolution": "La resolución debe cerrar la pregunta dramática principal y costo del protagonista.",
                "issues": [] if len(scoped_sequences) >= 2 else ["Posible baja segmentación estructural por secuencias."],
                "recommendations": ["Definir objetivo y obstáculo por secuencia para clarificar progresión de actos."],
            },
            "comparato": {
                "idea": f"La idea matriz debe sostener {len(scoped_scenes)} escenas sin perder causalidad dramática.",
                "conflict_matrix": conflict_matrix,
                "dramatic_action": f"Acción dramática visible en {signals['action_hits']} escenas; reforzar decisión-consecuencia en cada bloque.",
                "character_function": f"Funciones dramáticas detectables: {key_characters}.",
                "issues": [] if scores["conflict_strength"] >= 45 else ["Conflicto podría ser insuficiente en desarrollo actual."],
                "recommendations": ["Aumentar oposición activa en secuencias intermedias y elevar costo de decisión."],
            },
            "mckee": {
                "scene_value_shifts": [
                    f"Escena 1->{min(2, len(scoped_scenes))}: pasar de expectativa a presión.",
                    f"Bloque medio (escena {max(1, len(scoped_scenes)//2)}): giro de valor hacia riesgo/urgencia.",
                ] if scoped_scenes else ["Sin escenas suficientes para inferir cambios de valor."],
                "conflict_levels": ["interno", "interpersonal", "social"],
                "crisis_climax_resolution": f"Escalonar crisis->clímax->resolución sobre {len(scoped_sequences)} secuencias, evitando resolución abrupta.",
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
