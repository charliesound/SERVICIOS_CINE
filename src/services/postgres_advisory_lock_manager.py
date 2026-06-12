from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

DANGEROUS_ORG_IDS = frozenset({"*", "all", "all-tenants", "global"})
_VALID_SCOPES = frozenset({"tenant", "global"})
_MIN_SIGNED_64BIT = -(2**63)
_MAX_SIGNED_64BIT = 2**63 - 1


@dataclass(frozen=True)
class PostgresAdvisoryLockRequest:
    lock_name: str
    scope: str = "tenant"
    organization_id: str | None = None


@dataclass(frozen=True)
class PostgresAdvisoryLockResult:
    lock_name: str
    lock_key: int
    scope: str
    acquired: bool


def _normalize_lock_name(lock_name: str) -> str:
    normalized = lock_name.strip() if lock_name else ""
    if not normalized:
        raise ValueError("lock_name must be non-empty")
    return normalized


def _normalize_organization_id(organization_id: str | None) -> str | None:
    if organization_id is None:
        return None
    normalized = organization_id.strip()
    return normalized or None


def _validate_lock_key(lock_key: int) -> int:
    if not isinstance(lock_key, int) or isinstance(lock_key, bool):
        raise ValueError("lock_key must be an int")
    if lock_key < _MIN_SIGNED_64BIT or lock_key > _MAX_SIGNED_64BIT:
        raise ValueError("lock_key must fit signed 64-bit range")
    return lock_key


def _derive_lock_key(lock_name: str, scope: str, organization_id: str | None) -> int:
    normalized_lock_name = _normalize_lock_name(lock_name)
    normalized_organization_id = _normalize_organization_id(organization_id)
    raw = f"{normalized_lock_name}:{scope}:{normalized_organization_id or ''}"
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=True)


class PostgresAdvisoryLockManager:
    async def try_acquire(
        self, session: Any, request: PostgresAdvisoryLockRequest
    ) -> PostgresAdvisoryLockResult:
        lock_name = _normalize_lock_name(request.lock_name)
        if request.scope not in _VALID_SCOPES:
            raise ValueError(f"Invalid scope: {request.scope!r}")
        organization_id = _normalize_organization_id(request.organization_id)
        if request.scope == "tenant":
            if not organization_id:
                raise ValueError("organization_id is required for tenant scope")
            normalized = organization_id.lower()
            if normalized in DANGEROUS_ORG_IDS:
                raise ValueError(
                    f"Rejected dangerous organization_id: {organization_id!r}"
                )
        elif request.scope == "global":
            if organization_id:
                raise ValueError(
                    "organization_id must not be provided for global scope"
                )
        lock_key = _derive_lock_key(lock_name, request.scope, organization_id)
        result = await session.execute(
            text("SELECT pg_try_advisory_lock(:lock_key)"),
            {"lock_key": lock_key},
        )
        scalar = result.scalar()
        return PostgresAdvisoryLockResult(
            lock_name=lock_name,
            lock_key=lock_key,
            scope=request.scope,
            acquired=bool(scalar),
        )

    async def release(self, session: Any, lock_key: int) -> bool:
        lock_key = _validate_lock_key(lock_key)
        result = await session.execute(
            text("SELECT pg_advisory_unlock(:lock_key)"),
            {"lock_key": lock_key},
        )
        scalar = result.scalar()
        return bool(scalar)
