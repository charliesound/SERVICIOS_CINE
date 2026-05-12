from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

logger = logging.getLogger("servicios_cine.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Enterprise lifespan: log startup/shutdown, validate config, no silent swallows."""

    from core.config import get_settings

    settings = get_settings()

    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("=== %s v%s starting [env=%s] ===", settings.app_name, settings.app_version, settings.app_env)

    _validate_minimum_config(settings)

    app.state.settings = settings
    app.state.startup_ok = True

    try:
        await _run_startup_tasks(app, settings)
    except Exception:
        logger.exception("Startup task failed — app will start in degraded mode")
        app.state.startup_ok = False

    yield  # ← app runs here

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("=== %s shutting down ===", settings.app_name)
    await _run_shutdown_tasks(app, settings)


def _validate_minimum_config(settings) -> None:
    """Fail fast if critical config is missing — do not swallow."""
    if settings.app_env == "production":
        if not settings.jwt_secret or len(settings.jwt_secret) < 32:
            raise RuntimeError("JWT_SECRET is required (≥32 chars) in production — aborting startup")
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required in production — aborting startup")


async def _run_startup_tasks(app: FastAPI, settings) -> None:
    """Initialize database, registry, queue, etc."""
    from database import init_db

    await init_db()
    logger.info("Database initialized successfully")

    instance_config_path = os.getenv("INSTANCE_CONFIG_PATH")
    from services.instance_registry import registry

    registry.load_config(instance_config_path if instance_config_path else None)
    logger.info("Backend registry loaded")

    from services.queue_service import queue_service

    recovery_summary = queue_service.recover_on_startup()
    logger.info("Queue recovery summary: %s", recovery_summary)

    auto_start = os.getenv("QUEUE_AUTO_START_SCHEDULER", "1").strip().lower() not in {"0", "false", "no", "off"}
    if auto_start:
        from services.job_scheduler import scheduler

        await scheduler.start()
    else:
        logger.warning("Scheduler autostart disabled by QUEUE_AUTO_START_SCHEDULER")

    from services.matcher_worker_service import matcher_worker_service

    await matcher_worker_service.start()

    if settings.queue_persistence_mode == "memory":
        logger.warning("Queue persistence mode is MEMORY_ONLY. Suitable for demo/dev, not durable enough for full production.")

    if settings.demo_enabled:
        logger.warning("Demo routes are enabled. Keep ENABLE_DEMO_ROUTES disabled in production deployments.")

    # ComfySearch auto-index
    try:
        from services.comfy_search_service import index_all

        count = index_all()
        logger.info("ComfySearch: indexados %s workflows", count)
    except Exception as exc:
        logger.warning("ComfySearch: error en indexación inicial: %s", exc)

    # Active Solutions seed
    try:
        from services.solutions_service import seed_defaults

        seed_defaults()
        logger.info("Active Solutions: defaults seeded")
    except Exception as exc:
        logger.warning("Active Solutions: error seeding defaults: %s", exc)

    # App Registry discover
    try:
        from services.app_registry import load_all

        apps = await load_all()
        logger.info("App Registry: %d apps descubiertas", len(apps))
    except Exception as exc:
        logger.warning("App Registry: error en descubrimiento: %s", exc)

    # Auto-seed narrative
    if settings.demo_auto_seed_narrative:
        from services.demo_service import demo_service

        try:
            result = await demo_service.seed_narrative_to_db()
            if result.get("status") != "already_seeded":
                logger.info("Narrative project auto-seeded: %s", result)
        except Exception as exc:
            logger.warning("Auto-seed failed: %s", exc)


async def _run_shutdown_tasks(app: FastAPI, settings) -> None:
    from services.job_scheduler import scheduler

    try:
        await scheduler.stop()
    except Exception:
        logger.exception("Error stopping scheduler during shutdown")
