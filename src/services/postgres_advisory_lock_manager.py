from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

DANGEROUS_ORG_IDS = frozenset({"*", "all", "all-tenants", "global"})
_VALID_SCOPES = frozenset({"tenant", "global"})


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


def _derive_lock_key(lock_name: str, scope: str, organization_id: str | None) -> int:
    raw = f"{lock_name}:{scope}:{organization_id or ''}"
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=True)


class PostgresAdvisoryLockManager:
    async def try_acquire(
        self, session: Any, request: PostgresAdvisoryLockRequest
    ) -> PostgresAdvisoryLockResult:
        if not request.lock_name or not request.lock_name.strip():
            raise ValueError("lock_name must be non-empty")
        if request.scope not in _VALID_SCOPES:
            raise ValueError(f"Invalid scope: {request.scope!r}")
        if request.scope == "tenant":
            org_id = (request.organization_id or "").strip()
            if not org_id:
                raise ValueError("organization_id is required for tenant scope")
            normalized = org_id.lower()
            if normalized in DANGEROUS_ORG_IDS:
                raise ValueError(
                    f"Rejected dangerous organization_id: {org_id!r}"
                )
        elif request.scope == "global":
            if request.organization_id:
                raise ValueError(
                    "organization_id must not be provided for global scope"
                )
        lock_key = _derive_lock_key(
            request.lock_name, request.scope, request.organization_id
        )
        result = await session.execute(
            text("SELECT pg_try_advisory_lock(:lock_key)"),
            {"lock_key": lock_key},
        )
        scalar = result.scalar()
        return PostgresAdvisoryLockResult(
            lock_name=request.lock_name,
            lock_key=lock_key,
            scope=request.scope,
            acquired=bool(scalar),
        )

    async def release(self, session: Any, lock_key: int) -> bool:
        result = await session.execute(
            text("SELECT pg_advisory_unlock(:lock_key)"),
            {"lock_key": lock_key},
        )
        scalar = result.scalar()
        return bool(scalar)
