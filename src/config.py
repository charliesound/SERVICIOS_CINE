import os
from pathlib import Path
from typing import Any, Dict
import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./ailinkcinema_s2.db"


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
