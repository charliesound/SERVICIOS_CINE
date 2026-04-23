import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from models.storage import (
    IngestEvent,
    IngestEventType,
    StorageAuthorization,
    StorageAuthorizationMode,
    StorageAuthorizationStatus,
    StorageSource,
    StorageSourceStatus,
    StorageWatchPath,
    StorageWatchPathStatus,
)


class StorageService:
    def normalize_path(self, path: str) -> str:
        normalized = os.path.normpath(path.strip())
        return normalized

    def validate_path_exists(self, path: str) -> dict[str, Any]:
        normalized = self.normalize_path(path)
        p = Path(normalized)

        metadata: dict[str, Any] = {
            "exists": p.exists(),
            "is_dir": False,
            "readable": False,
            "writable": False,
            "free_space": None,
            "total_space": None,
            "normalized_path": normalized,
        }

        if not metadata["exists"]:
            return metadata

        try:
            metadata["is_dir"] = p.is_dir()
        except (OSError, PermissionError):
            pass

        try:
            os.access(str(p), os.R_OK)
            metadata["readable"] = True
        except (OSError, PermissionError):
            pass

        try:
            os.access(str(p), os.W_OK)
            metadata["writable"] = True
        except (OSError, PermissionError):
            pass

        try:
            if os.name == "nt":
                import shutil

                usage = shutil.disk_usage(str(p))
                metadata["free_space"] = usage.free
                metadata["total_space"] = usage.total
            elif hasattr(os, "statvfs"):
                stat = os.statvfs(str(p))
                metadata["free_space"] = stat.f_bavail * stat.f_frsize
                metadata["total_space"] = stat.f_blocks * stat.f_frsize
        except Exception:
            pass

        return metadata

    async def create_storage_source(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
        name: str,
        source_type: str,
        mount_path: str,
        created_by: Optional[str] = None,
    ) -> StorageSource:
        normalized_mount_path = self.normalize_path(mount_path)

        existing_result = await db.execute(
            select(StorageSource).where(
                StorageSource.organization_id == organization_id,
                StorageSource.project_id == project_id,
                StorageSource.name == name,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Storage source with name '{name}' already exists in this project",
            )

        storage_source = StorageSource(
            organization_id=organization_id,
            project_id=project_id,
            name=name.strip(),
            source_type=source_type.strip(),
            mount_path=normalized_mount_path,
            status=StorageSourceStatus.ACTIVE,
            created_by=created_by,
        )
        db.add(storage_source)
        await db.commit()
        await db.refresh(storage_source)

        await self._log_ingest_event(
            db,
            organization_id=organization_id,
            project_id=project_id,
            storage_source_id=str(storage_source.id),
            event_type=IngestEventType.SOURCE_CREATED,
            event_payload={
                "name": name,
                "source_type": source_type,
                "mount_path": normalized_mount_path,
            },
            created_by=created_by,
        )

        return storage_source

    async def get_storage_source(
        self, db: AsyncSession, source_id: str
    ) -> Optional[StorageSource]:
        result = await db.execute(
            select(StorageSource).where(StorageSource.id == source_id)
        )
        return result.scalar_one_or_none()

    async def list_storage_sources(
        self, db: AsyncSession, organization_id: str, project_id: Optional[str] = None
    ) -> list[StorageSource]:
        query = select(StorageSource).where(
            StorageSource.organization_id == organization_id
        )
        if project_id:
            query = query.where(StorageSource.project_id == project_id)
        query = query.order_by(StorageSource.created_at.desc(), StorageSource.id.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def update_storage_source(
        self,
        db: AsyncSession,
        source: StorageSource,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> StorageSource:
        if name is not None:
            source.name = name.strip()
        if status is not None:
            normalized_status = status.strip().lower()
            if normalized_status not in (
                StorageSourceStatus.ACTIVE,
                StorageSourceStatus.INACTIVE,
                StorageSourceStatus.ERROR,
            ):
                raise HTTPException(status_code=400, detail="Invalid status value")
            source.status = normalized_status

        await db.commit()
        await db.refresh(source)
        return source

    async def validate_storage_source(
        self,
        db: AsyncSession,
        source: StorageSource,
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        metadata = self.validate_path_exists(source.mount_path)

        await self._log_ingest_event(
            db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=str(source.id),
            event_type=IngestEventType.SOURCE_VALIDATED,
            event_payload={
                "mount_path": source.mount_path,
                "metadata": metadata,
            },
            created_by=user_id,
        )

        return {
            "source_id": str(source.id),
            "mount_path": source.mount_path,
            "metadata": metadata,
        }

    async def authorize_storage_source(
        self,
        db: AsyncSession,
        source: StorageSource,
        authorization_mode: str,
        scope_path: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> StorageAuthorization:
        normalized_scope_path = self.normalize_path(scope_path)
        normalized_mode = authorization_mode.strip().lower()

        if normalized_mode not in (
            StorageAuthorizationMode.READ,
            StorageAuthorizationMode.WRITE,
            StorageAuthorizationMode.READ_WRITE,
        ):
            raise HTTPException(status_code=400, detail="Invalid authorization mode")

        authorization = StorageAuthorization(
            storage_source_id=str(source.id),
            authorization_mode=normalized_mode,
            scope_path=normalized_scope_path,
            status=StorageAuthorizationStatus.ACTIVE,
            granted_by=granted_by,
            granted_at=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        db.add(authorization)
        await db.commit()
        await db.refresh(authorization)

        await self._log_ingest_event(
            db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=str(source.id),
            event_type=IngestEventType.SOURCE_AUTHORIZED,
            event_payload={
                "authorization_id": str(authorization.id),
                "authorization_mode": normalized_mode,
                "scope_path": normalized_scope_path,
            },
            created_by=granted_by,
        )

        return authorization

    async def list_authorizations(
        self, db: AsyncSession, source_id: str
    ) -> list[StorageAuthorization]:
        result = await db.execute(
            select(StorageAuthorization)
            .where(StorageAuthorization.storage_source_id == source_id)
            .order_by(
                StorageAuthorization.granted_at.desc(), StorageAuthorization.id.desc()
            )
        )
        return result.scalars().all()

    async def create_watch_path(
        self,
        db: AsyncSession,
        source: StorageSource,
        watch_path: str,
    ) -> StorageWatchPath:
        normalized_watch_path = self.normalize_path(watch_path)

        existing_result = await db.execute(
            select(StorageWatchPath).where(
                StorageWatchPath.storage_source_id == str(source.id),
                StorageWatchPath.watch_path == normalized_watch_path,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Watch path already exists for this storage source",
            )

        watch = StorageWatchPath(
            storage_source_id=str(source.id),
            watch_path=normalized_watch_path,
            status=StorageWatchPathStatus.ACTIVE,
        )
        db.add(watch)
        await db.commit()
        await db.refresh(watch)

        await self._log_ingest_event(
            db,
            organization_id=source.organization_id,
            project_id=source.project_id,
            storage_source_id=str(source.id),
            event_type=IngestEventType.WATCH_PATH_ADDED,
            event_payload={"watch_path": normalized_watch_path},
        )

        return watch

    async def list_watch_paths(
        self, db: AsyncSession, source_id: str
    ) -> list[StorageWatchPath]:
        result = await db.execute(
            select(StorageWatchPath)
            .where(StorageWatchPath.storage_source_id == source_id)
            .order_by(StorageWatchPath.created_at.desc(), StorageWatchPath.id.desc())
        )
        return result.scalars().all()

    async def log_ingest_event(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
        event_type: str,
        event_payload: Optional[dict] = None,
        storage_source_id: Optional[str] = None,
        document_asset_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> IngestEvent:
        return await self._log_ingest_event(
            db,
            organization_id=organization_id,
            project_id=project_id,
            event_type=event_type,
            event_payload=event_payload,
            storage_source_id=storage_source_id,
            document_asset_id=document_asset_id,
            created_by=created_by,
        )

    async def _log_ingest_event(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str,
        event_type: str,
        event_payload: Optional[dict] = None,
        storage_source_id: Optional[str] = None,
        document_asset_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> IngestEvent:
        event = IngestEvent(
            organization_id=organization_id,
            project_id=project_id,
            storage_source_id=storage_source_id,
            document_asset_id=document_asset_id,
            event_type=event_type,
            event_payload_json=json.dumps(event_payload, ensure_ascii=False)
            if event_payload
            else None,
            created_by=created_by,
        )
        db.add(event)
        await db.commit()
        return event


storage_service = StorageService()
