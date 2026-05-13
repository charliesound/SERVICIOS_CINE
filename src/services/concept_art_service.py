from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.core import Project, ProjectJob
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
    if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


async def list_dry_run_jobs(
    db: AsyncSession,
    *,
    project_id: str,
    tenant: TenantContext,
) -> list[dict[str, Any]]:
    await _get_project_for_tenant(db, project_id=project_id, tenant=tenant)
    result = await db.execute(
        select(ProjectJob)
        .where(
            ProjectJob.project_id == project_id,
            ProjectJob.organization_id == tenant.organization_id,
            ProjectJob.job_type.in_(["concept_art", "key_visual"]),
        )
        .order_by(ProjectJob.created_at.desc(), ProjectJob.id.desc())
    )
    jobs = result.scalars().all()
    output: list[dict[str, Any]] = []
    for j in jobs:
        rd: dict[str, Any] = {}
        if j.result_data:
            try:
                rd = json.loads(j.result_data)
            except Exception:
                rd = {}
        output.append({
            "job_id": str(j.id),
            "task_type": str(j.job_type),
            "status": str(j.status),
            "workflow_id": rd.get("workflow_id"),
            "model_family": rd.get("model_family"),
            "safe_to_render": rd.get("safe_to_render", False),
            "dry_run": rd.get("dry_run", True),
            "render_executed": rd.get("render_executed", False),
            "prompt_called": rd.get("prompt_called", False),
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "created_by": str(j.created_by) if j.created_by else None,
        })
    return output


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


async def _persist_dry_run_job(
    db: AsyncSession,
    *,
    project_id: str,
    tenant: TenantContext,
    task_type: str,
    plan: dict[str, Any],
    compiled: dict[str, Any],
) -> str:
    pipeline = plan.get("pipeline", {})
    result_data = {
        "task_type": task_type,
        "dry_run": True,
        "render_executed": False,
        "prompt_called": False,
        "workflow_id": compiled.get("workflow_id", pipeline.get("workflow_id")),
        "model_family": pipeline.get("model_family"),
        "models": {
            "unet": pipeline.get("unet"),
            "clip_l": pipeline.get("clip_l"),
            "t5xxl": pipeline.get("t5xxl"),
            "vae": pipeline.get("vae"),
        },
        "missing_models": pipeline.get("missing_models", []),
        "safe_to_render": pipeline.get("safe_to_render", False),
        "validation": compiled.get("validation"),
    }
    job = ProjectJob(
        organization_id=tenant.organization_id,
        project_id=project_id,
        job_type=task_type,
        status="dry_run_completed",
        result_data=json.dumps(result_data, default=str),
        created_by=tenant.user_id,
    )
    db.add(job)
    await db.flush()
    return str(job.id)


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

    job_id = await _persist_dry_run_job(
        db, project_id=project_id, tenant=tenant,
        task_type="concept_art", plan=plan, compiled=compiled,
    )

    return {
        "status": "ok",
        "project_id": project_id,
        "job_id": job_id,
        "workflow_id": compiled.get("workflow_id", plan.get("pipeline", {}).get("workflow_id")),
        "pipeline": plan.get("pipeline", {}),
        "compiled_workflow_preview": compiled,
        "dry_run": True,
        "render_executed": False,
        "prompt_called": False,
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

    job_id = await _persist_dry_run_job(
        db, project_id=project_id, tenant=tenant,
        task_type="key_visual", plan=plan, compiled=compiled,
    )

    return {
        "status": "ok",
        "project_id": project_id,
        "job_id": job_id,
        "workflow_id": compiled.get("workflow_id", plan.get("pipeline", {}).get("workflow_id")),
        "pipeline": plan.get("pipeline", {}),
        "compiled_workflow_preview": compiled,
        "dry_run": True,
        "render_executed": False,
        "prompt_called": False,
    }
