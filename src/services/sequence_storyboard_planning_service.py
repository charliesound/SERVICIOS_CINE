from __future__ import annotations

import re
from typing import Any

from schemas.cid_sequence_first_schema import (
    PlannedStoryboardShot,
    ScriptSequenceMapEntry,
    SequenceStoryboardPlan,
)

_DIALOGUE_PATTERN = re.compile(r"(?:^|\n)\s*([A-ZÁÉÍÓÚÑa-záéíóúñ]+)\s*:")
_ACTION_VERBS: set[str] = {
    "entra", "sale", "camina", "corre", "mira", "mueve", "levanta", "toma",
    "empuja", "jala", "golpea", "abre", "cierra", "cruza", "salta", "sienta",
    "entrega", "recoge", "lanza", "atrapa", "sigue", "persigue", "escapa",
    "entran", "salen", "caminan", "corren", "miran", "cruzan",
}
_EMOTION_WORDS: set[str] = {
    "tensa", "tenso", "alegre", "triste", "dramático", "dramática",
    "enojado", "enojada", "furioso", "furiosa", "asustado", "asustada",
    "nervioso", "nerviosa", "emocionado", "emocionada", "sereno", "serena",
    "angustiado", "angustiada", "sorprendido", "sorprendida",
}
_LOCATION_KEYWORDS: set[str] = {
    "interior", "exterior", "int", "ext", "casa", "calle", "oficina",
    "habitación", "cocina", "salón", "sala", "patio", "jardín",
    "parque", "plaza", "edificio", "coche", "auto", "vehículo",
}

_SHOT_TYPE_MAP: dict[str, dict[str, Any]] = {
    "ESTABLISHING": {
        "framing": "wide",
        "camera_angle": "eye-level",
        "camera_movement": "static",
        "lens_suggestion": "18mm",
    },
    "WS": {
        "framing": "wide",
        "camera_angle": "eye-level",
        "camera_movement": "static",
        "lens_suggestion": "24mm",
    },
    "MS": {
        "framing": "medium",
        "camera_angle": "eye-level",
        "camera_movement": "static",
        "lens_suggestion": "50mm",
    },
    "CU": {
        "framing": "close-up",
        "camera_angle": "eye-level",
        "camera_movement": "static",
        "lens_suggestion": "85mm",
    },
    "OTS": {
        "framing": "medium",
        "camera_angle": "over-shoulder",
        "camera_movement": "static",
        "lens_suggestion": "50mm",
    },
    "POV": {
        "framing": "close-up",
        "camera_angle": "eye-level",
        "camera_movement": "handheld",
        "lens_suggestion": "35mm",
    },
    "DETAIL": {
        "framing": "extreme-close-up",
        "camera_angle": "eye-level",
        "camera_movement": "static",
        "lens_suggestion": "100mm",
    },
    "TRACKING": {
        "framing": "medium",
        "camera_angle": "eye-level",
        "camera_movement": "tracking",
        "lens_suggestion": "35mm",
    },
}


class SequenceStoryboardPlanningService:

    def _has_dialogue(self, excerpt: str) -> bool:
        return bool(_DIALOGUE_PATTERN.search(excerpt))

    def _character_names_from_excerpt(self, excerpt: str, known: list[str]) -> list[str]:
        found: set[str] = set()
        for match in _DIALOGUE_PATTERN.finditer(excerpt):
            candidate = match.group(1).strip()
            if candidate and candidate[0].isupper():
                found.add(candidate)
        found.update(n for n in known if n)
        return sorted(found)

    def _detect_action_verbs(self, excerpt: str) -> list[str]:
        excerpt_lower = excerpt.lower()
        return [v for v in _ACTION_VERBS if v in excerpt_lower]

    def _detect_emotion_words(self, excerpt: str) -> list[str]:
        excerpt_lower = excerpt.lower()
        return [w for w in _EMOTION_WORDS if w in excerpt_lower]

    def _has_location_intro(self, entry: ScriptSequenceMapEntry) -> bool:
        excerpt_lower = entry.script_excerpt.lower()
        location_lower = entry.location.lower() if entry.location else ""
        if location_lower and location_lower in excerpt_lower:
            return True
        return any(kw in excerpt_lower for kw in _LOCATION_KEYWORDS)

    def _has_physical_action(self, excerpt: str) -> bool:
        return bool(self._detect_action_verbs(excerpt))

    def _has_emotional_tension(self, excerpt: str) -> bool:
        return bool(self._detect_emotion_words(excerpt))

    def _has_decision_or_revelation(self, entry: ScriptSequenceMapEntry) -> bool:
        dr = entry.dramatic_function.lower() if entry.dramatic_function else ""
        if any(w in dr for w in ("revelación", "decisión", "giro", "clímax", "revelation", "decision", "twist", "climax")):
            return True
        excerpt_lower = entry.script_excerpt.lower()
        if any(w in excerpt_lower for w in ("descubre", "revela", "decide", "entiende", "comprende")):
            return True
        return False

    def _important_object_detected(self, excerpt: str) -> bool:
        obj_keywords = {"objeto", "llave", "carta", "foto", "arma", "reloj", "anillo",
                        "documento", "maletín", "caja", "teléfono", "pistola", "cuchillo"}
        return any(kw in excerpt.lower() for kw in obj_keywords)

    def _pick_time_based_lighting(self, time_of_day: str) -> str:
        tod = time_of_day.lower().strip() if time_of_day else ""
        if any(w in tod for w in ("noche", "night", "oscuro")):
            return "low-key / noche"
        if any(w in tod for w in ("atardecer", "ocaso", "dusk", "sunset")):
            return "golden hour / cálido"
        if any(w in tod for w in ("amanecer", "dawn", "sunrise")):
            return "luz suave matutina"
        if any(w in tod for w in ("interior", "int")):
            return "luz artificial ambiente"
        return "luz natural / difusa"

    def _guess_visual_style(self, entry: ScriptSequenceMapEntry) -> str:
        parts: list[str] = []
        loc = entry.location.lower() if entry.location else ""
        if any(w in loc for w in ("noche", "oscuro", "sótano")):
            parts.append("iluminación low-key con sombras marcadas")
        elif any(w in loc for w in ("playa", "campo", "exterior")):
            parts.append("luz natural saturada con paleta vibrante")
        elif any(w in loc for w in ("oficina", "interior", "casa")):
            parts.append("iluminación artificial con tonos neutros")
        else:
            parts.append("iluminación ambiental balanceada")

        emotion = entry.emotional_goal.lower() if entry.emotional_goal else ""
        if "tensa" in emotion or "suspenso" in emotion:
            parts.append("composición asimétrica con sombras pronunciadas")
        elif "alegre" in emotion or "ligero" in emotion:
            parts.append("colores cálidos y composición abierta")
        elif "triste" in emotion or "melancólico" in emotion:
            parts.append("paleta desaturada con tonos fríos")
        else:
            parts.append("estilo visual neutral")

        return " / ".join(parts)

    def _build_shot(self, *, shot_number: int, shot_type: str, action: str,
                    characters: list[str], location: str, time_of_day: str,
                    script_excerpt: str, reason: str, excerpt_used: str) -> PlannedStoryboardShot:
        config = _SHOT_TYPE_MAP.get(shot_type, _SHOT_TYPE_MAP["MS"])
        emotion_words = self._detect_emotion_words(script_excerpt)
        if emotion_words:
            emotional_intent = ", ".join(emotion_words[:2])
        else:
            emotional_intent = "neutral"

        lighting = self._pick_time_based_lighting(time_of_day)
        action_clean = action[:200] if action else ""
        framing = config["framing"]
        camera_angle = config["camera_angle"]
        camera_movement = config["camera_movement"]
        lens = config["lens_suggestion"]

        shot_type_desc = {"ESTABLISHING": "establishing", "WS": "wide", "MS": "medium",
                          "CU": "close-up", "OTS": "over-the-shoulder", "POV": "point-of-view",
                          "DETAIL": "detail", "TRACKING": "tracking"}.get(shot_type, shot_type.lower())

        prompt_brief = f"{shot_type_desc} shot of {action_clean[:120]}. {emotional_intent} mood, {lighting}, {framing} framing.".strip()
        prompt_brief = prompt_brief[:200]

        return PlannedStoryboardShot(
            shot_number=shot_number,
            shot_type=shot_type,
            framing=framing,
            camera_angle=camera_angle,
            camera_movement=camera_movement,
            lens_suggestion=lens,
            action=action_clean,
            characters=sorted(set(characters)),
            location=location,
            lighting=lighting,
            emotional_intent=emotional_intent,
            prompt_brief=prompt_brief,
            negative_prompt_guidance="evitar distorsión, desenfoque excesivo, artefactos",
            shot_plan_reason=reason,
            script_excerpt_used=excerpt_used,
        )

    def plan_sequence(self, entry: ScriptSequenceMapEntry) -> SequenceStoryboardPlan:
        excerpt = entry.script_excerpt or ""
        characters = entry.characters
        location = entry.location or ""
        time_of_day = entry.time_of_day or ""
        title = entry.title or ""
        summary = entry.summary or ""

        excerpt_chars = self._character_names_from_excerpt(excerpt, characters)
        if not excerpt_chars and characters:
            excerpt_chars = list(characters)
        all_chars = excerpt_chars or ["Personaje"]

        has_dialogue = self._has_dialogue(excerpt)
        has_action = self._has_physical_action(excerpt)
        has_emotion = self._has_emotional_tension(excerpt)
        has_location_intro = self._has_location_intro(entry)
        has_decision = self._has_decision_or_revelation(entry)
        has_object = self._important_object_detected(excerpt)

        action_verbs = self._detect_action_verbs(excerpt)
        action_text = ", ".join(action_verbs[:3]) if action_verbs else "acción general"
        emotion_words = self._detect_emotion_words(excerpt)

        excerpt_sentences = [s.strip() for s in re.split(r'[.!?\n]+', excerpt) if s.strip()]

        shots: list[PlannedStoryboardShot] = []
        shot_idx = 0

        def _add_shot(shot_type: str, reason: str, excerpt_fragment: str = "") -> None:
            nonlocal shot_idx
            shot_idx += 1
            frag = excerpt_fragment or (excerpt_sentences[0] if excerpt_sentences else excerpt[:150])
            shots.append(self._build_shot(
                shot_number=shot_idx,
                shot_type=shot_type,
                action=action_text if not excerpt_fragment else excerpt_fragment[:200],
                characters=all_chars,
                location=location,
                time_of_day=time_of_day,
                script_excerpt=excerpt,
                reason=reason,
                excerpt_used=frag[:250],
            ))

        total_sentences = len(excerpt_sentences)

        # 1. Establishing / location intro
        if has_location_intro:
            _add_shot("ESTABLISHING",
                      "Toma de establecimiento para ubicar al espectador en la localización.",
                      excerpt_sentences[0] if total_sentences > 0 else excerpt[:200])
        else:
            _add_shot("WS",
                      "Toma abierta inicial que presenta el espacio escénico.",
                      excerpt_sentences[0] if total_sentences > 0 else excerpt[:200])

        # 2. Wide shot with characters
        _add_shot("WS",
                  "Plano general que introduce a los personajes en el entorno.",
                  excerpt_sentences[1] if total_sentences > 1 else excerpt[:200])

        # 3. Medium shot for action or dialogue setup
        if has_action:
            _add_shot("MS",
                      "Plano medio para captar la acción física de los personajes.",
                      excerpt_sentences[2] if total_sentences > 2 else excerpt[:200])
        else:
            _add_shot("MS",
                      "Plano medio para establecer la presencia de los personajes.",
                      excerpt_sentences[2] if total_sentences > 2 else excerpt[:200])

        # 4. Dialogue handling
        if has_dialogue and len(all_chars) >= 2:
            _add_shot("OTS",
                      "Plano over-shoulder para capturar el intercambio de diálogo.",
                      excerpt_sentences[3] if total_sentences > 3 else excerpt[:200])
            _add_shot("OTS",
                      "Contraplano over-shoulder para el diálogo en dirección opuesta.",
                      excerpt_sentences[4] if total_sentences > 4 else excerpt[:200])

        # 5. Emotional close-up
        if has_emotion:
            _add_shot("CU",
                      "Primer plano para capturar la reacción emocional del personaje.",
                      excerpt_sentences[3] if total_sentences > 3 and not has_dialogue else (
                          excerpt_sentences[5] if total_sentences > 5 else excerpt[:200]))

        # 6. Detail shot for important object
        if has_object:
            _add_shot("DETAIL",
                      "Toma de detalle para resaltar el objeto importante en la escena.",
                      excerpt_sentences[4] if total_sentences > 4 else excerpt[:200])

        # 7. Action / tracking
        if has_action:
            _add_shot("TRACKING",
                      "Travelling para seguir el movimiento y mantener la energía de la acción.",
                      excerpt_sentences[5] if total_sentences > 5 else excerpt[:200])

        # 8. Closing shot
        if has_decision:
            _add_shot("CU",
                      "Primer plano de cierre para enfatizar la decisión o revelación.",
                      excerpt_sentences[-1] if total_sentences > 0 else excerpt[:200])
        else:
            _add_shot("MS",
                      "Plano medio de cierre que concluye la secuencia visualmente.",
                      excerpt_sentences[-1] if total_sentences > 0 else excerpt[:200])

        # Fill remaining up to minimum of 5 shots
        while len(shots) < 5:
            _add_shot("MS",
                      "Plano medio adicional para completar la progresión visual.",
                      excerpt[:200])

        continuity_plan: list[str] = [
            "Mantener la posición relativa de los personajes entre tomas.",
            "Respetar el eje de cámara (regla de los 180 grados).",
            "Consistencia en la iluminación: misma fuente y temperatura de color.",
            "Continuidad de utilería: los objetos deben mantener su posición y estado.",
            "Dirección de miradas coherente entre tomas con diálogo.",
        ]
        if has_dialogue and len(all_chars) >= 2:
            continuity_plan.insert(2, "Respetar el eje de diálogo entre los interlocutores.")
        if has_action:
            continuity_plan.insert(3, "Trayectoria de movimiento consistente en acciones físicas.")

        visual_style = self._guess_visual_style(entry)

        warnings: list[str] = []
        if not excerpt:
            warnings.append("La secuencia no contiene extracto de guion.")
        if not location:
            warnings.append("No se especificó ubicación para la secuencia.")
        if not all_chars:
            warnings.append("No se detectaron personajes en la secuencia.")

        return SequenceStoryboardPlan(
            project_id="",
            sequence_id=entry.sequence_id,
            sequence_title=title,
            sequence_summary=summary,
            shot_plan=shots,
            continuity_plan=continuity_plan,
            visual_style_guidance=visual_style,
            estimated_shot_count=len(shots),
            warnings=warnings,
        )

    def plan_sequence_from_entry(self, entry: ScriptSequenceMapEntry) -> SequenceStoryboardPlan:
        return self.plan_sequence(entry)


sequence_storyboard_planning_service = SequenceStoryboardPlanningService()
