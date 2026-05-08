from __future__ import annotations

from schemas.cid_script_to_prompt_schema import (
    CinematicIntent,
    PromptSpec,
    SemanticPromptValidationResult,
)


GENERIC_PHRASES = [
    "cinematic image",
    "beautiful shot",
    "ai generated",
    "high quality image",
    "dramatic scene",
]

FORBIDDEN_STYLE_PATTERNS = [
    "in the style of",
    "kubrick style",
    "spielberg style",
    "hitchcock style",
    "almodovar style",
    "almodóvar style",
    "kurosawa style",
    "tarkovsky style",
    "fellini style",
    "coppola style",
    "scorsese style",
    "lynch style",
    "bergman style",
    "welles style",
]


class SemanticPromptValidationService:
    def validate(self, prompt: PromptSpec, intent: CinematicIntent) -> SemanticPromptValidationResult:
        positive_lower = (prompt.positive_prompt or "").lower()
        negative_lower = (prompt.negative_prompt or "").lower()

        errors: list[str] = []
        warnings: list[str] = []
        missing_required_fields: list[str] = []
        ambiguous_terms: list[str] = []
        forbidden_terms_detected: list[str] = []

        if not intent.subject or intent.subject.lower() not in positive_lower:
            missing_required_fields.append("subject")
            errors.append("subject_not_explicitly_grounded")
        if not intent.action or intent.action.lower() not in positive_lower:
            missing_required_fields.append("action")
            errors.append("action_not_explicitly_grounded")
        if not intent.environment or intent.environment.lower() not in positive_lower:
            missing_required_fields.append("environment")
            errors.append("environment_not_explicitly_grounded")
        if not intent.dramatic_intent or intent.dramatic_intent.lower() not in positive_lower:
            missing_required_fields.append("dramatic_intent")
            warnings.append("dramatic_intent_not_clearly_grounded")
        if not prompt.negative_prompt:
            missing_required_fields.append("negative_prompt")
            errors.append("negative_prompt_missing")
        if not prompt.editorial_purpose:
            missing_required_fields.append("editorial_purpose")
            errors.append("editorial_purpose_missing")
        if intent.output_type == "storyboard_frame" and not intent.montage_intent:
            missing_required_fields.append("montage_intent")
            errors.append("montage_intent_missing_for_storyboard")

        if intent.continuity_anchors:
            continuity_hits = 0
            for anchor in intent.continuity_anchors:
                normalized = anchor.split(":", 1)[-1].replace("_", " ").lower().strip()
                if normalized and normalized in positive_lower:
                    continuity_hits += 1
            if continuity_hits == 0:
                warnings.append("continuity_anchors_not_explicitly_grounded")
        elif intent.output_type == "storyboard_frame":
            warnings.append("storyboard_frame_missing_continuity_anchors")

        if "editorial function:" not in positive_lower:
            errors.append("editorial_function_not_grounded")
        if "shot editorial purpose:" not in positive_lower and intent.output_type == "storyboard_frame":
            errors.append("shot_editorial_purpose_not_grounded")
        if "cut reason:" not in positive_lower and intent.output_type == "storyboard_frame":
            warnings.append("cut_reason_not_grounded")
        if not any(token in positive_lower for token in ["previous shot relationship:", "next shot relationship:", "transition strategy:"]):
            warnings.append("shot_connection_not_grounded")
        if not any(token in positive_lower for token in ["eyeline strategy:", "visual continuity:", "emotional continuity:"]):
            warnings.append("continuity_strategy_not_grounded")
        if "poster" in positive_lower and "not" not in positive_lower:
            warnings.append("poster_like_language_detected")

        for phrase in GENERIC_PHRASES:
            if phrase in positive_lower:
                ambiguous_terms.append(phrase)

        for forbidden_pattern in FORBIDDEN_STYLE_PATTERNS:
            if forbidden_pattern in positive_lower:
                forbidden_terms_detected.append(forbidden_pattern)

        if forbidden_terms_detected:
            errors.append("named_director_style_reference_detected")

        for term in intent.forbidden_elements:
            normalized = term.replace("_", " ").lower().strip()
            if normalized and normalized in positive_lower and "avoid" not in positive_lower:
                forbidden_terms_detected.append(normalized)

        if ambiguous_terms and len(prompt.semantic_anchors) < 4:
            errors.append("prompt_too_generic")
        elif ambiguous_terms:
            warnings.append("generic_phrases_present_but_anchored")

        if len(prompt.positive_prompt.split()) < 18:
            warnings.append("positive_prompt_too_short")
        if "generic sci-fi interface" not in negative_lower:
            warnings.append("negative_prompt_missing_generic_ui_block")

        bonus = 0.0
        if "cut reason:" in positive_lower:
            bonus += 0.05
        if "reveal points:" in positive_lower:
            bonus += 0.04
        if "eyeline strategy:" in positive_lower:
            bonus += 0.04
        if "sound bridge strategy:" in positive_lower or "emotional continuity:" in positive_lower:
            bonus += 0.03
        if "coverage strategy:" in positive_lower:
            bonus += 0.04
        if "previous shot relationship:" in positive_lower or "next shot relationship:" in positive_lower:
            bonus += 0.05

        score = 1.0
        score -= 0.18 * len(errors)
        score -= 0.05 * len(warnings)
        score -= 0.08 * len(ambiguous_terms)
        score -= 0.1 * len(forbidden_terms_detected)
        score += bonus
        score = max(0.0, min(1.0, round(score, 2)))
        is_valid = not errors and score >= 0.6

        return SemanticPromptValidationResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            missing_required_fields=missing_required_fields,
            ambiguous_terms=ambiguous_terms,
            forbidden_terms_detected=forbidden_terms_detected,
        )


semantic_prompt_validation_service = SemanticPromptValidationService()
