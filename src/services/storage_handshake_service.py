from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import os
import shutil

from fastapi import HTTPException
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ingest_handshake import (
    IngestEvent,
    StorageAuthorization,
    StorageSource,
    StorageWatchPath,
)


def normalize_mounted_path(raw_path: str) -> str:
    path = Path(raw_path.strip()).expanduser()
    try:
        return str(path.resolve(strict=False))
    except RuntimeError:
        return str(path.absolute())


def resolve_organization_id(
    payload: Dict[str, Any],
    requested_organization_id: Optional[str],
    user_id: str,
    use_user_fallback: bool = True,
) -> Optional[str]:
    token_org = payload.get("organization_id") or payload.get("org_id")
    if (
        token_org
        and requested_organization_id
        and str(token_org) != requested_organization_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Organization mismatch between token and request",
        )
    if token_org:
        return str(token_org)
    if requested_organization_id:
        return requested_organization_id
    if use_user_fallback:
        return f"user:{user_id}"
    return None


def get_path_handshake(path_value: str) -> Dict[str, Any]:
    normalized = normalize_mounted_path(path_value)
    candidate = Path(normalized)

    exists = candidate.exists()
    is_dir = candidate.is_dir() if exists else False
    readable = os.access(str(candidate), os.R_OK) if exists else False

    free_space = None
    total_space = None
    if exists:
        try:
            usage = shutil.disk_usage(str(candidate))
            free_space = usage.free
            total_space = usage.total
        except OSError:
            pass

    status = "valid" if exists and is_dir and readable else "invalid"
    if status == "valid":
        message = "Mounted path is accessible"
    elif not exists:
        message = "Path does not exist"
    elif not is_dir:
        message = "Path exists but is not a directory"
    else:
        message = "Path is not readable"

    return {
        "validated_path": normalized,
        "exists": exists,
        "is_dir": is_dir,
        "readable": readable,
        "free_space": free_space,
        "total_space": total_space,
        "status": status,
        "message": message,
    }


def resolve_under_mount(mount_path: str, target_path: str) -> str:
    mount = Path(normalize_mounted_path(mount_path))
    provided = Path(target_path)
    resolved = (
        Path(normalize_mounted_path(str(provided)))
        if provided.is_absolute()
        else Path(normalize_mounted_path(str(mount / provided)))
    )
    try:
        resolved.relative_to(mount)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Path is outside the mounted source scope",
        ) from exc
    return str(resolved)


async def log_ingest_event(
    db: AsyncSession,
    organization_id: str,
    project_id: str,
    event_type: str,
    payload: Dict[str, Any],
    created_by: Optional[str] = None,
    storage_source_id: Optional[str] = None,
) -> IngestEvent:
    event = IngestEvent(
        organization_id=organization_id,
        project_id=project_id,
        storage_source_id=storage_source_id,
        event_type=event_type,
        event_payload_json=payload,
        created_by=created_by,
    )
    db.add(event)
    await db.flush()
    return event


async def get_owned_storage_source(
    db: AsyncSession,
    source_id: str,
    organization_id: Optional[str],
    user_id: str,
) -> StorageSource:
    filters = [StorageSource.id == source_id, StorageSource.created_by == user_id]
    if organization_id is not None:
        filters.append(StorageSource.organization_id == organization_id)

    result = await db.execute(select(StorageSource).where(and_(*filters)))
    source = result.scalar_one_or_none()
    if source is None:
        raise HTTPException(status_code=404, detail="Storage source not found")
    return source


async def get_active_authorization(
    db: AsyncSession,
    storage_source_id: str,
) -> Optional[StorageAuthorization]:
    now = datetime.utcnow()
    result = await db.execute(
        select(StorageAuthorization)
        .where(
            and_(
                StorageAuthorization.storage_source_id == storage_source_id,
                StorageAuthorization.status == "authorized",
                StorageAuthorization.revoked_at.is_(None),
            )
        )
        .order_by(desc(StorageAuthorization.granted_at))
    )
    authorization = result.scalar_one_or_none()
    if authorization is None:
        return None
    expires_at = getattr(authorization, "expires_at", None)
    if expires_at is not None and expires_at <= now:
        return None
    return authorization
