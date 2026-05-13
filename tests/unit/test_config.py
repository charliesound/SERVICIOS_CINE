from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class TestSettingsProdValidation:
    def test_production_without_jwt_secret_fails(self):
        from core.config import Settings

        with pytest.raises(ValueError, match="JWT_SECRET is required"):
            Settings(
                app_env="production",
                jwt_secret="",
                database_url="sqlite+aiosqlite:///test.db",
            )

    def test_production_with_short_jwt_secret_fails(self):
        from core.config import Settings

        with pytest.raises(ValueError, match="JWT_SECRET is required"):
            Settings(
                app_env="production",
                jwt_secret="short",
                database_url="sqlite+aiosqlite:///test.db",
            )

    def test_production_with_cors_wildcard_fails(self):
        from core.config import Settings

        with pytest.raises(ValueError, match="CORS_ALLOWED_ORIGINS cannot contain"):
            Settings(
                app_env="production",
                jwt_secret="a" * 32,
                database_url="sqlite+aiosqlite:///test.db",
                cors_allowed_origins=["*"],
            )

    def test_production_without_database_url_fails(self):
        from core.config import Settings

        with pytest.raises(ValueError, match="DATABASE_URL is required"):
            Settings(
                app_env="production",
                jwt_secret="a" * 32,
                database_url="",
            )

    def test_production_valid_config_succeeds(self):
        from core.config import Settings

        s = Settings(
            app_env="production",
            jwt_secret="a" * 32,
            database_url="sqlite+aiosqlite:///test.db",
            cors_allowed_origins=["https://example.com"],
            auth_disabled=False,
        )
        assert s.app_env == "production"
        assert s.jwt_secret == "a" * 32

    def test_development_loads_defaults(self):
        from core.config import Settings

        s = Settings(app_env="development")
        assert s.app_env == "development"
        assert s.cors_allowed_origins is not None
        assert s.jwt_secret is not None

    def test_log_level_invalid_fails(self):
        from core.config import Settings

        with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
            Settings(log_level="TRACE")

    def test_get_settings_lru_cache(self):
        from core.config import get_settings, reload_settings

        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

        reload_settings()
        s3 = get_settings()
        assert s3 is not s1


class TestLegacyConfigCompat:
    def test_legacy_config_dict_accessible(self):
        from config import config, get_database_url

        assert isinstance(config, dict)
        assert "app" in config
        assert "auth" in config
        url = get_database_url()
        assert url.startswith("sqlite")

    def test_legacy_get_llm_settings(self):
        from config import get_llm_settings

        llm = get_llm_settings()
        assert isinstance(llm, dict)
        assert "provider" in llm
