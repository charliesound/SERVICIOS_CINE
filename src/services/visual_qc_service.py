from __future__ import annotations

from schemas.cid_script_to_prompt_schema import (
    PromptSpec,
    SemanticPromptValidationResult,
    VisualQAEvaluation,
)


class VisualQCService:
    """Stub visual QA service.

    Future versions should compare generated assets against CinematicIntent and
    real images, but this version scores the prompt-level readiness only.
    """

    def evaluate_prompt(
        self,
        prompt: PromptSpec,
        validation: SemanticPromptValidationResult,
    ) -> VisualQAEvaluation:
        if validation.is_valid:
            semantic_match_score = max(0.75, validation.score)
            cinematic_match_score = 0.78
            continuity_score = 0.76 if prompt.continuity_anchors else 0.68
            recommendation = "approve_for_render"
            detected_issues = validation.warnings[:]
        else:
            semantic_match_score = min(validation.score, 0.45)
            cinematic_match_score = 0.42
            continuity_score = 0.35 if prompt.continuity_anchors else 0.25
            recommendation = "needs_prompt_revision"
            detected_issues = validation.errors + validation.warnings

        return VisualQAEvaluation(
            image_ref=None,
            prompt_id=prompt.prompt_id,
            semantic_match_score=round(semantic_match_score, 2),
            cinematic_match_score=round(cinematic_match_score, 2),
            continuity_score=round(continuity_score, 2),
            detected_issues=detected_issues,
            recommendation=recommendation,
        )


visual_qc_service = VisualQCService()
