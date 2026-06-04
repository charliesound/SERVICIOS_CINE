"""
Budget routes.
API endpoints for budget estimation.
"""

import json
import csv
from datetime import datetime
from io import StringIO
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.module_access import require_module_access
from dependencies.tenant_context import (
    get_tenant_context,
    require_organization,
    require_write_permission,
    validate_project_access,
)
from models.budget_estimator import BudgetEstimate, BudgetLineItem, BUDGET_LEVELS
from models.core import Project
from schemas.auth_schema import TenantContext
from services.budget_estimator_service import (
    generate_budget_from_project,
    generate_budget_from_text,
    recalculate_budget,
    archive_budget,
    get_active_budget,
    get_budget_by_id,
    list_budgets,
    get_budget_lines,
)
from services.role_permission_service import (
    get_permissions_for_role,
    get_role_default,
)
from services.project_access_service import check_permission


router = APIRouter(
    prefix="/api/projects/{project_id}/budgets",
    tags=["budgets"],
    dependencies=[
        Depends(get_tenant_context),
        Depends(require_module_access("budget_lite")),
    ],
)


class GenerateBudgetPayload(BaseModel):
    level: str = "medium"
    script_text: Optional[str] = None


class RecalculatePayload(BaseModel):
    level: str


def _budget_to_dict(budget: BudgetEstimate, role: Optional[str] = None) -> dict:
    """Convert budget to dict with role summary."""
    result = {
        "id": budget.id,
        "project_id": budget.project_id,
        "title": budget.title,
        "currency": budget.currency,
        "budget_level": budget.budget_level,
        "status": budget.status,
        "total_min": budget.total_min,
        "total_estimated": budget.total_estimated,
        "total_max": budget.total_max,
        "contingency_percent": budget.contingency_percent,
        "assumptions_json": budget.assumptions_json or [],
        "role_summaries_json": budget.role_summaries_json or {},
        "created_at": budget.created_at.isoformat() if budget.created_at else None,
    }
    
    if role and budget.role_summaries_json:
        result["role_summary"] = budget.role_summaries_json.get(role, {})
    
    return result


def _line_to_dict(line: BudgetLineItem) -> dict:
    return {
        "id": line.id,
        "category": line.category,
        "subcategory": line.subcategory,
        "description": line.description,
        "unit": line.unit,
        "quantity": line.quantity,
        "unit_cost_min": line.unit_cost_min,
        "unit_cost_estimated": line.unit_cost_estimated,
        "unit_cost_max": line.unit_cost_max,
        "total_min": line.total_min,
        "total_estimated": line.total_estimated,
        "total_max": line.total_max,
        "source": line.source,
        "confidence": line.confidence,
        "notes": line.notes,
    }


async def _check_budget_access(
    project_id: str,
    tenant: TenantContext,
    db: AsyncSession,
) -> None:
    """Check user has access to project budget."""
    has_perm = await check_permission(
        db, project_id, tenant.user_id, "budget.view"
    )
    if has_perm:
        return
    
    from services.role_permission_service import has_admin_access
    from models.core import User
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == tenant.user_id)
    )
    user = result.scalar_one_or_none()
    if user and has_admin_access(get_role_default(user.role)):
        return
    raise HTTPException(status_code=403, detail="Permission denied")


@router.get("")
async def list_project_budgets(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_organization),
):
    """List all budgets for a project."""
    await _check_budget_access(project_id, _tenant, db)
    
    budgets = await list_budgets(db, project_id)
    return {"budgets": [_budget_to_dict(b) for b in budgets]}


@router.post("/generate")
async def generate_budget(
    project_id: str,
    payload: GenerateBudgetPayload,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Generate a budget estimate from project data or script text."""
    has_perm = await check_permission(
        db, project_id, _tenant.user_id, "budget.generate"
    )
    if not has_perm:
        raise HTTPException(status_code=403, detail="Cannot generate budget")
    
    if payload.level not in BUDGET_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid level: {payload.level}")
    
    organization_id = project.organization_id
    
    user_role = _tenant.role
    permissions = get_permissions_for_role(get_role_default(user_role))
    
    if "budget.generate" not in permissions:
        raise HTTPException(status_code=403, detail="Cannot generate budget")
    
    script_text = payload.script_text
    source_script_version_id = None
    
    if not script_text:
        if project.script_text:
            script_text = project.script_text
        else:
            from models.script_versioning import ScriptVersion
            from sqlalchemy import select
            result = await db.execute(
                select(ScriptVersion).where(
                    ScriptVersion.project_id == project_id,
                    ScriptVersion.status == "active"
                )
            )
            sv = result.scalars().first()
            if sv:
                script_text = sv.script_text
                source_script_version_id = sv.id
    
    estimate = await generate_budget_from_text(
        db, project_id, organization_id, script_text or "",
        payload.level, _tenant.user_id,
        source_script_version_id, None
    )
    
    return {"budget": _budget_to_dict(estimate)}


@router.get("/active")
async def get_active_budget_endpoint(
    project_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_organization),
):
    """Get the active budget for a project."""
    await _check_budget_access(project_id, _tenant, db)
    
    budget = await get_active_budget(db, project_id)
    if not budget:
        raise HTTPException(status_code=404, detail="No active budget")
    
    return {"budget": _budget_to_dict(budget, role)}


@router.get("/{budget_id}")
async def get_budget(
    project_id: str,
    budget_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_organization),
):
    """Get a specific budget."""
    await _check_budget_access(project_id, _tenant, db)
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    if budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    lines = await get_budget_lines(db, budget_id)
    
    return {
        "budget": _budget_to_dict(budget, role),
        "lines": [_line_to_dict(l) for l in lines],
    }


@router.post("/{budget_id}/activate")
async def activate_budget(
    project_id: str,
    budget_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Activate a budget."""
    has_perm = await check_permission(
        db, project_id, _tenant.user_id, "budget.generate"
    )
    if not has_perm:
        raise HTTPException(status_code=403, detail="Cannot activate budget")
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget or budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget.status = "active"
    await db.commit()
    await db.refresh(budget)
    
    return {"budget": _budget_to_dict(budget)}


@router.post("/{budget_id}/recalculate")
async def recalculate_budget_endpoint(
    project_id: str,
    budget_id: str,
    payload: RecalculatePayload,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Recalculate budget with new level."""
    has_perm = await check_permission(
        db, project_id, _tenant.user_id, "budget.generate"
    )
    if not has_perm:
        raise HTTPException(status_code=403, detail="Cannot recalculate budget")
    
    if payload.level not in BUDGET_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid level: {payload.level}")
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget or budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget = await recalculate_budget(db, budget_id, payload.level)
    
    return {"budget": _budget_to_dict(budget)}


@router.post("/{budget_id}/archive")
async def archive_budget_endpoint(
    project_id: str,
    budget_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_write_permission),
):
    """Archive a budget."""
    has_perm = await check_permission(
        db, project_id, _tenant.user_id, "budget.generate"
    )
    if not has_perm:
        raise HTTPException(status_code=403, detail="Cannot archive budget")
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget or budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget = await archive_budget(db, budget_id)
    
    return {"budget": _budget_to_dict(budget)}


@router.get("/{budget_id}/export/json")
async def export_budget_json(
    project_id: str,
    budget_id: str,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_organization),
):
    """Export budget as JSON."""
    await _check_budget_access(project_id, _tenant, db)
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget or budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    lines = await get_budget_lines(db, budget_id)
    
    export_data = {
        "budget": _budget_to_dict(budget, role),
        "lines": [_line_to_dict(l) for l in lines],
        "exported_at": datetime.utcnow().isoformat(),
    }
    
    return Response(
        content=json.dumps(export_data, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=budget_{budget_id}.json"},
    )


@router.get("/{budget_id}/export/csv")
async def export_budget_csv(
    project_id: str,
    budget_id: str,
    db: AsyncSession = Depends(get_db),
    project: Project = Depends(validate_project_access),
    _tenant: TenantContext = Depends(require_organization),
):
    """Export budget lines as CSV."""
    await _check_budget_access(project_id, _tenant, db)
    
    budget = await get_budget_by_id(db, budget_id)
    if not budget or budget.project_id != project_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    lines = await get_budget_lines(db, budget_id)
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "category", "description", "unit", "quantity",
        "unit_cost_estimated", "total_estimated", "confidence", "notes"
    ])
    
    for line in lines:
        writer.writerow([
            line.category,
            line.description or "",
            line.unit or "",
            line.quantity,
            line.unit_cost_estimated,
            line.total_estimated,
            line.confidence,
            line.notes or "",
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=budget_{budget_id}.csv"},
    )
