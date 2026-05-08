from __future__ import annotations

import re
from typing import Any

import yaml
from pathlib import Path

from schemas.cid_visual_reference_schema import (
    AlignmentMode,
    EnrichedVisualIntent,
    ScriptVisualAlignmentRequest,
    ScriptVisualAlignmentResult,
    StyleReferenceProfile,
)


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "config" / "cid_visual_reference_alignment_rules.yaml"


class ScriptVisualAlignmentService:
    def __init__(self) -> None:
        self._rules_cache: dict[str, Any] | None = None

    def _load_rules(self) -> dict[str, Any]:
        if self._rules_cache is None:
            with RULES_PATH.open("r", encoding="utf-8") as f:
                self._rules_cache = yaml.safe_load(f) or {}
        return self._rules_cache

    def align(
        self,
        request: ScriptVisualAlignmentRequest,
    ) -> tuple[ScriptVisualAlignmentResult, EnrichedVisualIntent]:
        rules = self._load_rules()

        script_summary = self._summarize_script(request.script_excerpt)
        profile = request.reference_profile or StyleReferenceProfile()
        ref_summary = profile.visual_summary

        matching = self._find_matching(script_summary, ref_summary, profile, rules)
        missing_img = self._find_missing_from_image(script_summary, profile)
        missing_script = self._find_missing_from_script(ref_summary, script_summary)
        tensions = self._find_tensions(script_summary, ref_summary, profile, rules)
        direction = self._recommend_direction(script_summary, ref_summary, matching, tensions, profile, rules)
        continuity = self._build_continuity_notes(script_summary, profile)
        constraints = self._build_safe_constraints(profile, rules)
        warnings = self._build_warnings(tensions, profile, rules)

        result = ScriptVisualAlignmentResult(
            script_summary=script_summary,
            reference_visual_summary=ref_summary,
            alignment_score=self._compute_alignment_score(matching, tensions),
            matching_elements=matching,
            missing_from_image=missing_img,
            missing_from_script=missing_script,
            tension_points=tensions,
            recommended_visual_direction=direction,
            recommended_prompt_guidance=direction,
            continuity_notes=continuity,
            warnings=warnings,
            safe_constraints=constraints,
        )

        enriched = self._build_enriched_intent(request, result, profile, rules)

        return result, enriched

    def _summarize_script(self, script_excerpt: str) -> str:
        if not script_excerpt.strip():
            return "No script excerpt provided"
        lines = [l.strip() for l in script_excerpt.strip().split("\n") if l.strip()]
        summary_parts: list[str] = []
        for line in lines[:8]:
            if re.match(r"^(INT|EXT|INT\./EXT\.)", line, re.IGNORECASE):
                summary_parts.append(f"Location/Time: {line}")
            elif re.match(r"^[A-Z\s]{3,}", line) and len(line) < 60:
                summary_parts.append(f"Character: {line.strip()}")
            else:
                summary_parts.append(line[:120])
        return " | ".join(summary_parts) if summary_parts else script_excerpt[:200]

    def _find_matching(
        self,
        script: str,
        ref: str,
        profile: StyleReferenceProfile,
        rules: dict[str, Any],
    ) -> list[str]:
        matches: list[str] = []
        script_lower = script.lower()

        mood_keywords = rules.get("alignment_keywords", {}).get("mood", [])
        for kw in mood_keywords:
            if kw in script_lower:
                if "mood" in ref.lower() or "atmosphere" in profile.atmosphere_description.lower():
                    matches.append(f"Mood/atmosphere alignment: script mentions '{kw}' and reference defines atmosphere")

        lighting_keywords = rules.get("alignment_keywords", {}).get("lighting", [])
        for kw in lighting_keywords:
            if kw in script_lower:
                if profile.lighting_description and "not requested" not in profile.lighting_description:
                    matches.append(f"Lighting alignment: script suggests '{kw}' and reference provides lighting guidance")

        location_match = self._extract_location(script)
        if location_match and profile.production_design_signals:
            matches.append(f"Location/environment: script indicates '{location_match}', reference provides production design cues")

        time_match = self._extract_time_of_day(script)
        if time_match and profile.palette_description:
            matches.append(f"Time of day: script indicates '{time_match}', reference can inform palette for this time")

        return matches if matches else ["No explicit conflicts detected in mood and atmosphere"]

    def _extract_location(self, script: str) -> str | None:
        match = re.search(r"(INT\.|EXT\.|INT/EXT\.)\s*(.*?)(?:-{2}|$)", script, re.IGNORECASE)
        return match.group(2).strip() if match else None

    def _extract_time_of_day(self, script: str) -> str | None:
        for token in ["NOCHE", "DIA", "MADRUGADA", "ATARDECER", "AMANECER", "DAY", "NIGHT", "DAWN", "DUSK"]:
            if token in script.upper():
                return token.capitalize()
        if "- N" in script.upper() or "-N" in script.upper():
            return "Noche"
        return None

    def _find_missing_from_image(self, script_summary: str, profile: StyleReferenceProfile) -> list[str]:
        missing: list[str] = []
        script_upper = script_summary.upper()
        if "NOCHE" in script_upper or "NIGHT" in script_upper:
            if "dark" not in profile.palette_description.lower() and "dark" not in profile.lighting_description.lower():
                missing.append("Night/dark scene required by script but reference may not convey darkness")
        if re.search(r"(personaje|character|actor|protagonista)", script_summary, re.IGNORECASE):
            if "character" not in " ".join(profile.non_transferable_traits).lower():
                missing.append("Character presence implied by script but reference focuses on environment")
        return missing

    def _find_missing_from_script(self, ref_summary: str, script_summary: str) -> list[str]:
        missing: list[str] = []
        if "tech" in ref_summary.lower() or "technological" in ref_summary.lower():
            if "tech" not in script_summary.lower():
                missing.append("Reference has technological elements not present in script")
        if "sci-fi" in ref_summary.lower() or "futuristic" in ref_summary.lower():
            if not any(w in script_summary.lower() for w in ["futur", "sci-fi", "technolog"]):
                missing.append("Reference has sci-fi/futuristic elements not present in script")
        return missing

    def _find_tensions(
        self,
        script_summary: str,
        ref_summary: str,
        profile: StyleReferenceProfile,
        rules: dict[str, Any],
    ) -> list[str]:
        tensions: list[str] = []
        script_upper = script_summary.upper()
        ref_lower = ref_summary.lower()

        if "realist" in ref_lower and ("fantasy" in script_upper.lower() or "surreal" in script_upper.lower()):
            tensions.append("Reference realism level may conflict with script's fantastic/surreal tone")

        if profile.genre_signals:
            for genre in profile.genre_signals:
                g = genre.lower()
                if g in ("sci-fi", "futuristic", "fantasy") and "realist" in script_upper.lower():
                    tensions.append(f"Genre tension: reference signals '{genre}' but script grounding is realistic")

        story_priorities = rules.get("decision_rules", {})
        if story_priorities.get("script_overrides_visual_literal", True):
            if "specific action" in script_summary.lower():
                action = re.search(r"(?:action|blocking|movement|entra|sale|se sienta|se levanta)", script_summary, re.IGNORECASE)
                if action and "composition" in profile.composition_description.lower():
                    tensions.append(f"Script defines specific blocking/action ({action.group()}) that may conflict with reference composition")

        return tensions

    def _recommend_direction(
        self,
        script_summary: str,
        ref_summary: str,
        matching: list[str],
        tensions: list[str],
        profile: StyleReferenceProfile,
        rules: dict[str, Any],
    ) -> str:
        lines: list[str] = []
        lines.append("Visual direction derived from script-reference alignment:")

        lines.append("  FROM SCRIPT (non-negotiable):")
        location = self._extract_location(script_summary)
        if location:
            lines.append(f"    - Location: {location}")
        time_day = self._extract_time_of_day(script_summary)
        if time_day:
            lines.append(f"    - Time: {time_day}")
        if re.search(r"(triste|agotado|cansado|tensión|conflicto|emoción)", script_summary, re.IGNORECASE):
            lines.append("    - Emotional tone defined by script")
        if re.search(r"(acci.n|movimiento|entra|sale|camina|corre)", script_summary, re.IGNORECASE):
            lines.append("    - Physical action/blocking defined by script")

        lines.append("  FROM REFERENCE (adaptable):")
        if profile.palette_description and "not requested" not in profile.palette_description:
            lines.append(f"    - Palette direction: {profile.palette_description}")
        if profile.lighting_description and "not requested" not in profile.lighting_description:
            lines.append(f"    - Lighting direction: {profile.lighting_description}")
        if profile.atmosphere_description:
            lines.append(f"    - Atmosphere reference: {profile.atmosphere_description}")

        if tensions:
            lines.append("  TENSION RESOLUTION:")
            for t in tensions[:3]:
                lines.append(f"    - {t}")

        lines.append("  FINAL PRINCIPLE: The script truth must dominate. Reference enriches but does not replace narrative.")

        return "\n".join(lines)

    def _build_continuity_notes(self, script_summary: str, profile: StyleReferenceProfile) -> list[str]:
        notes: list[str] = []
        location = self._extract_location(script_summary)
        if location:
            notes.append(f"Maintain location continuity: {location}")
        time_day = self._extract_time_of_day(script_summary)
        if time_day:
            notes.append(f"Maintain time-of-day consistency: {time_day}")
        if profile.palette_description:
            notes.append("Apply palette consistently across shots in same scene")
        return notes

    def _build_safe_constraints(self, profile: StyleReferenceProfile, rules: dict[str, Any]) -> list[str]:
        constraints: list[str] = []
        constraints.append("Do NOT copy identity, logos, brands, people, or specific content from reference")
        constraints.append("Do NOT use 'in the style of' any named director or artist")
        constraints.append("Reference guides mood/palette/lighting; script guides narrative/action/character")
        if profile.non_transferable_traits:
            for t in profile.non_transferable_traits:
                constraints.append(f"Do NOT transfer: {t}")
        return constraints

    def _build_warnings(self, tensions: list[str], profile: StyleReferenceProfile, rules: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        if tensions:
            warnings.append(f"{len(tensions)} tension points detected between script and reference")
        if profile.confidence_score < 0.5:
            warnings.append("Low confidence in reference analysis; manual review recommended")
        return warnings

    def _compute_alignment_score(self, matching: list[str], tensions: list[str]) -> float:
        base = 0.5
        base += len(matching) * 0.08
        base -= len(tensions) * 0.1
        return max(0.0, min(1.0, base))

    def _build_enriched_intent(
        self,
        request: ScriptVisualAlignmentRequest,
        result: ScriptVisualAlignmentResult,
        profile: StyleReferenceProfile,
        rules: dict[str, Any],
    ) -> EnrichedVisualIntent:
        script = request.script_excerpt

        narrative = f"Scene requires: {result.script_summary}" if result.script_summary else "Narrative intent from script"
        visual = f"Visual mood from reference: {profile.visual_summary}" if profile.visual_summary else "Visual intent from reference"

        merged = f"Script-driven narrative with visual enrichment from reference. "
        if result.matching_elements:
            merged += f"Alignment strengths: {'; '.join(result.matching_elements[:3])}. "
        if result.tension_points:
            merged += f"Resolved tensions: {'; '.join(result.tension_points[:2])}. "
        merged += "Script truth prioritized over visual literalness."

        scene_reqs: list[str] = []
        location = self._extract_location(script)
        if location:
            scene_reqs.append(f"Location: {location}")
        time_day = self._extract_time_of_day(script)
        if time_day:
            scene_reqs.append(f"Time: {time_day}")
        if re.search(r"(triste|agotado|cansado|tensi.n|conflicto|emoci.n)", script, re.IGNORECASE):
            scene_reqs.append("Emotional tone from script")
        if re.search(r"(acci.n|movimiento|entra|sale|camina|corre)", script, re.IGNORECASE):
            scene_reqs.append("Physical blocking from script")

        visual_reqs: list[str] = []
        if profile.palette_description and "not requested" not in profile.palette_description:
            visual_reqs.append(f"Palette: {profile.palette_description}")
        if profile.lighting_description and "not requested" not in profile.lighting_description:
            visual_reqs.append(f"Lighting: {profile.lighting_description}")
        if profile.atmosphere_description:
            visual_reqs.append(f"Atmosphere: {profile.atmosphere_description}")

        non_neg_story = [
            "Location and time of day as written in script",
            "Character actions and blocking as described",
            "Emotional/dramatic intent of the scene",
        ]

        non_neg_visual = [
            "Do not copy specific content from reference",
            "Do not replace script-defined action with reference composition",
        ]

        qa = [
            "VERIFICAR: La escena respeta la localización y hora del guion",
            "VERIFICAR: La atmósfera visual sigue la referencia sin copiarla",
            "VERIFICAR: No hay elementos narrativos del guion reemplazados por la imagen",
        ]

        return EnrichedVisualIntent(
            narrative_intent=narrative,
            visual_intent=visual,
            merged_intent_summary=merged,
            scene_requirements=scene_reqs,
            visual_requirements=visual_reqs,
            non_negotiable_story_elements=non_neg_story,
            non_negotiable_visual_elements=non_neg_visual,
            prompt_guidance=result.recommended_prompt_guidance,
            negative_guidance="; ".join(result.safe_constraints),
            qa_checklist=qa,
        )


script_visual_alignment_service = ScriptVisualAlignmentService()
