from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from schemas.cid_script_to_prompt_schema import CinematicIntent, PromptSpec
from schemas.cid_visual_reference_schema import EnrichedVisualIntent, ScriptVisualAlignmentResult, StyleReferenceProfile


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "config" / "cid_script_to_prompt_rules.yaml"


class PromptConstructionService:
    def __init__(self) -> None:
        self._rules_cache: dict[str, Any] | None = None

    def build_prompt_spec(
        self,
        intent: CinematicIntent,
        *,
        style_preset: str = "premium_cinematic_saas",
        width: int = 1536,
        height: int = 864,
        allow_director_reference_names: bool = False,
        visual_reference_profile: StyleReferenceProfile | None = None,
        enriched_intent: EnrichedVisualIntent | None = None,
    ) -> PromptSpec:
        positive_prompt = self._build_positive_prompt(intent, style_preset, allow_director_reference_names, visual_reference_profile, enriched_intent)
        negative_prompt = self._build_negative_prompt(intent, visual_reference_profile=visual_reference_profile, enriched_intent=enriched_intent)
        semantic_anchors = [
            f"subject:{intent.subject}",
            f"action:{intent.action}",
            f"environment:{intent.environment}",
            f"dramatic_intent:{intent.dramatic_intent}",
            f"output_type:{intent.output_type}",
        ]
        return PromptSpec(
            prompt_id=f"prompt_{intent.scene_id}_{intent.output_type}",
            scene_id=intent.scene_id,
            output_type=intent.output_type,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            model_hint="flux_or_sdxl",
            width=width,
            height=height,
            seed_hint=self._seed_hint(intent),
            continuity_anchors=intent.continuity_anchors,
            semantic_anchors=semantic_anchors,
            editorial_purpose=intent.shot_editorial_purpose,
            montage_intent=intent.montage_intent,
            validation_status="pending",
            validation_errors=[],
        )

    def _build_positive_prompt(
        self,
        intent: CinematicIntent,
        style_preset: str,
        allow_director_reference_names: bool,
        visual_reference_profile: StyleReferenceProfile | None = None,
        enriched_intent: EnrichedVisualIntent | None = None,
    ) -> str:
        required_elements = ", ".join(intent.required_elements)
        continuity_text = ", ".join(intent.continuity_anchors) if intent.continuity_anchors else "maintain project visual coherence"
        directorial = intent.directorial_intent
        montage_intent = intent.montage_intent
        editorial_purpose = intent.shot_editorial_purpose
        directorial_segments = []
        if directorial is not None:
            directorial_segments = [
                f"mise en scene: {directorial.mise_en_scene}",
                f"blocking: {directorial.blocking}",
                f"camera strategy: {directorial.camera_strategy}",
                f"suspense or emotion strategy: {directorial.suspense_or_emotion_strategy}",
                f"rhythm strategy: {directorial.rhythm_strategy}",
                f"performance notes: {directorial.performance_notes}",
                f"editorial notes: {directorial.editorial_notes}",
            ]
            if directorial.visual_metaphor:
                directorial_segments.append(f"visual metaphor: {directorial.visual_metaphor}")
            if directorial.subtext_strategy:
                directorial_segments.append(f"subtext strategy: {directorial.subtext_strategy}")
            if directorial.montage_notes:
                directorial_segments.append(f"montage notes: {directorial.montage_notes}")
            if directorial.coverage_strategy:
                directorial_segments.append(f"coverage strategy: {', '.join(directorial.coverage_strategy)}")
            if directorial.edit_sensitive_prompt_guidance:
                directorial_segments.append(
                    f"edit sensitive guidance: {', '.join(directorial.edit_sensitive_prompt_guidance[:4])}"
                )
        montage_segments = []
        if montage_intent is not None:
            montage_segments = [
                f"editorial function: {montage_intent.editorial_function}",
                f"montage rhythm: {montage_intent.rhythm}",
                f"average shot duration: {montage_intent.average_shot_duration}",
                f"cutting pattern: {montage_intent.cutting_pattern}",
                f"transition strategy: {montage_intent.transition_strategy}",
                f"continuity strategy: {montage_intent.continuity_strategy}",
                f"eyeline strategy: {montage_intent.eyeline_strategy}",
            ]
            if montage_intent.sound_bridge_strategy:
                montage_segments.append(f"sound bridge strategy: {montage_intent.sound_bridge_strategy}")
            if montage_intent.reveal_points:
                montage_segments.append(f"reveal points: {', '.join(montage_intent.reveal_points[:3])}")
            if montage_intent.emotional_cut_points:
                montage_segments.append(f"emotional cut points: {', '.join(montage_intent.emotional_cut_points[:3])}")
        editorial_segments = []
        if editorial_purpose is not None:
            editorial_segments = [
                f"shot editorial purpose: {editorial_purpose.purpose}",
                f"cut reason: {editorial_purpose.cut_reason}",
                f"previous shot relationship: {editorial_purpose.previous_shot_relationship}",
                f"next shot relationship: {editorial_purpose.next_shot_relationship}",
                f"visual continuity: {editorial_purpose.visual_continuity}",
                f"emotional continuity: {editorial_purpose.emotional_continuity}",
            ]
        visual_reference_parts: list[str] = []
        if visual_reference_profile is not None:
            visual_reference_parts = [
                f"visual reference guidance: {visual_reference_profile.visual_summary}",
            ]
            ref_traits_lower = [t.lower() for t in visual_reference_profile.transferable_traits]
            if visual_reference_profile.palette_description and "palette" in " ".join(ref_traits_lower):
                visual_reference_parts.append(f"palette guided by reference: {visual_reference_profile.palette_description}")
            if visual_reference_profile.lighting_description and "lighting" in " ".join(ref_traits_lower):
                visual_reference_parts.append(f"lighting guided by reference: {visual_reference_profile.lighting_description}")
            if visual_reference_profile.atmosphere_description:
                visual_reference_parts.append(f"atmosphere guided by reference: {visual_reference_profile.atmosphere_description}")
            if visual_reference_profile.composition_description and "composition" in " ".join(ref_traits_lower):
                visual_reference_parts.append(f"composition guided by reference: {visual_reference_profile.composition_description}")
            if visual_reference_profile.texture_description and "texture" in " ".join(ref_traits_lower):
                visual_reference_parts.append(f"texture guided by reference: {visual_reference_profile.texture_description}")

        enriched_parts: list[str] = []
        if enriched_intent is not None:
            if enriched_intent.merged_intent_summary:
                enriched_parts.append(f"script-reference alignment: {enriched_intent.merged_intent_summary}")
            if enriched_intent.scene_requirements:
                enriched_parts.append(f"scene requirements: {'; '.join(enriched_intent.scene_requirements)}")
            if enriched_intent.visual_requirements:
                enriched_parts.append(f"visual requirements: {'; '.join(enriched_intent.visual_requirements)}")
            if enriched_intent.non_negotiable_story_elements:
                enriched_parts.append(f"non-negotiable story: {'; '.join(enriched_intent.non_negotiable_story_elements[:3])}")
            if enriched_intent.non_negotiable_visual_elements:
                enriched_parts.append(f"non-negotiable visual: {'; '.join(enriched_intent.non_negotiable_visual_elements[:3])}")

        positive_prompt = (
            f"{style_preset}, "
            f"subject: {intent.subject}, "
            f"action: {intent.action}, "
            f"environment: {intent.environment}, "
            f"dramatic intent: {intent.dramatic_intent}, "
            f"framing: {intent.framing}, shot size: {intent.shot_size}, camera angle: {intent.camera_angle}, lens: {intent.lens}, "
            f"lighting: {intent.lighting}, color palette: {intent.color_palette}, composition: {intent.composition}, "
            f"movement: {intent.movement or 'static or minimal cinematic motion'}, mood: {intent.mood}, "
            f"required visual elements: {required_elements}, continuity anchors: {continuity_text}, "
            f"{', '.join(directorial_segments + montage_segments + editorial_segments + visual_reference_parts + enriched_parts)}, "
            "clean, semantically grounded, cinematic, production-aware, premium visual language, precise symmetrical framing when needed, suspense built through negative space when needed, warm humanist blocking when needed, expressive color-coded melodrama when needed, surreal disruption inside a realistic social space when needed"
        )
        return self._sanitize_positive_prompt(positive_prompt)

    def _build_negative_prompt(
        self,
        intent: CinematicIntent,
        *,
        visual_reference_profile: StyleReferenceProfile | None = None,
        enriched_intent: EnrichedVisualIntent | None = None,
    ) -> str:
        rules = self._load_rules()
        global_forbidden = list(rules.get("semantic_rules", {}).get("universal", {}).get("avoid", []))
        output_forbidden = list(
            rules.get("output_types", {}).get(intent.output_type, {}).get("forbidden_elements", [])
        )
        forbidden = []
        for item in global_forbidden + output_forbidden + intent.forbidden_elements:
            normalized = str(item).replace("_", " ").strip()
            if normalized and normalized not in forbidden:
                forbidden.append(normalized)
        forbidden.extend(
            [
                "unreadable text",
                "watermark",
                "logo artifacts",
                "generic sci-fi interface",
                "meaningless abstraction",
                "in the style of any named director",
                "director imitation",
            ]
        )
        if visual_reference_profile is not None:
            for constraint in visual_reference_profile.negative_constraints:
                normalized = constraint.strip()
                if normalized and normalized not in forbidden:
                    forbidden.append(normalized)
        if enriched_intent is not None and enriched_intent.negative_guidance:
            for item in enriched_intent.negative_guidance.split(";"):
                normalized = item.strip()
                if normalized and normalized not in forbidden:
                    forbidden.append(normalized)
        unique = []
        seen: set[str] = set()
        for item in forbidden:
            if item in seen:
                continue
            seen.add(item)
            unique.append(item)
        return ", ".join(unique)

    def _load_rules(self) -> dict[str, Any]:
        if self._rules_cache is None:
            with RULES_PATH.open("r", encoding="utf-8") as handle:
                self._rules_cache = yaml.safe_load(handle) or {}
        return self._rules_cache

    def _seed_hint(self, intent: CinematicIntent) -> int:
        digest = hashlib.sha256(f"{intent.scene_id}:{intent.output_type}".encode("utf-8")).hexdigest()
        return int(digest[:10], 16) % 2147483647

    def _sanitize_positive_prompt(self, prompt: str) -> str:
        sanitized = prompt
        banned_patterns = [
            "in the style of ",
            "kubrick style",
            "spielberg style",
            "hitchcock style",
            "almodóvar style",
            "almodovar style",
            "kurosawa style",
            "tarkovsky style",
            "fellini style",
            "coppola style",
            "scorsese style",
            "lynch style",
            "bergman style",
            "welles style",
        ]
        lowered = sanitized.lower()
        for pattern in banned_patterns:
            if pattern in lowered:
                lowered = lowered.replace(pattern, "")
        if lowered != sanitized.lower():
            sanitized = lowered
        sanitized = sanitized.replace(" , ", ", ")
        sanitized = sanitized.replace("  ", " ")
        return sanitized.strip(" ,")


prompt_construction_service = PromptConstructionService()
