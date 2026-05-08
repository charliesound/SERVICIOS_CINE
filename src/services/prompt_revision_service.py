from __future__ import annotations

from typing import Any

from schemas.cid_director_feedback_schema import (
    DirectorFeedbackInterpretation,
    PromptRevisionPatch,
)
from services.prompt_construction_service import prompt_construction_service


class PromptRevisionService:
    """Revise a PromptSpec based on director feedback interpretation
    while preserving protected narrative and visual elements."""

    def revise_prompt_with_director_feedback(
        self,
        prompt_spec: dict[str, Any] | None = None,
        feedback_interpretation: DirectorFeedbackInterpretation | None = None,
        original_intent: dict[str, Any] | None = None,
        sequence_context: dict[str, Any] | None = None,
        shot_context: dict[str, Any] | None = None,
    ) -> PromptRevisionPatch:
        if prompt_spec is None:
            prompt_spec = {}
        if feedback_interpretation is None:
            feedback_interpretation = DirectorFeedbackInterpretation()

        original_pos = prompt_spec.get("positive_prompt", "")
        original_neg = prompt_spec.get("negative_prompt", "")

        preserved: list[str] = list(feedback_interpretation.protected_story_elements)
        preserved.extend(feedback_interpretation.protected_visual_elements)
        preserved = self._dedup(preserved)

        changed: list[str] = []
        rejected: list[str] = []

        # --- Build revised prompt ---
        revised_pos = original_pos
        revised_neg = original_neg

        # Add DIRECTOR REVISION NOTES block
        revision_notes = self._build_revision_block(
            feedback_interpretation, prompt_spec, original_intent
        )

        # Apply requested changes
        for change in feedback_interpretation.requested_changes:
            applied = self._apply_change_to_prompt(
                change, feedback_interpretation, prompt_spec
            )
            if applied:
                revised_pos, revised_neg = applied
                changed.append(change)
            else:
                rejected.append(change)

        # Add revision metadata to negative prompt
        added_restrictions = self._build_added_restrictions(feedback_interpretation)
        if added_restrictions:
            revised_neg = self._append_to_prompt(revised_neg, added_restrictions)

        # Build revision reason
        reason_parts: list[str] = ["Director feedback revision."]
        if changed:
            reason_parts.append(f"Applied: {'; '.join(changed[:3])}")
        if rejected:
            reason_parts.append(f"Rejected: {'; '.join(rejected[:3])}")
        if feedback_interpretation.conflict_with_script:
            reason_parts.append("Note: Some requests conflict with script constraints.")
        if feedback_interpretation.conflict_with_reference:
            reason_parts.append("Note: Some requests conflict with reference constraints.")
        revision_reason = " | ".join(reason_parts)

        # Add revision instruction blocks to positive prompt
        if self._has_substantial_changes(changed, feedback_interpretation):
            revised_pos = self._append_to_prompt(revised_pos, revision_notes)

        version = prompt_spec.get("_revision_version", 0) + 1

        return PromptRevisionPatch(
            original_prompt=original_pos,
            revised_prompt=revised_pos,
            original_negative_prompt=original_neg,
            revised_negative_prompt=revised_neg,
            preserved_elements=self._dedup(preserved),
            changed_elements=self._dedup(changed),
            rejected_changes=self._dedup(rejected),
            revision_reason=revision_reason,
            director_note_applied=feedback_interpretation.explanation[:300],
            version_number=version,
        )

    def _build_revision_block(
        self,
        interpretation: DirectorFeedbackInterpretation,
        prompt_spec: dict[str, Any] | None,
        original_intent: dict[str, Any] | None,
    ) -> str:
        lines: list[str] = []
        lines.append("DIRECTOR REVISION NOTES")
        lines.append(f"  Requested: {'; '.join(interpretation.requested_changes[:5])}")
        if interpretation.protected_story_elements:
            lines.append(f"  PRESERVE FROM ORIGINAL: {'; '.join(interpretation.protected_story_elements[:5])}")
        if interpretation.protected_visual_elements:
            lines.append(f"  PRESERVE FROM REFERENCE: {'; '.join(interpretation.protected_visual_elements[:3])}")
        if interpretation.conflict_with_script:
            lines.append("  DO NOT BREAK: script-defined location, time, character actions")
        if interpretation.conflict_with_reference:
            lines.append("  DO NOT BREAK: reference visual direction")
        lines.append("  CHANGE REQUEST: apply director adjustments while maintaining narrative truth")
        return ", ".join(lines)

    def _build_added_restrictions(
        self, interpretation: DirectorFeedbackInterpretation
    ) -> str:
        parts: list[str] = []
        for change in interpretation.requested_changes:
            if "oscuro" in change.lower() or "dark" in change.lower() or "brightness" in change.lower():
                parts.append("no underexposed, no crushed blacks")
            if "natural" in change.lower():
                parts.append("no artificial colored lighting")
            if "close" in change.lower() or "primer plano" in change.lower():
                parts.append("no wide establishing shot")
            if "espaldas" in change.lower() or "back" in change.lower():
                parts.append("no character facing away from camera")
            if "vida" in change.lower() or "dynamic" in change.lower():
                parts.append("no static flat composition")
            if "serio" in change.lower() or "tens" in change.lower():
                parts.append("no cheerful or comedic atmosphere")
        deduped = self._dedup(parts)
        return ", ".join(deduped) if deduped else ""

    def _apply_change_to_prompt(
        self,
        change: str,
        interpretation: DirectorFeedbackInterpretation,
        prompt_spec: dict[str, Any] | None,
    ) -> tuple[str, str] | None:
        change_lower = change.lower()
        pos = (prompt_spec.get("positive_prompt", "") or "") if prompt_spec else ""
        neg = (prompt_spec.get("negative_prompt", "") or "") if prompt_spec else ""
        new_pos = pos
        new_neg = neg

        # Lighting adjustments
        if any(kw in change_lower for kw in ("brightness", "exposure", "fill light")):
            if "well-lit" not in new_pos.lower():
                new_pos = new_pos.rstrip(", ") + ", well-lit professional atmosphere, clear visibility"
            new_neg = new_neg.rstrip(", ") + ", underexposed, crushed blacks, dark underexposed areas"

        if "natural" in change_lower and "daylight" in change_lower:
            if "natural" not in new_pos.lower():
                new_pos = new_pos.rstrip(", ") + ", natural daylight illumination, soft window light"
            new_neg = new_neg.rstrip(", ") + ", colored stage lighting, dramatic colored gels"

        if "volumetric" in change_lower:
            if "volumetric" not in new_pos.lower():
                new_pos = new_pos.rstrip(", ") + ", volumetric light rays, atmospheric depth"

        if "warm" in change_lower or "ámber" in change_lower:
            if "amber" not in new_pos.lower():
                new_pos = new_pos.rstrip(", ") + ", warm amber color temperature"
            new_neg = new_neg.rstrip(", ") + ", cold blue tint, fluorescent green"

        if "cool" in change_lower or "azul" in change_lower:
            if "cool" not in new_pos.lower():
                new_pos = new_pos.rstrip(", ") + ", cool blue color temperature"
            new_neg = new_neg.rstrip(", ") + ", warm amber tint, yellow cast"

        # Camera adjustments
        if "medium shot" in change_lower or "ms" in change_lower:
            new_pos = self._replace_shot_type(new_pos, "medium shot, waist-up framing")
        if "close-up" in change_lower or "cu" in change_lower:
            new_pos = self._replace_shot_type(new_pos, "close-up shot, tight framing on face or detail")
        if "wide shot" in change_lower or "ws" in change_lower:
            new_pos = self._replace_shot_type(new_pos, "wide shot, full environment visible")

        if "over-the-shoulder" in change_lower or "reverse" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", over-the-shoulder angle, reverse shot coverage, eyeline match"
            new_neg = new_neg.rstrip(", ") + ", flat single-camera angle, no eyeline continuity"

        if "high angle" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", high angle looking down on subject"
        if "low angle" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", low angle looking up at subject"

        # Character adjustments
        if "face camera" in change_lower or "front-facing" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", character facing camera or action"
            new_neg = new_neg.rstrip(", ") + ", character from behind, character facing away"

        # Composition adjustments
        if "dynamic" in change_lower or "energy" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", dynamic composition, visual energy, foreground depth"
            new_neg = new_neg.rstrip(", ") + ", static flat composition, empty frame"

        if "symmetr" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", symmetrical balanced composition"

        # Tone adjustments
        if "serious" in change_lower or "dramatic" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", serious dramatic tone, intense atmosphere"
            new_neg = new_neg.rstrip(", ") + ", cheerful mood, comedic atmosphere, lighthearted"

        if "tension" in change_lower:
            new_pos = new_pos.rstrip(", ") + ", tense atmosphere, tight framing, dramatic tension"
            new_neg = new_neg.rstrip(", ") + ", relaxed mood, calm atmosphere"

        if new_pos != pos or new_neg != neg:
            return new_pos, new_neg
        return None

    def _replace_shot_type(self, prompt: str, replacement: str) -> str:
        patterns = [
            "wide shot", "medium shot", "close-up shot",
            "establishing shot", "over-the-shoulder",
            "ws", "ms", "cu", "ots", "pov",
            "full shot", "cowboy shot", "two-shot",
        ]
        result = prompt
        for pat in patterns:
            idx = result.lower().find(pat)
            if idx != -1:
                start = idx
                end = idx + len(pat)
                result = result[:start] + replacement + result[end:]
                return result
        return prompt.rstrip(", ") + f", {replacement}"

    def _append_to_prompt(self, prompt: str, addition: str) -> str:
        if not addition:
            return prompt
        prompt = prompt.rstrip(", ")
        addition = addition.strip().strip(",")
        if addition in prompt:
            return prompt
        return f"{prompt}, {addition}"

    def _has_substantial_changes(
        self, changed: list[str], interpretation: DirectorFeedbackInterpretation
    ) -> bool:
        if len(changed) >= 2:
            return True
        if interpretation.conflict_with_script or interpretation.conflict_with_reference:
            return True
        return False

    def dedup_preserved(self, items: list[str]) -> list[str]:
        return self._dedup(items)

    @staticmethod
    def _dedup(items: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            normalized = item.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result


prompt_revision_service = PromptRevisionService()
