import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.storage import (
    IngestEventType,
    IngestScan,
    IngestScanStatus,
    MediaAsset,
    MediaAssetStatus,
    MediaAssetType,
    StorageAuthorization,
    StorageAuthorizationStatus,
    StorageSource,
    StorageWatchPath,
    StorageWatchPathStatus,
)
from services.logging_service import logger
from services.storage_service import storage_service


class IngestService:
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".mxf", ".avi", ".mkv", ".webm"}
    AUDIO_EXTENSIONS = {".wav", ".mp3", ".aac", ".flac", ".aif", ".aiff", ".m4a"}
    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".bmp",
        ".gif",
        ".webp",
        ".exr",
    }
    DOCUMENT_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".csv",
        ".xls",
        ".xlsx",
    }

    def normalize_path(self, path: str) -> str:
        return os.path.realpath(os.path.normpath(path.strip()))

    def infer_asset_type(self, file_path: str, mime_type: Optional[str]) -> str:
        extension = Path(file_path).suffix.lower()
        if extension in self.VIDEO_EXTENSIONS:
            return MediaAssetType.VIDEO
        if extension in self.AUDIO_EXTENSIONS:
            return MediaAssetType.AUDIO
        if extension in self.IMAGE_EXTENSIONS:
            return MediaAssetType.IMAGE
        if extension in self.DOCUMENT_EXTENSIONS:
            return MediaAssetType.DOCUMENT
        if mime_type:
            if mime_type.startswith("video/"):
                return MediaAssetType.VIDEO
            if mime_type.startswith("audio/"):
                return MediaAssetType.AUDIO
            if mime_type.startswith("image/"):
                return MediaAssetType.IMAGE
            if mime_type in {"application/pdf", "text/plain", "text/csv"}:
                return MediaAssetType.DOCUMENT
        return MediaAssetType.OTHER

    def is_path_within(self, child_path: str, parent_path: str) -> bool:
        try:
            child = self.normalize_path(child_path)
            parent = self.normalize_path(parent_path)
            return os.path.commonpath([child, parent]) == parent
        except ValueError:
            return False

    def compute_relative_path(self, canonical_path: str, base_path: str) -> str:
        canonical = self.normalize_path(canonical_path)
        base = self.normalize_path(base_path)
        if self.is_path_within(canonical, base):
            return os.path.relpath(canonical, base)
        return os.path.basename(canonical)

    async def list_scans(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[IngestScan]:
        query = select(IngestScan).where(IngestScan.organization_id == organization_id)
        if project_id:
            query = query.where(IngestScan.project_id == project_id)
        if source_id:
            query = query.where(IngestScan.storage_source_id == source_id)
        if status:
            query = query.where(IngestScan.status == status.strip().lower())
        query = query.order_by(IngestScan.started_at.desc(), IngestScan.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_scan(
        self, db: AsyncSession, scan_id: str, organization_id: str
    ) -> Optional[IngestScan]:
        result = await db.execute(
            select(IngestScan).where(
                IngestScan.id == scan_id,
                IngestScan.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_assets(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: Optional[str] = None,
        source_id: Optional[str] = None,
        status: Optional[str] = None,
        asset_type: Optional[str] = None,
    ) -> list[MediaAsset]:
        query = select(MediaAsset).where(MediaAsset.organization_id == organization_id)
        if project_id:
            query = query.where(MediaAsset.project_id == project_id)
        if source_id:
            query = query.where(MediaAsset.storage_source_id == source_id)
        if status:
            query = query.where(MediaAsset.status == status.strip().lower())
        if asset_type:
            query = query.where(MediaAsset.asset_type == asset_type.strip().lower())
        query = query.order_by(MediaAsset.discovered_at.desc(), MediaAsset.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_asset(
        self, db: AsyncSession, asset_id: str, organization_id: str
    ) -> Optional[MediaAsset]:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def launch_scan(
        self,
        db: AsyncSession,
        source: StorageSource,
        created_by: Optional[str] = None,
        watch_path_id: Optional[str] = None,
    ) -> IngestScan:
        eligible_watch_paths = await self._get_eligible_watch_paths(
            db, source, watch_path_id
        )
        if not eligible_watch_paths:
            raise HTTPException(
                status_code=400,
                detail="No active authorized watch paths available for scanning",
            )

        scan = IngestScan(
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=str(source.id),
            watch_path_id=watch_path_id,
            status=IngestScanStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
            created_by=created_by,
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)

        await storage_service.log_ingest_event(
            db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=str(source.id),
            event_type=IngestEventType.SCAN_STARTED,
            event_payload={
                "scan_id": str(scan.id),
                "watch_path_ids": [str(watch.id) for watch in eligible_watch_paths],
            },
            created_by=created_by,
        )

        files_discovered = 0
        files_indexed = 0
        files_skipped = 0
        warnings: list[str] = []

        try:
            for watch_path in eligible_watch_paths:
                normalized_watch_path = self.normalize_path(str(watch_path.watch_path))
                if not os.path.isdir(normalized_watch_path):
                    files_skipped += 1
                    warnings.append(
                        f"Watch path is not accessible directory: {normalized_watch_path}"
                    )
                    setattr(watch_path, "last_validated_at", datetime.now(timezone.utc))
                    continue

                setattr(watch_path, "last_validated_at", datetime.now(timezone.utc))

                for root, dirs, files in os.walk(normalized_watch_path):
                    dirs[:] = [
                        directory for directory in dirs if not directory.startswith(".")
                    ]
                    for file_name in files:
                        candidate_path = os.path.join(root, file_name)
                        files_discovered += 1
                        try:
                            await self._upsert_asset(
                                db=db,
                                source=source,
                                watch_path=watch_path,
                                scan=scan,
                                file_path=candidate_path,
                                created_by=created_by,
                            )
                            files_indexed += 1
                        except OSError as asset_error:
                            files_skipped += 1
                            warnings.append(str(asset_error))
                            logger.warning(
                                "Skipping asset during scan %s for source %s: %s",
                                scan.id,
                                source.id,
                                asset_error,
                            )

            scan.files_discovered_count = files_discovered
            scan.files_indexed_count = files_indexed
            scan.files_skipped_count = files_skipped
            scan.finished_at = datetime.now(timezone.utc)
            scan.status = IngestScanStatus.COMPLETED
            scan.error_message = "; ".join(warnings) if warnings else None
            await db.commit()
            await db.refresh(scan)

            await storage_service.log_ingest_event(
                db,
                organization_id=source.organization_id,
                project_id=source.project_id,
                storage_source_id=str(source.id),
                event_type=IngestEventType.SCAN_COMPLETED,
                event_payload={
                    "scan_id": str(scan.id),
                    "files_discovered_count": files_discovered,
                    "files_indexed_count": files_indexed,
                    "files_skipped_count": files_skipped,
                },
                created_by=created_by,
            )
            return scan
        except HTTPException:
            raise
        except Exception as scan_error:
            await db.rollback()
            scan.status = IngestScanStatus.FAILED
            scan.finished_at = datetime.now(timezone.utc)
            scan.error_message = str(scan_error)
            db.add(scan)
            await db.commit()
            await db.refresh(scan)
            await storage_service.log_ingest_event(
                db,
                organization_id=source.organization_id,
                project_id=source.project_id,
                storage_source_id=str(source.id),
                event_type=IngestEventType.SCAN_FAILED,
                event_payload={"scan_id": str(scan.id), "error": str(scan_error)},
                created_by=created_by,
            )
            raise HTTPException(status_code=500, detail="Scan failed") from scan_error

    async def _get_eligible_watch_paths(
        self,
        db: AsyncSession,
        source: StorageSource,
        watch_path_id: Optional[str],
    ) -> list[StorageWatchPath]:
        query = select(StorageWatchPath).where(
            StorageWatchPath.storage_source_id == str(source.id),
            StorageWatchPath.status == StorageWatchPathStatus.ACTIVE,
        )
        if watch_path_id:
            query = query.where(StorageWatchPath.id == watch_path_id)

        watch_path_result = await db.execute(query)
        watch_paths = watch_path_result.scalars().all()
        if watch_path_id and not watch_paths:
            raise HTTPException(status_code=404, detail="Watch path not found")

        auth_result = await db.execute(
            select(StorageAuthorization).where(
                StorageAuthorization.storage_source_id == str(source.id),
                StorageAuthorization.status == StorageAuthorizationStatus.ACTIVE,
            )
        )
        authorizations = auth_result.scalars().all()
        active_authorizations = [
            authorization
            for authorization in authorizations
            if authorization.revoked_at is None
            and (
                authorization.expires_at is None
                or authorization.expires_at >= datetime.now(timezone.utc)
            )
        ]

        eligible: list[StorageWatchPath] = []
        for watch_path in watch_paths:
            if not self.is_path_within(
                str(watch_path.watch_path), str(source.mount_path)
            ):
                continue
            if any(
                self.is_path_within(
                    str(watch_path.watch_path), str(authorization.scope_path)
                )
                for authorization in active_authorizations
            ):
                eligible.append(watch_path)
        return eligible

    async def _upsert_asset(
        self,
        db: AsyncSession,
        source: StorageSource,
        watch_path: StorageWatchPath,
        scan: IngestScan,
        file_path: str,
        created_by: Optional[str],
    ) -> MediaAsset:
        canonical_path = self.normalize_path(file_path)
        file_stat = os.stat(canonical_path)
        mime_type, _ = mimetypes.guess_type(canonical_path)
        relative_path = self.compute_relative_path(
            canonical_path, str(watch_path.watch_path)
        )
        file_extension = Path(canonical_path).suffix.lower().lstrip(".")
        asset_type = self.infer_asset_type(canonical_path, mime_type)
        modified_at = datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc)

        existing_result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.storage_source_id == str(source.id),
                MediaAsset.canonical_path == canonical_path,
            )
        )
        asset = existing_result.scalar_one_or_none()

        if asset is None:
            asset = MediaAsset(
                organization_id=source.organization_id,
                project_id=source.project_id,
                storage_source_id=str(source.id),
                watch_path_id=str(watch_path.id),
                ingest_scan_id=str(scan.id),
                file_name=os.path.basename(canonical_path),
                relative_path=relative_path,
                canonical_path=canonical_path,
                file_extension=file_extension,
                mime_type=mime_type,
                asset_type=asset_type,
                file_size=int(file_stat.st_size),
                modified_at=modified_at,
                discovered_at=datetime.now(timezone.utc),
                status=MediaAssetStatus.INDEXED,
                created_by=created_by,
            )
            db.add(asset)
        else:
            asset.watch_path_id = str(watch_path.id)
            asset.ingest_scan_id = str(scan.id)
            asset.file_name = os.path.basename(canonical_path)
            asset.relative_path = relative_path
            asset.file_extension = file_extension
            asset.mime_type = mime_type
            asset.asset_type = asset_type
            asset.file_size = int(file_stat.st_size)
            asset.modified_at = modified_at
            asset.discovered_at = datetime.now(timezone.utc)
            asset.status = MediaAssetStatus.INDEXED
            if created_by:
                asset.created_by = created_by

        await db.flush()
        return asset


ingest_service = IngestService()
