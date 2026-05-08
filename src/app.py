from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import time

from config import load_config, validate_runtime_security

# Imports de routers
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.render_routes import router as render_router
from routes.queue_routes import router as queue_router
from routes.workflow_routes import router as workflow_router
from routes.plan_routes import router as plan_router
from routes.ops_routes import router as ops_router
from routes.admin_routes import router as admin_router
from routes.demo_routes import router as demo_router
from routes.metrics_routes import router as metrics_router
from routes.events_routes import router as events_router
from routes.project_routes import router as project_router
from routes.postproduction_routes import router as postproduction_router
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
from routes.funding_routes import router as funding_router
from routes.funding_catalog_routes import router as funding_catalog_router
from routes.funding_private_routes import private_source_router
from routes.admin_funding_routes import router as admin_funding_router
from routes.intake_routes import router as intake_router
from routes.budget_routes import router as budget_router
from routes.project_funding_routes import router as project_funding_router
from routes.project_document_routes import router as project_document_router
from routes.google_drive_routes import router as google_drive_router
from routes.matcher_routes import router as matcher_router
from routes.editorial_routes import router as editorial_router
from routes.script_version_routes import router as script_version_router
from routes.project_member_routes import router as project_member_router
from routes.change_governance_routes import router as change_governance_router
from routes.shotlist_routes import router as shotlist_router
from routes.shooting_plan_routes import router as shooting_plan_router
from routes.producer_pitch_routes import router as producer_pitch_router
from routes.distribution_pack_routes import router as distribution_pack_router
from routes.sales_targets_routes import router as sales_targets_router
from routes.crm_routes import router as crm_router
from routes.cid_pipeline_routes import router as cid_pipeline_router
from routes.ops_routes import pipeline_router
from routes.ollama_storyboard_routes import router as ollama_storyboard_router
from routes.comfyui_storyboard_routes import router as comfyui_storyboard_router
from routes.concept_art_routes import router as concept_art_router
from routes.cid_script_to_prompt_routes import router as cid_script_to_prompt_router

# Services
from services.logging_service import logger, request_logger
from services.metrics_service import metrics_collector
from services.instance_registry import registry
from services.job_scheduler import scheduler
from services.queue_service import queue_service
from middleware.rate_limiter import rate_limit_middleware
from database import init_db


config = load_config()
validate_runtime_security(config)

app_config = config.get("app", {})
cors_config = config.get("cors", {})
features = config.get("features", {})

app = FastAPI(
    title=app_config.get("name", "AILinkCinema"),
    debug=app_config.get("debug", False),
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allow_origins", ["*"]),
    allow_credentials=cors_config.get("allow_credentials", True),
    allow_methods=cors_config.get("allow_methods", ["*"]),
    allow_headers=cors_config.get("allow_headers", ["*"]),
)

app.middleware("http")(rate_limit_middleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
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


@app.get("/")
def root():
    return {
        "name": app_config.get("name", "AILinkCinema"),
        "status": "ok",
        "env": app_config.get("env", "production"),
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": app_config.get("name", "AILinkCinema"),
        "env": app_config.get("env", "production"),
    }


@app.get("/ready")
async def ready():
    from database import engine
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from services.logging_service import logger

        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "database": "disconnected",
                "error": str(e),
            },
        )


# Routers base (ya incluyen su propio prefix)
app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["users"])
app.include_router(render_router, tags=["render"])
app.include_router(queue_router, tags=["queue"])
app.include_router(workflow_router, tags=["workflows"])
app.include_router(plan_router, tags=["plans"])
app.include_router(ops_router, tags=["ops"])
app.include_router(metrics_router, tags=["metrics"])
app.include_router(events_router, tags=["events"])
app.include_router(project_router, tags=["projects"])
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
app.include_router(funding_router, tags=["funding"])
app.include_router(funding_catalog_router, tags=["funding-public"])
app.include_router(private_source_router, tags=["funding-private"])
app.include_router(admin_funding_router, tags=["admin-funding"])
app.include_router(intake_router, tags=["intake"])
app.include_router(budget_router, tags=["budget"])
app.include_router(change_governance_router, tags=["change-governance"])
app.include_router(shotlist_router, tags=["shotlist"])
app.include_router(shooting_plan_router, tags=["shooting-plans"])
app.include_router(project_funding_router, tags=["project-funding"])
app.include_router(project_document_router, tags=["project-documents"])
app.include_router(google_drive_router, tags=["google-drive-integrations"])
app.include_router(matcher_router, tags=["matcher"])
app.include_router(editorial_router, tags=["editorial"])
app.include_router(script_version_router, tags=["script-versioning"])
app.include_router(project_member_router, tags=["project-members"])
app.include_router(producer_pitch_router, tags=["producer-pitch"])
app.include_router(distribution_pack_router, tags=["distribution"])
app.include_router(sales_targets_router, tags=["sales-targets"])
app.include_router(crm_router, tags=["commercial-crm"])
app.include_router(pipeline_router, tags=["pipelines"])
app.include_router(cid_pipeline_router, tags=["cid-pipelines"])
app.include_router(ollama_storyboard_router, tags=["ollama-storyboard"])
app.include_router(comfyui_storyboard_router, tags=["comfyui-storyboard"])
app.include_router(concept_art_router, tags=["concept-art"])
app.include_router(cid_script_to_prompt_router, tags=["cid-script-to-prompt"])

if os.getenv("CID_INTERNAL_TEST_MODE_ENABLED", "false").strip().lower() == "true":
    from routes.cid_test_routes import router as cid_test_router

    app.include_router(cid_test_router, tags=["cid-internal-test"])

if features.get("postproduction", False):
    app.include_router(postproduction_router, tags=["postproduction"])

# Routers opcionales por feature flag
if features.get("admin", True):
    app.include_router(admin_router, tags=["admin"])

if features.get("experimental", False):
    try:
        from routes.experimental_routes import router as experimental_router

        app.include_router(experimental_router, tags=["experimental"])
    except Exception:
        pass

if config.get("demo", {}).get("enabled", True):
    app.include_router(demo_router, tags=["demo"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    logger.info("Database initialized successfully")
    instance_config_path = os.getenv("INSTANCE_CONFIG_PATH")
    registry.load_config(instance_config_path if instance_config_path else None)
    logger.info("Backend registry loaded")

    recovery_summary = queue_service.recover_on_startup()
    logger.info("Queue recovery summary: %s", recovery_summary)

    auto_start_scheduler = os.getenv(
        "QUEUE_AUTO_START_SCHEDULER", "1"
    ).strip().lower() not in {"0", "false", "no", "off"}
    if auto_start_scheduler:
        await scheduler.start()
    else:
        logger.warning("Scheduler autostart disabled by QUEUE_AUTO_START_SCHEDULER")

    # Start matcher worker service
    from services.matcher_worker_service import matcher_worker_service
    await matcher_worker_service.start()

    if config.get("queue", {}).get("persistence_mode", "memory").lower() == "memory":
        logger.warning(
            "Queue persistence mode is MEMORY_ONLY. Suitable for demo/dev, not durable enough for full production."
        )

    if config.get("demo", {}).get("enabled", False):
        logger.warning(
            "Demo routes are enabled. Keep ENABLE_DEMO_ROUTES disabled in production deployments."
        )

    if not features.get("postproduction", False):
        logger.info(
            "Postproduction routes disabled: module remains non-production-ready"
        )

    # Auto-seed narrative project if configured
    demo_config = config.get("demo", {})
    if demo_config.get("auto_seed_narrative", False):
        from services.demo_service import demo_service

        try:
            result = await demo_service.seed_narrative_to_db()
            if result.get("status") != "already_seeded":
                logger.info(f"Narrative project auto-seeded: {result}")
        except Exception as e:
            logger.warning(f"Auto-seed failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    await scheduler.stop()


logger.info(
    f"AILinkCinema started - environment: {app_config.get('env', 'production')}"
)
