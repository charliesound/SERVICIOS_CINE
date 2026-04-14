from typing import AsyncGenerator

from sqlalchemy import event, inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import get_database_settings
from services.producer_catalog import DEMO_OPPORTUNITIES, parse_catalog_deadline


DATABASE_SETTINGS = get_database_settings()
DATABASE_URL = str(DATABASE_SETTINGS["url"])


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def is_postgresql_url(database_url: str) -> bool:
    return database_url.startswith("postgresql") or database_url.startswith("postgres")


def validate_database_url(database_url: str) -> str:
    normalized = database_url.strip()
    if not normalized:
        raise ValueError("DATABASE_URL must not be empty")

    if is_sqlite_url(normalized):
        return normalized

    if is_postgresql_url(normalized):
        if "+asyncpg://" not in normalized:
            raise ValueError(
                "PostgreSQL DATABASE_URL must use the asyncpg driver, e.g. postgresql+asyncpg://..."
            )
        return normalized

    raise ValueError(
        "Unsupported DATABASE_URL. Use sqlite+aiosqlite:// or postgresql+asyncpg://"
    )


DATABASE_URL = validate_database_url(DATABASE_URL)
IS_SQLITE = is_sqlite_url(DATABASE_URL)
RUNTIME_SCHEMA_SYNC = bool(DATABASE_SETTINGS.get("runtime_schema_sync", True))
SQLITE_LEGACY_BOOTSTRAP = bool(DATABASE_SETTINGS.get("sqlite_legacy_bootstrap", True))

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False, "timeout": 30} if IS_SQLITE else {},
)


if IS_SQLITE:

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()


async def _bootstrap_sqlite_schema(conn) -> None:
    saved_columns = await _get_sqlite_columns(conn, "saved_opportunities")
    if "created_at" not in saved_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE saved_opportunities ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )

    demo_request_columns = await _get_sqlite_columns(conn, "producer_demo_requests")
    if "source" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE producer_demo_requests ADD COLUMN source VARCHAR(100) DEFAULT 'website'"
        )
    if "status" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE producer_demo_requests ADD COLUMN status VARCHAR(50) DEFAULT 'new'"
        )
    if "created_at" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE producer_demo_requests ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )

    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_saved_opportunities_created_at ON saved_opportunities(created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_producer_demo_requests_created_at ON producer_demo_requests(created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_producer_demo_requests_status_created_at ON producer_demo_requests(status, created_at)"
    )

    await _bootstrap_review_delivery_schema(conn)


async def _get_sqlite_columns(conn, table_name: str) -> list[str]:
    result = await conn.exec_driver_sql(f"PRAGMA table_info({table_name})")
    return [row[1] for row in result.fetchall()]


async def _has_table(conn, table_name: str) -> bool:
    return await conn.run_sync(
        lambda sync_conn: inspect(sync_conn).has_table(table_name)
    )


async def _bootstrap_review_delivery_schema(conn) -> None:
    review_columns = await _get_sqlite_columns(conn, "reviews")
    if "created_at" not in review_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE reviews ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    if "status" not in review_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE reviews ADD COLUMN status VARCHAR(50) DEFAULT 'pending'"
        )
    if "updated_at" not in review_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE reviews ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE reviews SET status = 'pending' WHERE status IS NULL OR trim(status) = ''"
    )
    await conn.exec_driver_sql(
        "UPDATE reviews SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )
    await conn.exec_driver_sql(
        "UPDATE reviews SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP) WHERE updated_at IS NULL"
    )

    approval_columns = await _get_sqlite_columns(conn, "approval_decisions")
    if "status_applied" not in approval_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE approval_decisions ADD COLUMN status_applied VARCHAR(50) DEFAULT 'pending'"
        )
    if "author_id" not in approval_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE approval_decisions ADD COLUMN author_id VARCHAR(36)"
        )
    if "author_name" not in approval_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE approval_decisions ADD COLUMN author_name VARCHAR(100)"
        )
    if "rationale_note" not in approval_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE approval_decisions ADD COLUMN rationale_note TEXT"
        )
    if "created_at" not in approval_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE approval_decisions ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE approval_decisions SET status_applied = 'pending' WHERE status_applied IS NULL OR trim(status_applied) = ''"
    )
    await conn.exec_driver_sql(
        "UPDATE approval_decisions SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )

    comment_columns = await _get_sqlite_columns(conn, "review_comments")
    if "author_id" not in comment_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE review_comments ADD COLUMN author_id VARCHAR(36)"
        )
    if "author_name" not in comment_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE review_comments ADD COLUMN author_name VARCHAR(100)"
        )
    if "created_at" not in comment_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE review_comments ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE review_comments SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )

    deliverable_columns = await _get_sqlite_columns(conn, "deliverables")
    if "source_review_id" not in deliverable_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE deliverables ADD COLUMN source_review_id VARCHAR(36)"
        )
    if "delivery_payload" not in deliverable_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE deliverables ADD COLUMN delivery_payload JSON DEFAULT '{}'"
        )
    if "created_at" not in deliverable_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE deliverables ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    if "status" not in deliverable_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE deliverables ADD COLUMN status VARCHAR(20) DEFAULT 'draft'"
        )
    if "updated_at" not in deliverable_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE deliverables ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE deliverables SET delivery_payload = '{}' WHERE delivery_payload IS NULL"
    )
    await conn.exec_driver_sql(
        "UPDATE deliverables SET status = 'draft' WHERE status IS NULL OR trim(status) = ''"
    )
    await conn.exec_driver_sql(
        "UPDATE deliverables SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )
    await conn.exec_driver_sql(
        "UPDATE deliverables SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP) WHERE updated_at IS NULL"
    )

    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_reviews_project_target_created_at ON reviews(project_id, target_type, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_reviews_project_target_id_created_at ON reviews(project_id, target_type, target_id, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_reviews_project_status_created_at ON reviews(project_id, status, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_approval_decisions_review_created_at ON approval_decisions(review_id, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_approval_decisions_review_status_created_at ON approval_decisions(review_id, status_applied, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_review_comments_review_created_at ON review_comments(review_id, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_deliverables_project_status_created_at ON deliverables(project_id, status, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_deliverables_project_source_review_created_at ON deliverables(project_id, source_review_id, created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_deliverables_source_review_id ON deliverables(source_review_id)"
    )

    duplicate_source_reviews = await conn.exec_driver_sql(
        "SELECT source_review_id FROM deliverables WHERE source_review_id IS NOT NULL GROUP BY source_review_id HAVING COUNT(*) > 1 LIMIT 1"
    )
    if duplicate_source_reviews.fetchone() is None:
        await conn.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_deliverables_source_review_id ON deliverables(source_review_id) WHERE source_review_id IS NOT NULL"
        )


async def _seed_funding_catalog() -> None:
    from models.producer import FundingOpportunity

    async with AsyncSessionLocal() as session:
        existing_ids = {
            row[0]
            for row in (await session.execute(select(FundingOpportunity.id))).all()
        }

        for opportunity in DEMO_OPPORTUNITIES:
            if opportunity["id"] in existing_ids:
                continue

            session.add(
                FundingOpportunity(
                    id=opportunity["id"],
                    title=opportunity["title"],
                    description=opportunity.get("description"),
                    amount_range=opportunity.get("amount_range"),
                    deadline=parse_catalog_deadline(opportunity.get("deadline")),
                    metadata_json={
                        "source_id": opportunity.get("source_id"),
                        "eligibility": opportunity.get("eligibility", []),
                        "tags": opportunity.get("tags", []),
                    },
                )
            )

        await session.commit()


async def _verify_database_connection() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def _seed_funding_catalog_if_ready() -> None:
    async with engine.connect() as conn:
        if not await _has_table(conn, "funding_opportunities"):
            return

    await _seed_funding_catalog()


async def init_db():
    """Initialize the configured database.

    Behavior by configuration:
    - PostgreSQL: Alembic is primary (user must run migrations manually)
    - SQLite with USE_ALEMBIC=true: Use Alembic, skip runtime bootstrap
    - SQLite default: Legacy runtime bootstrap (for dev convenience)
    """
    import os
    from models import Organization, Project, User
    from models.delivery import Deliverable
    from models.review import ApprovalDecision, Review, ReviewComment
    from models.narrative import Character, Scene, Sequence, scene_character_link
    from models.postproduction import AssemblyCut, Clip
    from models.producer import (
        DemoRequestRecord,
        FundingOpportunity,
        LeadGenEvent,
        SavedOpportunity,
    )
    from models.visual import Shot, VisualAsset

    del (
        Organization,
        Project,
        User,
        Deliverable,
        ApprovalDecision,
        Review,
        ReviewComment,
        Character,
        Scene,
        Sequence,
        scene_character_link,
        AssemblyCut,
        Clip,
        DemoRequestRecord,
        FundingOpportunity,
        LeadGenEvent,
        SavedOpportunity,
        Shot,
        VisualAsset,
    )

    use_alembic = os.getenv("USE_ALEMBIC", "").lower() in ("1", "true", "yes")
    is_postgresql = not IS_SQLITE

    if is_postgresql or use_alembic:
        await _verify_database_connection()
        await _seed_funding_catalog_if_ready()
        return

    if IS_SQLITE and RUNTIME_SCHEMA_SYNC:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            if SQLITE_LEGACY_BOOTSTRAP:
                await _bootstrap_sqlite_schema(conn)

        await _seed_funding_catalog()
        return

    await _verify_database_connection()
    await _seed_funding_catalog_if_ready()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to yield an async DB session for FastAPI endpoints.
    Ensures safe rollback on exception and cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
