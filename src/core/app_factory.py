from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from core.errors import register_error_handlers
from core.lifespan import lifespan

logger = logging.getLogger("servicios_cine.factory")


def create_app() -> FastAPI:
    """Enterprise application factory.

    Creates and returns a fully configured FastAPI instance with:
    - Pydantic Settings
    - CORS (strict per environment)
    - Request ID middleware
    - Global error handlers
    - Health check endpoints
    - Lifespan (startup / shutdown)
    - All existing routers
    """
    settings = get_settings()

    # ── Build app ────────────────────────────────────────────────────────
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # ── Store settings on app state ──────────────────────────────────────
    app.state.settings = settings
    app.state.startup_ok = True

    # ── CORS ─────────────────────────────────────────────────────────────
    origins = settings.cors_allowed_origins
    if settings.app_env == "development" and "*" in origins:
        logger.warning("CORS allows '*' in development — insecure if exposed externally")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )

    # ── Request ID middleware ────────────────────────────────────────────
    from middleware.request_id import request_id_middleware

    app.middleware("http")(request_id_middleware)

    # ── Rate limiter middleware ──────────────────────────────────────────
    from middleware.rate_limiter import rate_limit_middleware

    app.middleware("http")(rate_limit_middleware)

    # ── Request logging middleware ───────────────────────────────────────
    import time

    from services.logging_service import logger as svc_logger, request_logger
    from services.metrics_service import metrics_collector

    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        metrics_collector.record_request(duration_ms)
        request_logger.log_request(
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    # ── Error handlers ───────────────────────────────────────────────────
    register_error_handlers(app, settings)

    # ── Catch-all outer middleware for truly unhandled exceptions ────────
    # Handles ExceptionGroup wrapping from Starlette's middleware internals
    # that bypasses the standard exception_handlers dict.
    @app.middleware("http")
    async def catch_unhandled_exceptions(request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            from core.errors import build_error_response

            logger.exception("Unhandled exception caught by outer middleware: %s", exc)
            body = build_error_response(request, 500, "INTERNAL_ERROR", "An unexpected internal error occurred")
            return JSONResponse(status_code=500, content=body)

    # ── Register routers ────────────────────────────────────────────────
    _register_routers(app, settings)

    logger.info(
        "App factory created: %s v%s [%s] — %d routes",
        settings.app_name,
        settings.app_version,
        settings.app_env,
        len(app.routes),
    )

    return app


def _register_routers(app: FastAPI, settings) -> None:
    """Register all existing application routers."""

    # ── Health — first so they are always available ──────────────────────
    from routes.health import router as health_router

    app.include_router(health_router)

    # ── Existing /health and /ready aliases (backward compat) ────────────
    from fastapi.responses import JSONResponse
    from sqlalchemy import text

    @app.get("/health")
    async def health_compat():
        """Legacy alias — delegates to /health/live."""
        return {
            "name": settings.app_name,
            "status": "ok",
            "env": settings.app_env,
        }

    @app.get("/ready")
    async def ready_compat():
        """Legacy alias — delegates to /health/ready."""
        try:
            from database import engine

            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ready", "database": "connected"}
        except Exception as exc:
            from services.logging_service import logger

            logger.error("Health check failed: %s", exc)
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "database": "disconnected", "error": str(exc)},
            )

    # ── Auth / user ──────────────────────────────────────────────────────
    from routes.auth_routes import router as auth_router

    app.include_router(auth_router, tags=["auth"])

    from routes.user_routes import router as user_router

    app.include_router(user_router, tags=["users"])

    # ── Core feature routers ─────────────────────────────────────────────
    from routes.render_routes import router as render_router
    from routes.queue_routes import router as queue_router
    from routes.workflow_routes import router as workflow_router
    from routes.plan_routes import router as plan_router
    from routes.ops_routes import router as ops_router
    from routes.metrics_routes import router as metrics_router
    from routes.events_routes import router as events_router

    app.include_router(render_router, tags=["render"])
    app.include_router(queue_router, tags=["queue"])
    app.include_router(workflow_router, tags=["workflows"])
    app.include_router(plan_router, tags=["plans"])
    app.include_router(ops_router, tags=["ops"])
    app.include_router(metrics_router, tags=["metrics"])
    app.include_router(events_router, tags=["events"])

    # ── Project / project-related ────────────────────────────────────────
    from routes.project_routes import router as project_router

    app.include_router(project_router, tags=["projects"])

    from routes.review_routes import router as review_router
    from routes.delivery_routes import router as delivery_router
    from routes.producer_routes import router as producer_router
    from routes.storage_routes import router as storage_router
    from routes.ingest_routes import router as ingest_router
    from routes.document_routes import router as document_router
    from routes.report_routes import router as report_router
    from routes.presentation_routes import router as presentation_router
    from routes.shot_routes import router as shot_router
    from routes.storyboard_routes import router as storyboard_router
    from routes.funding_routes import funding_router, router as funding_project_router
    from routes.funding_catalog_routes import router as funding_catalog_router

    app.include_router(review_router, tags=["reviews"])
    app.include_router(delivery_router, tags=["delivery"])
    app.include_router(producer_router, tags=["producer"])
    app.include_router(storage_router, tags=["storage-sources"])
    app.include_router(ingest_router, tags=["ingest"])
    app.include_router(document_router, tags=["documents"])
    app.include_router(report_router, tags=["structured-reports"])
    app.include_router(presentation_router, tags=["presentation"])
    app.include_router(shot_router, tags=["shots"])
    app.include_router(storyboard_router, tags=["storyboard"])
    app.include_router(funding_router, tags=["funding-public"])
    app.include_router(funding_catalog_router, tags=["funding-catalog"])
    app.include_router(funding_project_router, tags=["funding"])

    # ── Funding private / admin ──────────────────────────────────────────
    from routes.funding_private_routes import private_source_router
    from routes.admin_funding_routes import router as admin_funding_router

    app.include_router(private_source_router, tags=["funding-private"])
    app.include_router(admin_funding_router, tags=["admin-funding"])

    # ── Intake / budget / project-funding ────────────────────────────────
    from routes.intake_routes import router as intake_router
    from routes.budget_routes import router as budget_router
    from routes.project_funding_routes import router as project_funding_router
    from routes.project_document_routes import router as project_document_router
    from routes.google_drive_routes import router as google_drive_router
    from routes.matcher_routes import router as matcher_router

    app.include_router(intake_router, tags=["intake"])
    app.include_router(budget_router, tags=["budget"])
    app.include_router(project_funding_router, tags=["project-funding"])
    app.include_router(project_document_router, tags=["project-documents"])
    app.include_router(google_drive_router, tags=["google-drive-integrations"])
    app.include_router(matcher_router, tags=["matcher"])

    # ── Editorial / script / members / change-governance ─────────────────
    from routes.editorial_routes import router as editorial_router
    from routes.script_version_routes import router as script_version_router
    from routes.project_member_routes import router as project_member_router
    from routes.change_governance_routes import router as change_governance_router

    app.include_router(editorial_router, tags=["editorial"])
    app.include_router(script_version_router, tags=["script-versioning"])
    app.include_router(project_member_router, tags=["project-members"])
    app.include_router(change_governance_router, tags=["change-governance"])

    # ── Shooting plan / shot list / producer pitch / distribution ────────
    from routes.shotlist_routes import router as shotlist_router
    from routes.shooting_plan_routes import router as shooting_plan_router
    from routes.producer_pitch_routes import router as producer_pitch_router
    from routes.distribution_pack_routes import router as distribution_pack_router
    from routes.sales_targets_routes import router as sales_targets_router
    from routes.crm_routes import router as crm_router

    app.include_router(shotlist_router, tags=["shotlist"])
    app.include_router(shooting_plan_router, tags=["shooting-plans"])
    app.include_router(producer_pitch_router, tags=["producer-pitch"])
    app.include_router(distribution_pack_router, tags=["distribution"])
    app.include_router(sales_targets_router, tags=["sales-targets"])
    app.include_router(crm_router, tags=["commercial-crm"])

    # ── CID pipelines / storyboard / concept-art ─────────────────────────
    from routes.cid_pipeline_routes import router as cid_pipeline_router
    from routes.ops_routes import pipeline_router

    app.include_router(cid_pipeline_router, tags=["cid-pipelines"])
    app.include_router(pipeline_router, tags=["pipelines"])

    from routes.ollama_storyboard_routes import router as ollama_storyboard_router
    from routes.comfyui_storyboard_routes import router as comfyui_storyboard_router
    from routes.concept_art_routes import router as concept_art_router
    from routes.cid_script_to_prompt_routes import router as cid_script_to_prompt_router
    from routes.cid_visual_reference_routes import router as cid_visual_reference_router

    app.include_router(ollama_storyboard_router, tags=["ollama-storyboard"])
    app.include_router(comfyui_storyboard_router, tags=["comfyui-storyboard"])
    app.include_router(concept_art_router, tags=["concept-art"])
    app.include_router(cid_script_to_prompt_router, tags=["cid-script-to-prompt"])
    app.include_router(cid_visual_reference_router, tags=["cid-visual-reference"])

    # ── ComfySearch / Solutions / Dubbing / App Registry ─────────────────
    from routes.comfysearch_routes import router as comfysearch_router
    from routes.solutions_routes import router as solutions_router
    from routes.dubbing_bridge_routes import router as dubbing_bridge_router
    from routes.app_registry_routes import router as app_registry_router

    app.include_router(comfysearch_router, tags=["comfysearch"])
    app.include_router(solutions_router, tags=["solutions"])
    app.include_router(app_registry_router, tags=["app-registry"])
    app.include_router(dubbing_bridge_router, tags=["dubbing-bridge"])

    # ── Postproduction (feature-flagged) ─────────────────────────────────
    if settings.feature_postproduction:
        from routes.postproduction_routes import router as postproduction_router

        app.include_router(postproduction_router, tags=["postproduction"])

    # ── Admin (feature-flagged) ──────────────────────────────────────────
    if settings.feature_admin:
        from routes.admin_routes import router as admin_router

        app.include_router(admin_router, tags=["admin"])

    # ── Demo (config-controlled) ─────────────────────────────────────────
    if settings.demo_enabled:
        from routes.demo_routes import router as demo_router

        app.include_router(demo_router, tags=["demo"])

    # ── Experimental (feature-flagged) ───────────────────────────────────
    if settings.feature_experimental:
        try:
            from routes.experimental_routes import router as experimental_router

            app.include_router(experimental_router, tags=["experimental"])
        except Exception:
            pass

    # ── ComfyUI Instance Registry ────────────────────────────────────────
    from routes.comfyui_instance_routes import router as comfyui_instance_router

    app.include_router(comfyui_instance_router, tags=["comfyui"])

    # ── CID internal test mode ───────────────────────────────────────────
    import os

    if os.getenv("CID_INTERNAL_TEST_MODE_ENABLED", "false").strip().lower() == "true":
        from routes.cid_test_routes import router as cid_test_router

        app.include_router(cid_test_router, tags=["cid-internal-test"])
