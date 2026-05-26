from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context, TenantContext
from models.core import Project
from schemas.character_bible_schema import (
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleEntryCreate,
    CharacterBibleEntryUpdate,
    CharacterBibleListResponse,
    CharacterBibleResolveRequest,
    CharacterBibleResolveResult,
    CharacterLookVariant,
    LookVariantCreate,
    ReferenceAssetCreate,
    TraceResponse,
)
from services.character_bible_service import character_bible_service

router = APIRouter(
    prefix="/api/projects/{project_id}/character-bible",
    tags=["character-bible"],
)


async def _get_project_or_404(
    project_id: str,
    tenant: TenantContext,
    db: AsyncSession,
) -> Project:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == str(tenant.organization_id),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=CharacterBibleListResponse)
async def list_character_bible(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CharacterBibleListResponse:
    await _get_project_or_404(project_id, tenant, db)
    entries = character_bible_service.list_entries(project_id)
    return CharacterBibleListResponse(entries=entries, total=len(entries))


@router.get("/{character_id}", response_model=CharacterBibleEntry)
async def get_character_bible_entry(
    project_id: str,
    character_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CharacterBibleEntry:
    await _get_project_or_404(project_id, tenant, db)
    entry = character_bible_service.get_entry(project_id, character_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Character bible entry not found")
    return entry


@router.put("/{character_id}", response_model=CharacterBibleEntry)
async def create_or_update_character_bible_entry(
    project_id: str,
    character_id: str,
    payload: CharacterBibleEntryCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CharacterBibleEntry:
    await _get_project_or_404(project_id, tenant, db)
    if payload.character_id != character_id:
        raise HTTPException(status_code=400, detail="character_id in path and body must match")
    entry = character_bible_service.create_or_update_entry(project_id, payload)
    return entry


@router.post("/{character_id}/look-variants", response_model=CharacterLookVariant)
async def add_look_variant(
    project_id: str,
    character_id: str,
    payload: LookVariantCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CharacterLookVariant:
    await _get_project_or_404(project_id, tenant, db)
    variant = character_bible_service.add_look_variant(project_id, character_id, payload)
    if variant is None:
        raise HTTPException(status_code=404, detail="Character bible entry not found")
    return variant


@router.post("/{character_id}/references", response_model=ApprovedReferenceAsset)
async def add_reference(
    project_id: str,
    character_id: str,
    payload: ReferenceAssetCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ApprovedReferenceAsset:
    await _get_project_or_404(project_id, tenant, db)
    if not payload.asset_id.strip():
        raise HTTPException(status_code=400, detail="asset_id must not be empty")
    if any(p in payload.asset_id for p in ("/", "\\", "..")):
        raise HTTPException(status_code=400, detail="Invalid asset_id format")
    ref = character_bible_service.add_reference(project_id, character_id, payload)
    if ref is None:
        raise HTTPException(status_code=404, detail="Character bible entry not found")
    return ref


@router.post("/{character_id}/resolve", response_model=CharacterBibleResolveResult)
async def resolve_character(
    project_id: str,
    character_id: str,
    resolve_request: CharacterBibleResolveRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CharacterBibleResolveResult:
    await _get_project_or_404(project_id, tenant, db)
    if resolve_request.project_id != project_id:
        raise HTTPException(status_code=400, detail="project_id in path and body must match")
    if resolve_request.character_id != character_id:
        raise HTTPException(status_code=400, detail="character_id in path and body must match")
    result = character_bible_service.resolve(project_id, character_id, resolve_request)
    if result is None:
        raise HTTPException(status_code=404, detail="Character bible entry not found")
    return result


@router.get("/{character_id}/trace", response_model=TraceResponse)
async def get_character_trace(
    project_id: str,
    character_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> TraceResponse:
    await _get_project_or_404(project_id, tenant, db)
    trace = character_bible_service.get_trace(project_id, character_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Character bible entry not found")
    return TraceResponse(**trace)
