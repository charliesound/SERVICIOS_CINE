from __future__ import annotations

from schemas.cid_script_to_prompt_schema import (
    CinematicIntent,
    DirectorialIntent,
    DirectorLensDecision,
    ScriptScene,
)
from services.director_lens_service import director_lens_service


class DirectorialIntentService:
    def build_directorial_intent(
        self,
        scene: ScriptScene,
        cinematic_intent: CinematicIntent | None,
        lens_decision: DirectorLensDecision,
    ) -> DirectorialIntent:
        profile = director_lens_service.get_profile(lens_decision.selected_lens_id)
        subject = cinematic_intent.subject if cinematic_intent else (scene.characters[0] if scene.characters else scene.location or "the scene subject")
        dramatic_goal = cinematic_intent.dramatic_intent if cinematic_intent else (scene.dramatic_objective or "advance the dramatic beat")
        mood = cinematic_intent.mood if cinematic_intent else (scene.emotional_tone or "focused tension")
        location = scene.location or "the primary location"
        time_of_day = scene.time_of_day or "unspecified time"

        mise_en_scene = (
            f"{subject} is staged inside {location.lower()} at {time_of_day.lower()}, with props and spatial cues supporting {dramatic_goal}; "
            f"the set must reveal {mood} through controlled placement, readable layers and narrative objects rather than abstract atmosphere."
        )
        blocking = (
            f"Blocking should prioritize {subject} in relation to key props and secondary characters, keeping emotional distance or pressure visible; "
            f"use {profile.framing_bias[0] if profile.framing_bias else 'clear spatial hierarchy'} and maintain continuity of table, papers, screens or environmental anchors when present."
        )
        camera_strategy = (
            f"Camera strategy should follow {', '.join(profile.camera_movement_bias[:2]) or 'motivated movement'} while preserving {cinematic_intent.framing if cinematic_intent else 'scene clarity'}; "
            f"the frame must reveal story information before style flourish."
        )
        suspense_or_emotion_strategy = (
            f"Primary emotional strategy: {profile.emotional_strategy[0] if profile.emotional_strategy else 'make the dramatic pressure legible'}; "
            f"shape tension or feeling through offscreen implication, proximity, pause, or human reaction depending on the scene need."
        )
        visual_metaphor = self._visual_metaphor(scene, lens_decision)
        subtext_strategy = self._subtext_strategy(scene, lens_decision)
        rhythm_strategy = (
            f"Rhythm should follow {', '.join(profile.rhythm_bias[:2]) or 'measured escalation'} and editorially preserve the scene's dramatic turn without flattening subtext."
        )
        performance_notes = (
            f"Performance should stay grounded and cinematic: keep gestures specific, eyes and pauses meaningful, and let the body language reveal {scene.conflict or mood}."
        )
        editorial_notes = (
            f"Editorially the scene should cut or hold according to {profile.narrative_strategy[0] if profile.narrative_strategy else 'narrative clarity'}; "
            f"prefer readable progression over decorative fragmentation."
        )
        prompt_guidance = self._prompt_guidance(scene, cinematic_intent, profile, lens_decision)
        coverage_strategy = self._coverage_strategy(scene, cinematic_intent)
        edit_sensitive_prompt_guidance = self._edit_sensitive_guidance(scene, cinematic_intent)

        return DirectorialIntent(
            scene_id=scene.scene_id,
            director_lens=lens_decision,
            mise_en_scene=mise_en_scene,
            blocking=blocking,
            camera_strategy=camera_strategy,
            suspense_or_emotion_strategy=suspense_or_emotion_strategy,
            visual_metaphor=visual_metaphor,
            subtext_strategy=subtext_strategy,
            rhythm_strategy=rhythm_strategy,
            performance_notes=performance_notes,
            editorial_notes=editorial_notes,
            montage_notes="pending montage intelligence enrichment",
            coverage_strategy=coverage_strategy,
            edit_sensitive_prompt_guidance=edit_sensitive_prompt_guidance,
            prompt_guidance=prompt_guidance,
        )

    def _visual_metaphor(self, scene: ScriptScene, lens_decision: DirectorLensDecision) -> str | None:
        text = f"{scene.action_summary} {scene.dialogue_summary or ''}".lower()
        if "storyboard" in text and any(word in text for word in ["decision", "version", "respira"]):
            return "the distance between characters and materials becomes a metaphor for unresolved creative pressure"
        if lens_decision.selected_lens_id == "formal_symmetry_control":
            return "perfect order in the space suggests emotional fracture beneath the surface"
        if lens_decision.selected_lens_id == "urban_moral_energy":
            return "the city or room geometry traps the character inside moral velocity"
        return None

    def _subtext_strategy(self, scene: ScriptScene, lens_decision: DirectorLensDecision) -> str | None:
        if scene.conflict:
            return f"Subtext should appear through spatial tension, withheld reaction and controlled composition rather than explicit explanation; lens mode {lens_decision.selected_lens_id} should reinforce pressure without overstatement."
        return None

    def _prompt_guidance(
        self,
        scene: ScriptScene,
        cinematic_intent: CinematicIntent | None,
        profile,
        lens_decision: DirectorLensDecision,
    ) -> list[str]:
        guidance = [
            f"apply_principle:{principle}" for principle in profile.cinematic_principles[:4]
        ]
        guidance.extend(
            [
                f"framing_bias:{value}" for value in profile.framing_bias[:2]
            ]
        )
        if cinematic_intent:
            guidance.append(f"camera_strategy:{cinematic_intent.framing}")
            guidance.append(f"lighting_strategy:{cinematic_intent.lighting}")
            guidance.append(f"composition_strategy:{cinematic_intent.composition}")
        guidance.append(f"lens_selection_reason:{lens_decision.reason}")
        if scene.characters:
            guidance.append("preserve_character_relationships")
        if scene.location:
            guidance.append("preserve_location_logic")
        return guidance

    def _coverage_strategy(self, scene: ScriptScene, cinematic_intent: CinematicIntent | None) -> list[str]:
        strategies = ["master shot for geography", "reaction coverage for emotional pivots"]
        if scene.characters and len(scene.characters) >= 2:
            strategies.append("eyeline-compatible counter coverage")
        if cinematic_intent and cinematic_intent.output_type in {"storyboard_frame", "storyboard_board"}:
            strategies.append("panel-to-panel continuity coverage")
        return strategies

    def _edit_sensitive_guidance(self, scene: ScriptScene, cinematic_intent: CinematicIntent | None) -> list[str]:
        guidance = [
            "prepare a readable cut to the next emotional beat",
            "reserve part of the information for the following shot when tension is unresolved",
        ]
        if scene.dialogue_summary:
            guidance.append("hold reaction space for editorial punctuation")
        if cinematic_intent and cinematic_intent.output_type == "controlled_frame_generation":
            guidance.append("show process order clearly so editorial logic remains visible")
        return guidance


directorial_intent_service = DirectorialIntentService()
