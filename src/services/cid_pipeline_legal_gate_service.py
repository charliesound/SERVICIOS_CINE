from __future__ import annotations

from schemas.cid_pipeline_schema import (
    CIDPipelineDefinition,
    CIDPipelineValidationIssue,
)


class CIDPipelineLegalGateService:
    def evaluate(self, pipeline: CIDPipelineDefinition) -> tuple[list[CIDPipelineValidationIssue], list[CIDPipelineValidationIssue], bool]:
        errors: list[CIDPipelineValidationIssue] = []
        warnings: list[CIDPipelineValidationIssue] = []

        legal = pipeline.legal
        if pipeline.task_type == "dubbing" and legal.voice_cloning and not legal.consent:
            errors.append(
                CIDPipelineValidationIssue(
                    code="legal.voice_cloning_requires_consent",
                    message="Voice cloning for dubbing requires explicit consent=true.",
                    severity="error",
                    field="legal.consent",
                )
            )

        if not legal.rights_declared:
            warnings.append(
                CIDPipelineValidationIssue(
                    code="legal.rights_missing",
                    message="Rights declarations are missing. Declare ownership or licensed usage before execution.",
                    severity="warning",
                    field="legal.rights_declared",
                )
            )

        if not legal.rights_notes:
            warnings.append(
                CIDPipelineValidationIssue(
                    code="legal.rights_notes_missing",
                    message="Rights notes are recommended to document source ownership and permitted usage.",
                    severity="warning",
                    field="legal.rights_notes",
                )
            )

        blocked = len(errors) > 0
        return errors, warnings, blocked


cid_pipeline_legal_gate_service = CIDPipelineLegalGateService()
