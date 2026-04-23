from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.ingest_handshake import (
    StorageAuthorization,
    StorageSource,
    StorageWatchPath,
)
from routes.auth_routes import get_authenticated_user, get_token_payload
from schemas.storage_handshake_schema import (
    StorageAuthorizeRequest,
    StorageAuthorizationResponse,
    StorageHandshakeResponse,
    StorageSourceCreate,
    StorageSourceListResponse,
    StorageSourceResponse,
    StorageSourceUpdate,
    StorageValidateRequest,
    StorageWatchPathCreate,
    StorageWatchPathListResponse,
    StorageWatchPathResponse,
)
from services.storage_handshake_service import (
    get_active_authorization,
    get_owned_storage_source,
    get_path_handshake,
    log_ingest_event,
    normalize_mounted_path,
    resolve_organization_id,
    resolve_under_mount,
)

router = APIRouter(prefix="/api/storage-sources", tags=["storage-sources"])

ALLOWED_SOURCE_TYPES = {
    "local_mounted_path",
    "smb_mounted_path",
    "nfs_mounted_path",
}


@router.post("", response_model=StorageSourceResponse)
async def create_storage_source(
    payload: StorageSourceCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    if payload.source_type not in ALLOWED_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Phase 1 supports mounted paths only (local/smb/nfs)",
        )

    organization_id = resolve_organization_id(
        token_payload, payload.organization_id, user.user_id
    )

    source = StorageSource(
        organization_id=organization_id,
        project_id=payload.project_id,
        name=payload.name,
        source_type=payload.source_type,
        mount_path=normalize_mounted_path(payload.mount_path),
        status="draft",
        created_by=user.user_id,
    )
    db.add(source)
    await db.flush()
    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="storage_source.created",
        payload={"name": source.name, "mount_path": source.mount_path},
        created_by=user.user_id,
    )
    await db.refresh(source)
    return source


@router.get("", response_model=StorageSourceListResponse)
async def list_storage_sources(
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    organization_id = resolve_organization_id(
        token_payload, None, user.user_id, use_user_fallback=False
    )
    filters = [
        StorageSource.created_by == user.user_id,
    ]
    if organization_id is not None:
        filters.append(StorageSource.organization_id == organization_id)
    if project_id:
        filters.append(StorageSource.project_id == project_id)

    result = await db.execute(select(StorageSource).where(and_(*filters)))
    items = result.scalars().all()
    return StorageSourceListResponse(items=items)


@router.get("/{source_id}", response_model=StorageSourceResponse)
async def get_storage_source(
    source_id: str,
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
    return source


@router.patch("/{source_id}", response_model=StorageSourceResponse)
async def update_storage_source(
    source_id: str,
    payload: StorageSourceUpdate,
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

    if payload.source_type and payload.source_type not in ALLOWED_SOURCE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Phase 1 supports mounted paths only (local/smb/nfs)",
        )

    if payload.name is not None:
        source.name = payload.name
    if payload.source_type is not None:
        source.source_type = payload.source_type
    if payload.mount_path is not None:
        source.mount_path = normalize_mounted_path(payload.mount_path)
    if payload.status is not None:
        source.status = payload.status

    source.updated_at = datetime.utcnow()
    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="storage_source.updated",
        payload={"source_id": source.id},
        created_by=user.user_id,
    )
    await db.flush()
    await db.refresh(source)
    return source


@router.post("/{source_id}/validate", response_model=StorageHandshakeResponse)
async def validate_storage_source(
    source_id: str,
    payload: StorageValidateRequest,
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

    path_to_validate = source.mount_path
    if payload.path_override:
        path_to_validate = resolve_under_mount(source.mount_path, payload.path_override)

    result = get_path_handshake(path_to_validate)
    source.status = "validated" if result["status"] == "valid" else "error"
    source.updated_at = datetime.utcnow()

    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="storage_source.validated",
        payload={
            "validated_path": result["validated_path"],
            "status": result["status"],
            "message": result["message"],
        },
        created_by=user.user_id,
    )

    await db.flush()
    return StorageHandshakeResponse(source_id=source.id, **result)


@router.post("/{source_id}/authorize", response_model=StorageAuthorizationResponse)
async def authorize_storage_source(
    source_id: str,
    payload: StorageAuthorizeRequest,
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

    normalized_scope = resolve_under_mount(source.mount_path, payload.scope_path)
    scope_check = get_path_handshake(normalized_scope)
    if scope_check["status"] != "valid":
        raise HTTPException(
            status_code=400,
            detail=f"Scope path is not accessible: {scope_check['message']}",
        )

    authorization = StorageAuthorization(
        storage_source_id=source.id,
        authorization_mode=payload.authorization_mode,
        scope_path=normalized_scope,
        status="authorized",
        granted_by=user.user_id,
        granted_at=datetime.utcnow(),
        expires_at=payload.expires_at,
    )
    db.add(authorization)
    source.status = "authorized"
    source.updated_at = datetime.utcnow()

    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="storage_source.authorized",
        payload={
            "authorization_mode": payload.authorization_mode,
            "scope_path": normalized_scope,
        },
        created_by=user.user_id,
    )

    await db.flush()
    await db.refresh(authorization)
    return authorization


@router.post("/{source_id}/watch-paths", response_model=StorageWatchPathResponse)
async def create_watch_path(
    source_id: str,
    payload: StorageWatchPathCreate,
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

    authorization = await get_active_authorization(db, source.id)
    if not authorization:
        raise HTTPException(
            status_code=400,
            detail="No active authorization found for this storage source",
        )

    normalized_watch_path = resolve_under_mount(source.mount_path, payload.watch_path)
    auth_scope = Path(authorization.scope_path)
    try:
        Path(normalized_watch_path).relative_to(auth_scope)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Watch path is outside authorized scope",
        ) from exc

    watch_check = get_path_handshake(normalized_watch_path)
    watch = StorageWatchPath(
        storage_source_id=source.id,
        watch_path=normalized_watch_path,
        status="active" if watch_check["status"] == "valid" else "invalid",
        last_validated_at=datetime.utcnow(),
    )
    db.add(watch)

    await log_ingest_event(
        db=db,
        organization_id=source.organization_id,
        project_id=source.project_id,
        storage_source_id=source.id,
        event_type="storage_watch_path.created",
        payload={
            "watch_path": normalized_watch_path,
            "status": watch.status,
            "validation_message": watch_check["message"],
        },
        created_by=user.user_id,
    )

    await db.flush()
    await db.refresh(watch)
    return watch


@router.get("/{source_id}/watch-paths", response_model=StorageWatchPathListResponse)
async def list_watch_paths(
    source_id: str,
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

    result = await db.execute(
        select(StorageWatchPath).where(StorageWatchPath.storage_source_id == source.id)
    )
    items = result.scalars().all()
    return StorageWatchPathListResponse(items=items)
