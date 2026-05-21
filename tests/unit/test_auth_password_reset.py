from __future__ import annotations

import hashlib
import os
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("JWT_SECRET", "a" * 32)
os.environ.setdefault("JWT_ISSUER", "ailinkcinema")
os.environ.setdefault("JWT_AUDIENCE", "cid-api")
os.environ.setdefault("FRONTEND_BASE_URL", "http://localhost:3000")
os.environ.setdefault("PASSWORD_RESET_TOKEN_TTL_MINUTES", "30")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from routes.auth_routes import router
from schemas.auth_schema import ForgotPasswordResponse, ResetPasswordResponse
from services.password_reset_service import (
    _PASSWORD_PATTERN,
    request_password_reset,
    validate_reset_token,
    reset_password,
)

SYNC_DB_URL = "sqlite:///file::memory:?cache=shared"


class _FakeExecuteResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _FakeDb:
    def __init__(self, user=None, token=None):
        self.user = user
        self.token = token
        self.added_objects: list = []
        self.committed = False

    async def execute(self, stmt):
        sql = str(stmt)
        if "password_reset_tokens" in sql:
            return _FakeExecuteResult(self.token)
        if "users" in sql:
            return _FakeExecuteResult(self.user)
        return _FakeExecuteResult(None)

    def add(self, obj):
        self.added_objects.append(obj)

    async def commit(self):
        self.committed = True


def _make_user(uid="user-1", email="test@example.com", is_active=True):
    return SimpleNamespace(
        id=uid,
        email=email,
        is_active=is_active,
        hashed_password=secrets.token_hex(16),
        organization_id="org-1",
    )


def _make_token(
    user_id="user-1",
    token_str=None,
    expires_offset_minutes=30,
    used=False,
):
    if token_str is None:
        token_str = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_str.encode()).hexdigest()
    return (
        SimpleNamespace(
            id="tok-1",
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_offset_minutes),
            used_at=datetime.utcnow() if used else None,
            created_at=datetime.utcnow(),
        ),
        token_str,
    )


# ─── Service-level tests ──────────────────────────────────────────────


class TestRequestPasswordReset:
    async def test_returns_none_for_nonexistent_email(self):
        db = _FakeDb(user=None)
        result = await request_password_reset(db, "noexiste@test.com")
        assert result is None
        assert not db.added_objects

    async def test_creates_token_for_active_user(self):
        user = _make_user()
        db = _FakeDb(user=user)
        await request_password_reset(db, user.email)
        assert len(db.added_objects) == 1
        assert db.added_objects[0].user_id == user.id
        assert db.committed

    async def test_does_not_create_token_for_inactive_user(self):
        user = _make_user(is_active=False)
        db = _FakeDb(user=user)
        await request_password_reset(db, user.email)
        assert not db.added_objects


class TestValidateResetToken:
    async def test_validates_unused_token(self):
        token_obj, raw_token = _make_token()
        db = _FakeDb(token=token_obj)
        result = await validate_reset_token(db, raw_token)
        assert result.id == "tok-1"

    async def test_rejects_nonexistent_token(self):
        db = _FakeDb(token=None)
        with pytest.raises(Exception) as exc:
            await validate_reset_token(db, "invalid-token")
        assert "400" in str(exc) or "Invalid" in str(exc)

    async def test_rejects_used_token(self):
        token_obj, raw_token = _make_token(used=True)
        db = _FakeDb(token=token_obj)
        with pytest.raises(Exception) as exc:
            await validate_reset_token(db, raw_token)
        assert "400" in str(exc) or "already been used" in str(exc)

    async def test_rejects_expired_token(self):
        token_obj, raw_token = _make_token(expires_offset_minutes=-5)
        db = _FakeDb(token=token_obj)
        with pytest.raises(Exception) as exc:
            await validate_reset_token(db, raw_token)
        assert "400" in str(exc) or "expired" in str(exc)


class TestResetPassword:
    async def test_changes_password_with_valid_token(self):
        user = _make_user()
        old_hash = user.hashed_password
        token_obj, raw_token = _make_token()
        db = _FakeDb(user=user, token=token_obj)
        await reset_password(db, raw_token, "NewPass123", "NewPass123")
        assert user.hashed_password != old_hash
        assert token_obj.used_at is not None
        assert db.committed

    async def test_fails_if_passwords_do_not_match(self):
        user = _make_user()
        token_obj, raw_token = _make_token()
        db = _FakeDb(user=user, token=token_obj)
        with pytest.raises(Exception) as exc:
            await reset_password(db, raw_token, "NewPass123", "Different456")
        assert "400" in str(exc) or "do not match" in str(exc)

    async def test_fails_with_weak_password(self):
        user = _make_user()
        token_obj, raw_token = _make_token()
        db = _FakeDb(user=user, token=token_obj)
        with pytest.raises(Exception) as exc:
            await reset_password(db, raw_token, "short", "short")
        assert "400" in str(exc) or "Password must" in str(exc)
        with pytest.raises(Exception):
            await reset_password(db, raw_token, "nouppercase1", "nouppercase1")
        with pytest.raises(Exception):
            await reset_password(db, raw_token, "NOLOWERCASE1", "NOLOWERCASE1")
        with pytest.raises(Exception):
            await reset_password(db, raw_token, "NoDigits!", "NoDigits!")

    async def test_token_cannot_be_reused(self):
        user = _make_user()
        token_obj, raw_token = _make_token(used=True)
        db = _FakeDb(user=user, token=token_obj)
        with pytest.raises(Exception) as exc:
            await reset_password(db, raw_token, "NewPass123", "NewPass123")
        assert "400" in str(exc)


# ─── Password pattern validation ──────────────────────────────────────


class TestPasswordPattern:
    def test_valid_password(self):
        assert _PASSWORD_PATTERN.match("Abcdef1g")

    def test_too_short(self):
        assert not _PASSWORD_PATTERN.match("Ab1")

    def test_no_uppercase(self):
        assert not _PASSWORD_PATTERN.match("abcdef1g")

    def test_no_lowercase(self):
        assert not _PASSWORD_PATTERN.match("ABCDEF1G")

    def test_no_digit(self):
        assert not _PASSWORD_PATTERN.match("Abcdefgh")


# ─── FastAPI endpoint tests ───────────────────────────────────────────

async def _override_db():
    yield _FakeDb(user=None)


def _override_tenant():
    from schemas.auth_schema import TenantContext
    return TenantContext(user_id="user-1", organization_id="org-1", role="admin", is_admin=True)


class TestForgotPasswordEndpoint:
    def test_returns_generic_response_for_nonexistent_email(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = _override_db
        from dependencies.tenant_context import get_tenant_context as deps_get_tenant_context
        app.dependency_overrides[deps_get_tenant_context] = _override_tenant

        with TestClient(app) as client:
            response = client.post(
                "/api/auth/forgot-password",
                json={"email": "noexiste@test.com"},
            )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "registrado" in data["message"]


class TestResetPasswordEndpoint:
    def test_fails_with_weak_password(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = _override_db
        from dependencies.tenant_context import get_tenant_context as deps_get_tenant_context
        app.dependency_overrides[deps_get_tenant_context] = _override_tenant

        with TestClient(app) as client:
            response = client.post(
                "/api/auth/reset-password",
                json={"token": "some-token", "new_password": "nouppercase1", "confirm_password": "nouppercase1"},
            )
        assert response.status_code == 400

    def test_fails_with_mismatched_passwords(self):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = _override_db
        from dependencies.tenant_context import get_tenant_context as deps_get_tenant_context
        app.dependency_overrides[deps_get_tenant_context] = _override_tenant

        with TestClient(app) as client:
            response = client.post(
                "/api/auth/reset-password",
                json={"token": "some-token", "new_password": "ValidPass1", "confirm_password": "Different1"},
            )
        assert response.status_code == 400
