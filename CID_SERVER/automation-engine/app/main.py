import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.schemas.lead_event import LeadEvent
from app.schemas.script_event import ScriptEvent
from app.schemas.routing_result import RoutingResult, ScriptRoutingResult
from app.services.dispatcher import Dispatcher

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Automation Engine V1 starting (dry_run=%s)", settings.DRY_RUN)
    yield
    logger.info("Automation Engine V1 shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

dispatcher = Dispatcher()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "dry_run": settings.DRY_RUN,
    }


@app.post("/route/lead", response_model=RoutingResult)
async def route_lead(event: LeadEvent):
    result = await dispatcher.route_lead(event)
    return result


@app.post("/route/script", response_model=ScriptRoutingResult)
async def route_script(event: ScriptEvent):
    result = await dispatcher.route_script(event)
    return result
