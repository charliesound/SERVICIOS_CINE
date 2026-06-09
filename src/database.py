from typing import AsyncGenerator

import json

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import get_database_settings
from services.producer_catalog import DEMO_OPPORTUNITIES, parse_catalog_deadline

DATABASE_SETTINGS = get_database_settings()
DATABASE_URL = str(DATABASE_SETTINGS["url"])

def is_postgresql_url(database_url: str) -> bool:
    return database_url.startswith("postgresql") or database_url.startswith("postgres")

def validate_database_url(database_url: str) -> str:
    normalized = database_url.strip()
    if not normalized:
        raise ValueError("DATABASE_URL must not be empty")

    if not normalized.startswith("postgresql+asyncpg://"):
        raise ValueError(
            "CID requires postgresql+asyncpg:// DATABASE_URL."
        )

    return normalized

DATABASE_URL = validate_database_url(DATABASE_URL)

engine_kwargs = {
    "echo": False,
    "future": True,
    "pool_pre_ping": True,
    "connect_args": {"server_settings": {"search_path": "cid,public"}},
}

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()

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

    PostgreSQL is the only supported backend.
    Schema management is done via Alembic migrations.
    """
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
