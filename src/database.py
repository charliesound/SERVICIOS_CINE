from typing import AsyncGenerator

import uuid
import json

from sqlalchemy import event, inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

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

engine_kwargs = {
    "echo": False,
    "future": True,
}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 60}
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(DATABASE_URL, **engine_kwargs)


if IS_SQLITE:

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=60000")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
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

    demo_request_columns = await _get_sqlite_columns(conn, "demo_request_records")
    if "source" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE demo_request_records ADD COLUMN source VARCHAR(100) DEFAULT 'website'"
        )
    if "status" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE demo_request_records ADD COLUMN status VARCHAR(50) DEFAULT 'new'"
        )
    if "created_at" not in demo_request_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE demo_request_records ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )

    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_demo_request_records_created_at ON demo_request_records(created_at)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_demo_request_records_status_created_at ON demo_request_records(status, created_at)"
    )

    await _bootstrap_core_schema(conn)
    await _bootstrap_account_schema(conn)
    await _bootstrap_review_delivery_schema(conn)
    await _bootstrap_ingest_document_schema(conn)


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


async def _bootstrap_core_schema(conn) -> None:
    organization_columns = await _get_sqlite_columns(conn, "organizations")
    if "is_active" not in organization_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE organizations ADD COLUMN is_active BOOLEAN DEFAULT 1"
        )
    if "created_at" not in organization_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE organizations ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE organizations SET is_active = COALESCE(is_active, 1)"
    )
    await conn.exec_driver_sql(
        "UPDATE organizations SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )

    project_columns = await _get_sqlite_columns(conn, "projects")
    if "status" not in project_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE projects ADD COLUMN status VARCHAR(50) DEFAULT 'active'"
        )
    if "script_text" not in project_columns:
        await conn.exec_driver_sql("ALTER TABLE projects ADD COLUMN script_text TEXT")
    if "created_at" not in project_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE projects ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE projects SET status = COALESCE(NULLIF(trim(status), ''), 'active')"
    )
    await conn.exec_driver_sql(
        "UPDATE projects SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )

    user_columns = await _get_sqlite_columns(conn, "users")
    if "full_name" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN full_name VARCHAR(255)"
        )
    if "role" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN role VARCHAR(8) DEFAULT 'user'"
        )
    if "is_active" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1"
        )
    if "created_at" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    await conn.exec_driver_sql(
        "UPDATE users SET role = COALESCE(NULLIF(trim(role), ''), 'user')"
    )
    await conn.exec_driver_sql("UPDATE users SET is_active = COALESCE(is_active, 1)")
    await conn.exec_driver_sql(
        "UPDATE users SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
    )

    project_job_columns = await _get_sqlite_columns(conn, "project_jobs")
    if "status" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"
        )
    if "result_data" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN result_data TEXT"
        )
    if "error_message" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN error_message VARCHAR(2000)"
        )
    if "created_by" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN created_by VARCHAR(36)"
        )
    if "updated_at" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    if "completed_at" not in project_job_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE project_jobs ADD COLUMN completed_at DATETIME"
        )
    await conn.exec_driver_sql(
        "UPDATE project_jobs SET status = COALESCE(NULLIF(trim(status), ''), 'pending')"
    )
    await conn.exec_driver_sql(
        "UPDATE project_jobs SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP) WHERE updated_at IS NULL"
    )


async def _bootstrap_account_schema(conn) -> None:
    organization_columns = await _get_sqlite_columns(conn, "organizations")
    if "billing_plan" not in organization_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE organizations ADD COLUMN billing_plan VARCHAR(50) DEFAULT 'free'"
        )
    await conn.exec_driver_sql(
        "UPDATE organizations SET billing_plan = COALESCE(NULLIF(trim(billing_plan), ''), 'free')"
    )

    user_columns = await _get_sqlite_columns(conn, "users")
    if "username" not in user_columns:
        await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN username VARCHAR(100)")
    if "billing_plan" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN billing_plan VARCHAR(50) DEFAULT 'free'"
        )
    if "program" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN program VARCHAR(50) DEFAULT 'demo'"
        )
    if "signup_type" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN signup_type VARCHAR(50) DEFAULT 'cid_user'"
        )
    if "account_status" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN account_status VARCHAR(50) DEFAULT 'active'"
        )
    if "access_level" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN access_level VARCHAR(50) DEFAULT 'standard'"
        )
    if "cid_enabled" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN cid_enabled BOOLEAN DEFAULT 1"
        )
    if "onboarding_completed" not in user_columns:
        await conn.exec_driver_sql(
            "ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0"
        )
    if "company" not in user_columns:
        await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN company VARCHAR(255)")
    if "country" not in user_columns:
        await conn.exec_driver_sql("ALTER TABLE users ADD COLUMN country VARCHAR(100)")

    await conn.exec_driver_sql(
        "UPDATE users SET username = COALESCE(NULLIF(trim(username), ''), NULLIF(trim(full_name), ''), substr(email, 1, instr(email, '@') - 1), 'user')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET billing_plan = COALESCE(NULLIF(trim(billing_plan), ''), 'free')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET program = COALESCE(NULLIF(trim(program), ''), 'demo')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET signup_type = COALESCE(NULLIF(trim(signup_type), ''), 'cid_user')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET account_status = COALESCE(NULLIF(trim(account_status), ''), 'active')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET access_level = COALESCE(NULLIF(trim(access_level), ''), 'standard')"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET cid_enabled = COALESCE(cid_enabled, 1)"
    )
    await conn.exec_driver_sql(
        "UPDATE users SET onboarding_completed = COALESCE(onboarding_completed, 0)"
    )


async def _bootstrap_ingest_document_schema(conn) -> None:
    if await _has_table(conn, "ingest_events"):
        ingest_event_columns = await _get_sqlite_columns(conn, "ingest_events")
        if "document_asset_id" not in ingest_event_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE ingest_events ADD COLUMN document_asset_id VARCHAR(36)"
            )
        await conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_ingest_events_document_asset_id ON ingest_events(document_asset_id)"
        )


async def _bootstrap_funding_catalog_schema(conn) -> None:
    if await _has_table(conn, "funding_sources"):
        funding_source_columns = await _get_sqlite_columns(conn, "funding_sources")
        if "organization_id" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN organization_id VARCHAR(36) DEFAULT ''"
            )
        if "agency_name" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN agency_name VARCHAR(255)"
            )
        if "official_url" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN official_url VARCHAR(500)"
            )
        if "description" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN description TEXT"
            )
        if "region_scope" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN region_scope VARCHAR(32) DEFAULT 'spain'"
            )
        if "country_or_program" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN country_or_program VARCHAR(100)"
            )
        if "source_type" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN source_type VARCHAR(30) DEFAULT 'institutional'"
            )
        if "verification_status" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN verification_status VARCHAR(20) DEFAULT 'official'"
            )
        if "is_active" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN is_active BOOLEAN DEFAULT 1"
            )
        if "last_synced_at" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN last_synced_at DATETIME"
            )
        if "created_at" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
            )
        if "updated_at" not in funding_source_columns:
            await conn.exec_driver_sql(
                "ALTER TABLE funding_sources ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
            )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET organization_id = COALESCE(organization_id, '')"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET region_scope = COALESCE(region_scope, region, 'spain')"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET country_or_program = COALESCE(country_or_program, territory, name)"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET verification_status = COALESCE(NULLIF(trim(verification_status), ''), 'official')"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET is_active = COALESCE(is_active, 1)"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_sources SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP) WHERE updated_at IS NULL"
        )
        await conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_funding_source_code ON funding_sources(code)"
        )
        await conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_funding_source_org_id ON funding_sources(organization_id)"
        )

    if await _has_table(conn, "funding_calls"):
        funding_call_columns = await _get_sqlite_columns(conn, "funding_calls")
        for statement in (
            ("region_scope", "ALTER TABLE funding_calls ADD COLUMN region_scope VARCHAR(32) DEFAULT 'spain'"),
            ("country_or_program", "ALTER TABLE funding_calls ADD COLUMN country_or_program VARCHAR(100) DEFAULT 'Espana'"),
            ("agency_name", "ALTER TABLE funding_calls ADD COLUMN agency_name VARCHAR(255) DEFAULT ''"),
            ("open_date", "ALTER TABLE funding_calls ADD COLUMN open_date DATETIME"),
            ("close_date", "ALTER TABLE funding_calls ADD COLUMN close_date DATETIME"),
            ("max_award_per_project", "ALTER TABLE funding_calls ADD COLUMN max_award_per_project FLOAT"),
            ("total_budget_pool", "ALTER TABLE funding_calls ADD COLUMN total_budget_pool FLOAT"),
            ("currency", "ALTER TABLE funding_calls ADD COLUMN currency VARCHAR(3) DEFAULT 'EUR'"),
            ("eligibility_json", "ALTER TABLE funding_calls ADD COLUMN eligibility_json TEXT"),
            ("requirements_json", "ALTER TABLE funding_calls ADD COLUMN requirements_json TEXT"),
            ("collaboration_rules_json", "ALTER TABLE funding_calls ADD COLUMN collaboration_rules_json TEXT"),
            ("point_system_json", "ALTER TABLE funding_calls ADD COLUMN point_system_json TEXT"),
            ("eligible_formats_json", "ALTER TABLE funding_calls ADD COLUMN eligible_formats_json TEXT"),
            ("notes_json", "ALTER TABLE funding_calls ADD COLUMN notes_json TEXT"),
            ("created_at", "ALTER TABLE funding_calls ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "ALTER TABLE funding_calls ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ):
            if statement[0] not in funding_call_columns:
                await conn.exec_driver_sql(statement[1])
        await conn.exec_driver_sql(
            "UPDATE funding_calls SET region_scope = COALESCE(region_scope, region, 'spain')"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_calls SET country_or_program = COALESCE(country_or_program, territory, 'Espana')"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_calls SET close_date = COALESCE(close_date, deadline)"
        )
        await conn.exec_driver_sql(
            "UPDATE funding_calls SET currency = COALESCE(currency, 'EUR')"
        )
        await conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_funding_call_region_scope ON funding_calls(region_scope)"
        )

    if not await _has_table(conn, "funding_requirements"):
        await conn.exec_driver_sql(
            """
            CREATE TABLE funding_requirements (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                call_id VARCHAR(36) NOT NULL,
                category VARCHAR(50) NOT NULL DEFAULT 'general',
                requirement_text TEXT NOT NULL,
                is_mandatory BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                notes_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(call_id) REFERENCES funding_calls (id) ON DELETE CASCADE
            )
            """
        )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_funding_requirement_call_id ON funding_requirements(call_id)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_funding_requirement_category ON funding_requirements(category)"
    )


async def _bootstrap_project_funding_matcher_schema(conn) -> None:
    if not await _has_table(conn, "project_funding_matches"):
        await conn.exec_driver_sql(
            """
            CREATE TABLE project_funding_matches (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                organization_id VARCHAR(36) NOT NULL,
                funding_call_id VARCHAR(36) NOT NULL,
                match_score FLOAT DEFAULT 0.0,
                baseline_score FLOAT,
                rag_enriched_score FLOAT,
                fit_level VARCHAR(20),
                fit_summary TEXT,
                blocking_reasons TEXT,
                missing_documents TEXT,
                recommended_actions TEXT,
                evidence_chunks_json TEXT,
                rag_rationale TEXT,
                rag_missing_requirements TEXT,
                confidence_level VARCHAR(20),
                rag_confidence_level VARCHAR(20),
                matcher_mode VARCHAR(30) DEFAULT 'classic',
                evaluation_version VARCHAR(20),
                computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(funding_call_id) REFERENCES funding_calls (id)
            )
            """
        )
    else:
        matcher_columns = await _get_sqlite_columns(conn, "project_funding_matches")
        for statement in (
            ("organization_id", "ALTER TABLE project_funding_matches ADD COLUMN organization_id VARCHAR(36) DEFAULT ''"),
            ("baseline_score", "ALTER TABLE project_funding_matches ADD COLUMN baseline_score FLOAT"),
            ("rag_enriched_score", "ALTER TABLE project_funding_matches ADD COLUMN rag_enriched_score FLOAT"),
            ("fit_level", "ALTER TABLE project_funding_matches ADD COLUMN fit_level VARCHAR(20)"),
            ("evidence_chunks_json", "ALTER TABLE project_funding_matches ADD COLUMN evidence_chunks_json TEXT"),
            ("rag_rationale", "ALTER TABLE project_funding_matches ADD COLUMN rag_rationale TEXT"),
            ("rag_missing_requirements", "ALTER TABLE project_funding_matches ADD COLUMN rag_missing_requirements TEXT"),
            ("confidence_level", "ALTER TABLE project_funding_matches ADD COLUMN confidence_level VARCHAR(20)"),
            ("rag_confidence_level", "ALTER TABLE project_funding_matches ADD COLUMN rag_confidence_level VARCHAR(20)"),
            ("matcher_mode", "ALTER TABLE project_funding_matches ADD COLUMN matcher_mode VARCHAR(30) DEFAULT 'classic'"),
            ("evaluation_version", "ALTER TABLE project_funding_matches ADD COLUMN evaluation_version VARCHAR(20)"),
        ):
            if statement[0] not in matcher_columns:
                await conn.exec_driver_sql(statement[1])

    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_match_project_id ON project_funding_matches(project_id)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_match_project_org ON project_funding_matches(project_id, organization_id)"
    )
    await conn.exec_driver_sql(
        "CREATE INDEX IF NOT EXISTS ix_match_funding_call_id ON project_funding_matches(funding_call_id)"
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
                    metadata_json=json.dumps(
                        {
                            "source_id": opportunity.get("source_id"),
                            "eligibility": opportunity.get("eligibility", []),
                            "tags": opportunity.get("tags", []),
                        },
                        ensure_ascii=False,
                    ),
                )
            )

        await session.commit()


async def _seed_institutional_funding_catalog() -> None:
    from services.funding_ingestion_service import funding_ingestion_service

    async with AsyncSessionLocal() as session:
        await funding_ingestion_service.seed_catalog(session, force=False)


async def _verify_database_connection() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def _seed_funding_catalog_if_ready() -> None:
    async with engine.connect() as conn:
        if not await _has_table(conn, "funding_opportunities"):
            return

    await _seed_funding_catalog()


async def _seed_institutional_funding_catalog_if_ready() -> None:
    async with engine.connect() as conn:
        if not await _has_table(conn, "funding_sources"):
            return

    await _seed_institutional_funding_catalog()


async def init_db():
    """Initialize the configured database.

    Behavior by configuration:
    - PostgreSQL: Alembic is primary (user must run migrations manually)
    - SQLite with USE_ALEMBIC=true: Use Alembic, skip runtime bootstrap
    - SQLite default: Legacy runtime bootstrap (for dev convenience)
    """
    import os
    from models import JobHistory, Organization, Project, User
    from models.delivery import Deliverable
    from models.review import ApprovalDecision, Review, ReviewComment
    from models.narrative import Character, Scene, Sequence, scene_character_link
    from models.postproduction import AssemblyCut, AssemblyCutItem, Clip, Take
    from models.producer import (
        DemoRequestRecord,
        FundingOpportunity,
        LeadGenEvent,
        SavedOpportunity,
    )
    from models.visual import Shot, VisualAsset
    from models.storyboard import StoryboardShot
    from models.document import (
        DocumentChunk,
        DocumentAsset,
        DocumentClassification,
        DocumentExtraction,
        DocumentLink,
        ProjectDocument,
        DocumentStructuredData,
    )
    from models.integration import (
        ExternalDocumentSyncState,
        IntegrationConnection,
        IntegrationToken,
        ProjectExternalFolderLink,
    )
    from models.report import CameraReport, DirectorNote, ScriptNote, SoundReport
    from models.production import (
        BudgetLine,
        BudgetScenario,
        DepartmentLineItem,
        FundingCall,
        FundingRequirement,
        FundingSource,
        PrivateFundingSource,
        PrivateOpportunity,
        ProductionBreakdown,
        ProjectBudget,
        ProjectFundingMatch,
        ProjectFundingSource,
    )
    from models.storage import (
        IngestEvent,
        IngestScan,
        MediaAsset,
        StorageAuthorization,
        StorageSource,
        StorageWatchPath,
    )

    del (
        JobHistory,
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
        Take,
        AssemblyCutItem,
        DemoRequestRecord,
        FundingOpportunity,
        LeadGenEvent,
        SavedOpportunity,
        Shot,
        VisualAsset,
        StoryboardShot,
        DocumentChunk,
        DocumentAsset,
        DocumentClassification,
        DocumentExtraction,
        DocumentLink,
        ProjectDocument,
        DocumentStructuredData,
        ExternalDocumentSyncState,
        IntegrationConnection,
        IntegrationToken,
        ProjectExternalFolderLink,
        CameraReport,
        DirectorNote,
        ScriptNote,
        SoundReport,
        BudgetLine,
        BudgetScenario,
        DepartmentLineItem,
        FundingCall,
        FundingRequirement,
        FundingSource,
        PrivateFundingSource,
        PrivateOpportunity,
        ProductionBreakdown,
        ProjectBudget,
        ProjectFundingMatch,
        ProjectFundingSource,
        IngestEvent,
        IngestScan,
        MediaAsset,
        StorageAuthorization,
        StorageSource,
        StorageWatchPath,
    )

    use_alembic_env = os.getenv("USE_ALEMBIC", "").lower() in ("1", "true", "yes")
    use_alembic_config = DATABASE_SETTINGS.get("use_alembic", False)
    is_postgresql = not IS_SQLITE

    if is_postgresql or use_alembic_env or use_alembic_config:
        await _verify_database_connection()
        await _seed_funding_catalog_if_ready()
        await _seed_institutional_funding_catalog_if_ready()
        return

    if IS_SQLITE and RUNTIME_SCHEMA_SYNC:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

            if SQLITE_LEGACY_BOOTSTRAP:
                await _bootstrap_sqlite_schema(conn)
                await _bootstrap_funding_catalog_schema(conn)
                await _bootstrap_project_funding_matcher_schema(conn)

        await _seed_funding_catalog()
        await _seed_institutional_funding_catalog()
        return

    await _verify_database_connection()
    await _seed_funding_catalog_if_ready()
    await _seed_institutional_funding_catalog_if_ready()


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
