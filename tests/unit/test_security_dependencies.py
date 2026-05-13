from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("JWT_SECRET", "a" * 32)


class TestRequireAuth:
    @pytest.mark.asyncio
    async def test_require_auth_without_token_raises_401(self):
        from dependencies.security import require_auth

        with pytest.raises(Exception) as excinfo:
            await require_auth(token=None)
        assert excinfo.typename == "HTTPException" or "401" in str(excinfo.value)


class TestRequireScope:
    @pytest.mark.asyncio
    async def test_missing_scope_raises_403(self):
        from dependencies.security import TokenData, require_scope

        token = TokenData({
            "sub": "user-1",
            "roles": ["viewer"],
            "scopes": ["comfyui:read"],
        })

        dep = require_scope("admin:write")
        with pytest.raises(Exception) as excinfo:
            await dep(token)
        assert excinfo.typename == "HTTPException" or "403" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_valid_scope_passes(self):
        from dependencies.security import TokenData, require_scope

        token = TokenData({
            "sub": "user-1",
            "roles": ["viewer"],
            "scopes": ["comfyui:read", "comfyui:health"],
        })

        dep = require_scope("comfyui:read")
        result = await dep(token)
        assert result.sub == "user-1"

    @pytest.mark.asyncio
    async def test_admin_role_bypasses_scope_check(self):
        from dependencies.security import TokenData, require_scope

        token = TokenData({
            "sub": "admin-1",
            "roles": ["admin"],
            "scopes": [],
        })

        dep = require_scope("any:scope")
        result = await dep(token)
        assert result.sub == "admin-1"


class TestRequireRole:
    @pytest.mark.asyncio
    async def test_missing_role_raises_403(self):
        from dependencies.security import TokenData, require_role

        token = TokenData({
            "sub": "user-1",
            "roles": ["viewer"],
            "scopes": [],
        })

        dep = require_role("admin")
        with pytest.raises(Exception) as excinfo:
            await dep(token)
        assert excinfo.typename == "HTTPException" or "403" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_valid_role_passes(self):
        from dependencies.security import TokenData, require_role

        token = TokenData({
            "sub": "user-1",
            "roles": ["admin"],
            "scopes": [],
        })

        dep = require_role("admin")
        result = await dep(token)
        assert result.sub == "user-1"


class TestInternalApiKey:
    @pytest.mark.asyncio
    async def test_valid_internal_api_key_passes(self, monkeypatch):
        monkeypatch.setenv("INTERNAL_API_KEY_ENABLED", "true")
        monkeypatch.setenv("INTERNAL_API_KEYS", "key-abc,key-def")
        from core.config import reload_settings

        reload_settings()
        from dependencies.security import optional_internal_api_key

        from unittest.mock import Mock

        request = Mock()
        request.headers = {"X-Internal-API-Key": "key-abc"}

        result = await optional_internal_api_key(request)
        assert result == "key-abc"

    @pytest.mark.asyncio
    async def test_invalid_internal_api_key_raises_403(self, monkeypatch):
        monkeypatch.setenv("INTERNAL_API_KEY_ENABLED", "true")
        monkeypatch.setenv("INTERNAL_API_KEYS", "key-abc,key-def")
        from core.config import reload_settings

        reload_settings()
        from dependencies.security import optional_internal_api_key

        from unittest.mock import Mock

        request = Mock()
        request.headers = {"X-Internal-API-Key": "key-evil"}

        with pytest.raises(Exception) as excinfo:
            await optional_internal_api_key(request)
        assert excinfo.typename == "HTTPException" or "403" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_disabled_api_key_returns_none(self, monkeypatch):
        monkeypatch.setenv("INTERNAL_API_KEY_ENABLED", "false")
        from core.config import reload_settings

        reload_settings()
        from dependencies.security import optional_internal_api_key

        from unittest.mock import Mock

        request = Mock()

        result = await optional_internal_api_key(request)
        assert result is None
