import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = "cid-manifest.json"
_registry: dict[str, dict] = {}
_loaded = False
_base_dir = Path(__file__).parent.parent.parent

_httpx_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _httpx_client
    if _httpx_client is None:
        _httpx_client = httpx.AsyncClient(timeout=5.0)
    return _httpx_client


def _get_search_dirs() -> list[Path]:
    env_dirs = os.getenv("CID_APPS_DIRS", "")
    if env_dirs.strip():
        return [Path(d.strip()) for d in env_dirs.split(",") if d.strip()]
    return [
        _base_dir / "comfysearch",
        _base_dir / "ai-dubbing-legal-studio",
        _base_dir / "CID_VOICE_CHATBOT",
    ]


def discover_apps() -> list[Path]:
    found = []
    search_dirs = _get_search_dirs()
    for d in search_dirs:
        if d.exists():
            manifest = d / MANIFEST_FILENAME
            if manifest.exists() and d not in found:
                found.append(d)
        else:
            logger.debug("App Registry: search dir %s does not exist", d)
    for entry in sorted(_base_dir.iterdir()):
        if entry.is_dir():
            manifest = entry / MANIFEST_FILENAME
            if manifest.exists() and entry not in found:
                found.append(entry)
    return found


def load_manifest(app_dir: Path) -> Optional[dict]:
    manifest_path = app_dir / MANIFEST_FILENAME
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest["_path"] = str(app_dir)
        manifest["_manifest_path"] = str(manifest_path)
        return manifest
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("App Registry: error loading manifest %s: %s", manifest_path, e)
        return None


async def check_app_health(manifest: dict) -> dict:
    health: dict = {"status": "unknown", "latency_ms": None}
    entrypoints = manifest.get("entrypoints", {})
    api = entrypoints.get("api", {})
    health_endpoint = api.get("health_endpoint", "/health")
    base_url = api.get("url", "")
    if not base_url:
        return health
    try:
        client = _get_client()
        start = asyncio.get_event_loop().time()
        resp = await client.get(f"{base_url.rstrip('/')}/{health_endpoint.lstrip('/')}")
        latency = int((asyncio.get_event_loop().time() - start) * 1000)
        if resp.status_code < 500:
            health["status"] = "online" if resp.status_code < 400 else "degraded"
        else:
            health["status"] = "offline"
        health["latency_ms"] = latency
        health["status_code"] = resp.status_code
    except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError):
        health["status"] = "offline"
    return health


async def load_all():
    global _registry, _loaded
    _registry = {}
    apps = discover_apps()
    for app_dir in apps:
        manifest = load_manifest(app_dir)
        if manifest:
            app_id = manifest.get("app_id", app_dir.name)
            manifest["_last_seen"] = datetime.now(timezone.utc).isoformat()
            manifest["_health"] = await check_app_health(manifest)
            _registry[app_id] = manifest
            logger.info("App Registry: cargada app '%s' (%s)", app_id, app_dir.name)
    _loaded = True
    logger.info("App Registry: %d apps cargadas", len(_registry))
    return _registry


async def get_all_apps() -> list[dict]:
    if not _loaded:
        await load_all()
    tasks = []
    for app_id, manifest in list(_registry.items()):
        tasks.append(_refresh_health(app_id, manifest))
    if tasks:
        await asyncio.gather(*tasks)
    return list(_registry.values())


async def _refresh_health(app_id: str, manifest: dict):
    manifest["_health"] = await check_app_health(manifest)


async def get_app(app_id: str) -> Optional[dict]:
    if not _loaded:
        await load_all()
    manifest = _registry.get(app_id)
    if manifest:
        manifest["_health"] = await check_app_health(manifest)
    return manifest


def get_app_by_directory(dirname: str) -> Optional[dict]:
    if not _loaded:
        return None
    for manifest in _registry.values():
        path: str = manifest.get("_path", "")
        if path.endswith(dirname) or dirname in path:
            return manifest
    return None


async def get_integrated_apps() -> list[dict]:
    apps = await get_all_apps()
    return [a for a in apps if a.get("entrypoints", {}).get("cid_integration", {}).get("api_prefix")]


async def get_standalone_apps() -> list[dict]:
    apps = await get_all_apps()
    return [a for a in apps if not a.get("entrypoints", {}).get("cid_integration", {}).get("api_prefix")]


async def get_apps_by_category(category: str) -> list[dict]:
    return [a for a in await get_all_apps() if a.get("category") == category]


async def get_app_categories() -> list[str]:
    cats = set()
    for a in await get_all_apps():
        cat = a.get("category")
        if cat:
            cats.add(cat)
    return sorted(cats)
