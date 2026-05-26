from __future__ import annotations

import re
from typing import Any

from schemas.cinematic_grammar_schema import (
    BeatType,
    CinematicFunction,
    CinematicGrammarRequest,
    CinematicGrammarResult,
    CinematicShotSpec,
    CinematicShotType,
    ContinuityRule,
    CoveragePattern,
    EditorialRole,
    OrderedShotPlan,
    ReferenceMode,
    SceneType,
    ShotPriority,
)

_SHOT_TYPE_BY_ROLE: dict[str, CinematicShotType] = {
    "WS": CinematicShotType.LONG_SHOT,
    "ELS": CinematicShotType.EXTREME_LONG_SHOT,
    "MS": CinematicShotType.MEDIUM_SHOT,
    "MCU": CinematicShotType.MEDIUM_CLOSE_UP,
    "CU": CinematicShotType.CLOSE_UP,
    "ECU": CinematicShotType.EXTREME_CLOSE_UP,
    "INSERT": CinematicShotType.INSERT,
    "POV": CinematicShotType.POV,
    "OTS": CinematicShotType.OVER_THE_SHOULDER,
    "LA": CinematicShotType.LOW_ANGLE,
    "HA": CinematicShotType.HIGH_ANGLE,
    "DA": CinematicShotType.DUTCH_ANGLE,
    "2SHOT": CinematicShotType.TWO_SHOT,
    "REV": CinematicShotType.REVERSE,
    "MLS": CinematicShotType.MEDIUM_LONG_SHOT,
}

_SCENE_KEYWORDS: dict[SceneType, list[str]] = {
    SceneType.SUSPENSE: [
        "silencio", "silencio", "cruje", "sombra", "oscuro", "oscuridad",
        "quieto", "quieta", "paso", "pasos", "miedo", "temor",
        "respira", "respiración", "contiene", "aliento",
        "susurro", "sigiloso", "sigilosa", "acecha", "acechan",
        "pregunta", "fondo", "alguien", "linterna", "entra",
    ],
    SceneType.TERROR: [
        "grita", "grito", "terror", "horror", "sangre", "monstruo",
        "fantasma", "pesadilla", "pánico", "corre", "huye",
        "desesperado", "desesperada", "amenaza", "mata",
    ],
    SceneType.INTERIOR_EXPLORATION: [
        "entra", "linterna", "casa", "habitación", "cuarto", "pasillo",
        "puerta", "abre", "entrar", "explora", "recorre",
        "mira", "observa", "examina", "revisa",
    ],
    SceneType.PURSUIT: [
        "persigue", "corre", "huye", "escapa", "alcanza",
        "acelerado", "acelerada", "carrera",
    ],
    SceneType.DIALOGUE: [
        "dice", "pregunta", "responde", "contesta", "habla",
        "conversación", "dialogo", "diálogo",
    ],
    SceneType.CONFRONTATION: [
        "enfrenta", "discute", "discusión", "pelea", "grita",
        "acusación", "acusaciones", "tensión",
    ],
    SceneType.PHYSICAL_ACTION: [
        "golpea", "empuja", "lanza", "salta", "cae", "corre",
        "pelea", "lucha", "forcejeo",
    ],
    SceneType.DISCOVERY: [
        "encuentra", "descubre", "ve", "mira", "observa",
        "revelación", "sorprende", "asombro",
    ],
    SceneType.TRANSITION: [
        "amanecer", "atardecer", "anochece", "amanece",
        "días después", "horas después", "más tarde",
    ],
    SceneType.EMOTIONAL_SCENE: [
        "llora", "abraza", "sonríe", "triste", "feliz",
        "emoción", "emotivo", "emotiva", "sentimiento",
    ],
    SceneType.KEY_OBJECT: [
        "objeto", "llave", "carta", "foto", "fotografía",
        "reliquia", "símbolo", "simbólico",
    ],
    SceneType.IMPORTANT_SOUND: [
        "sonido", "ruido", "cruje", "chasquido", "golpe",
        "campana", "alarma", "sirena", "música", "melodía",
    ],
}

_CONTINUITY_RULES_BY_PATTERN: dict[CoveragePattern, list[ContinuityRule]] = {
    CoveragePattern.CLASSIC_COVERAGE: [
        ContinuityRule.CONTINUITY_CUT,
        ContinuityRule.AXIS_OF_ACTION,
    ],
    CoveragePattern.THREAT_COVERAGE: [
        ContinuityRule.EYELINE_MATCH,
        ContinuityRule.CROSS_CUTTING,
        ContinuityRule.SCREEN_DIRECTION,
    ],
    CoveragePattern.SUSPENSE_COVERAGE: [
        ContinuityRule.EYELINE_MATCH,
        ContinuityRule.CONTINUITY_CUT,
        ContinuityRule.SCREEN_DIRECTION,
    ],
    CoveragePattern.EXPLORATION_COVERAGE: [
        ContinuityRule.EYELINE_MATCH,
        ContinuityRule.MATCH_ON_ACTION,
        ContinuityRule.SCREEN_DIRECTION,
    ],
    CoveragePattern.ACTION_LINEAR: [
        ContinuityRule.MATCH_ON_ACTION,
        ContinuityRule.SCREEN_DIRECTION,
    ],
    CoveragePattern.DIALOGUE_COVERAGE: [
        ContinuityRule.AXIS_OF_ACTION,
        ContinuityRule.EYELINE_MATCH,
    ],
    CoveragePattern.CONFRONTATION_COVERAGE: [
        ContinuityRule.AXIS_OF_ACTION,
        ContinuityRule.EYELINE_MATCH,
        ContinuityRule.CONTINUITY_CUT,
    ],
    CoveragePattern.DISCOVERY_COVERAGE: [
        ContinuityRule.CONTINUITY_CUT,
        ContinuityRule.CUTAWAY,
    ],
    CoveragePattern.TRANSITION_COVERAGE: [
        ContinuityRule.SOUND_BRIDGE,
        ContinuityRule.MATCH_CUT,
    ],
    CoveragePattern.EMOTIONAL_COVERAGE: [
        ContinuityRule.CONTINUITY_CUT,
        ContinuityRule.CUTAWAY,
    ],
    CoveragePattern.SOUND_FOCUS_COVERAGE: [
        ContinuityRule.INSERT_CUT,
        ContinuityRule.SOUND_BRIDGE,
    ],
}


_CoverageShotTemplate = tuple[
    str, EditorialRole, CinematicFunction, BeatType, ShotPriority
]

_PATTERNS: dict[CoveragePattern, list[_CoverageShotTemplate]] = {
    CoveragePattern.SUSPENSE_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.ACTION_BEAT, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("INSERT", EditorialRole.SOUND_DETAIL, CinematicFunction.SOUND_FOCUS, BeatType.SOUND, ShotPriority.HIGH),
        ("MCU", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MUST_HAVE),
        ("POV", EditorialRole.POV, CinematicFunction.REVEAL_THREAT, BeatType.REVEAL, ShotPriority.MUST_HAVE),
        ("MLS", EditorialRole.THREAT_INDICATOR, CinematicFunction.BUILD_TENSION, BeatType.ATMOSPHERE, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("WS", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.HIGH),
    ],
    CoveragePattern.EXPLORATION_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.ACTION_BEAT, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("INSERT", EditorialRole.INSERT, CinematicFunction.ATMOSPHERE, BeatType.DESCRIPTION, ShotPriority.MEDIUM),
        ("POV", EditorialRole.POV, CinematicFunction.DISCOVERY, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.HIGH),
        ("MLS", EditorialRole.CLOSING, CinematicFunction.TRANSITION_DEVICE, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.THREAT_COVERAGE: [
        ("MS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("POV", EditorialRole.POV, CinematicFunction.REVEAL_THREAT, BeatType.REVEAL, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("WS", EditorialRole.COVERAGE, CinematicFunction.BUILD_TENSION, BeatType.ATMOSPHERE, ShotPriority.HIGH),
        ("CU", EditorialRole.THREAT_INDICATOR, CinematicFunction.BUILD_TENSION, BeatType.ACTION, ShotPriority.HIGH),
        ("ECU", EditorialRole.CLOSING, CinematicFunction.CLIMAX, BeatType.REACTION, ShotPriority.MUST_HAVE),
    ],
    CoveragePattern.CLASSIC_COVERAGE: [
        ("ELS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("WS", EditorialRole.MASTER, CinematicFunction.EXPOSITION, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.COVERAGE, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.HIGH),
        ("CU", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MEDIUM),
        ("WS", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.DIALOGUE_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("2SHOT", EditorialRole.MASTER, CinematicFunction.EXPOSITION, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("OTS", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MUST_HAVE),
        ("REV", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MUST_HAVE),
        ("MCU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.HIGH),
        ("WS", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.CONFRONTATION_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.MASTER, CinematicFunction.BUILD_TENSION, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("OTS", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.COVERAGE, CinematicFunction.EXPOSITION, BeatType.DIALOGUE, ShotPriority.HIGH),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("DA", EditorialRole.THREAT_INDICATOR, CinematicFunction.BUILD_TENSION, BeatType.ATMOSPHERE, ShotPriority.HIGH),
        ("WS", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.ACTION_LINEAR: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.ACTION_BEAT, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.ACTION_BEAT, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.HIGH),
        ("LA", EditorialRole.ACTION_BEAT, CinematicFunction.CLIMAX, BeatType.ACTION, ShotPriority.HIGH),
        ("WS", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.DISCOVERY_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.ACTION_BEAT, CinematicFunction.ACTION_BEAT, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("INSERT", EditorialRole.INSERT, CinematicFunction.DISCOVERY, BeatType.ACTION, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("WS", EditorialRole.CLOSING, CinematicFunction.TRANSITION_DEVICE, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.TRANSITION_COVERAGE: [
        ("ELS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MLS", EditorialRole.TRANSITION, CinematicFunction.TRANSITION_DEVICE, BeatType.TRANSITION, ShotPriority.MUST_HAVE),
        ("WS", EditorialRole.CLOSING, CinematicFunction.TRANSITION_DEVICE, BeatType.TRANSITION, ShotPriority.MEDIUM),
    ],
    CoveragePattern.EMOTIONAL_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("MS", EditorialRole.COVERAGE, CinematicFunction.EXPOSITION, BeatType.ACTION, ShotPriority.HIGH),
        ("CU", EditorialRole.COVERAGE, CinematicFunction.DIALOGUE, BeatType.DIALOGUE, ShotPriority.MUST_HAVE),
        ("ECU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.CLOSING, CinematicFunction.RESOLUTION, BeatType.TRANSITION, ShotPriority.HIGH),
    ],
    CoveragePattern.SOUND_FOCUS_COVERAGE: [
        ("WS", EditorialRole.ESTABLISHING, CinematicFunction.ESTABLISH_CONTEXT, BeatType.DESCRIPTION, ShotPriority.MUST_HAVE),
        ("INSERT", EditorialRole.SOUND_DETAIL, CinematicFunction.SOUND_FOCUS, BeatType.SOUND, ShotPriority.MUST_HAVE),
        ("CU", EditorialRole.REACTION, CinematicFunction.REACTION, BeatType.REACTION, ShotPriority.MUST_HAVE),
        ("MCU", EditorialRole.COVERAGE, CinematicFunction.ATMOSPHERE, BeatType.ATMOSPHERE, ShotPriority.HIGH),
        ("INSERT", EditorialRole.CLOSING, CinematicFunction.SOUND_FOCUS, BeatType.SOUND, ShotPriority.MEDIUM),
    ],
}

_PATTERN_BY_SCENE_TYPE: dict[SceneType, CoveragePattern] = {
    SceneType.SUSPENSE: CoveragePattern.SUSPENSE_COVERAGE,
    SceneType.TERROR: CoveragePattern.THREAT_COVERAGE,
    SceneType.INTERIOR_EXPLORATION: CoveragePattern.EXPLORATION_COVERAGE,
    SceneType.PURSUIT: CoveragePattern.ACTION_LINEAR,
    SceneType.DIALOGUE: CoveragePattern.DIALOGUE_COVERAGE,
    SceneType.CONFRONTATION: CoveragePattern.CONFRONTATION_COVERAGE,
    SceneType.PHYSICAL_ACTION: CoveragePattern.ACTION_LINEAR,
    SceneType.DISCOVERY: CoveragePattern.DISCOVERY_COVERAGE,
    SceneType.TRANSITION: CoveragePattern.TRANSITION_COVERAGE,
    SceneType.EMOTIONAL_SCENE: CoveragePattern.EMOTIONAL_COVERAGE,
    SceneType.KEY_OBJECT: CoveragePattern.DISCOVERY_COVERAGE,
    SceneType.IMPORTANT_SOUND: CoveragePattern.SOUND_FOCUS_COVERAGE,
}

_PRIORITY_LABELS: dict[ShotPriority, str] = {
    ShotPriority.MUST_HAVE: "Obligatorio",
    ShotPriority.HIGH: "Alta prioridad",
    ShotPriority.MEDIUM: "Prioridad media",
    ShotPriority.LOW: "Baja prioridad",
    ShotPriority.OPTIONAL: "Opcional",
}

_SOUND_KEYWORDS = [
    "sonido", "ruido", "cruje", "chasquido", "golpe", "silencio",
    "música", "melodía", "campana", "alarma", "sirena", "susurro",
    "paso", "pasos",
]

_DIALOGUE_KEYWORDS = [
    "dice", "pregunta", "responde", "contesta", "habla", "grita",
    "susurra", "exclama", "alguien",
]

_THREAT_KEYWORDS = [
    "sombra", "figura", "silueta", "presencia", "amenaza",
    "cruza al fondo", "aparece al fondo", "algo cruza",
]

_DEFAULT_SCENE_TYPE = SceneType.SUSPENSE


class CinematicShotGrammarEngine:
    def detect_scene_type(self, scene_text: str) -> SceneType:
        lower = scene_text.lower()
        scores: dict[SceneType, int] = {}
        for scene_type, keywords in _SCENE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score > 0:
                scores[scene_type] = score
        if not scores:
            return _DEFAULT_SCENE_TYPE
        return max(scores, key=scores.get)

    def select_coverage_pattern(self, scene_type: SceneType) -> CoveragePattern:
        return _PATTERN_BY_SCENE_TYPE.get(scene_type, CoveragePattern.CLASSIC_COVERAGE)

    def detect_scene_type_and_confidence(self, scene_text: str) -> tuple[SceneType, float]:
        lower = scene_text.lower()
        scores: dict[SceneType, float] = {}
        total_kw = 0
        for scene_type, keywords in _SCENE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in lower)
            if score > 0:
                scores[scene_type] = float(score)
                total_kw += score
        if not scores:
            return _DEFAULT_SCENE_TYPE, 0.1
        best = max(scores, key=scores.get)
        if total_kw == 0:
            return best, 0.1
        confidence = min(scores[best] / float(max(total_kw, 1)), 1.0) * 0.9 + 0.1
        return best, round(confidence, 2)

    def _detect_beats(self, scene_text: str) -> list[BeatType]:
        lower = scene_text.lower()
        sentences = re.split(r"[.!?]\s*", scene_text)
        beats: list[BeatType] = []
        for sentence in sentences:
            if not sentence.strip():
                continue
            s_lower = sentence.lower()
            if any(kw in s_lower for kw in _DIALOGUE_KEYWORDS):
                beats.append(BeatType.DIALOGUE)
            elif any(kw in s_lower for kw in _SOUND_KEYWORDS):
                beats.append(BeatType.SOUND)
            elif any(kw in s_lower for kw in _THREAT_KEYWORDS):
                beats.append(BeatType.REVEAL)
            elif any(kw in s_lower for kw in ["mira", "observa", "ve", "encuentra"]):
                beats.append(BeatType.REVEAL)
            elif any(kw in s_lower for kw in ["quieto", "quieta", "silencio", "miedo"]):
                beats.append(BeatType.ATMOSPHERE)
            elif any(kw in s_lower for kw in ["entra", "cruza", "llega", "sale"]):
                beats.append(BeatType.ACTION)
            else:
                beats.append(BeatType.DESCRIPTION)
        if not beats:
            beats = [BeatType.DESCRIPTION]
        return beats

    def _extract_character_names(self, scene_text: str) -> list[str]:
        words = re.findall(r"\b[A-Z][a-záéíóúñ]+\b", scene_text)
        if not words:
            return []
        skip = {"El", "La", "Los", "Las", "Un", "Una", "En", "Por", "Para", "Con", "Sin", "Su", "Sus", "Del", "Al"}
        return list({w for w in words if w not in skip})

    def _apply_visual_raccord(
        self,
        shots: list[CinematicShotSpec],
        scene_text: str,
        character_names: list[str],
    ) -> list[CinematicShotSpec]:
        lower = scene_text.lower()
        main_char = character_names[0] if character_names else None

        props: list[str] = []
        if "linterna" in lower:
            props.append("flashlight")

        location: str | None = None
        if any(w in lower for w in ["casa", "habitación", "cuarto"]):
            location = "abandoned_house_hallway" if "pasillo" in lower else "abandoned_house"

        lighting: str | None = None
        if "linterna" in lower:
            lighting = "low_key_night_with_flashlight"
        elif any(w in lower for w in ["oscuro", "oscuridad"]):
            lighting = "low_key_night"

        atmosphere: str | None = None
        if "silencio" in lower:
            atmosphere = "silent_tense"
        elif any(w in lower for w in ["polvo", "viejo", "abandonado"]):
            atmosphere = "dusty_aged"

        char_note: str | None = None
        if main_char:
            prop_detail = f", same {props[0]}" if props else ""
            char_note = f"{main_char} must remain visually consistent across all shots: same face, same hair, same wardrobe{prop_detail}."
        wardrobe_note: str | None = "Same wardrobe across the sequence." if main_char else None
        prop_note: str | None = None
        if props:
            pn = ", ".join(props)
            ref = main_char or "the character"
            prop_note = f"{pn.capitalize()} remains the key prop and stays with {ref} across shots."
        set_note: str | None = None
        if location == "abandoned_house_hallway":
            set_note = "Same abandoned house hallway with cracked wooden floor, peeling walls, darkness and narrow corridor."
        elif location:
            set_note = f"Same {location.replace('_', ' ')}."
        lighting_note: str | None = None
        if lighting == "low_key_night_with_flashlight":
            lighting_note = "Maintain low-key night lighting and flashlight beam as motivated light."
        elif lighting:
            lighting_note = "Maintain low-key night lighting."
        atmos_note: str | None = None
        if atmosphere == "silent_tense":
            atmos_note = "Dusty, silent, tense abandoned-house atmosphere."

        visual_raccord: str | None = None
        if main_char or set_note or lighting_note:
            visual_raccord = "Preserve character, wardrobe, prop, location, lighting and atmosphere continuity across the sequence."

        result: list[CinematicShotSpec] = []
        for i, shot in enumerate(shots):
            axis_note: str | None = None
            if shot.shot_type in (CinematicShotType.POV, CinematicShotType.OVER_THE_SHOULDER):
                axis_note = "Maintain 180-degree axis of action"
            elif shot.coverage_role == EditorialRole.ESTABLISHING:
                axis_note = "Establish 180-degree axis"
            elif shot.coverage_role == EditorialRole.CLOSING:
                axis_note = "Respect established axis"

            movement_note: str | None = None
            if shot.movement and shot.movement not in ("static",):
                movement_note = f"Consistent {shot.movement} direction"
            elif shot.dramatic_function == CinematicFunction.ACTION_BEAT:
                movement_note = "Match direction of movement across cut"

            updated = shot.model_copy(update={
                "character_continuity_note": char_note,
                "character_reference_id": main_char,
                "wardrobe_continuity_note": wardrobe_note,
                "prop_continuity_note": prop_note,
                "set_continuity_note": set_note,
                "location_reference_id": location,
                "lighting_continuity_note": lighting_note,
                "atmosphere_continuity_note": atmos_note,
                "axis_continuity_note": axis_note,
                "movement_direction_note": movement_note,
                "visual_raccord_note": visual_raccord,
            })
            result.append(updated)
        return result

    def build_ordered_shot_plan(
        self,
        scene_text: str,
        coverage_pattern: CoveragePattern,
        character_names: list[str] | None = None,
    ) -> OrderedShotPlan:
        template = _PATTERNS.get(coverage_pattern, _PATTERNS[CoveragePattern.CLASSIC_COVERAGE])
        beats = self._detect_beats(scene_text)
        scene_type, _ = self.detect_scene_type_and_confidence(scene_text)
        shots: list[CinematicShotSpec] = []
        for i, (shot_key, role, func, default_beat, priority) in enumerate(template, start=1):
            beat = default_beat
            if i <= len(beats):
                beat = beats[i - 1]
            shot_type = _SHOT_TYPE_BY_ROLE.get(shot_key, CinematicShotType.MEDIUM_SHOT)
            camera_angle, movement = self._suggest_camera(shot_type, role, func)
            lens = self._suggest_lens(shot_type)
            spec = CinematicShotSpec(
                shot_number=i,
                coverage_pattern=coverage_pattern,
                shot_type=shot_type,
                coverage_role=role,
                beat_type=beat,
                dramatic_function=func,
                edit_role=role,
                camera_angle=camera_angle,
                lens_suggestion=lens,
                movement=movement,
                priority=priority,
                cinematic_grammar_version="v0.1",
            )
            shots.append(spec)
        shots = self._apply_prompt_intents(shots, scene_text)
        shots = self.apply_continuity_notes(shots)
        char_names = character_names if character_names else self._extract_character_names(scene_text)
        shots = self._apply_visual_raccord(shots, scene_text, char_names)
        shots = self.assign_priorities(shots)
        rules = _CONTINUITY_RULES_BY_PATTERN.get(coverage_pattern, [])
        return OrderedShotPlan(
            scene_type=scene_type,
            coverage_pattern=coverage_pattern,
            shots=shots,
            continuity_rules=rules,
            cinematic_grammar_version="v0.1",
        )

    def _suggest_camera(
        self,
        shot_type: CinematicShotType,
        role: EditorialRole,
        func: CinematicFunction,
    ) -> tuple[str, str]:
        if role == EditorialRole.POV:
            return "subjetivo", "handheld"
        if role == EditorialRole.THREAT_INDICATOR:
            return "contrapicado", "travelling_lento"
        if role == EditorialRole.REACTION:
            return "frontal", "static"
        if func == CinematicFunction.ACTION_BEAT:
            return "normal", "seguimiento"
        if func == CinematicFunction.ESTABLISH_CONTEXT:
            return "cenital", "static"
        if func == CinematicFunction.SOUND_FOCUS:
            return "detalle", "static"
        if shot_type in (CinematicShotType.CLOSE_UP, CinematicShotType.EXTREME_CLOSE_UP):
            return "frontal", "static"
        return "normal", "static"

    def _suggest_lens(self, shot_type: CinematicShotType) -> str:
        lens_map: dict[CinematicShotType, str] = {
            CinematicShotType.EXTREME_LONG_SHOT: "gran angular 18mm",
            CinematicShotType.LONG_SHOT: "gran angular 24mm",
            CinematicShotType.MEDIUM_LONG_SHOT: "35mm",
            CinematicShotType.MEDIUM_SHOT: "50mm",
            CinematicShotType.MEDIUM_CLOSE_UP: "85mm",
            CinematicShotType.CLOSE_UP: "100mm",
            CinematicShotType.EXTREME_CLOSE_UP: "macro 100mm",
            CinematicShotType.POV: "35mm",
            CinematicShotType.OVER_THE_SHOULDER: "85mm",
            CinematicShotType.INSERT: "macro 100mm",
            CinematicShotType.TWO_SHOT: "50mm",
            CinematicShotType.LOW_ANGLE: "gran angular 24mm",
            CinematicShotType.HIGH_ANGLE: "35mm",
            CinematicShotType.DUTCH_ANGLE: "24mm",
            CinematicShotType.AERIAL: "tele 200mm",
        }
        return lens_map.get(shot_type, "50mm")

    def _apply_prompt_intents(
        self, shots: list[CinematicShotSpec], scene_text: str
    ) -> list[CinematicShotSpec]:
        lower = scene_text.lower()
        result: list[CinematicShotSpec] = []
        for shot in shots:
            intent: str | None = None
            if shot.beat_type == BeatType.DIALOGUE and shot.shot_type == CinematicShotType.MEDIUM_CLOSE_UP:
                intent = "Personaje se detiene y pregunta — tensión contenida"
            elif shot.coverage_role == EditorialRole.THREAT_INDICATOR:
                if "sombra" in lower:
                    intent = "Sombra que cruza al fondo del pasillo — amenaza difusa"
                elif "figura" in lower or "silueta" in lower:
                    intent = "Figura que aparece al fondo — presencia inquietante"
                else:
                    intent = "Indicador de amenaza al fondo"
            elif shot.coverage_role == EditorialRole.POV:
                if "linterna" in lower:
                    intent = "Punto de vista de Marta — haz de linterna explorando la oscuridad"
                else:
                    intent = "Punto de vista del personaje explorando"
            elif shot.coverage_role == EditorialRole.SOUND_DETAIL:
                if "cruje" in lower:
                    intent = "Detalle del sonido — el suelo cruje bajo los pies"
                elif "silencio" in lower:
                    intent = "Atmósfera de silencio absoluto"
                else:
                    intent = "Detalle sonoro del entorno"
            elif shot.coverage_role == EditorialRole.REACTION:
                intent = "Reacción de Marta — se queda quieta, tensión creciente"
            updated = shot.model_copy(update={"prompt_intent": intent})
            result.append(updated)
        return result

    def apply_continuity_notes(self, shots: list[CinematicShotSpec]) -> list[CinematicShotSpec]:
        result: list[CinematicShotSpec] = []
        for i, shot in enumerate(shots):
            note_parts: list[str] = []
            eyeline: str | None = None
            raccord: str | None = None
            if shot.coverage_role == EditorialRole.REACTION:
                note_parts.append("Reacción a estímulo previo")
            if shot.coverage_role == EditorialRole.POV:
                note_parts.append("Punto de vista del personaje — mismo eje que plano anterior")
                eyeline = "Mirar hacia el estímulo — eje de mirada respetado"
            if shot.coverage_role == EditorialRole.SOUND_DETAIL:
                note_parts.append("Sincronizar sonido con imagen — corte por sonido")
            if shot.dramatic_function == CinematicFunction.ACTION_BEAT and i > 0:
                note_parts.append("Empalmar por movimiento — match on action")
            if shot.coverage_role == EditorialRole.ESTABLISHING:
                note_parts.append("Plano general de contexto — corte directo")
            if shot.coverage_role == EditorialRole.CLOSING:
                note_parts.append("Plano de cierre — disolver o corte directo")
            if shot.shot_type == CinematicShotType.DUTCH_ANGLE:
                note_parts.append("Ángulo holandés para desorientación")
            if shot.coverage_role == EditorialRole.THREAT_INDICATOR:
                note_parts.append("Indicador de amenaza — valor de aislamiento")
            if i > 0 and shots[i - 1].coverage_role == EditorialRole.POV:
                note_parts.append("Vuelta a plano objetivo tras POV")
                raccord = "Raccord de mirada — mantener dirección de mirada"
            if i > 0 and shots[i - 1].shot_type in (
                CinematicShotType.CLOSE_UP, CinematicShotType.EXTREME_CLOSE_UP
            ) and shot.shot_type in (
                CinematicShotType.LONG_SHOT, CinematicShotType.MEDIUM_SHOT
            ):
                raccord = "Raccord de posición — reubicar espacialmente tras primer plano"
            continuity = "; ".join(note_parts) if note_parts else None
            updated = shot.model_copy(update={
                "continuity_note": continuity,
                "eyeline_note": eyeline,
                "raccord_note": raccord,
            })
            result.append(updated)
        return result

    def assign_priorities(self, shots: list[CinematicShotSpec]) -> list[CinematicShotSpec]:
        return shots

    def plan_scene_coverage(self, request: CinematicGrammarRequest) -> CinematicGrammarResult:
        scene_type = (
            request.scene_type_hint
            if request.scene_type_hint
            else self.detect_scene_type(request.scene_text)
        )
        _, confidence = self.detect_scene_type_and_confidence(request.scene_text)
        coverage_pattern = self.select_coverage_pattern(scene_type)
        plan = self.build_ordered_shot_plan(request.scene_text, coverage_pattern, character_names=request.character_names)
        return CinematicGrammarResult(
            plan=plan,
            scene_text=request.scene_text,
            detected_scene_type=scene_type,
            confidence=confidence,
            cinematic_grammar_version="v0.1",
        )


cinematic_grammar_engine = CinematicShotGrammarEngine()
