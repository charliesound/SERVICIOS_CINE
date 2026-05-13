from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from jose import jwt

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("JWT_SECRET", "a" * 32)
os.environ.setdefault("JWT_ISSUER", "ailinkcinema")
os.environ.setdefault("JWT_AUDIENCE", "cid-api")


def _make_token(payload: dict) -> str:
    from routes.auth_routes import create_access_token

    return create_access_token(payload)


def _get_secret() -> str:
    from routes.auth_routes import _get_secret_key

    return _get_secret_key()


def _audience() -> str:
    from core.config import get_settings

    return get_settings().jwt_audience


class TestTokenCreation:
    def test_token_contains_standard_claims(self):
        payload = {"sub": "user-123"}
        token = _make_token(payload)
        decoded = jwt.decode(token, _get_secret(), algorithms=["HS256"], audience=_audience())
        assert decoded["sub"] == "user-123"
        assert "exp" in decoded
        assert "iat" in decoded
        assert "nbf" in decoded
        assert "iss" in decoded
        assert "aud" in decoded

    def test_token_issuer_is_correct(self):
        from core.config import get_settings

        payload = {"sub": "user-123"}
        token = _make_token(payload)
        decoded = jwt.decode(token, _get_secret(), algorithms=["HS256"], audience=_audience())
        assert decoded["iss"] == get_settings().jwt_issuer

    def test_token_audience_is_correct(self):
        from core.config import get_settings

        payload = {"sub": "user-123"}
        token = _make_token(payload)
        decoded = jwt.decode(token, _get_secret(), algorithms=["HS256"], audience=_audience())
        assert decoded["aud"] == get_settings().jwt_audience


class TestTokenValidation:
    def test_valid_token_passes(self):
        from routes.auth_routes import verify_token

        token = _make_token({"sub": "user-123"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_expired_token_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2),
                "nbf": datetime.utcnow() - timedelta(hours=2),
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_wrong_issuer_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "nbf": datetime.utcnow(),
                "iss": "evil-attacker",
                "aud": "cid-api",
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_wrong_audience_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "nbf": datetime.utcnow(),
                "iss": "ailinkcinema",
                "aud": "evil-app",
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_token_without_exp_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "iat": datetime.utcnow(),
                "nbf": datetime.utcnow(),
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_nbf_future_token_fails(self):
        import time

        from routes.auth_routes import verify_token

        future_nbf = time.time() + 3600
        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": time.time() + 7200,
                "iat": time.time(),
                "nbf": future_nbf,
                "iss": "ailinkcinema",
                "aud": "cid-api",
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_without_iat_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "nbf": datetime.utcnow(),
                "iss": "ailinkcinema",
                "aud": "cid-api",
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_iat_future_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() + timedelta(hours=2),
                "iat": datetime.utcnow() + timedelta(hours=1),
                "nbf": datetime.utcnow(),
                "iss": "ailinkcinema",
                "aud": "cid-api",
            },
            _get_secret(),
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None

    def test_invalid_signature_fails(self):
        from routes.auth_routes import verify_token

        token = jwt.encode(
            {
                "sub": "user-123",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "nbf": datetime.utcnow(),
            },
            "different-secret-key-here-32-chars-min!!",
            algorithm="HS256",
        )
        payload = verify_token(token)
        assert payload is None


class TestAuthDisabledValidation:
    def test_auth_disabled_default_false(self, monkeypatch):
        monkeypatch.delenv("AUTH_DISABLED", raising=False)
        from core.config import reload_settings, get_settings

        reload_settings()
        assert get_settings().auth_disabled is False

    def test_auth_disabled_allowed_in_development(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.setenv("APP_ENV", "development")
        from core.config import reload_settings

        s = reload_settings()
        assert s.auth_disabled is True

    def test_auth_disabled_rejected_in_production(self):
        import re

        from core.config import Settings

        with pytest.raises(ValueError, match=re.escape("AUTH_DISABLED=true is not allowed in production")):
            Settings(app_env="production", auth_disabled=True, jwt_secret="a" * 32)


class TestEnterpriseDeps:
    @pytest.mark.asyncio
    async def test_get_token_data_returns_dev_bypass_when_auth_disabled(self, monkeypatch):
        monkeypatch.setenv("AUTH_DISABLED", "true")
        monkeypatch.setenv("APP_ENV", "development")
        from core.config import reload_settings

        reload_settings()
        from dependencies.security import get_token_data

        from unittest.mock import Mock

        request = Mock()
        request.url.path = "/api/v1/comfyui/instances"

        result = await get_token_data(request, credentials=None)
        assert result is not None
        assert result.sub == "dev-bypass"
        assert "admin" in result.roles
        assert "comfyui:read" in result.scopes

        reload_settings()
