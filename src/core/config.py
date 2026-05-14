from __future__ import annotations

import os
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────
    app_name: str = "AILinkCinema"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    app_version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api"

    # ── CORS ─────────────────────────────────────────────────────────────
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cors_allow_credentials: bool = True
    cors_allowed_methods: list[str] = ["*"]
    cors_allowed_headers: list[str] = ["*"]

    # ── Auth / JWT ──────────────────────────────────────────────────────
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "ailinkcinema"
    jwt_audience: str = "cid-api"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    auth_disabled: bool = False

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = ""
    database_runtime_schema_sync: bool = True
    database_sqlite_legacy_bootstrap: bool = True
    database_use_alembic: bool = False

    # ── Redis (optional) ────────────────────────────────────────────────
    redis_url: str = ""

    # ── Internal API Key ────────────────────────────────────────────────
    internal_api_key_enabled: bool = False
    internal_api_keys: str = ""

    # ── Rate Limit ──────────────────────────────────────────────────────
    rate_limit_backend: Literal["memory", "redis"] = "memory"
    login_rate_limit_per_minute: int = 10

    # ── Observability ────────────────────────────────────────────────────
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"

    # ── Health ───────────────────────────────────────────────────────────
    healthcheck_db_enabled: bool = True
    healthcheck_redis_enabled: bool = False

    # ── Feature flags ───────────────────────────────────────────────────
    feature_workflows: bool = True
    feature_presets: bool = True
    feature_plans: bool = True
    feature_queue: bool = True
    feature_admin: bool = True
    feature_experimental: bool = False
    feature_postproduction: bool = False
    queue_persistence_mode: Literal["memory", "database"] = "database"

    # ── Demo ─────────────────────────────────────────────────────────────
    demo_enabled: bool = False
    demo_auto_seed_narrative: bool = False

    # ── LLM ──────────────────────────────────────────────────────────────
    llm_provider: str = "ollama"
    llm_ollama_base_url: str = "http://127.0.0.1:11434"
    llm_ollama_model: str = "qwen2.5:14b"
    llm_timeout_seconds: int = 120
    llm_temperature: float = 0.2
    llm_enable_fallback: bool = True

    # ── Storage ──────────────────────────────────────────────────────────
    storage_type: str = "local"
    storage_data_dir: str = "data"
    storage_temp_dir: str = "data/temp"
    storage_output_dir: str = "data/output"

    # ── Instance config ──────────────────────────────────────────────────
    instance_config_path: str = ""

    # ── ComfyUI Instance Registry ────────────────────────────────────────
    comfyui_instances_config: str = ""
    comfyui_image_url: str = "http://127.0.0.1:8188"
    comfyui_video_cine_url: str = "http://127.0.0.1:8189"
    comfyui_dubbing_audio_url: str = "http://127.0.0.1:8190"
    comfyui_restoration_url: str = "http://127.0.0.1:8191"
    comfyui_3d_url: str = "http://127.0.0.1:8192"
    comfyui_timeout_seconds: int = 120
    comfyui_health_timeout_seconds: int = 5
    comfyui_poll_interval_seconds: int = 2

    # ── Fallback / legacy key (read from APP_SECRET_KEY) ─────────────────
    app_secret_key: str = ""

    # ── CID / ComfySearch ────────────────────────────────────────────────
    comfysearch_roots: str = ""
    comfysearch_embedding_model: str = "all-MiniLM-L6-v2"

    # ─────────────────────────────────────────────────────────────────────
    # Validators
    # ─────────────────────────────────────────────────────────────────────

    @field_validator("jwt_secret")
    @classmethod
    def _jwt_secret_production(cls, v: str, info) -> str:
        env = info.data.get("app_env")
        if env == "production" and (not v or len(v) < 32):
            raise ValueError(
                "JWT_SECRET is required and must be at least 32 characters in production"
            )
        return v

    @field_validator("cors_allowed_origins")
    @classmethod
    def _cors_no_wildcard_production(cls, v: list[str], info) -> list[str]:
        env = info.data.get("app_env")
        if env == "production" and ("*" in v):
            raise ValueError(
                "CORS_ALLOWED_ORIGINS cannot contain '*' in production. "
                "Use explicit origin URLs."
            )
        return v

    @field_validator("database_url")
    @classmethod
    def _database_url_production(cls, v: str, info) -> str:
        env = info.data.get("app_env")
        if env == "production" and not v:
            raise ValueError("DATABASE_URL is required in production")
        return v

    @field_validator("log_level")
    @classmethod
    def _log_level_valid(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return upper

    @field_validator("auth_disabled")
    @classmethod
    def _auth_disabled_production(cls, v: bool, info) -> bool:
        env = info.data.get("app_env")
        if env == "production" and v:
            raise ValueError(
                "AUTH_DISABLED=true is not allowed in production. "
                "Set AUTH_DISABLED=false or use development/staging."
            )
        return v

    @model_validator(mode="after")
    def _validate_model(self) -> "Settings":
        if self.app_env == "development" and "*" in self.cors_allowed_origins:
            warnings.warn(
                "CORS allows '*' in development — insecure if exposed to the internet"
            )
        if self.app_env == "production" and self.rate_limit_backend == "redis" and not self.redis_url:
            raise ValueError(
                "RATE_LIMIT_BACKEND=redis requires REDIS_URL to be set in production"
            )
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
