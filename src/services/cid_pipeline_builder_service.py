from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any, Optional

from schemas.cid_pipeline_schema import (
    CIDPipelineDefinition,
    CIDPipelineGenerateRequest,
    CIDPipelineLegalContext,
    CIDPipelineStage,
)
from services.cid_pipeline_preset_service import cid_pipeline_preset_service
from services.workflow_builder import builder as workflow_builder
from services.workflow_planner import planner as workflow_planner


class CIDPipelineBuilderService:
    def build_pipeline(self, request: CIDPipelineGenerateRequest) -> CIDPipelineDefinition:
        preset = cid_pipeline_preset_service.resolve_preset(request.preset_key, request.intent)
        context = deepcopy(request.context)
        analysis = workflow_planner.analyze_intent(request.intent or preset["name"], context)

        workflow_key = preset.get("default_workflow_key") or analysis.detected_workflow
        backend = preset.get("default_backend") or analysis.backend
        pipeline_title = request.title or preset["name"]
        intent = request.intent or preset["description"]
        legal = self._build_legal_context(request.legal, preset.get("task_type", ""), context)

        metadata: dict[str, Any] = {
            "preset_description": preset["description"],
            "requires_legal_gate": bool(preset.get("requires_legal_gate", False)),
            "planner_confidence": analysis.confidence,
            "planner_reasoning": analysis.reasoning,
            "context_keys": sorted(context.keys()),
        }
        if workflow_key:
            metadata["workflow_preview"] = workflow_builder.get_workflow_preview(workflow_key)
            metadata["planner_detected_workflow"] = analysis.detected_workflow

        stages = [CIDPipelineStage(**stage) for stage in preset.get("stages", [])]
        return CIDPipelineDefinition(
            pipeline_id=uuid.uuid4().hex,
            mode="simulated",
            title=pipeline_title,
            summary=self._build_summary(preset, analysis.reasoning),
            preset_key=preset["key"],
            preset_name=preset["name"],
            task_type=preset["task_type"],
            project_id=request.project_id,
            intent=intent,
            workflow_key=workflow_key,
            backend=backend,
            stages=stages,
            legal=legal,
            metadata=metadata,
        )

    def _build_legal_context(
        self,
        legal: CIDPipelineLegalContext,
        task_type: str,
        context: dict[str, Any],
    ) -> CIDPipelineLegalContext:
        return CIDPipelineLegalContext(
            voice_cloning=bool(legal.voice_cloning or context.get("voice_cloning", False) or task_type == "dubbing" and bool(context.get("reference_audio"))),
            consent=bool(legal.consent or context.get("consent", False)),
            rights_declared=bool(legal.rights_declared or context.get("rights_declared", False)),
            rights_notes=legal.rights_notes or context.get("rights_notes"),
        )

    def _build_summary(self, preset: dict[str, Any], planner_reasoning: Optional[str]) -> str:
        base = f"Simulated pipeline for {preset['name'].lower()}."
        if planner_reasoning:
            return f"{base} {planner_reasoning}"
        return base


cid_pipeline_builder_service = CIDPipelineBuilderService()
