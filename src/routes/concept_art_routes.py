from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from services.comfyui_model_inventory_service import ComfyUIInventoryError
from services.concept_art_service import (
    build_project_concept_art_compile_preview,
    build_project_key_visual_compile_preview,
    list_dry_run_jobs,
)


router = APIRouter(prefix="/api/projects", tags=["concept-art"])


@router.post("/{project_id}/concept-art/compile-workflow-dry-run")
async def project_concept_art_compile_dry_run(
    project_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        result = await build_project_concept_art_compile_preview(
            db,
            project_id=project_id,
            tenant=tenant,
            prompt=payload.get("prompt"),
            negative_prompt=payload.get("negative_prompt"),
            width=payload.get("width"),
            height=payload.get("height"),
            steps=payload.get("steps"),
            cfg=payload.get("cfg"),
            seed=payload.get("seed"),
        )
        await db.commit()
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{project_id}/key-visual/compile-workflow-dry-run")
async def project_key_visual_compile_dry_run(
    project_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    try:
        result = await build_project_key_visual_compile_preview(
            db,
            project_id=project_id,
            tenant=tenant,
            prompt=payload.get("prompt"),
            negative_prompt=payload.get("negative_prompt"),
            width=payload.get("width"),
            height=payload.get("height"),
            steps=payload.get("steps"),
            cfg=payload.get("cfg"),
            seed=payload.get("seed"),
        )
        await db.commit()
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ComfyUIInventoryError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "inventory_found": False,
                "message": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{project_id}/concept-art/jobs")
async def project_concept_art_list_jobs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict:
    jobs = await list_dry_run_jobs(db, project_id=project_id, tenant=tenant)
    return {
        "status": "ok",
        "project_id": project_id,
        "jobs": jobs,
    }
