import os

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import BudgetEstimate, BudgetLineItem
from .services import generate_budget, recalculate_budget
from .core import verify_token

router = APIRouter(prefix="/api/budget", tags=["budget"])

VALID_LEVELS = {"low", "medium", "high"}


def get_db():
    from .main import SessionLocal
    if SessionLocal is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def require_auth(authorization: str = Header("")) -> dict:
    jwt_secret = os.getenv("JWT_SECRET", "")
    if not jwt_secret:
        return {"sub": "anonymous", "role": "admin"}
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ")
    try:
        return verify_token(token, jwt_secret)
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))


def budget_to_dict(b: BudgetEstimate) -> dict:
    return {
        "id": b.id,
        "project_id": b.project_id,
        "organization_id": b.organization_id,
        "title": b.title,
        "currency": b.currency,
        "budget_level": b.budget_level,
        "status": b.status,
        "total_min": b.total_min,
        "total_estimated": b.total_estimated,
        "total_max": b.total_max,
        "contingency_percent": b.contingency_percent,
        "assumptions": b.assumptions_json,
        "role_summaries": b.role_summaries_json,
        "created_by": b.created_by,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }


def line_to_dict(l: BudgetLineItem) -> dict:
    return {
        "id": l.id,
        "budget_estimate_id": l.budget_estimate_id,
        "category": l.category,
        "subcategory": l.subcategory,
        "description": l.description,
        "unit": l.unit,
        "quantity": l.quantity,
        "unit_cost_min": l.unit_cost_min,
        "unit_cost_estimated": l.unit_cost_estimated,
        "unit_cost_max": l.unit_cost_max,
        "total_min": l.total_min,
        "total_estimated": l.total_estimated,
        "total_max": l.total_max,
        "source": l.source,
        "confidence": l.confidence,
        "notes": l.notes,
    }


@router.get("/projects/{project_id}")
async def list_budgets(project_id: str, db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not project_id or len(project_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid project_id")
    result = db.execute(select(BudgetEstimate).where(BudgetEstimate.project_id == project_id).order_by(BudgetEstimate.created_at.desc()))
    budgets = result.scalars().all()
    return {"budgets": [budget_to_dict(b) for b in budgets]}


@router.get("/projects/{project_id}/active")
async def get_active_budget(project_id: str, db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not project_id or len(project_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid project_id")
    result = db.execute(select(BudgetEstimate).where(BudgetEstimate.project_id == project_id, BudgetEstimate.status == "active"))
    budget = result.scalars().first()
    return {"budget": budget_to_dict(budget) if budget else None}


@router.post("/projects/{project_id}/generate", status_code=201)
async def create_budget(
    project_id: str,
    level: str = Query("medium"),
    script_text: str = Query(""),
    organization_id: str = Query(""),
    db: Session = Depends(get_db),
    auth: dict = Depends(require_auth),
):
    if not project_id or len(project_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid project_id")
    if level not in VALID_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid level '{level}'. Must be one of: {', '.join(sorted(VALID_LEVELS))}")
    if len(script_text) > 100000:
        raise HTTPException(status_code=400, detail="Script text too long (max 100k chars)")
    budget = generate_budget(db, project_id, level, script_text, organization_id, auth.get("sub", ""))
    return {"budget": budget_to_dict(budget)}


@router.get("/templates")
async def list_templates(auth: dict = Depends(require_auth)):
    return {
        "templates": [
            {"id": "film_low", "name": "Largometraje bajo presupuesto", "default_level": "low"},
            {"id": "film_medium", "name": "Largometraje medio", "default_level": "medium"},
            {"id": "film_high", "name": "Largometraje alto", "default_level": "high"},
            {"id": "tv_series", "name": "Serie TV por episodio", "default_level": "medium"},
            {"id": "docu", "name": "Documental", "default_level": "low"},
        ]
    }


@router.get("/{budget_id}")
async def get_budget(budget_id: str, db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not budget_id or len(budget_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid budget_id")
    budget = db.get(BudgetEstimate, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    result = db.execute(select(BudgetLineItem).where(BudgetLineItem.budget_estimate_id == budget_id))
    lines = result.scalars().all()
    return {"budget": budget_to_dict(budget), "lines": [line_to_dict(l) for l in lines]}


@router.post("/{budget_id}/activate")
async def activate_budget(budget_id: str, db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not budget_id or len(budget_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid budget_id")
    budget = db.get(BudgetEstimate, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    result = db.execute(select(BudgetEstimate).where(BudgetEstimate.project_id == budget.project_id, BudgetEstimate.status == "active"))
    for active in result.scalars().all():
        active.status = "archived"
    budget.status = "active"
    db.commit()
    db.refresh(budget)
    return {"budget": budget_to_dict(budget)}


@router.post("/{budget_id}/recalculate")
async def recalculate(budget_id: str, level: str = Query("medium"), db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not budget_id or len(budget_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid budget_id")
    if level not in VALID_LEVELS:
        raise HTTPException(status_code=400, detail=f"Invalid level")
    try:
        budget = recalculate_budget(db, budget_id, level)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"budget": budget_to_dict(budget)}


@router.post("/{budget_id}/archive")
async def archive_budget(budget_id: str, db: Session = Depends(get_db), auth: dict = Depends(require_auth)):
    if not budget_id or len(budget_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid budget_id")
    budget = db.get(BudgetEstimate, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    budget.status = "archived"
    db.commit()
    db.refresh(budget)
    return {"budget": budget_to_dict(budget)}


@router.get("/templates")
async def list_templates(auth: dict = Depends(require_auth)):
    return {
        "templates": [
            {"id": "film_low", "name": "Largometraje bajo presupuesto", "default_level": "low"},
            {"id": "film_medium", "name": "Largometraje medio", "default_level": "medium"},
            {"id": "film_high", "name": "Largometraje alto", "default_level": "high"},
            {"id": "tv_series", "name": "Serie TV por episodio", "default_level": "medium"},
            {"id": "docu", "name": "Documental", "default_level": "low"},
        ]
    }
