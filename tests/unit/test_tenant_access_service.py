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


class TestCanWriteProject:
    def test_admin_can_write(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_write_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="admin",
            is_admin=True,
        )
        assert can_write_project(tenant) is True

    def test_viewer_cannot_write(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_write_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="viewer",
            is_admin=False,
        )
        assert can_write_project(tenant) is False

    def test_producer_can_write(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_write_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="producer",
            is_admin=False,
        )
        assert can_write_project(tenant) is True

    def test_global_admin_can_write(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_write_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="admin",
            is_admin=True,
            is_global_admin=True,
        )
        assert can_write_project(tenant) is True

    def test_operator_can_write(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_write_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="operator",
            is_admin=False,
        )
        assert can_write_project(tenant) is True


class TestCanReadProject:
    def test_anyone_can_read(self):
        from schemas.auth_schema import TenantContext
        from services.tenant_access_service import can_read_project

        tenant = TenantContext(
            user_id="u1",
            organization_id="org-a",
            role="viewer",
        )
        assert can_read_project(tenant) is True


class TestApplyTenantFilter:
    def test_apply_tenant_filter_adds_where_clause(self):
        from unittest.mock import Mock
        from services.tenant_access_service import apply_tenant_filter

        query = Mock()
        model = Mock()
        model.organization_id = "col"

        result = apply_tenant_filter(query, model, "org-a")
        query.where.assert_called_once()
