from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.storyboard import StoryboardShot
from models.production import ProductionBreakdown
from services.logging_service import logger
from services.rag_embedding_service import rag_embedding_service
from services.qdrant_memory_service import qdrant_memory_service


SOURCE_TYPE_SCRIPT = "script_text"
SOURCE_TYPE_STORYBOARD = "storyboard_shot"
SOURCE_TYPE_BREAKDOWN = "production_breakdown"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if not text or not text.strip():
        return []
    text = " ".join(text.split())
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            newline = text.rfind("\n\n", start, end)
            if newline > start + chunk_size * 0.5:
                end = newline + 2
            else:
                space = text.rfind(" ", start, end)
                if space > start + chunk_size * 0.5:
                    end = space
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks if chunks else [text]


async def _index_script_text(db: AsyncSession, project: Project) -> list[dict[str, Any]]:
    if not project.script_text or not project.script_text.strip():
        return []

    chunks = _chunk_text(project.script_text)
    if not chunks:
        return []

    embeddings = await rag_embedding_service.embed_batch(chunks)
    if len(embeddings) != len(chunks):
        logger.error("Script embedding count mismatch: chunks=%d embeddings=%d", len(chunks), len(embeddings))
        return []

    title = f"Script - {project.name}"
    points = await qdrant_memory_service.upsert_memory(
        organization_id=project.organization_id,
        project_id=project.id,
        source_type=SOURCE_TYPE_SCRIPT,
        source_id=project.id,
        source_table="projects",
        title=title,
        chunks=chunks,
        embedding_vectors=embeddings,
        tags=["script"],
    )

    return [{
        "source_type": SOURCE_TYPE_SCRIPT,
        "source_id": project.id,
        "chunks": len(chunks),
        "points_upserted": points,
    }]


async def _index_storyboard_shots(db: AsyncSession, project: Project) -> list[dict[str, Any]]:
    result = await db.execute(
        select(StoryboardShot).where(
            StoryboardShot.project_id == project.id,
            StoryboardShot.organization_id == project.organization_id,
            StoryboardShot.is_active == True,
        ).order_by(StoryboardShot.sequence_order.asc())
    )
    shots = list(result.scalars().all())
    if not shots:
        return []

    results: list[dict[str, Any]] = []
    batch_texts: list[str] = []
    batch_shot_ids: list[str] = []
    batch_titles: list[str] = []

    for shot in shots:
        narrative = (shot.narrative_text or "").strip()
        heading = (shot.scene_heading or "").strip()
        if not narrative:
            continue
        text = f"{heading}: {narrative}" if heading else narrative
        batch_texts.append(text)
        batch_shot_ids.append(shot.id)
        batch_titles.append(f"Shot {shot.shot_number or ''} - {heading or shot.id}")

    if not batch_texts:
        return []

    embeddings = await rag_embedding_service.embed_batch(batch_texts)
    if len(embeddings) != len(batch_texts):
        logger.error("Storyboard embedding count mismatch")
        return []

    for i, (shot_text, shot_id, title) in enumerate(zip(batch_texts, batch_shot_ids, batch_titles)):
        vector = embeddings[i]
        point_id = _deterministic_shot_id(project.organization_id, project.id, shot_id)
        import uuid as uuid_lib
        namespace = uuid_lib.uuid5(
            uuid_lib.NAMESPACE_DNS,
            f"cid-memory/1/{project.organization_id}/{project.id}/storyboard_shots/{shot_id}/0",
        )
        point_id = str(namespace)
        from services.qdrant_memory_service import _build_payload
        import os
        settings = __import__("core.config", fromlist=["get_settings"]).get_settings()
        embedding_model = settings.embedding_model
        payload = _build_payload(
            organization_id=project.organization_id,
            project_id=project.id,
            source_type=SOURCE_TYPE_STORYBOARD,
            source_id=shot_id,
            source_table="storyboard_shots",
            title=title,
            text=shot_text,
            chunk_index=0,
            chunk_count=1,
            tags=["storyboard"],
            embedding_model=embedding_model,
        )
        point = {"id": point_id, "vector": vector, "payload": payload}
        from services.qdrant_service import qdrant_service
        ok = await qdrant_service.upsert_points(collection="cid_memory", points=[point])

        results.append({
            "source_type": SOURCE_TYPE_STORYBOARD,
            "source_id": shot_id,
            "chunks": 1,
            "points_upserted": 1 if ok else 0,
        })

    return results


async def _index_production_breakdowns(db: AsyncSession, project: Project) -> list[dict[str, Any]]:
    result = await db.execute(
        select(ProductionBreakdown).where(
            ProductionBreakdown.project_id == project.id,
            ProductionBreakdown.organization_id == project.organization_id,
        )
    )
    breakdowns = list(result.scalars().all())
    if not breakdowns:
        return []

    results: list[dict[str, Any]] = []
    for bd in breakdowns:
        text = (bd.script_text or "").strip() or (bd.breakdown_json or "")[:2000]
        if not text:
            continue
        chunks = _chunk_text(text)
        if not chunks:
            continue
        embeddings = await rag_embedding_service.embed_batch(chunks)
        if len(embeddings) != len(chunks):
            continue
        title = f"Breakdown - {bd.id}"
        points = await qdrant_memory_service.upsert_memory(
            organization_id=project.organization_id,
            project_id=project.id,
            source_type=SOURCE_TYPE_BREAKDOWN,
            source_id=bd.id,
            source_table="production_breakdowns",
            title=title,
            chunks=chunks,
            embedding_vectors=embeddings,
            tags=["breakdown"],
        )
        results.append({
            "source_type": SOURCE_TYPE_BREAKDOWN,
            "source_id": bd.id,
            "chunks": len(chunks),
            "points_upserted": points,
        })

    return results


async def index_project(
    db: AsyncSession,
    *,
    organization_id: str,
    project_id: str,
) -> dict[str, Any]:
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        return {"error": "Project not found", "project_id": project_id}

    sources: list[dict[str, Any]] = []
    errors: list[str] = []
    total_chunks = 0
    total_points = 0

    try:
        script_results = await _index_script_text(db, project)
        sources.extend(script_results)
        for s in script_results:
            total_chunks += s["chunks"]
            total_points += s["points_upserted"]
    except Exception as exc:
        logger.exception("Script text indexing failed")
        errors.append(f"script_text: {exc}")

    try:
        shot_results = await _index_storyboard_shots(db, project)
        sources.extend(shot_results)
        for s in shot_results:
            total_chunks += s["chunks"]
            total_points += s["points_upserted"]
    except Exception as exc:
        logger.exception("Storyboard indexing failed")
        errors.append(f"storyboard_shots: {exc}")

    try:
        breakdown_results = await _index_production_breakdowns(db, project)
        sources.extend(breakdown_results)
        for s in breakdown_results:
            total_chunks += s["chunks"]
            total_points += s["points_upserted"]
    except Exception as exc:
        logger.exception("Production breakdown indexing failed")
        errors.append(f"production_breakdowns: {exc}")

    return {
        "project_id": project_id,
        "organization_id": organization_id,
        "project_name": project.name,
        "sources_indexed": sources,
        "total_chunks": total_chunks,
        "total_points_upserted": total_points,
        "errors": errors if errors else None,
    }


def _deterministic_shot_id(organization_id: str, project_id: str, shot_id: str) -> str:
    import uuid as uuid_lib
    namespace = uuid_lib.uuid5(
        uuid_lib.NAMESPACE_DNS,
        f"cid-memory/1/{organization_id}/{project_id}/storyboard_shots/{shot_id}/0",
    )
    return str(namespace)
