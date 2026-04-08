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

# Services
from services.logging_service import logger, request_logger
from services.metrics_service import metrics_collector
from middleware.rate_limiter import rate_limit_middleware


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

# Routers opcionales por feature flag
if features.get("admin", True):
    app.include_router(admin_router, tags=["admin"])

if features.get("experimental", True):
    try:
        from routes.experimental_routes import router as experimental_router

        app.include_router(experimental_router, tags=["experimental"])
    except Exception:
        pass

if config.get("demo", {}).get("enabled", True):
    app.include_router(demo_router, tags=["demo"])


logger.info(
    f"AILinkCinema started - environment: {app_config.get('env', 'production')}"
)
