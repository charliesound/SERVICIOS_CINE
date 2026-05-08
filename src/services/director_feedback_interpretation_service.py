from __future__ import annotations

import re
from typing import Any

from schemas.cid_director_feedback_schema import (
    DirectorFeedbackInterpretation,
    DirectorFeedbackNote,
    FeedbackCategory,
    FeedbackSeverity,
)


class DirectorFeedbackInterpretationService:
    """Interpret a director's natural-language note against the original context
    (prompt, script, visual reference) and decide what can safely change."""

    def interpret_feedback(
        self,
        note: DirectorFeedbackNote,
        original_prompt: dict[str, Any] | None = None,
        script_context: dict[str, Any] | None = None,
        visual_reference_context: dict[str, Any] | None = None,
        storyboard_metadata: dict[str, Any] | None = None,
    ) -> DirectorFeedbackInterpretation:
        requested_changes: list[str] = []
        protected_story: list[str] = []
        protected_visual: list[str] = []
        conflict_script = False
        conflict_script_detail = ""
        conflict_ref = False
        conflict_ref_detail = ""
        conflict_prompt = False
        conflict_prompt_detail = ""
        note_text = note.note_text.lower()
        explanation_parts: list[str] = []

        # --- Extract protected elements from original context ---
        if storyboard_metadata:
            sv_align = storyboard_metadata.get("script_visual_alignment", {})
            if isinstance(sv_align, dict):
                non_neg_story = sv_align.get("non_negotiable_story_elements", [])
                if isinstance(non_neg_story, list):
                    protected_story.extend(non_neg_story)
                non_neg_visual = sv_align.get("non_negotiable_visual_elements", [])
                if isinstance(non_neg_visual, list):
                    protected_visual.extend(non_neg_visual)

            intent = storyboard_metadata.get("directorial_intent", {})
            if isinstance(intent, dict):
                for key in ("blocking", "camera_strategy", "performance_notes"):
                    val = intent.get(key, "")
                    if val:
                        protected_story.append(f"Original {key}: {val}")

            ref_profile = storyboard_metadata.get("visual_reference_profile", {})
            if isinstance(ref_profile, dict):
                ref_summary = ref_profile.get("visual_summary", "")
                if ref_summary:
                    protected_visual.append(f"Reference visual summary: {ref_summary}")
                ref_non_transferable = ref_profile.get("non_transferable_traits", [])
                if isinstance(ref_non_transferable, list):
                    for t in ref_non_transferable:
                        protected_visual.append(f"Do NOT transfer from reference: {t}")

        if script_context:
            location = script_context.get("location", "")
            if location:
                protected_story.append(f"Script location: {location}")
            time_of_day = script_context.get("time_of_day", "")
            if time_of_day:
                protected_story.append(f"Script time of day: {time_of_day}")
            characters = script_context.get("characters", [])
            if isinstance(characters, list) and characters:
                protected_story.append(f"Script characters: {', '.join(characters)}")

        # --- Note interpretation by category ---
        base_explanation = self._interpret_note_text(note_text, note.category)

        if note.category == FeedbackCategory.lighting:
            requested_changes = self._interpret_lighting_note(note_text)
            conflict_prompt, conflict_prompt_detail = self._check_lighting_prompt_conflict(
                note_text, original_prompt
            )

        elif note.category == FeedbackCategory.camera:
            requested_changes = self._interpret_camera_note(note_text)
            conflict_script, conflict_script_detail = self._check_camera_script_conflict(
                note_text, script_context
            )

        elif note.category == FeedbackCategory.character:
            requested_changes = self._interpret_character_note(note_text)
            conflict_script, conflict_script_detail = self._check_character_script_conflict(
                note_text, script_context
            )

        elif note.category == FeedbackCategory.composition:
            requested_changes = self._interpret_composition_note(note_text)
            conflict_ref, conflict_ref_detail = self._check_composition_reference_conflict(
                note_text, visual_reference_context
            )

        elif note.category == FeedbackCategory.continuity:
            requested_changes = self._interpret_continuity_note(note_text)

        elif note.category == FeedbackCategory.tone:
            requested_changes = self._interpret_tone_note(note_text)
            conflict_prompt, conflict_prompt_detail = self._check_tone_prompt_conflict(
                note_text, original_prompt
            )

        elif note.category == FeedbackCategory.production:
            requested_changes = self._interpret_production_note(note_text)

        else:
            requested_changes = [f"Review requested: {note.note_text[:200]}"]

        # --- Assess risk ---
        risk_level = self._assess_risk(
            note.severity, conflict_script, conflict_ref, conflict_prompt
        )

        # --- Build explanation ---
        explanation_parts.append(base_explanation)
        if conflict_script and conflict_script_detail:
            explanation_parts.append(f"SCRIPT CONFLICT: {conflict_script_detail}")
        if conflict_ref and conflict_ref_detail:
            explanation_parts.append(f"REFERENCE CONFLICT: {conflict_ref_detail}")
        if conflict_prompt and conflict_prompt_detail:
            explanation_parts.append(f"PROMPT CONFLICT: {conflict_prompt_detail}")
        if note.preserve_original_logic:
            explanation_parts.append("Preserving original narrative logic as requested.")

        # --- Build recommended action ---
        if risk_level == "high":
            recommended = (
                "Requires director confirmation. "
                "Requested change conflicts with script or reference constraints."
            )
        elif conflict_prompt:
            recommended = (
                "Change can be applied with adjustments. "
                "Prompt will be modified but narrative intent preserved."
            )
        else:
            recommended = "Change can be applied safely. Revisions will be generated."

        return DirectorFeedbackInterpretation(
            requested_changes=_clean_list(requested_changes),
            protected_story_elements=_clean_list(protected_story),
            protected_visual_elements=_clean_list(protected_visual),
            conflict_with_script=conflict_script,
            conflict_with_script_details=conflict_script_detail,
            conflict_with_reference=conflict_ref,
            conflict_with_reference_details=conflict_ref_detail,
            conflict_with_initial_prompt=conflict_prompt,
            conflict_with_initial_prompt_details=conflict_prompt_detail,
            recommended_action=recommended,
            risk_level=risk_level,
            explanation=" | ".join(explanation_parts),
        )

    # ---- Lighting ----
    def _interpret_lighting_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "oscuro" in text or "dark" in text or "más luz" in text or "brillante" in text:
            changes.append("Increase overall brightness and exposure")
            changes.append("Reduce shadow density")
            changes.append("Add fill light to reveal details")
        if "natural" in text:
            changes.append("Shift to natural daylight lighting")
            changes.append("Use soft diffused window light")
            changes.append("Add ambient fill from practical sources")
        if "volumétric" in text or "volumetric" in text:
            changes.append("Add volumetric light rays")
            changes.append("Increase atmospheric depth")
        if "contraste" in text or "contrast" in text:
            changes.append("Adjust contrast ratio")
        if "cálido" in text or "warm" in text:
            changes.append("Shift color temperature to warm amber tones")
        if "frío" in text or "cold" in text or "azul" in text:
            changes.append("Shift color temperature to cool blue tones")
        return _clean_list(changes)

    def _check_lighting_prompt_conflict(
        self, text: str, original_prompt: dict[str, Any] | None
    ) -> tuple[bool, str]:
        if not original_prompt:
            return False, ""
        prompt_text = (original_prompt.get("positive_prompt", "") or "").lower()
        if ("oscuro" in text or "dark" in text) and "nocturn" in prompt_text:
            return True, "Script requires night scene but director wants more light. Apply with caution."
        if ("natural" in text) and ("night" in prompt_text or "nocturn" in prompt_text or "oscur" in prompt_text):
            return True, "Script indicates night/dark scene but director requests natural light. Adjust within scene constraints."
        return False, ""

    # ---- Camera ----
    def _interpret_camera_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "plano medio" in text or "medium" in text:
            changes.append("Change shot type to medium shot (MS)")
            changes.append("Frame from waist up")
        if "primer plano" in text or "close" in text:
            changes.append("Change shot type to close-up (CU)")
            changes.append("Frame on face or detail")
        if "plano general" in text or "wide" in text:
            changes.append("Change shot type to wide shot (WS)")
            changes.append("Show full environment")
        if "contraplano" in text or "over shoulder" in text:
            changes.append("Add over-the-shoulder shot")
            changes.append("Add reverse shot")
            changes.append("Maintain eyeline match")
            changes.append("Add shot/reverse-shot coverage")
        if "contraplano" in text or "shot reverse" in text:
            changes.append("Implement shot/reverse-shot pattern")
            changes.append("Ensure eyeline continuity")
        if "cámara" in text and "alta" in text:
            changes.append("Change camera angle to high angle")
        if "cámara" in text and "baja" in text:
            changes.append("Change camera angle to low angle")
        if "estático" in text or "static" in text:
            changes.append("Use static camera, no movement")
        if "movimiento" in text or "track" in text:
            changes.append("Add camera movement")
        if "abierto" in text or "open" in text:
            changes.append("Open up the frame, wider lens")
        return _clean_list(changes)

    def _check_camera_script_conflict(
        self, text: str, script_context: dict[str, Any] | None
    ) -> tuple[bool, str]:
        if not script_context:
            return False, ""
        action = (script_context.get("action_summary", "") or "").lower()
        if "close" in text or "primer plano" in text:
            if "lejos" in action or "distante" in action:
                return True, "Script indicates distant action; close-up may need context-establishing shot first."
        return False, ""

    # ---- Character ----
    def _interpret_character_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "espaldas" in text or "back" in text:
            changes.append("Rotate character to face camera or action")
            changes.append("Do NOT show character from behind")
        if "de frente" in text or "front" in text:
            changes.append("Show character front-facing")
        if "expresión" in text or "expression" in text:
            changes.append("Emphasize character facial expression")
        if "entra" in text or "entrance" in text:
            changes.append("Show character entrance/arrival")
        return _clean_list(changes)

    def _check_character_script_conflict(
        self, text: str, script_context: dict[str, Any] | None
    ) -> tuple[bool, str]:
        if not script_context:
            return False, ""
        characters = script_context.get("characters", [])
        action = (script_context.get("action_summary", "") or "").lower()
        if ("espaldas" in text or "back" in text) and ("de espaldas" in action or "from behind" in action):
            return True, "Script specifies character from behind; changing to front-facing may alter blocking intent."
        if ("de frente" in text or "front" in text) and ("de espaldas" in action or "from behind" in action):
            return True, "Script specifies back-facing; front-facing request contradicts script blocking."
        return False, ""

    # ---- Composition ----
    def _interpret_composition_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "vida" in text or "dinamismo" in text or "life" in text or "dynamic" in text:
            changes.append("Add visual energy and movement")
            changes.append("Use dynamic composition")
            changes.append("Add depth through foreground elements")
        if "limpio" in text or "clean" in text:
            changes.append("Simplify composition, remove clutter")
            changes.append("Use negative space intentionally")
        if "simétric" in text or "symmetr" in text:
            changes.append("Use symmetrical composition")
        if "abierto" in text or "open" in text:
            changes.append("Use open frame composition")
        if "enmarcado" in text or "frame" in text:
            changes.append("Use foreground framing elements")
        return _clean_list(changes)

    def _check_composition_reference_conflict(
        self, text: str, visual_reference_context: dict[str, Any] | None
    ) -> tuple[bool, str]:
        if not visual_reference_context:
            return False, ""
        ref_composition = (visual_reference_context.get("composition_description", "") or "").lower()
        if ("simetr" in text) and ("asimétric" in ref_composition or "asymmetr" in ref_composition):
            return True, "Reference suggests asymmetric composition but director requests symmetry."
        return False, ""

    # ---- Continuity ----
    def _interpret_continuity_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "eje" in text or "180" in text:
            changes.append("Maintain 180-degree rule")
            changes.append("Keep camera on correct side of line")
        if "mirada" in text or "eyeline" in text:
            changes.append("Match eyeline between shots")
            changes.append("Ensure look-room in frame")
        if "raccord" in text or "match" in text:
            changes.append("Maintain visual continuity between cuts")
        if "vestuario" in text or "wardrobe" in text:
            changes.append("Keep wardrobe consistent with previous shots")
        return _clean_list(changes)

    # ---- Tone ----
    def _interpret_tone_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "serio" in text or "serious" in text:
            changes.append("Shift tone toward serious and dramatic")
        if "ligero" in text or "light" in text:
            changes.append("Shift tone toward lighter and more accessible")
        if "tenso" in text or "tens" in text:
            changes.append("Increase dramatic tension in composition")
            changes.append("Use tighter framing")
        if "atmosfera" in text or "mood" in text or "tono" in text:
            changes.append("Adjust atmosphere to match requested tone")
        return _clean_list(changes)

    def _check_tone_prompt_conflict(
        self, text: str, original_prompt: dict[str, Any] | None
    ) -> tuple[bool, str]:
        if not original_prompt:
            return False, ""
        prompt_text = (original_prompt.get("positive_prompt", "") or "").lower()
        if ("ligero" in text or "light" in text) and ("dramático" in prompt_text or "intense" in prompt_text or "tension" in prompt_text):
            return True, "Original prompt establishes dramatic tone; lighter tone may conflict with narrative intent."
        return False, ""

    # ---- Production ----
    def _interpret_production_note(self, text: str) -> list[str]:
        changes: list[str] = []
        if "localización" in text or "location" in text:
            changes.append("Update location reference")
        if "vestuario" in text or "costume" in text:
            changes.append("Update wardrobe/costume reference")
        if "attrezo" in text or "prop" in text:
            changes.append("Update prop reference")
        return _clean_list(changes)

    # ---- Generic ----
    def _interpret_note_text(self, text: str, category: FeedbackCategory) -> str:
        text_short = text[:150]
        category_name = category.value
        return f"Director note ({category_name}): \"{text_short}\" — interpreting requested changes against original context."

    # ---- Risk ----
    def _assess_risk(
        self,
        severity: FeedbackSeverity,
        conflict_script: bool,
        conflict_ref: bool,
        conflict_prompt: bool,
    ) -> str:
        if conflict_script:
            return "high"
        if conflict_ref and severity in (FeedbackSeverity.major, FeedbackSeverity.medium):
            return "high"
        if conflict_prompt and severity == FeedbackSeverity.major:
            return "medium"
        if severity == FeedbackSeverity.major and not conflict_script:
            return "medium"
        return "low"


def _clean_list(items: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned


director_feedback_interpretation_service = DirectorFeedbackInterpretationService()
