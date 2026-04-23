from datetime import datetime
from typing import Optional
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project, User as DBUser
from models.storage import (
    StorageAuthorization,
    StorageSource,
    StorageWatchPath,
)
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from schemas.ingest_schema import IngestScanLaunchRequest, IngestScanResponse
from schemas.storage_schema import (
    StorageAuthorizationCreate,
    StorageAuthorizationListResponse,
    StorageAuthorizationResponse as AuthResponseSchema,
    StorageHandshakeResponse,
    StorageSourceCreate,
    StorageSourceListResponse,
    StorageSourceResponse,
    StorageSourceUpdate,
    StorageSourceValidateResponse,
    StorageWatchPathCreate,
    StorageWatchPathListResponse,
    StorageWatchPathResponse,
)
from services.ingest_service import ingest_service
from services.storage_service import storage_service
from services.logging_service import logger


router = APIRouter(prefix="/api/storage-sources", tags=["storage-sources"])


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    result = await db.execute(select(DBUser).where(DBUser.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


async def _check_storage_source_access(
    source_id: str,
    user_id: str,
    db: AsyncSession,
) -> StorageSource:
    source = await storage_service.get_storage_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Storage source not found")

    user_org_id = await _get_user_org_id(user_id, db)
    if not user_org_id or source.organization_id != user_org_id:
        raise HTTPException(
            status_code=403, detail="Access denied to this storage source"
        )

    return source


def _source_response(source: StorageSource) -> StorageSourceResponse:
    return StorageSourceResponse(
        id=str(source.id),
        organization_id=str(source.organization_id),
        project_id=str(source.project_id),
        name=str(source.name),
        source_type=str(source.source_type),
        mount_path=str(source.mount_path),
        status=str(source.status),
        created_by=getattr(source, "created_by", None),
        created_at=cast(datetime, source.created_at),
        updated_at=cast(datetime, source.updated_at),
    )


def _authorization_response(auth: StorageAuthorization) -> AuthResponseSchema:
    return AuthResponseSchema(
        id=str(auth.id),
        storage_source_id=str(auth.storage_source_id),
        authorization_mode=str(auth.authorization_mode),
        scope_path=str(auth.scope_path),
        status=str(auth.status),
        granted_by=getattr(auth, "granted_by", None),
        granted_at=cast(datetime, auth.granted_at),
        expires_at=getattr(auth, "expires_at", None),
        revoked_at=getattr(auth, "revoked_at", None),
    )


def _watch_path_response(watch: StorageWatchPath) -> StorageWatchPathResponse:
    return StorageWatchPathResponse(
        id=str(watch.id),
        storage_source_id=str(watch.storage_source_id),
        watch_path=str(watch.watch_path),
        status=str(watch.status),
        last_validated_at=getattr(watch, "last_validated_at", None),
        created_at=cast(datetime, watch.created_at),
    )


def _scan_response(scan) -> IngestScanResponse:
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


@router.post("", response_model=StorageSourceResponse)
async def create_storage_source(
    payload: StorageSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageSourceResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    if payload.organization_id != user_org_id:
        raise HTTPException(
            status_code=403,
            detail="Cannot create storage source for a different organization",
        )

    project_result = await db.execute(
        select(Project).where(Project.id == payload.project_id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.organization_id != user_org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this project",
        )

    source = await storage_service.create_storage_source(
        db,
        organization_id=payload.organization_id,
        project_id=payload.project_id,
        name=payload.name,
        source_type=payload.source_type,
        mount_path=payload.mount_path,
        created_by=current_user.user_id,
    )

    return _source_response(source)


@router.get("", response_model=StorageSourceListResponse)
async def list_storage_sources(
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageSourceListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    if project_id:
        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if project and project.organization_id != user_org_id:
            raise HTTPException(status_code=403, detail="Access denied to this project")

    sources = await storage_service.list_storage_sources(db, user_org_id, project_id)
    return StorageSourceListResponse(
        storage_sources=[_source_response(s) for s in sources]
    )


@router.get("/{source_id}", response_model=StorageSourceResponse)
async def get_storage_source_detail(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageSourceResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    return _source_response(source)


@router.patch("/{source_id}", response_model=StorageSourceResponse)
async def update_storage_source(
    source_id: str,
    update: StorageSourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageSourceResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    updated = await storage_service.update_storage_source(
        db, source, name=update.name, status=update.status
    )
    return _source_response(updated)


@router.post("/{source_id}/validate", response_model=StorageSourceValidateResponse)
async def validate_storage_source(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageSourceValidateResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    result = await storage_service.validate_storage_source(
        db, source, user_id=current_user.user_id
    )
    return StorageSourceValidateResponse(**result)


@router.post("/{source_id}/authorize", response_model=AuthResponseSchema)
async def authorize_storage_source(
    source_id: str,
    payload: StorageAuthorizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> AuthResponseSchema:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    authorization = await storage_service.authorize_storage_source(
        db,
        source=source,
        authorization_mode=payload.authorization_mode,
        scope_path=payload.scope_path,
        granted_by=current_user.user_id,
        expires_at=payload.expires_at,
    )
    return _authorization_response(authorization)


@router.get(
    "/{source_id}/authorizations", response_model=StorageAuthorizationListResponse
)
async def list_storage_authorizations(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageAuthorizationListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await _check_storage_source_access(source_id, current_user.user_id, db)
    auths = await storage_service.list_authorizations(db, source_id)
    return StorageAuthorizationListResponse(
        authorizations=[_authorization_response(a) for a in auths]
    )


@router.post("/{source_id}/watch-paths", response_model=StorageWatchPathResponse)
async def create_watch_path(
    source_id: str,
    payload: StorageWatchPathCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageWatchPathResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    watch = await storage_service.create_watch_path(db, source, payload.watch_path)
    return _watch_path_response(watch)


@router.get("/{source_id}/watch-paths", response_model=StorageWatchPathListResponse)
async def list_watch_paths(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageWatchPathListResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    await _check_storage_source_access(source_id, current_user.user_id, db)
    paths = await storage_service.list_watch_paths(db, source_id)
    return StorageWatchPathListResponse(
        watch_paths=[_watch_path_response(p) for p in paths]
    )


@router.get("/{source_id}/handshake", response_model=StorageHandshakeResponse)
async def storage_handshake(
    source_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> StorageHandshakeResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    validation_result = await storage_service.validate_storage_source(
        db, source, user_id=current_user.user_id
    )
    auths = await storage_service.list_authorizations(db, source_id)

    metadata = validation_result.get("metadata", {})
    validated = metadata.get("exists", False) and metadata.get("readable", False)

    return StorageHandshakeResponse(
        source_id=str(source.id),
        mount_path=str(source.mount_path),
        metadata=metadata,
        validated=validated,
        authorizations=[_authorization_response(a) for a in auths],
    )


@router.post("/{source_id}/scan", response_model=IngestScanResponse)
async def launch_storage_scan(
    source_id: str,
    payload: IngestScanLaunchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
) -> IngestScanResponse:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    source = await _check_storage_source_access(source_id, current_user.user_id, db)
    scan = await ingest_service.launch_scan(
        db,
        source=source,
        created_by=current_user.user_id,
        watch_path_id=payload.watch_path_id,
    )
    return _scan_response(scan)
