"""Legacy config compatibility layer.

New code should import from ``core.config`` (Pydantic Settings).
This module maintains backward compatibility for existing consumers
that use ``from config import config`` or ``from config import load_config``.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

import yaml

from core.config import PROJECT_ROOT as _PROJECT_ROOT
from core.config import get_settings as _get_settings

_DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{_PROJECT_ROOT / 'ailinkcinema_s2.db'}"

logger = logging.getLogger(__name__)


# ── Re-export key paths for any legacy consumer ──────────────────────────
def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def get_project_root() -> Path:
    return get_base_dir().parent


def get_config_path() -> Path:
    return get_base_dir() / "config" / "config.yaml"


# ── Legacy YAML-based load (kept for modules that read config.yaml raw) ──
def load_config(force_reload: bool = False) -> Dict[str, Any]:
    """Load the legacy YAML config with env overrides.

    Deprecated: new code should use ``core.config.get_settings()``.

    This function now also layers the canonical Pydantic Settings values
    on top so both sources stay aligned.
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró config.yaml en: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("config.yaml debe contener un objeto YAML raíz")

    data = _apply_env_overrides(data)
    data = _merge_settings(data)
    return data


def _apply_env_overrides(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides on top of YAML."""
    app_config = data.setdefault("app", {})
    auth_config = data.setdefault("auth", {})
    demo_config = data.setdefault("demo", {})
    features_config = data.setdefault("features", {})
    queue_config = data.setdefault("queue", {})
    llm_config = data.setdefault("llm", {})

    app_env = os.getenv("APP_ENV", str(app_config.get("env", "production"))).strip()
    app_config["env"] = app_env

    app_debug = _parse_bool(os.getenv("APP_DEBUG")) if os.getenv("APP_DEBUG") else None
    if app_debug is not None:
        app_config["debug"] = app_debug

    app_secret = os.getenv("APP_SECRET_KEY")
    if app_secret:
        app_config["secret_key"] = app_secret

    auth_secret = os.getenv("AUTH_SECRET_KEY")
    if auth_secret:
        auth_config["secret_key"] = auth_secret
        if not app_secret:
            app_config["secret_key"] = auth_secret

    auth_alg = os.getenv("AUTH_ALGORITHM")
    if auth_alg:
        auth_config["algorithm"] = auth_alg

    at_min = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    if at_min:
        auth_config["access_token_expire_minutes"] = int(at_min)

    _apply_bool_env("ENABLE_DEMO_ROUTES", demo_config, "enabled", app_env)
    _apply_bool_env("ENABLE_EXPERIMENTAL_ROUTES", features_config, "experimental", app_env)
    _apply_bool_env("ENABLE_POSTPRODUCTION_ROUTES", features_config, "postproduction", app_env)

    demo_auto = os.getenv("DEMO_AUTO_SEED_NARRATIVE")
    if demo_auto is not None:
        demo_config["auto_seed_narrative"] = _parse_bool(demo_auto)

    queue_config["persistence_mode"] = os.getenv(
        "QUEUE_PERSISTENCE_MODE",
        str(queue_config.get("persistence_mode", "database")),
    ).strip()
    queue_config["production_ready"] = queue_config["persistence_mode"].lower() != "memory"

    llm_overrides = {
        "provider": ("LLM_PROVIDER", "ollama"),
        "ollama_base_url": ("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        "ollama_model": ("OLLAMA_MODEL", "qwen2.5:14b"),
        "timeout_seconds": ("LLM_TIMEOUT_SECONDS", 120),
        "temperature": ("LLM_TEMPERATURE", 0.2),
        "script_analysis_provider": ("SCRIPT_ANALYSIS_PROVIDER", "ollama"),
        "storyboard_prompt_provider": ("STORYBOARD_PROMPT_PROVIDER", "ollama"),
        "pipeline_builder_provider": ("PIPELINE_BUILDER_PROVIDER", "ollama"),
    }
    for key, (env_var, default) in llm_overrides.items():
        llm_config[key] = os.getenv(env_var, str(llm_config.get(key, default)))

    llm_enable = os.getenv("LLM_ENABLE_FALLBACK")
    if llm_enable is not None:
        llm_config["enable_fallback"] = _parse_bool(llm_enable)
    else:
        llm_config.setdefault("enable_fallback", True)

    return data


def _apply_bool_env(env_var: str, target: dict, key: str, app_env: str | None = None) -> None:
    val = os.getenv(env_var)
    if val is not None:
        target[key] = _parse_bool(val)
    elif app_env and app_env.lower() == "production":
        target[key] = False


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _merge_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Layer Pydantic Settings values on top of the YAML dict for alignment."""
    try:
        s = _get_settings()

        app = data.setdefault("app", {})
        app.setdefault("name", s.app_name)
        app.setdefault("env", s.app_env)
        app.setdefault("debug", s.debug)
        app.setdefault("secret_key", s.jwt_secret or s.app_secret_key)

        auth = data.setdefault("auth", {})
        auth.setdefault("secret_key", s.jwt_secret)
        auth.setdefault("algorithm", s.jwt_algorithm)
        auth.setdefault("access_token_expire_minutes", s.access_token_expire_minutes)

        data.setdefault("database", {}).setdefault("url", s.database_url)
        data.setdefault("database", {}).setdefault("runtime_schema_sync", s.database_runtime_schema_sync)
        data.setdefault("database", {}).setdefault("sqlite_legacy_bootstrap", s.database_sqlite_legacy_bootstrap)
        data.setdefault("database", {}).setdefault("use_alembic", s.database_use_alembic)

        data.setdefault("demo", {}).setdefault("enabled", s.demo_enabled)
        data.setdefault("demo", {}).setdefault("auto_seed_narrative", s.demo_auto_seed_narrative)

        data.setdefault("queue", {}).setdefault("persistence_mode", s.queue_persistence_mode)

        data.setdefault("features", {}).setdefault("experimental", s.feature_experimental)
        data.setdefault("features", {}).setdefault("postproduction", s.feature_postproduction)
        data.setdefault("features", {}).setdefault("admin", s.feature_admin)
    except Exception:
        pass
    return data


def get_config() -> Dict[str, Any]:
    return load_config()


def get_database_config() -> Dict[str, Any]:
    db_config = get_config().get("database", {})
    if not isinstance(db_config, dict):
        raise ValueError("config.database debe ser un objeto YAML")
    return db_config


def get_database_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    configured_url = get_database_config().get("url")
    if isinstance(configured_url, str) and configured_url.strip():
        url = configured_url.strip()
        if url.startswith("sqlite+aiosqlite:///") or url.startswith("sqlite:///"):
            prefix = "sqlite+aiosqlite:///" if url.startswith("sqlite+aiosqlite:///") else "sqlite:///"
            db_path = url[len(prefix) :]
            if not os.path.isabs(db_path):
                db_path = str(get_project_root() / db_path)
                return f"{prefix}{db_path}"
        return url

    return _DEFAULT_DATABASE_URL


def get_database_settings() -> Dict[str, Any]:
    db_config = dict(get_database_config())
    db_config["url"] = get_database_url()
    return db_config


def get_llm_settings() -> Dict[str, Any]:
    llm_config = get_config().get("llm", {})
    if not isinstance(llm_config, dict):
        raise ValueError("config.llm debe ser un objeto YAML")
    return {
        "provider": str(llm_config.get("provider", os.getenv("LLM_PROVIDER", "ollama"))).strip(),
        "ollama_base_url": str(llm_config.get("ollama_base_url", os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))).strip(),
        "ollama_model": str(llm_config.get("ollama_model", os.getenv("OLLAMA_MODEL", "qwen2.5:14b"))).strip(),
        "timeout_seconds": int(llm_config.get("timeout_seconds", os.getenv("LLM_TIMEOUT_SECONDS", 120))),
        "temperature": float(llm_config.get("temperature", os.getenv("LLM_TEMPERATURE", 0.2))),
        "script_analysis_provider": str(llm_config.get("script_analysis_provider", os.getenv("SCRIPT_ANALYSIS_PROVIDER", "ollama"))).strip(),
        "storyboard_prompt_provider": str(llm_config.get("storyboard_prompt_provider", os.getenv("STORYBOARD_PROMPT_PROVIDER", "ollama"))).strip(),
        "pipeline_builder_provider": str(llm_config.get("pipeline_builder_provider", os.getenv("PIPELINE_BUILDER_PROVIDER", "ollama"))).strip(),
        "enable_fallback": bool(llm_config.get("enable_fallback", True)),
    }


def validate_runtime_security(data: Dict[str, Any]) -> None:
    """Legacy security validation — delegates to core Settings validators.

    Deprecated: production config is now validated by core.config.Settings.
    """
    from core.config import get_settings

    try:
        s = get_settings()
        assert s is not None  # force validation
    except Exception as exc:
        raise RuntimeError(f"Runtime security validation failed via Settings: {exc}") from exc


# ── Legacy module-level singleton ────────────────────────────────────────
# Kept so ``from config import config`` continues to work.
# WARNING: this triggers YAML parsing on import. New code should use
# ``from core.config import get_settings`` instead.
config: Dict[str, Any] = load_config()
