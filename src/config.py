import os
from pathlib import Path
from typing import Any, Dict
import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./ailinkcinema_s2.db"


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_env_bool(name: str) -> bool | None:
    value = os.getenv(name)
    if value is None:
        return None
    return _parse_bool(value)


def _apply_env_overrides(data: Dict[str, Any]) -> Dict[str, Any]:
    app_config = data.setdefault("app", {})
    auth_config = data.setdefault("auth", {})
    demo_config = data.setdefault("demo", {})
    features_config = data.setdefault("features", {})
    queue_config = data.setdefault("queue", {})

    app_env = os.getenv("APP_ENV", str(app_config.get("env", "production"))).strip()
    app_config["env"] = app_env

    app_debug = _get_env_bool("APP_DEBUG")
    if app_debug is not None:
        app_config["debug"] = app_debug

    app_secret = os.getenv("APP_SECRET_KEY")
    if app_secret:
        app_config["secret_key"] = app_secret

    auth_secret = os.getenv("AUTH_SECRET_KEY")
    if auth_secret:
        auth_config["secret_key"] = auth_secret

    auth_algorithm = os.getenv("AUTH_ALGORITHM")
    if auth_algorithm:
        auth_config["algorithm"] = auth_algorithm

    access_token_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    if access_token_minutes:
        auth_config["access_token_expire_minutes"] = int(access_token_minutes)

    demo_enabled = _get_env_bool("ENABLE_DEMO_ROUTES")
    if demo_enabled is not None:
        demo_config["enabled"] = demo_enabled
    elif app_env.lower() == "production":
        demo_config["enabled"] = False

    auto_seed_narrative = _get_env_bool("DEMO_AUTO_SEED_NARRATIVE")
    if auto_seed_narrative is not None:
        demo_config["auto_seed_narrative"] = auto_seed_narrative

    experimental_enabled = _get_env_bool("ENABLE_EXPERIMENTAL_ROUTES")
    if experimental_enabled is not None:
        features_config["experimental"] = experimental_enabled
    elif app_env.lower() == "production":
        features_config["experimental"] = False

    postproduction_enabled = _get_env_bool("ENABLE_POSTPRODUCTION_ROUTES")
    if postproduction_enabled is not None:
        features_config["postproduction"] = postproduction_enabled
    elif app_env.lower() == "production":
        features_config["postproduction"] = False

    queue_config["persistence_mode"] = os.getenv(
        "QUEUE_PERSISTENCE_MODE",
        str(queue_config.get("persistence_mode", "memory")),
    ).strip()
    queue_config["production_ready"] = (
        queue_config["persistence_mode"].lower() != "memory"
    )

    return data


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def get_config_path() -> Path:
    return get_base_dir() / "config" / "config.yaml"


def load_config(force_reload: bool = False) -> Dict[str, Any]:
    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None and not force_reload:
        return _CONFIG_CACHE

    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró config.yaml en: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError("config.yaml debe contener un objeto YAML raíz")

    data = _apply_env_overrides(data)
    _CONFIG_CACHE = data
    return _CONFIG_CACHE


def get_config() -> Dict[str, Any]:
    return load_config()


def get_database_config() -> Dict[str, Any]:
    database_config = get_config().get("database", {})
    if not isinstance(database_config, dict):
        raise ValueError("config.database debe ser un objeto YAML")
    return database_config


def get_database_url() -> str:
    env_database_url = os.getenv("DATABASE_URL")
    if env_database_url:
        return env_database_url

    configured_url = get_database_config().get("url")
    if isinstance(configured_url, str) and configured_url.strip():
        return configured_url.strip()

    return DEFAULT_DATABASE_URL


def get_database_settings() -> Dict[str, Any]:
    database_config = dict(get_database_config())
    database_config["url"] = get_database_url()
    return database_config


config = load_config()
