from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from schemas.workflow_schema import (
    WorkflowPlanRequest,
    WorkflowBuildRequest,
    WorkflowValidateRequest,
    WorkflowCatalogItem,
    PresetCreate,
    PresetResponse,
)
from services.workflow_registry import workflow_registry
from services.workflow_planner import planner
from services.workflow_builder import builder
from services.workflow_validator import validator
from services.workflow_preset_service import preset_service

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/plan")
async def plan_workflow(request: WorkflowPlanRequest):
    analysis = planner.analyze_intent(request.intent, request.context)

    workflow = None
    if not analysis.missing_inputs:
        workflow = builder.build_from_intent(request.intent, request.context)

    return {
        "task_type": analysis.task_type,
        "backend": analysis.backend,
        "detected_workflow": analysis.detected_workflow,
        "confidence": analysis.confidence,
        "reasoning": analysis.reasoning,
        "missing_inputs": analysis.missing_inputs,
        "suggested_params": analysis.suggested_params,
        "workflow": workflow,
    }


@router.post("/build")
async def build_workflow(request: WorkflowBuildRequest):
    workflow = builder.build_workflow(
        request.workflow_key, request.inputs, request.overrides
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@router.post("/validate")
async def validate_workflow(request: WorkflowValidateRequest):
    result = validator.validate(request.workflow, strict=request.strict)
    return result.to_dict()


@router.get("/catalog", response_model=List[WorkflowCatalogItem])
async def get_catalog():
    return workflow_registry.get_catalog()


@router.get("/presets")
async def get_presets(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    include_public: bool = True,
):
    return preset_service.list_presets(
        user_id=user_id, include_public=include_public, category=category
    )


@router.post("/presets", response_model=PresetResponse)
async def create_preset(preset: PresetCreate, user_id: str = "default"):
    created = preset_service.create_preset(
        name=preset.name,
        workflow_key=preset.workflow_key,
        inputs=preset.inputs,
        user_id=user_id,
        description=preset.description or "",
        tags=preset.tags,
        is_public=preset.is_public,
    )

    if not created:
        raise HTTPException(status_code=400, detail="Failed to create preset")

    return PresetResponse(
        id=created.id,
        name=created.name,
        workflow_key=created.workflow_key,
        description=created.description,
        category=created.category,
        backend=created.backend,
        tags=created.tags,
        is_public=created.is_public,
        created_by=created.created_by,
        created_at=created.created_at.isoformat(),
    )


@router.get("/presets/{preset_id}")
async def get_preset(preset_id: str):
    preset = preset_service.get_preset(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")

    return {
        "id": preset.id,
        "name": preset.name,
        "workflow_key": preset.workflow_key,
        "inputs": preset.inputs,
        "description": preset.description,
        "category": preset.category,
        "backend": preset.backend,
        "tags": preset.tags,
        "is_public": preset.is_public,
        "created_by": preset.created_by,
        "created_at": preset.created_at.isoformat(),
    }
