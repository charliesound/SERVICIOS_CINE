from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project, User as DBUser
from models.storage import IngestScan, MediaAsset
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.ingest_schema import (
    IngestScanListResponse,
    IngestScanResponse,
    MediaAssetListResponse,
    MediaAssetResponse,
)
from services.ingest_service import ingest_service


router = APIRouter(prefix="/api/ingest", tags=["ingest"])


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


async def _ensure_project_access(
    project_id: Optional[str], organization_id: str, db: AsyncSession
) -> None:
    if not project_id:
        return

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Access denied to this project")


def _scan_response(scan: IngestScan) -> IngestScanResponse:
    return IngestScanResponse(
        id=str(scan.id),
        organization_id=str(scan.organization_id),
        project_id=str(scan.project_id),
        storage_source_id=str(scan.storage_source_id),
        watch_path_id=str(scan.watch_path_id)
        if getattr(scan, "watch_path_id", None)
        else None,
        status=str(scan.status),
        started_at=cast(datetime, scan.started_at),
        finished_at=getattr(scan, "finished_at", None),
        files_discovered_count=int(getattr(scan, "files_discovered_count", 0)),
        files_indexed_count=int(getattr(scan, "files_indexed_count", 0)),
        files_skipped_count=int(getattr(scan, "files_skipped_count", 0)),
        error_message=getattr(scan, "error_message", None),
        created_by=getattr(scan, "created_by", None),
    )


def _asset_response(asset: MediaAsset) -> MediaAssetResponse:
    return MediaAssetResponse(
        id=str(asset.id),
        organization_id=str(asset.organization_id),
        project_id=str(asset.project_id),
        storage_source_id=str(asset.storage_source_id),
        watch_path_id=str(asset.watch_path_id)
        if getattr(asset, "watch_path_id", None)
        else None,
        ingest_scan_id=str(asset.ingest_scan_id)
        if getattr(asset, "ingest_scan_id", None)
        else None,
        file_name=str(asset.file_name),
        relative_path=str(asset.relative_path),
        canonical_path=str(asset.canonical_path),
        file_extension=str(asset.file_extension),
        mime_type=getattr(asset, "mime_type", None),
        asset_type=str(asset.asset_type),
        file_size=int(getattr(asset, "file_size", 0)),
        modified_at=getattr(asset, "modified_at", None),
        discovered_at=cast(datetime, asset.discovered_at),
        status=str(asset.status),
        created_by=getattr(asset, "created_by", None),
    )


@router.get("/scans", response_model=IngestScanListResponse)
async def list_ingest_scans(
    project_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> IngestScanListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    await _ensure_project_access(project_id, user_org_id, db)
    scans = await ingest_service.list_scans(
        db,
        organization_id=user_org_id,
        project_id=project_id,
        source_id=source_id,
        status=status,
    )
    return IngestScanListResponse(scans=[_scan_response(scan) for scan in scans])


@router.get("/scans/{scan_id}", response_model=IngestScanResponse)
async def get_ingest_scan_detail(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> IngestScanResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    scan = await ingest_service.get_scan(db, scan_id, user_org_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Ingest scan not found")
    return _scan_response(scan)


@router.get("/assets", response_model=MediaAssetListResponse)
async def list_media_assets(
    project_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> MediaAssetListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    await _ensure_project_access(project_id, user_org_id, db)
    assets = await ingest_service.list_assets(
        db,
        organization_id=user_org_id,
        project_id=project_id,
        source_id=source_id,
        status=status,
        asset_type=asset_type,
    )
    return MediaAssetListResponse(assets=[_asset_response(asset) for asset in assets])


@router.get("/assets/{asset_id}", response_model=MediaAssetResponse)
async def get_media_asset_detail(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> MediaAssetResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    asset = await ingest_service.get_asset(db, asset_id, user_org_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return _asset_response(asset)
