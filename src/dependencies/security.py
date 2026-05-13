from __future__ import annotations

import os
import logging
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import get_settings
from routes.auth_routes import verify_token
from services.security_audit_service import (
    auth_disabled_dev_bypass,
    auth_success,
    internal_api_key_used,
    missing_role,
    missing_scope,
    token_invalid,
)

logger = logging.getLogger("servicios_cine.security_deps")

security_scheme = HTTPBearer(auto_error=False)

PUBLIC_PATHS = {
    "/health/live",
    "/health/ready",
    "/health/startup",
    "/docs",
    "/redoc",
    "/openapi.json",
}

TOKEN_DATA_FIELDS = {"sub", "iss", "aud", "exp", "iat", "nbf", "roles", "scopes", "organization_id"}


class TokenData:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.sub: str = payload.get("sub", "")
        self.iss: str = payload.get("iss", "")
        self.aud: str = payload.get("aud", "")
        self.roles: list[str] = payload.get("roles", [])
        self.scopes: list[str] = payload.get("scopes", [])
        self.organization_id: str = payload.get("organization_id", "")
        self.raw: dict[str, Any] = payload


def _is_auth_disabled() -> bool:
    return get_settings().auth_disabled


def _is_development() -> bool:
    return get_settings().app_env == "development"


def _is_public_path(path: str) -> bool:
    for p in PUBLIC_PATHS:
        if path == p or path.startswith(p):
            return True
    return False


async def get_token_data(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[TokenData]:
    path = request.url.path

    if _is_public_path(path):
        return None

    if _is_auth_disabled() and _is_development():
        auth_disabled_dev_bypass(path)
        return TokenData({
            "sub": "dev-bypass",
            "roles": ["admin"],
            "scopes": ["projects:read", "projects:write", "comfyui:read", "comfyui:health", "admin:read", "admin:write"],
            "organization_id": "dev-org",
            "iss": get_settings().jwt_issuer,
            "aud": get_settings().jwt_audience,
        })

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    payload = verify_token(credentials.credentials)
    if not payload:
        token_invalid("decode_failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    token_invalid_reason = _validate_token_enterprise(payload)
    if token_invalid_reason:
        token_invalid(token_invalid_reason)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    auth_success(user_id=payload.get("sub", "unknown"))
    return TokenData(payload)


def _validate_token_enterprise(payload: dict[str, Any]) -> Optional[str]:
    settings = get_settings()

    if not payload.get("exp"):
        return "missing_exp"

    iss = payload.get("iss")
    if iss and iss != settings.jwt_issuer:
        return "invalid_issuer"

    aud = payload.get("aud")
    if aud and aud != settings.jwt_audience:
        return "invalid_audience"

    nbf = payload.get("nbf")
    if nbf:
        import time
        now = time.time()
        if now < nbf:
            return "nbf_future"

    return None


async def require_auth(token: Optional[TokenData] = Depends(get_token_data)) -> TokenData:
    if token is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return token


def require_scope(scope: str):
    async def _require_scope(token: TokenData = Depends(require_auth)) -> TokenData:
        if scope not in token.scopes and "admin" not in token.roles:
            missing_scope(token.sub, scope)
            raise HTTPException(status_code=403, detail=f"Insufficient scope: {scope}")
        return token
    return _require_scope


def require_role(role: str):
    async def _require_role(token: TokenData = Depends(require_auth)) -> TokenData:
        if role not in token.roles and "admin" not in token.roles:
            missing_role(token.sub, role)
            raise HTTPException(status_code=403, detail=f"Insufficient role: {role}")
        return token
    return _require_role


async def optional_internal_api_key(request: Request) -> Optional[str]:
    settings = get_settings()
    if not settings.internal_api_key_enabled:
        return None

    header_key = request.headers.get("X-Internal-API-Key", "")
    if not header_key:
        return None

    valid_keys_str = settings.internal_api_keys
    if not valid_keys_str:
        return None

    valid_keys = [k.strip() for k in valid_keys_str.split(",") if k.strip()]
    if header_key in valid_keys:
        internal_api_key_used()
        return header_key

    raise HTTPException(status_code=403, detail="Invalid internal API key")
