from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from schemas.cid_script_to_prompt_schema import (
    CinematicIntent,
    DirectorialIntent,
    EditorialBeat,
    MontageIntent,
    ScriptScene,
    ShotEditorialPurpose,
)


ROOT = Path(__file__).resolve().parents[1]
MONTAGE_RULES_PATH = ROOT / "config" / "cid_montage_principles.yaml"


class MontageIntelligenceService:
    def __init__(self) -> None:
        self._profiles_cache: list[dict[str, Any]] | None = None

    def list_profiles(self) -> list[dict]:
        return list(self._load_profiles())

    def choose_montage_profile(
        self,
        scene: ScriptScene,
        directorial_intent: DirectorialIntent | None = None,
        requested_profile_id: str | None = "adaptive_montage",
    ) -> str:
        requested = requested_profile_id or "adaptive_montage"
        if requested != "adaptive_montage":
            self._get_profile(requested)
            return requested

        text = f"{scene.heading} {scene.action_summary} {scene.dialogue_summary or ''} {scene.conflict or ''} {scene.emotional_tone or ''}"
        lowered = text.lower()
        directorial_text = ""
        if directorial_intent:
            directorial_text = f" {directorial_intent.camera_strategy} {directorial_intent.suspense_or_emotion_strategy} {directorial_intent.rhythm_strategy}".lower()
            lowered += directorial_text

        if any(word in lowered for word in ["amenaza", "secreto", "misterio", "threat", "investiga", "oculta"]):
            return "suspense_information_control"
        if any(word in lowered for word in ["ruido", "puerta", "sombra", "oculto", "hidden_threat", "amenaza"]):
            return "suspense_information_control"
        if any(word in lowered for word in ["culpa", "paranoia", "memoria", "sueño", "sueno", "identidad", "fractura"]):
            return "psychological_fragmentation"
        if any(word in lowered for word in ["persec", "pelea", "huye", "corre", "golpe", "impacto", "accion", "acción"]):
            return "action_spatial_clarity"
        if any(word in lowered for word in ["duelo", "soledad", "silencio", "observa", "contempla", "grief_observation"]) and not scene.dialogue_summary:
            return "contemplative_long_take"
        if any(word in lowered for word in ["simbolo", "símbolo", "recuerdo", "memoria", "poetica", "poética", "epilogo", "prólogo", "prologo"]):
            return "poetic_associative_montage"
        if any(word in lowered for word in ["discute", "negocia", "negoci", "decision", "reunion", "reunión", "version"]):
            return "rhythmic_dialogue_pressure"
        return "invisible_continuity_editing"

    def build_editorial_beats(self, scene: ScriptScene) -> list[EditorialBeat]:
        beats: list[EditorialBeat] = []
        start_state = scene.emotional_tone or "focused"
        beats.append(
            EditorialBeat(
                beat_id=f"{scene.scene_id}_beat_01",
                scene_id=scene.scene_id,
                beat_order=1,
                dramatic_function="establish dramatic situation",
                emotional_state_start=start_state,
                emotional_state_end=start_state,
                information_revealed=[scene.location or scene.heading, scene.action_summary],
                tension_change="baseline established",
                suggested_shot_count=1,
                suggested_duration_seconds=3.0,
            )
        )
        if scene.dialogue_summary or scene.conflict:
            beats.append(
                EditorialBeat(
                    beat_id=f"{scene.scene_id}_beat_02",
                    scene_id=scene.scene_id,
                    beat_order=2,
                    dramatic_function="pressure the decision or emotional conflict",
                    emotional_state_start=start_state,
                    emotional_state_end=scene.conflict or "heightened tension",
                    information_revealed=[scene.dialogue_summary or scene.conflict or "reaction"],
                    tension_change="rises",
                    suggested_shot_count=2,
                    suggested_duration_seconds=2.4,
                )
            )
        if any(keyword in (scene.action_summary or "").lower() for keyword in ["decisi", "revisa", "respira", "otra version", "otra versión"]):
            beats.append(
                EditorialBeat(
                    beat_id=f"{scene.scene_id}_beat_03",
                    scene_id=scene.scene_id,
                    beat_order=3,
                    dramatic_function="prepare reveal or next editorial cut",
                    emotional_state_start=scene.conflict or start_state,
                    emotional_state_end="suspended resolution",
                    information_revealed=["decision withheld", "next visual detail prepared"],
                    tension_change="held before release",
                    suggested_shot_count=1,
                    suggested_duration_seconds=2.0,
                )
            )
        return beats

    def build_montage_intent(
        self,
        scene: ScriptScene,
        cinematic_intent: CinematicIntent | None,
        directorial_intent: DirectorialIntent | None,
        requested_profile_id: str | None = "adaptive_montage",
    ) -> MontageIntent:
        profile_id = self.choose_montage_profile(scene, directorial_intent, requested_profile_id)
        profile = self._get_profile(profile_id)
        rhythm = ", ".join(profile.get("rhythm_bias", [])[:2]) or "adaptive pacing"
        transition_strategy = ", ".join(profile.get("transition_bias", [])[:2]) or "motivated transition"
        coverage_requirements = list(profile.get("coverage_bias", []))
        sound_bias = list(profile.get("sound_bias", []))
        beats = self.build_editorial_beats(scene)
        cutting_pattern = self._cutting_pattern(profile_id, scene)
        editorial_function = self._editorial_function(scene, profile_id)
        continuity_strategy = self._continuity_strategy(scene, profile_id)
        eyeline_strategy = self._eyeline_strategy(scene, profile_id)
        sound_bridge_strategy = sound_bias[0] if sound_bias else None
        emotional_cut_points = [beat.emotional_state_end for beat in beats]
        reveal_points = [item for beat in beats for item in beat.information_revealed[:1]]
        shots_to_avoid = list(profile.get("forbidden_cliches", []))

        return MontageIntent(
            scene_id=scene.scene_id,
            sequence_id=None,
            editorial_function=editorial_function,
            rhythm=rhythm,
            average_shot_duration=self._average_shot_duration(profile_id),
            cutting_pattern=cutting_pattern,
            transition_strategy=transition_strategy,
            continuity_strategy=continuity_strategy,
            eyeline_strategy=eyeline_strategy,
            sound_bridge_strategy=sound_bridge_strategy,
            emotional_cut_points=emotional_cut_points,
            reveal_points=reveal_points,
            coverage_requirements=coverage_requirements,
            shots_to_avoid=shots_to_avoid,
            editorial_notes=self._editorial_notes(scene, profile_id, directorial_intent),
        )

    def build_shot_editorial_purpose(
        self,
        scene: ScriptScene,
        shot_order: int,
        shot_type: str,
        montage_intent: MontageIntent,
        previous_shot_type: str | None = None,
        next_shot_type: str | None = None,
    ) -> ShotEditorialPurpose:
        purpose = self._shot_purpose(scene, shot_order, shot_type, montage_intent)
        return ShotEditorialPurpose(
            shot_id=f"{scene.scene_id}_shot_{shot_order:02d}",
            scene_id=scene.scene_id,
            shot_order=shot_order,
            shot_type=shot_type,
            purpose=purpose,
            previous_shot_relationship=previous_shot_type or "starts the current editorial beat",
            next_shot_relationship=next_shot_type or "prepares the next reveal or reaction",
            cut_reason=self._cut_reason(scene, shot_order, montage_intent),
            estimated_duration_seconds=self._estimated_duration_seconds(montage_intent, shot_order),
            sound_continuity=montage_intent.sound_bridge_strategy or "maintain room tone continuity",
            visual_continuity=montage_intent.continuity_strategy,
            emotional_continuity=f"carry {scene.emotional_tone or 'scene tension'} into the next beat",
        )

    def _load_profiles(self) -> list[dict[str, Any]]:
        if self._profiles_cache is None:
            with MONTAGE_RULES_PATH.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
            self._profiles_cache = list(payload.get("profiles", [])) if isinstance(payload, dict) else []
        return self._profiles_cache

    def _get_profile(self, profile_id: str) -> dict[str, Any]:
        for profile in self._load_profiles():
            if profile.get("profile_id") == profile_id:
                return profile
        raise ValueError(f"Unknown montage profile: {profile_id}")

    def _cutting_pattern(self, profile_id: str, scene: ScriptScene) -> str:
        if profile_id == "rhythmic_dialogue_pressure":
            return "alternate intention-based cuts with held reactions and silence punctuation"
        if profile_id == "suspense_information_control":
            return "delay cuts until new threat or information enters the frame"
        if profile_id == "psychological_fragmentation":
            return "controlled discontinuity with subjective jumps and perceptual emphasis"
        if profile_id == "action_spatial_clarity":
            return "establish geography first, then cut on directional movement and impact"
        if profile_id == "contemplative_long_take":
            return "minimal cuts, holding until emotion shifts inside the frame"
        if profile_id == "poetic_associative_montage":
            return "associate images through idea, color, texture and sound bridge"
        return f"maintain readable continuity while supporting {scene.dramatic_objective or 'narrative clarity'}"

    def _editorial_function(self, scene: ScriptScene, profile_id: str) -> str:
        if profile_id == "rhythmic_dialogue_pressure":
            return "shape power exchange through reactions, pauses and escalating intent"
        if profile_id == "suspense_information_control":
            return "control reveal and withhold information until pressure peaks"
        if profile_id == "psychological_fragmentation":
            return "mirror unstable perception and fractured interiority"
        if profile_id == "action_spatial_clarity":
            return "keep physical orientation readable while intensifying impact"
        if profile_id == "contemplative_long_take":
            return "let duration carry emotion and tension without overcutting"
        if profile_id == "poetic_associative_montage":
            return "build emotional or symbolic linkage through associative editorial logic"
        return "support clean dramatic progression and intelligible scene coverage"

    def _continuity_strategy(self, scene: ScriptScene, profile_id: str) -> str:
        if profile_id == "action_spatial_clarity":
            return "protect axis, direction of movement and geography across cuts"
        if profile_id == "psychological_fragmentation":
            return "break literal continuity only when tied to subjective perception"
        if scene.characters:
            return "maintain eyeline, emotional and prop continuity between character reactions"
        return "maintain spatial and tonal continuity between editorial beats"

    def _eyeline_strategy(self, scene: ScriptScene, profile_id: str) -> str:
        if profile_id == "suspense_information_control":
            return "use eyelines to delay what the viewer can fully see"
        if profile_id == "rhythmic_dialogue_pressure":
            return "alternate eyeline matches with held reaction cuts"
        return "preserve readable eyeline continuity across the sequence"

    def _editorial_notes(self, scene: ScriptScene, profile_id: str, directorial_intent: DirectorialIntent | None) -> str:
        notes = [
            f"profile {profile_id} should keep the scene readable while serving {scene.dramatic_objective or 'the dramatic turn'}",
            "coverage exists to support the cut, not as decorative redundancy",
        ]
        if directorial_intent is not None:
            notes.append(f"directorial rhythm cue: {directorial_intent.rhythm_strategy}")
        return "; ".join(notes)

    def _average_shot_duration(self, profile_id: str) -> str:
        mapping = {
            "rhythmic_dialogue_pressure": "2-4 seconds with strategic holds on reactions",
            "suspense_information_control": "3-6 seconds with withheld release",
            "psychological_fragmentation": "variable and perception-driven",
            "action_spatial_clarity": "1-3 seconds after orientation is established",
            "contemplative_long_take": "6-12 seconds or longer when emotion has not shifted",
            "poetic_associative_montage": "2-5 seconds depending on symbolic resonance",
            "invisible_continuity_editing": "3-5 seconds with motivated continuity",
        }
        return mapping.get(profile_id, "adaptive to dramatic need")

    def _shot_purpose(self, scene: ScriptScene, shot_order: int, shot_type: str, montage_intent: MontageIntent) -> str:
        if shot_order == 1:
            return f"establish the scene function and prepare {montage_intent.reveal_points[0] if montage_intent.reveal_points else 'the next reveal'}"
        return f"advance {montage_intent.editorial_function} through {shot_type} emphasis"

    def _cut_reason(self, scene: ScriptScene, shot_order: int, montage_intent: MontageIntent) -> str:
        if shot_order == 1:
            return f"cut when the audience has enough context and the next shot can sharpen {scene.conflict or scene.dramatic_objective or 'the tension'}"
        return f"cut to increase clarity around {montage_intent.editorial_function}"

    def _estimated_duration_seconds(self, montage_intent: MontageIntent, shot_order: int) -> float | None:
        if "6-12" in montage_intent.average_shot_duration:
            return 7.5 if shot_order == 1 else 6.0
        if "1-3" in montage_intent.average_shot_duration:
            return 2.0
        if "2-4" in montage_intent.average_shot_duration:
            return 3.0
        if "3-6" in montage_intent.average_shot_duration:
            return 4.0
        if "2-5" in montage_intent.average_shot_duration:
            return 3.5
        return 3.0


montage_intelligence_service = MontageIntelligenceService()
