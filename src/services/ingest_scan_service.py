from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import mimetypes
import os

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ingest_handshake import (
    StorageAuthorization,
    StorageSource,
    StorageWatchPath,
)
from models.ingest_scan import IngestScan, MediaAsset
from services.storage_handshake_service import (
    get_active_authorization,
    get_owned_storage_source,
    log_ingest_event,
    normalize_mounted_path,
    resolve_organization_id,
)


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mxf", ".avi", ".mkv", ".wmv"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".aac", ".flac", ".aif", ".aiff", ".m4a"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".heic"}
DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".csv",
    ".xls",
    ".xlsx",
    ".rtf",
}


def determine_asset_type(file_extension: str) -> str:
    extension = file_extension.lower()
    if extension in VIDEO_EXTENSIONS:
        return "video"
    if extension in AUDIO_EXTENSIONS:
        return "audio"
    if extension in IMAGE_EXTENSIONS:
        return "image"
    if extension in DOCUMENT_EXTENSIONS:
        return "document"
    return "other"


def iter_files_in_watch_path(watch_path: str) -> Iterable[Tuple[str, os.stat_result]]:
    for root, _dirs, files in os.walk(watch_path):
        for file_name in files:
            candidate = os.path.join(root, file_name)
            try:
                stat_result = os.stat(candidate)
            except OSError:
                continue
            yield candidate, stat_result


def get_relative_path(base_mount_path: str, candidate_path: str) -> str:
    mount = Path(normalize_mounted_path(base_mount_path))
    candidate = Path(normalize_mounted_path(candidate_path))
    try:
        return str(candidate.relative_to(mount))
    except ValueError:
        return candidate.name


async def get_owned_scan(
    db: AsyncSession,
    scan_id: str,
    organization_id: Optional[str],
    user_id: str,
) -> IngestScan:
    filters = [IngestScan.id == scan_id, IngestScan.created_by == user_id]
    if organization_id is not None:
        filters.append(IngestScan.organization_id == organization_id)

    result = await db.execute(select(IngestScan).where(and_(*filters)))
    scan = result.scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Ingest scan not found")
    return scan


async def get_owned_asset(
    db: AsyncSession,
    asset_id: str,
    organization_id: Optional[str],
    user_id: str,
) -> MediaAsset:
    filters = [MediaAsset.id == asset_id, MediaAsset.created_by == user_id]
    if organization_id is not None:
        filters.append(MediaAsset.organization_id == organization_id)

    result = await db.execute(select(MediaAsset).where(and_(*filters)))
    asset = result.scalar_one_or_none()
    if asset is None:
        raise HTTPException(status_code=404, detail="Media asset not found")
    return asset


async def get_watch_paths_for_scan(
    db: AsyncSession,
    source: StorageSource,
    requested_watch_path_id: Optional[str] = None,
) -> List[StorageWatchPath]:
    authorization = await get_active_authorization(db, source.id)
    if authorization is None:
        raise HTTPException(
            status_code=400,
            detail="No active authorization found for this storage source",
        )

    filters = [
        StorageWatchPath.storage_source_id == source.id,
        StorageWatchPath.status == "active",
    ]
    if requested_watch_path_id:
        filters.append(StorageWatchPath.id == requested_watch_path_id)

    result = await db.execute(select(StorageWatchPath).where(and_(*filters)))
    watch_paths = result.scalars().all()
    if not watch_paths:
        raise HTTPException(
            status_code=400, detail="No active watch paths available for scan"
        )

    authorized_root = Path(normalize_mounted_path(authorization.scope_path))
    scoped_watch_paths: List[StorageWatchPath] = []
    for watch_path in watch_paths:
        normalized = Path(normalize_mounted_path(watch_path.watch_path))
        try:
            normalized.relative_to(authorized_root)
            scoped_watch_paths.append(watch_path)
        except ValueError:
            continue

    if not scoped_watch_paths:
        raise HTTPException(
            status_code=400, detail="No watch paths are within authorized scope"
        )

    return scoped_watch_paths


async def run_manual_scan(
    db: AsyncSession,
    source: StorageSource,
    watch_paths: List[StorageWatchPath],
    created_by: str,
) -> IngestScan:
    scan = IngestScan(
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        watch_path_id=watch_paths[0].id if len(watch_paths) == 1 else None,
        status="running",
        started_at=datetime.utcnow(),
        created_by=created_by,
    )
    db.add(scan)
    await db.flush()

    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="ingest_scan.started",
        payload={"scan_id": scan.id, "watch_path_count": len(watch_paths)},
        created_by=created_by,
    )

    discovered = 0
    indexed = 0
    skipped = 0

    try:
        for watch_path in watch_paths:
            watch_root = normalize_mounted_path(watch_path.watch_path)
            for candidate_path, stat_result in iter_files_in_watch_path(watch_root):
                discovered += 1
                canonical_path = normalize_mounted_path(candidate_path)

                existing_result = await db.execute(
                    select(MediaAsset).where(
                        and_(
                            MediaAsset.storage_source_id == source.id,
                            MediaAsset.canonical_path == canonical_path,
                        )
                    )
                )
                existing_asset = existing_result.scalar_one_or_none()
                if existing_asset is not None:
                    skipped += 1
                    continue

                file_name = Path(canonical_path).name
                extension = Path(canonical_path).suffix.lower()
                mime_type, _encoding = mimetypes.guess_type(file_name)
                asset = MediaAsset(
                    organization_id=source.organization_id,
                    project_id=source.project_id,
                    storage_source_id=source.id,
                    watch_path_id=watch_path.id,
                    ingest_scan_id=scan.id,
                    file_name=file_name,
                    relative_path=get_relative_path(source.mount_path, canonical_path),
                    canonical_path=canonical_path,
                    file_extension=extension,
                    mime_type=mime_type,
                    asset_type=determine_asset_type(extension),
                    file_size=stat_result.st_size,
                    modified_at=datetime.utcfromtimestamp(stat_result.st_mtime),
                    discovered_at=datetime.utcnow(),
                    status="indexed",
                    created_by=created_by,
                )
                db.add(asset)
                await db.flush()
                indexed += 1

                await log_ingest_event(
                    db=db,
                    organization_id=source.organization_id,
                    project_id=source.project_id,
                    storage_source_id=source.id,
                    event_type="media_asset.indexed",
                    payload={
                        "scan_id": scan.id,
                        "asset_id": asset.id,
                        "canonical_path": asset.canonical_path,
                        "asset_type": asset.asset_type,
                    },
                    created_by=created_by,
                )

        scan.status = "completed"
        scan.finished_at = datetime.utcnow()
        scan.files_discovered_count = discovered
        scan.files_indexed_count = indexed
        scan.files_skipped_count = skipped
        await log_ingest_event(
            db=db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=source.id,
            event_type="ingest_scan.completed",
            payload={
                "scan_id": scan.id,
                "files_discovered_count": discovered,
                "files_indexed_count": indexed,
                "files_skipped_count": skipped,
            },
            created_by=created_by,
        )
    except Exception as exc:
        scan.status = "failed"
        scan.finished_at = datetime.utcnow()
        scan.files_discovered_count = discovered
        scan.files_indexed_count = indexed
        scan.files_skipped_count = skipped
        scan.error_message = str(exc)
        await log_ingest_event(
            db=db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=source.id,
            event_type="ingest_scan.failed",
            payload={"scan_id": scan.id, "error_message": scan.error_message},
            created_by=created_by,
        )
        raise

    await db.flush()
    await db.refresh(scan)
    return scan
