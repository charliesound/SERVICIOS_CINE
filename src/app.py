from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from config import load_config

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
from routes.visual_routes import router as visual_router
from routes.postproduction_routes import router as postproduction_router
from routes.review_routes import router as review_router
from routes.delivery_routes import router as delivery_router
from routes.producer_routes import router as producer_router
from routes.storage_routes import router as storage_router
from routes.ingest_routes import router as ingest_router
from routes.document_routes import router as document_router
from routes.report_routes import router as report_router

# Services
from services.logging_service import logger, request_logger
from services.metrics_service import metrics_collector
from middleware.rate_limiter import rate_limit_middleware
from database import init_db


config = load_config()

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
app.include_router(visual_router, tags=["visual-pipeline"])
app.include_router(review_router, tags=["reviews"])
app.include_router(delivery_router, tags=["delivery"])
app.include_router(producer_router, tags=["producer"])
app.include_router(storage_router, tags=["storage-sources"])
app.include_router(ingest_router, tags=["ingest"])
app.include_router(document_router, tags=["documents"])
app.include_router(report_router, tags=["structured-reports"])

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


logger.info(
    f"AILinkCinema started - environment: {app_config.get('env', 'production')}"
)
