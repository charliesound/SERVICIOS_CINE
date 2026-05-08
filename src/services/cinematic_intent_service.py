from __future__ import annotations

import re

from schemas.cid_script_to_prompt_schema import CinematicIntent, ScriptScene
from services.director_lens_service import director_lens_service
from services.directorial_intent_service import directorial_intent_service
from services.montage_intelligence_service import montage_intelligence_service


class CinematicIntentService:
    STYLE_PRESET = "premium_cinematic_saas"

    def build_intent(
        self,
        scene: ScriptScene,
        output_type: str,
        *,
        continuity_anchors: list[str] | None = None,
        director_lens_id: str | None = "adaptive_auteur_fusion",
        montage_profile_id: str | None = "adaptive_montage",
        allow_director_reference_names: bool = False,
    ) -> CinematicIntent:
        scene_text = f"{scene.action_summary} {scene.dialogue_summary or ''} {scene.raw_text}".lower()
        subject = self._infer_subject(scene, output_type)
        action = self._infer_action(scene, output_type)
        environment = self._infer_environment(scene)
        dramatic_intent = scene.dramatic_objective or self._infer_dramatic_intent(scene_text, output_type)
        framing, shot_size, camera_angle, lens, movement = self._infer_camera_language(scene, output_type, scene_text)
        lighting = self._infer_lighting(scene, scene_text)
        color_palette = self._infer_palette(scene, output_type)
        composition = self._infer_composition(output_type, scene, subject)
        mood = scene.emotional_tone or self._infer_mood(scene_text)
        required_elements = self._required_elements(output_type, scene)
        forbidden_elements = self._forbidden_elements(output_type, scene)
        intent = CinematicIntent(
            intent_id=f"intent_{scene.scene_id}_{output_type}",
            scene_id=scene.scene_id,
            output_type=output_type,
            subject=subject,
            action=action,
            environment=environment,
            dramatic_intent=dramatic_intent,
            framing=framing,
            shot_size=shot_size,
            camera_angle=camera_angle,
            lens=lens,
            lighting=lighting,
            color_palette=color_palette,
            composition=composition,
            movement=movement,
            mood=mood,
            continuity_anchors=continuity_anchors or scene.visual_anchors,
            required_elements=required_elements,
            forbidden_elements=forbidden_elements,
            director_lens_id=None,
            directorial_intent=None,
        )

        lens_decision = director_lens_service.choose_lens_for_scene(
            scene,
            requested_lens_id=director_lens_id,
        )
        lens_profile = director_lens_service.get_profile(lens_decision.selected_lens_id)
        directorial_intent = directorial_intent_service.build_directorial_intent(
            scene,
            intent,
            lens_decision,
        )
        montage_intent = montage_intelligence_service.build_montage_intent(
            scene,
            intent,
            directorial_intent,
            requested_profile_id=montage_profile_id,
        )
        editorial_beats = montage_intelligence_service.build_editorial_beats(scene)
        shot_editorial_purpose = montage_intelligence_service.build_shot_editorial_purpose(
            scene,
            shot_order=1,
            shot_type=intent.shot_size,
            montage_intent=montage_intent,
            previous_shot_type=None,
            next_shot_type="reaction_or_reveal",
        )
        del allow_director_reference_names

        intent.framing = self._merge_text(intent.framing, directorial_intent.camera_strategy)
        intent.lighting = self._merge_text(intent.lighting, ", ".join(lens_profile.lighting_bias[:2]))
        intent.composition = self._merge_text(intent.composition, directorial_intent.mise_en_scene)
        intent.mood = self._merge_text(intent.mood, directorial_intent.suspense_or_emotion_strategy)
        intent.continuity_anchors = list(
            dict.fromkeys(
                (intent.continuity_anchors or [])
                + directorial_intent.prompt_guidance[:4]
                + montage_intent.coverage_requirements[:3]
                + montage_intent.emotional_cut_points[:2]
            )
        )
        intent.required_elements = list(
            dict.fromkeys(
                (intent.required_elements or [])
                + ["directorial clarity", "mise en scene", "blocking logic"]
                + montage_intent.coverage_requirements
                + ["editorial function", "cut motivation"]
            )
        )
        intent.forbidden_elements = list(dict.fromkeys((intent.forbidden_elements or []) + ["director name imitation", "style of named director"]))
        intent.director_lens_id = lens_decision.selected_lens_id
        intent.directorial_intent = directorial_intent
        intent.montage_intent = montage_intent
        intent.editorial_beats = editorial_beats
        intent.shot_editorial_purpose = shot_editorial_purpose
        intent.directorial_intent.montage_notes = montage_intent.editorial_notes
        intent.directorial_intent.coverage_strategy = montage_intent.coverage_requirements
        intent.directorial_intent.edit_sensitive_prompt_guidance = list(
            dict.fromkeys(
                (intent.directorial_intent.edit_sensitive_prompt_guidance or [])
                + montage_intent.reveal_points
                + montage_intent.emotional_cut_points
                + [shot_editorial_purpose.cut_reason]
            )
        )
        intent.directorial_intent = directorial_intent

        return intent

    def _infer_subject(self, scene: ScriptScene, output_type: str) -> str:
        if output_type == "analysis_view":
            return "screenplay pages and breakdown dashboard"
        if output_type == "moodboard":
            return "character, atmosphere and art-direction reference board"
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return "storyboard panels for the scene"
        if output_type == "controlled_frame_generation":
            return "prompt preparation panel, node workflow and generated frame"
        if scene.characters:
            return ", ".join(scene.characters[:2]).lower()
        if scene.location:
            return scene.location.lower()
        return "main dramatic subject of the scene"

    def _infer_action(self, scene: ScriptScene, output_type: str) -> str:
        if output_type == "analysis_view":
            return "extracting scenes, characters, locations and production needs from the screenplay"
        if output_type == "moodboard":
            return "organizing editorial references for character, atmosphere and palette"
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return "mapping the scene into readable shot panels with camera logic"
        if output_type == "controlled_frame_generation":
            return "preparing the prompt, running generation and validating consistency"
        return self._shorten_action(scene.action_summary)

    def _infer_environment(self, scene: ScriptScene) -> str:
        int_ext = (scene.int_ext or "scene").replace("/", " and ").lower()
        location = (scene.location or "unspecified location").lower()
        time_of_day = (scene.time_of_day or "unspecified time").lower()
        return f"{int_ext} {location} at {time_of_day}"

    def _infer_dramatic_intent(self, scene_text: str, output_type: str) -> str:
        if output_type == "analysis_view":
            return "make the screenplay structure legible for creative and production teams"
        if output_type == "moodboard":
            return "lock art direction before shooting"
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return "translate dramatic beats into clear shot planning"
        if output_type == "controlled_frame_generation":
            return "show that generation is guided, reviewed and semantically controlled"
        if any(word in scene_text for word in ["espera", "decisi", "review", "revisa"]):
            return "support a moment of evaluation and narrative decision"
        if any(word in scene_text for word in ["discute", "argue", "debate"]):
            return "intensify interpersonal tension"
        return "advance the scene with cinematic clarity"

    def _infer_camera_language(self, scene: ScriptScene, output_type: str, scene_text: str) -> tuple[str, str, str, str, str | None]:
        if output_type == "analysis_view":
            return ("structured interface tableau", "medium wide", "eye level", "35mm", "subtle push-in")
        if output_type == "moodboard":
            return ("editorial board composition", "wide board view", "slight top-down", "40mm", None)
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return ("multi-panel previs layout", "wide board view", "slight overhead", "35mm", None)
        if output_type == "controlled_frame_generation":
            return ("process-oriented layered composition", "medium wide", "eye level", "35mm", "left to right flow")
        if any(word in scene_text for word in ["discute", "dice", "responde", "espera"]):
            return ("shot reverse shot coverage", "medium close-up", "eye level", "50mm", "subtle dolly")
        if any(word in scene_text for word in ["corre", "entra", "sale", "camina"]):
            return ("dynamic follow coverage", "wide shot", "waist level", "28mm", "tracking")
        return ("controlled narrative framing", "medium shot", "eye level", "40mm", None)

    def _infer_lighting(self, scene: ScriptScene, scene_text: str) -> str:
        int_ext = (scene.int_ext or "").upper()
        time_of_day = (scene.time_of_day or "").upper()
        location = (scene.location or "").lower()
        if int_ext == "INT" and time_of_day in {"NIGHT", "NOCHE"}:
            return "low-key lighting with warm practicals, controlled contrast, readable shadows and premium amber accents"
        if int_ext == "EXT" and time_of_day in {"DAY", "DIA", "DÍA"}:
            return "natural daylight with crisp readable contrast and wider environmental visibility"
        if any(keyword in location for keyword in ["hotel", "oficina", "reunion", "reunión"]):
            return "controlled corporate cinematic lighting with warm practicals, soft screen glow and clean readability"
        if "storyboard" in scene_text or "guion" in scene_text:
            return "clear editorial tabletop lighting with readable documents and balanced monitor highlights"
        return "balanced premium cinematic lighting with clear subject separation and controlled warm-cool contrast"

    def _infer_palette(self, scene: ScriptScene, output_type: str) -> str:
        if output_type == "moodboard":
            return "premium editorial palette with charcoal, warm amber, refined cyan, wardrobe neutrals and atmosphere accents"
        if output_type in {"analysis_view", "controlled_frame_generation"}:
            return "charcoal, amber, soft white and elegant cyan for structured production interfaces"
        if (scene.time_of_day or "").upper() in {"NIGHT", "NOCHE"}:
            return "charcoal, amber practicals and restrained cyan highlights"
        return "premium cinematic saas palette with warm-cool balance and readable contrast"

    def _infer_composition(self, output_type: str, scene: ScriptScene, subject: str) -> str:
        if output_type == "analysis_view":
            return "editorial dashboard hierarchy with screenplay origin, central breakdown board and secondary production modules"
        if output_type == "moodboard":
            return "editorial board with clear focal image plus grouped reference clusters and breathing room"
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return "horizontal multi-panel layout with obvious sequence logic, camera marks and continuity flow"
        if output_type == "controlled_frame_generation":
            return "left-to-right pipeline with prompt prep, node flow, generated frame and validation checkpoint"
        return f"clear focal hierarchy around {subject} with readable environment context and premium negative space"

    def _infer_mood(self, scene_text: str) -> str:
        if any(word in scene_text for word in ["tension", "tensión", "espera", "duda"]):
            return "contained tension"
        if any(word in scene_text for word in ["urgente", "corre", "rapido", "rápido"]):
            return "urgency"
        return "focused cinematic clarity"

    def _required_elements(self, output_type: str, scene: ScriptScene) -> list[str]:
        if output_type == "analysis_view":
            return ["script pages", "breakdown dashboard", "characters", "locations", "production needs"]
        if output_type == "moodboard":
            return ["character references", "palette", "atmosphere", "wardrobe", "location references"]
        if output_type in {"storyboard_frame", "storyboard_board"}:
            return ["multiple panels", "shot planning", "camera marks", "continuity cues"]
        if output_type == "controlled_frame_generation":
            return ["prompt preparation", "node workflow", "generated frame", "validation checkpoint"]
        elements = [scene.location or "scene location"]
        if scene.characters:
            elements.append(scene.characters[0])
        return elements

    def _forbidden_elements(self, output_type: str, scene: ScriptScene) -> list[str]:
        base = list(scene.forbidden_elements)
        if output_type == "analysis_view":
            base.extend(["generic node art", "abstract control room"])
        elif output_type == "moodboard":
            base.extend(["single dark figure", "abstract void"])
        elif output_type in {"storyboard_frame", "storyboard_board"}:
            base.extend(["single hero frame", "poster-like composition"])
        elif output_type == "controlled_frame_generation":
            base.extend(["isolated single node", "process-free narrative still"])
        return list(dict.fromkeys(base))

    def _shorten_action(self, action_summary: str) -> str:
        if not action_summary:
            return "advancing the dramatic beat"
        shortened = re.sub(r"\s+", " ", action_summary).strip()
        return shortened[:180]

    def _merge_text(self, base: str | None, addition: str | None) -> str:
        base_value = (base or "").strip()
        addition_value = (addition or "").strip()
        if not addition_value:
            return base_value
        if not base_value:
            return addition_value
        if addition_value.lower() in base_value.lower():
            return base_value
        return f"{base_value}; {addition_value}"


cinematic_intent_service = CinematicIntentService()
