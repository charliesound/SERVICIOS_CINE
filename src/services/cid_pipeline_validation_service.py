from __future__ import annotations

from schemas.cid_pipeline_schema import (
    CIDPipelineDefinition,
    CIDPipelineStage,
    CIDPipelineValidationIssue,
    CIDPipelineValidationResponse,
)
from services.cid_pipeline_legal_gate_service import cid_pipeline_legal_gate_service


class CIDPipelineValidationService:
    def validate_pipeline(self, pipeline: CIDPipelineDefinition) -> CIDPipelineValidationResponse:
        errors: list[CIDPipelineValidationIssue] = []
        warnings: list[CIDPipelineValidationIssue] = []

        if not pipeline.pipeline_id:
            errors.append(self._issue("pipeline.pipeline_id_missing", "pipeline_id is required", "error", "pipeline_id"))
        if not pipeline.task_type:
            errors.append(self._issue("pipeline.task_type_missing", "task_type is required", "error", "task_type"))
        if not pipeline.stages:
            errors.append(self._issue("pipeline.stages_missing", "stages must contain at least one stage", "error", "stages"))

        for index, stage in enumerate(pipeline.stages):
            errors.extend(self._validate_stage(stage, index))

        legal_errors, legal_warnings, blocked = cid_pipeline_legal_gate_service.evaluate(pipeline)
        errors.extend(legal_errors)
        warnings.extend(legal_warnings)

        valid = len(errors) == 0 and not blocked
        return CIDPipelineValidationResponse(
            valid=valid,
            blocked=blocked,
            errors=errors,
            warnings=warnings,
        )

    def _validate_stage(self, stage: CIDPipelineStage, index: int) -> list[CIDPipelineValidationIssue]:
        issues: list[CIDPipelineValidationIssue] = []
        stage_prefix = f"stages[{index}]"

        if not stage.id:
            issues.append(self._issue("stage.id_missing", "Stage id is required", "error", f"{stage_prefix}.id"))
        if not stage.name:
            issues.append(self._issue("stage.name_missing", "Stage name is required", "error", f"{stage_prefix}.name"))
        if not stage.type:
            issues.append(self._issue("stage.type_missing", "Stage type is required", "error", f"{stage_prefix}.type"))
        if stage.inputs is None:
            issues.append(self._issue("stage.inputs_missing", "Stage inputs are required", "error", f"{stage_prefix}.inputs"))
        if stage.outputs is None:
            issues.append(self._issue("stage.outputs_missing", "Stage outputs are required", "error", f"{stage_prefix}.outputs"))

        return issues

    def _issue(self, code: str, message: str, severity: str, field: str) -> CIDPipelineValidationIssue:
        return CIDPipelineValidationIssue(code=code, message=message, severity=severity, field=field)


cid_pipeline_validation_service = CIDPipelineValidationService()
