import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .models import Base
from .routes import router as budget_router
from .core import setup_logging, CORS_ORIGINS, RATE_LIMIT_PER_MINUTE

logger = setup_logging()

SessionLocal = None
engine = None


def init_db():
    global engine, SessionLocal
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cid_budget")
    engine = create_engine(db_url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database connected: %s", db_url.replace("://", "://***:***@") if "@" in db_url else db_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    jwt_secret = os.getenv("JWT_SECRET", "")
    if not jwt_secret:
        logger.warning("JWT_SECRET not set — authentication disabled. NOT PRODUCTION SAFE.")
    init_db()
    yield
    if engine:
        engine.dispose()


app = FastAPI(title="CID Budget Estimator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(budget_router)

_rate_store: dict = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if RATE_LIMIT_PER_MINUTE > 0:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60
        _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < window]
        if len(_rate_store[client_ip]) >= RATE_LIMIT_PER_MINUTE:
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        _rate_store[client_ip].append(now)
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    user = request.headers.get("authorization", "")[:20]
    logger.info("%s %s -> %d (%.0fms) [%.20s]", request.method, request.url.path, response.status_code, duration, user)
    return response


@app.get("/health")
async def health():
    db_ok = False
    try:
        if engine:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_ok = True
    except Exception:
        pass
    return {
        "status": "healthy" if db_ok else "degraded",
        "app": "CID Budget Estimator",
        "version": "1.0.0",
        "database": "connected" if db_ok else "disconnected",
        "auth": "enabled" if os.getenv("JWT_SECRET", "") else "disabled",
    }
