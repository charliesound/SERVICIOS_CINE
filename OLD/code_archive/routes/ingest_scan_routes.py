from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.ingest_scan import IngestScan, MediaAsset
from routes.auth_routes import get_authenticated_user, get_token_payload
from schemas.ingest_scan_schema import (
    IngestScanCreate,
    IngestScanListResponse,
    IngestScanResponse,
    MediaAssetListResponse,
    MediaAssetResponse,
)
from services.ingest_scan_service import (
    get_owned_asset,
    get_owned_scan,
    get_watch_paths_for_scan,
    run_manual_scan,
)
from services.storage_handshake_service import (
    get_owned_storage_source,
    resolve_organization_id,
)

router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/storage-sources/{source_id}/scan", response_model=IngestScanResponse)
async def create_manual_scan(
    source_id: str,
    payload: IngestScanCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    source = await get_owned_storage_source(
        db, source_id, organization_id, user.user_id
    )
    watch_paths = await get_watch_paths_for_scan(db, source, payload.watch_path_id)
    scan = await run_manual_scan(db, source, watch_paths, user.user_id)
    return scan


@router.get("/ingest/scans", response_model=IngestScanListResponse)
async def list_ingest_scans(
    project_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    filters = [IngestScan.created_by == user.user_id]
    if organization_id is not None:
        filters.append(IngestScan.organization_id == organization_id)
    if project_id is not None:
        filters.append(IngestScan.project_id == project_id)
    if source_id is not None:
        filters.append(IngestScan.storage_source_id == source_id)
    if status is not None:
        filters.append(IngestScan.status == status)

    result = await db.execute(select(IngestScan).where(and_(*filters)))
    return IngestScanListResponse(items=result.scalars().all())


@router.get("/ingest/scans/{scan_id}", response_model=IngestScanResponse)
async def get_ingest_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    scan = await get_owned_scan(db, scan_id, organization_id, user.user_id)
    return scan


@router.get("/ingest/assets", response_model=MediaAssetListResponse)
async def list_media_assets(
    project_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    filters = [MediaAsset.created_by == user.user_id]
    if organization_id is not None:
        filters.append(MediaAsset.organization_id == organization_id)
    if project_id is not None:
        filters.append(MediaAsset.project_id == project_id)
    if source_id is not None:
        filters.append(MediaAsset.storage_source_id == source_id)
    if status is not None:
        filters.append(MediaAsset.status == status)
    if asset_type is not None:
        filters.append(MediaAsset.asset_type == asset_type)

    result = await db.execute(select(MediaAsset).where(and_(*filters)))
    return MediaAssetListResponse(items=result.scalars().all())


@router.get("/ingest/assets/{asset_id}", response_model=MediaAssetResponse)
async def get_media_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    asset = await get_owned_asset(db, asset_id, organization_id, user.user_id)
    return asset
