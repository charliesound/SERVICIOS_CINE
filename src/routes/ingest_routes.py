from datetime import datetime
from typing import Optional, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies.tenant_context import get_tenant_context, TenantContext
from models.core import Project
from models.storage import IngestScan, MediaAsset
from schemas.ingest_schema import (
    IngestScanListResponse,
    IngestScanResponse,
    MediaAssetListResponse,
    MediaAssetResponse,
)
from services.ingest_service import ingest_service


router = APIRouter(prefix="/api/ingest", tags=["ingest"])


async def _ensure_project_access(
    project_id: Optional[str], tenant: TenantContext, db: AsyncSession
) -> None:
    if not project_id:
        return

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == str(tenant.organization_id),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")


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
        metadata_json=getattr(asset, "metadata_json", None),
        content_ref=getattr(asset, "content_ref", None),
        job_id=getattr(asset, "job_id", None),
        asset_source=getattr(asset, "asset_source", None),
    )


@router.get("/scans", response_model=IngestScanListResponse)
async def list_ingest_scans(
    project_id: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    ) -> IngestScanListResponse:
    await _ensure_project_access(project_id, tenant, db)
    scans = await ingest_service.list_scans(
        db,
        organization_id=str(tenant.organization_id),
        project_id=project_id,
        source_id=source_id,
        status=status,
    )
    return IngestScanListResponse(scans=[_scan_response(scan) for scan in scans])


@router.get("/scans/{scan_id}", response_model=IngestScanResponse)
async def get_ingest_scan_detail(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    ) -> IngestScanResponse:
    scan = await ingest_service.get_scan(db, scan_id, str(tenant.organization_id))
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
    tenant: TenantContext = Depends(get_tenant_context),
    ) -> MediaAssetListResponse:
    await _ensure_project_access(project_id, tenant, db)
    assets = await ingest_service.list_assets(
        db,
        organization_id=str(tenant.organization_id),
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
    tenant: TenantContext = Depends(get_tenant_context),
    ) -> MediaAssetResponse:
    asset = await ingest_service.get_asset(db, asset_id, str(tenant.organization_id))
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return _asset_response(asset)
