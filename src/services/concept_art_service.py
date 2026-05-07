from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.core import Project
from schemas.auth_schema import TenantContext
from services.comfyui_model_inventory_service import ComfyUIInventoryError
from services.comfyui_pipeline_builder_service import build_optimal_comfyui_pipeline
from services.comfyui_workflow_template_service import build_compiled_workflow_preview


async def _get_project_for_tenant(
    db: AsyncSession, *, project_id: str, tenant: TenantContext
) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


def _build_internal_payload(
    task_type: str,
    prompt: str | None,
    negative_prompt: str | None,
    width: int | None,
    height: int | None,
    steps: int | None,
    cfg: float | None,
    seed: int | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "task_type": task_type,
        "generation_mode": "SELECTED_SCENES",
        "selected_scenes": [1],
        "dry_run": True,
    }
    if prompt:
        payload["prompt"] = prompt
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if width:
        payload["width"] = width
    if height:
        payload["height"] = height
    if steps:
        payload["steps"] = steps
    if cfg:
        payload["cfg"] = cfg
    if seed is not None:
        payload["seed"] = seed
    return payload


async def build_project_concept_art_compile_preview(
    db: AsyncSession,
    *,
    project_id: str,
    tenant: TenantContext,
    prompt: str | None = None,
    negative_prompt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    cfg: float | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    await _get_project_for_tenant(db, project_id=project_id, tenant=tenant)

    internal = _build_internal_payload(
        task_type="concept_art",
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        seed=seed,
    )
    try:
        plan = build_optimal_comfyui_pipeline(internal)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        compiled = build_compiled_workflow_preview(
            plan=plan,
            prompt=prompt,
            negative_prompt=negative_prompt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "status": "ok",
        "project_id": project_id,
        "workflow_id": compiled.get("workflow_id", plan.get("pipeline", {}).get("workflow_id")),
        "pipeline": plan.get("pipeline", {}),
        "compiled_workflow_preview": compiled,
    }


async def build_project_key_visual_compile_preview(
    db: AsyncSession,
    *,
    project_id: str,
    tenant: TenantContext,
    prompt: str | None = None,
    negative_prompt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    cfg: float | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    await _get_project_for_tenant(db, project_id=project_id, tenant=tenant)

    internal = _build_internal_payload(
        task_type="key_visual",
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        cfg=cfg,
        seed=seed,
    )
    try:
        plan = build_optimal_comfyui_pipeline(internal)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        compiled = build_compiled_workflow_preview(
            plan=plan,
            prompt=prompt,
            negative_prompt=negative_prompt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "status": "ok",
        "project_id": project_id,
        "workflow_id": compiled.get("workflow_id", plan.get("pipeline", {}).get("workflow_id")),
        "pipeline": plan.get("pipeline", {}),
        "compiled_workflow_preview": compiled,
    }
