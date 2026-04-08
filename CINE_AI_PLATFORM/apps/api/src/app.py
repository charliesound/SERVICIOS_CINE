from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

from src.auth.dependencies import require_authenticated
from src.settings import settings
from src.storage.sqlite_auth_store import SQLiteAuthStore
from src.storage.json_shots_store import JsonShotsStore
from src.storage.render_jobs_repository import RenderJobsRepository
from src.storage.sequence_plan_runs_repository import SequencePlanRunsRepository
from src.storage.sqlite_render_jobs_store import SQLiteRenderJobsStore
from src.storage.sqlite_sequence_plan_runs_store import SQLiteSequencePlanRunsStore
from src.storage.sqlite_shots_store import SQLiteShotsStore
from src.services.render_jobs_service import RenderJobsService
from src.services.auth_service import AuthService
from src.services.embeddings_service import EmbeddingsService
from src.services.qdrant_context_service import QdrantContextService
from src.services.sequence_semantic_context_service import SequenceSemanticContextService
from src.services.sequence_plan_render_service import SequencePlanRenderService
from src.services.sequence_planner_service import SequencePlannerService
from src.services.shots_service import ShotsService
from src.services.health_service import HealthService
from src.services.comfyui_client import ComfyUIClient
from src.services.render_context_preparer import RenderContextPreparer
from src.services.storage_service import StorageService
from src.controllers.shots_controller import ShotsController
from src.routes.shots_routes import create_shots_router
from src.routes.auth import create_auth_router
from src.routes.health_routes import create_health_router
from src.routes.config_routes import create_config_router
from src.routes.render_jobs_routes import create_render_jobs_router
from src.routes.sequence_routes import create_sequence_router
from src.routes.context_semantic_routes import create_context_semantic_router
from src.routes.storage_routes import create_storage_router
from src.routes.characters import create_characters_router
from src.routes.legacy_routes import include_legacy_routers
from src.routes.followup_v3_routes import create_followup_v3_routes
from src.storage.sqlite_follow_ups_store import SQLiteFollowUpQueueStore
from src.services.followup_automation_service import FollowUpAutomationService
from src.services.email_provider import SMTPProvider


origins_source = settings.cors_origins.strip() or settings.frontend_origins
FRONTEND_ORIGINS = [origin.strip() for origin in origins_source.split(",") if origin.strip()]

OPENAPI_TAGS = [
    {
        "name": "OFFICIAL-STORAGE",
        "description": "Official backend family for storage-first read/write endpoints.",
    },
    {
        "name": "LEGACY-DEPRECATED",
        "description": "Temporary compatibility routes. Do not use for new integrations.",
    },
    {
        "name": "OFFICIAL-RENDER",
        "description": "Official minimal render jobs endpoints for homelab demos.",
    },
    {
        "name": "OFFICIAL-SEQUENCE",
        "description": "Official sequence planning endpoint for storyboard and render preparation.",
    },
    {
        "name": "OFFICIAL-CONTEXT",
        "description": "Official semantic context endpoints backed by embeddings and Qdrant.",
    },
]

if not FRONTEND_ORIGINS:
    FRONTEND_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

shots_backend = settings.shots_store_backend.strip().lower()
json_path = Path(settings.shots_json_file)
sqlite_path = Path(settings.shots_sqlite_file)
render_jobs_path = Path(settings.render_jobs_sqlite_file)

if shots_backend == "sqlite":
    store = SQLiteShotsStore(sqlite_path)
else:
    store = JsonShotsStore(json_path)

service = ShotsService(store)
comfyui_client = ComfyUIClient(
    base_url=settings.comfyui_base_url,
    timeout_seconds=settings.comfyui_timeout_seconds,
)
render_jobs_store = SQLiteRenderJobsStore(render_jobs_path)
render_jobs_repository = RenderJobsRepository(render_jobs_store)
sequence_plan_runs_store = SQLiteSequencePlanRunsStore(render_jobs_path)
sequence_plan_runs_repository = SequencePlanRunsRepository(sequence_plan_runs_store)
embeddings_service = EmbeddingsService(
    base_url=settings.embeddings_service_base_url,
    timeout_seconds=settings.embeddings_service_timeout_seconds,
    expected_dimensions=settings.semantic_context_vector_size,
)
qdrant_context_service = QdrantContextService(
    base_url=settings.qdrant_base_url,
    collection=settings.semantic_context_collection,
    timeout_seconds=settings.qdrant_timeout_seconds,
    vector_size=settings.semantic_context_vector_size,
)
sequence_semantic_context_service = SequenceSemanticContextService(
    embeddings_service=embeddings_service,
    qdrant_context_service=qdrant_context_service,
    default_limit=settings.sequence_semantic_context_limit,
)
auth_service = AuthService(
    store=SQLiteAuthStore(Path(settings.auth_sqlite_file)),
    settings=settings,
)
storage_service = StorageService(
    json_file=json_path,
    sqlite_file=sqlite_path,
)
render_context_preparer = RenderContextPreparer(storage_service)
render_jobs_service = RenderJobsService(
    repository=render_jobs_repository, 
    comfyui_client=comfyui_client,
    preparer=render_context_preparer,
    api_base_url=f"http://{settings.api_host}:{settings.api_port}",
)
sequence_planner_service = SequencePlannerService(
    semantic_context_service=sequence_semantic_context_service,
)
sequence_plan_render_service = SequencePlanRenderService(
    planner_service=sequence_planner_service,
    render_jobs_service=render_jobs_service,
    runs_repository=sequence_plan_runs_repository,
)
health_service = HealthService(
    store_backend=shots_backend,
    json_file=json_path,
    sqlite_file=sqlite_path,
    comfyui_client=comfyui_client,
)
controller = ShotsController(service)

# Follow-up V3 automation
follow_ups_path = Path(settings.followup_sqlite_file)
follow_ups_store = SQLiteFollowUpQueueStore(follow_ups_path)

smtp_provider = None
if settings.smtp_host and settings.smtp_username and settings.smtp_password:
    smtp_provider = SMTPProvider(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        use_tls=settings.smtp_use_tls,
        use_ssl=settings.smtp_use_ssl,
        timeout=settings.smtp_timeout_seconds,
        allow_self_signed=settings.smtp_allow_self_signed,
    )

followup_automation = FollowUpAutomationService(
    store=follow_ups_store,
    send_mode=settings.followup_send_mode,
    auto_send_enabled=settings.followup_auto_send_enabled,
    smtp_provider=smtp_provider,
    from_name=settings.followup_from_name,
    from_email=settings.followup_from_email,
    reply_to=settings.followup_reply_to or None,
    test_recipient=settings.followup_test_recipient or None,
    automation_enabled=True,
    retry_enabled=True,
    max_attempts=3,
    retry_base_minutes=30,
    queue_batch_size=20,
    auto_enqueue_on_generate=True,
    sequence_cid_storyboard_enabled=True,
)

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=OPENAPI_TAGS,
)

app.state.auth_service = auth_service


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    code = str(detail.get("code") or "HTTP_ERROR")
    message = str(detail.get("message") or exc.detail or "Request failed")
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": {"code": code, "message": message}},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(create_auth_router())
app.include_router(create_health_router(shots_backend, health_service))
app.include_router(create_config_router(shots_backend))
app.include_router(
    create_storage_router(shots_backend, storage_service),
    tags=["OFFICIAL-STORAGE"],
    dependencies=[Depends(require_authenticated)],
)
app.include_router(
    create_characters_router(shots_backend, storage_service),
    dependencies=[Depends(require_authenticated)],
)
app.include_router(
    create_shots_router(controller),
    dependencies=[Depends(require_authenticated)],
)
app.include_router(
    create_render_jobs_router(render_jobs_service),
    tags=["OFFICIAL-RENDER"],
    dependencies=[Depends(require_authenticated)],
)
app.include_router(
    create_sequence_router(sequence_planner_service, sequence_plan_render_service),
    tags=["OFFICIAL-SEQUENCE"],
    dependencies=[Depends(require_authenticated)],
)
app.include_router(
    create_context_semantic_router(embeddings_service, qdrant_context_service),
    tags=["OFFICIAL-CONTEXT"],
    dependencies=[Depends(require_authenticated)],
)

if settings.enable_legacy_routes:
    include_legacy_routers(app)

app.include_router(
    create_followup_v3_routes(followup_automation),
    tags=["FOLLOWUP-V3"],
)
