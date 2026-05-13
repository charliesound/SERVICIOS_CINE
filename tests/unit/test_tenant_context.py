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
os.environ.setdefault("AUTH_DISABLED", "true")


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


class TestTenantContext:
    @pytest.mark.asyncio
    async def test_token_without_organization_id_fails(self):
        from dependencies.security import TokenData
        from dependencies.tenant_context import get_tenant_context
        from unittest.mock import Mock, AsyncMock

        request = Mock()
        request.url.path = "/api/some-endpoint"
        db = AsyncMock()
        db.execute = AsyncMock()

        token = TokenData({
            "sub": "user-1",
            "roles": ["admin"],
            "scopes": [],
        })

        with pytest.raises(Exception) as excinfo:
            await get_tenant_context(request, token=token, db=db)
        assert excinfo.typename == "HTTPException" or "403" in str(excinfo.value)


class TestRequireOrganization:
    @pytest.mark.asyncio
    async def test_require_organization_with_valid_org(self):
        from schemas.auth_schema import TenantContext
        from dependencies.tenant_context import require_organization

        tenant = TenantContext(
            user_id="user-1",
            organization_id="org-a",
            role="admin",
            is_admin=True,
        )
        result = await require_organization(tenant)
        assert result.organization_id == "org-a"

    @pytest.mark.asyncio
    async def test_require_organization_without_org_fails(self):
        from schemas.auth_schema import TenantContext
        from dependencies.tenant_context import require_organization

        tenant = TenantContext(
            user_id="user-1",
            organization_id="",
            role="admin",
        )
        with pytest.raises(Exception) as excinfo:
            await require_organization(tenant)
        assert excinfo.typename == "HTTPException" or "403" in str(excinfo.value)


class TestAuthMethod:
    @pytest.mark.asyncio
    async def test_dev_bypass_sets_dev_bypass_auth_method(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.setenv("APP_ENV", "development")
        from core.config import reload_settings

        reload_settings()
        from dependencies.tenant_context import get_tenant_context
        from dependencies.security import get_token_data
        from unittest.mock import Mock

        request = Mock()
        request.url.path = "/api/some-endpoint"

        token = await get_token_data(request, credentials=None)
        assert token is not None
        tenant = await get_tenant_context(request, token=token)
        assert tenant.organization_id == "dev-org"
        assert tenant.is_admin is True
        assert tenant.is_global_admin is False
        reload_settings()
