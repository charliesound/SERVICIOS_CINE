from __future__ import annotations

import re
from typing import Any

from schemas.cid_script_to_prompt_schema import ScriptScene

BEAT_PATTERNS: list[dict[str, Any]] = [
    {
        "type": "character_entry",
        "patterns": [r"\bentra\b", r"\bentra\s+(?:en|por|a)\b", r"\bentering\b", r"\benters?\b", r"\b(?:viene|llega|appears?|enters?|comes?\s+in)\b"],
        "shot_type": "MS",
        "priority": 1,
    },
    {
        "type": "character_exit",
        "patterns": [r"\bsale\b", r"\bsale\s+(?:de|por|corriendo)\b", r"\bexits?\b", r"\bruns?\s+out\b", r"\b(?:escapa|huye|flee|escape)\b"],
        "shot_type": "MS",
        "priority": 1,
    },
    {
        "type": "sound_detail",
        "patterns": [r"\bcruje\b", r"\bcrujido\b", r"\bcreaks?\b", r"\bsound\b", r"\bruido\b", r"\b(?:silencio|silence|quiet|calm)\b", r"\bparpadea\b", r"\bflickers?\b"],
        "shot_type": "CU",
        "priority": 2,
    },
    {
        "type": "dialogue",
        "patterns": [r"¿.*\?", r"\".*?\"", r"\bdice\b", r"\bpregunta\b", r"\b(?:says?|asks?|whispers?|yells?|shouts?|murmurs?)\b"],
        "shot_type": "OTS",
        "priority": 1,
    },
    {
        "type": "reaction_closeup",
        "patterns": [r"\b(?:terror|miedo|susto|paralizad[ao]|quieta|quieto|frozen|terrified|scared|shocked|surprised)\b", r"\bse\s+queda\s+(?:quieta|quieto|inmóvil|paralizad[ao])\b"],
        "shot_type": "CU",
        "priority": 2,
    },
    {
        "type": "shadow_reveal",
        "patterns": [r"\bsombra\b", r"\b(?:shadow|figure|silhouette|shape|oscur)\b", r"\b(?:cruza|aparece|crosses?|appears?)\b"],
        "shot_type": "WS",
        "priority": 2,
    },
    {
        "type": "action_physical",
        "patterns": [r"\bcorre\b", r"\bcamina\b", r"\b(?:runs?|walks?|moves?|steps?|approaches?)\b", r"\blinterna\b", r"\b(?:flashlight|lantern|torch)\b"],
        "shot_type": "TRACKING",
        "priority": 1,
    },
    {
        "type": "reverse_angle",
        "patterns": [r"\bcontraplano\b", r"\b(?:over\s+shoulder|reverse|from\s+behind)\b"],
        "shot_type": "OTS",
        "priority": 3,
    },
    {
        "type": "detail_object",
        "patterns": [r"\bdetalle\b", r"\b(?:close[- ]?up|detail|macro)\b", r"\b(?:suelo|floor|ground|door|puerta|window|ventana)\b"],
        "shot_type": "CU",
        "priority": 2,
    },
    {
        "type": "figure_reveal",
        "patterns": [r"\bfigura\b", r"\b(?:figure|apparition|presence|silueta)\b"],
        "shot_type": "WS",
        "priority": 2,
    },
    {
        "type": "establishing",
        "patterns": [r"\bestablecimient", r"\bwide\s+shot\b", r"\b(?:establish|exterior|exterior|panoramic)\b"],
        "shot_type": "WS",
        "priority": 3,
    },
    {
        "type": "suspense_build",
        "patterns": [r"\btensión\b", r"\btension\b", r"\b(?:suspense|ominous|dread|amenaza)\b"],
        "shot_type": "MS",
        "priority": 2,
    },
]

MIN_SHOTS_DYNAMIC: dict[str, int] = {
    "very_short": 3,
    "dialogue_action_threat": 5,
    "chase_exit_reveal": 4,
    "default": 3,
}

LENS_OPTIONS = ["35mm", "50mm", "85mm", "macro", "24mm", "100mm"]

CAMERA_ANGLES = ["frontal", "lateral", "low angle", "high angle", "over shoulder", "eye level", "dutch angle"]


class StoryboardShotPlannerService:

    def plan_sequence_shots(
        self,
        scene: ScriptScene,
        *,
        mode: str = "auto_cinematic",
        manual_count: int | None = None,
        previous_scene: ScriptScene | None = None,
    ) -> list[dict[str, Any]]:
        raw_text = (scene.raw_text or "") + " " + (scene.action_summary or "")
        raw_text = raw_text.lower()

        beats: list[dict[str, Any]] = []
        matched_types: set[str] = set()

        analysis_beat_map: dict[str, str] = {
            "visual_beats": "character_entry",
            "sound_beats": "sound_detail",
            "dialogue_beats": "dialogue",
            "reaction_beats": "reaction_closeup",
            "threat_beats": "shadow_reveal",
            "object_beats": "detail_object",
        }

        for field_name, beat_type in analysis_beat_map.items():
            items = getattr(scene, field_name, None) or []
            if items and beat_type not in matched_types:
                for beat_def in BEAT_PATTERNS:
                    if beat_def["type"] == beat_type:
                        beats.append(beat_def)
                        matched_types.add(beat_type)
                        break

        suggested = getattr(scene, "suggested_coverage", None) or []
        if suggested and not beats:
            for coverage_item in suggested:
                coverage_lower = coverage_item.lower()
                for beat_def in BEAT_PATTERNS:
                    for pattern in beat_def["patterns"]:
                        if re.search(pattern, coverage_lower, re.IGNORECASE):
                            if beat_def["type"] not in matched_types:
                                beats.append(beat_def)
                                matched_types.add(beat_def["type"])
                            break

        for beat_def in BEAT_PATTERNS:
            if beat_def["type"] in matched_types:
                continue
            for pattern in beat_def["patterns"]:
                if re.search(pattern, raw_text, re.IGNORECASE):
                    beats.append(beat_def)
                    matched_types.add(beat_def["type"])
                    break

        beats.sort(key=lambda b: b["priority"])

        if mode == "minimal":
            target = 2
        elif mode == "manual_count" and manual_count is not None:
            target = max(1, manual_count)
        else:
            target = self._dynamic_shot_count(scene, beats, raw_text)

        shots: list[dict[str, Any]] = []
        scene_text = scene.raw_text or ""
        action_summary = scene.action_summary or ""
        dialogue_text = scene.dialogue_summary or ""

        for i in range(target):
            beat = beats[i % len(beats)] if beats else BEAT_PATTERNS[0]
            shot = self._build_shot(
                beat=beat,
                index=i,
                target=target,
                scene=scene,
                scene_text=scene_text,
                action_summary=action_summary,
                dialogue_text=dialogue_text,
                total_beats=len(beats),
            )
            shots.append(shot)

        if len(shots) < target:
            remaining = target - len(shots)
            for i in range(remaining):
                idx = len(shots)
                beat = {
                    "type": "action_physical",
                    "patterns": [],
                    "shot_type": "MS",
                    "priority": 4,
                }
                shot = self._build_shot(
                    beat=beat,
                    index=idx,
                    target=target,
                    scene=scene,
                    scene_text=scene_text,
                    action_summary=action_summary,
                    dialogue_text=dialogue_text,
                    total_beats=len(beats),
                )
                shots.append(shot)

        return shots

    def _dynamic_shot_count(self, scene: ScriptScene, beats: list[dict[str, Any]], raw_text: str) -> int:
        beat_types = {b["type"] for b in beats}

        has_dialogue = "dialogue" in beat_types
        has_action = "action_physical" in beat_types or "character_entry" in beat_types
        has_threat = "shadow_reveal" in beat_types or "suspense_build" in beat_types or "figure_reveal" in beat_types

        if has_dialogue and has_action and has_threat:
            return 5
        if has_threat and ("character_exit" in beat_types or "action_physical" in beat_types):
            return 4
        if has_action and has_dialogue:
            return 4
        if len(beats) >= 4:
            return len(beats)
        if len(beats) >= 2:
            return max(3, len(beats) + 1)
        return 3

    def _build_shot(
        self,
        beat: dict[str, Any],
        index: int,
        target: int,
        scene: ScriptScene,
        scene_text: str,
        action_summary: str,
        dialogue_text: str,
        total_beats: int,
    ) -> dict[str, Any]:
        beat_type = beat["type"]
        shot_type = beat["shot_type"]

        lens_idx = index % len(LENS_OPTIONS)
        angle_idx = (index + 1) % len(CAMERA_ANGLES)

        if total_beats > 1 and index < total_beats:
            shot_type = beat["shot_type"]
        elif index == 0:
            shot_type = "WS"
        elif index == target - 1:
            shot_type = "CU"
        else:
            shot_type = "MS"

        dramatic_intent_map: dict[str, str] = {
            "character_entry": "Establish character presence in the space",
            "character_exit": "Show character departure or escape",
            "sound_detail": "Emphasize diegetic sound for tension",
            "dialogue": "Capture character dialogue and reaction",
            "reaction_closeup": "Reveal character emotional response",
            "shadow_reveal": "Build suspense through off-screen threat",
            "action_physical": "Show physical movement through space",
            "reverse_angle": "Provide counter-angle for dramatic emphasis",
            "detail_object": "Highlight significant prop or texture",
            "figure_reveal": "Reveal threatening figure or presence",
            "establishing": "Establish location and spatial context",
            "suspense_build": "Build atmospheric tension",
        }

        dramatic_intent_es_map: dict[str, str] = {
            "character_entry": "Presentar al personaje en el espacio",
            "character_exit": "Mostrar la salida o huida del personaje",
            "sound_detail": "Enfatizar sonido diegético para tensión",
            "dialogue": "Capturar el diálogo y reacción del personaje",
            "reaction_closeup": "Revelar la respuesta emocional del personaje",
            "shadow_reveal": "Construir suspense con amenaza fuera de campo",
            "action_physical": "Mostrar movimiento físico por el espacio",
            "reverse_angle": "Ofrecer contraplano para énfasis dramático",
            "detail_object": "Destacar objeto significativo o textura",
            "figure_reveal": "Revelar figura o presencia amenazante",
            "establishing": "Establecer localización y contexto espacial",
            "suspense_build": "Construir tensión atmosférica",
        }

        continuity_notes: list[str] = []
        if scene.location:
            continuity_notes.append(f"location:{scene.location}")
        if scene.time_of_day:
            continuity_notes.append(f"time:{scene.time_of_day}")
        if scene.int_ext:
            continuity_notes.append(f"setting:{scene.int_ext}")

        prompt_description = self._build_prompt_description(
            scene, beat_type, action_summary, scene_text, index, target
        )

        return {
            "shot_number": index + 1,
            "shot_type": shot_type,
            "beat_type": beat_type,
            "camera_angle": CAMERA_ANGLES[angle_idx],
            "lens": LENS_OPTIONS[lens_idx],
            "visual_action": prompt_description,
            "dramatic_intent": dramatic_intent_map.get(beat_type, ""),
            "dramatic_intent_es": dramatic_intent_es_map.get(beat_type, ""),
            "sound_or_silence_note": self._sound_note(beat_type, scene_text),
            "script_reference": scene_text[:200] if scene_text else "",
            "continuity_notes": "; ".join(continuity_notes),
            "prompt_safe_description_en": prompt_description,
            "prompt_safe_description_es": self._translate_description(prompt_description),
            "display_description_en": prompt_description,
            "display_description_es": self._translate_description(prompt_description),
        }

    def _build_prompt_description(
        self,
        scene: ScriptScene,
        beat_type: str,
        action_summary: str,
        scene_text: str,
        index: int,
        target: int,
    ) -> str:
        if action_summary:
            base = action_summary[:160]
        elif scene_text:
            base = scene_text[:160]
        else:
            base = "Cinematic shot"

        beat_phrases: dict[str, str] = {
            "character_entry": "Character enters location",
            "character_exit": "Character exits or flees location",
            "sound_detail": "Close-up emphasizing ambient sound detail",
            "dialogue": "Character delivering or reacting to dialogue",
            "reaction_closeup": "Extreme close-up on character's emotional reaction",
            "shadow_reveal": "Wide shot revealing shadow or off-screen movement",
            "action_physical": "Tracking physical movement through space",
            "reverse_angle": "Reverse angle from opposite perspective",
            "detail_object": "Detail shot of significant object or texture",
            "figure_reveal": "Wide shot revealing a figure or presence",
            "establishing": "Establishing shot of the location",
            "suspense_build": "Tension-building atmospheric shot",
        }

        phrase = beat_phrases.get(beat_type, "Cinematic coverage shot")
        return f"{phrase}: {base}"

    def _translate_description(self, en: str) -> str:
        translations = {
            "Character enters location": "Personaje entra en la localización",
            "Character exits or flees location": "Personaje sale o huye de la localización",
            "Close-up emphasizing ambient sound detail": "Primer plano que enfatiza detalle sonoro ambiental",
            "Character delivering or reacting to dialogue": "Personaje en diálogo o reacción",
            "Extreme close-up on character's emotional reaction": "Primer plano extremo de la reacción emocional del personaje",
            "Wide shot revealing shadow or off-screen movement": "Plano general que revela sombra o movimiento fuera de campo",
            "Tracking physical movement through space": "Traveling que sigue el movimiento físico por el espacio",
            "Reverse angle from opposite perspective": "Contraplano desde perspectiva opuesta",
            "Detail shot of significant object or texture": "Plano detalle de objeto o textura significativa",
            "Wide shot revealing a figure or presence": "Plano general que revela una figura o presencia",
            "Establishing shot of the location": "Plano de establecimiento de la localización",
            "Tension-building atmospheric shot": "Plano atmosférico de construcción de tensión",
            "Cinematic coverage shot": "Plano de cobertura cinematográfica",
        }
        for en_key, es_val in translations.items():
            if en.startswith(en_key):
                return en.replace(en_key, es_val, 1)
        return en

    def _sound_note(self, beat_type: str, scene_text: str) -> str:
        sound_text = scene_text.lower()
        if re.search(r"\bcruje\b|\bcrujido\b|\bcreaks?\b", sound_text):
            return "Sound: floor creaking — emphasize diegetic audio"
        if re.search(r"\bsilencio\b|\bsilence\b", sound_text):
            return "Silence: no ambient sound — build tension through quiet"
        if re.search(r"\bparpadea\b|\bflickers?\b", sound_text):
            return "Sound: electrical flicker — emphasize unstable light source"
        if re.search(r"\bcorre\b|\bruns?\b", sound_text):
            return "Sound: rapid footsteps — build urgency"
        if beat_type == "dialogue":
            return "Dialogue: capture voice clearly with room tone"
        return "Natural ambient sound"


storyboard_shot_planner_service = StoryboardShotPlannerService()
