from __future__ import annotations

import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.qdrant_memory_service import (
    _build_point_id,
    _build_payload,
    _project_filter,
    qdrant_memory_service,
)
from services.rag_embedding_service import rag_embedding_service
from services.cid_memory_ingestion_service import _chunk_text, SOURCE_TYPE_SCRIPT


def test_deterministic_uuid() -> None:
    oid = "org-1"
    pid = "proj-1"
    sid = "src-1"
    id1 = _build_point_id(oid, pid, "projects", sid, 0)
    id2 = _build_point_id(oid, pid, "projects", sid, 0)
    id3 = _build_point_id(oid, pid, "projects", sid, 1)
    id4 = _build_point_id(oid, pid, "projects", "src-2", 0)
    assert id1 == id2, "same inputs must produce same UUID"
    assert id1 != id3, "different chunk_index must produce different UUID"
    assert id1 != id4, "different source_id must produce different UUID"
    assert isinstance(uuid.UUID(id1), uuid.UUID)


def test_deterministic_uuid_version() -> None:
    oid = "org-1"
    pid = "proj-1"
    sid = "src-1"
    pt = "projects"
    point_id_1 = _build_point_id(oid, pid, pt, sid, 0)
    point_id_2 = _build_point_id(oid, pid, pt, sid, 0)
    assert point_id_1 == point_id_2
    parsed = uuid.UUID(point_id_1)
    assert parsed.version == 5


def test_build_payload_has_all_fields() -> None:
    payload = _build_payload(
        organization_id="org-1",
        project_id="proj-1",
        source_type="script_text",
        source_id="proj-1",
        source_table="projects",
        title="Test Script",
        text="Some script text here",
        chunk_index=0,
        chunk_count=3,
        language="es",
        tags=["script", "test"],
        embedding_model="nomic-embed-text:v1.5",
    )
    assert payload["organization_id"] == "org-1"
    assert payload["project_id"] == "proj-1"
    assert payload["source_type"] == "script_text"
    assert payload["source_table"] == "projects"
    assert payload["title"] == "Test Script"
    assert payload["text"] == "Some script text here"
    assert payload["chunk_index"] == 0
    assert payload["chunk_count"] == 3
    assert payload["language"] == "es"
    assert payload["tags"] == ["script", "test"]
    assert payload["version"] == "1"
    assert payload["visibility"] == "organization"
    assert payload["embedding_model"] == "nomic-embed-text:v1.5"
    assert payload["metadata"] == {}
    assert "created_at" in payload
    assert "updated_at" in payload


def test_build_payload_defaults() -> None:
    payload = _build_payload(
        organization_id="o1",
        project_id="p1",
        source_type="storyboard_shot",
        source_id="shot-1",
        source_table="storyboard_shots",
        title="Shot 1",
        text="narrative",
        chunk_index=0,
        chunk_count=1,
        embedding_model="nomic-embed-text:v1.5",
    )
    assert payload["language"] == "es"
    assert payload["tags"] == []
    assert payload["metadata"] == {}


def test_project_filter_structure() -> None:
    filt = _project_filter("org-1", "proj-1")
    assert filt == {
        "must": [
            {"key": "organization_id", "match": {"value": "org-1"}},
            {"key": "project_id", "match": {"value": "proj-1"}},
        ]
    }


def test_chunk_text_empty() -> None:
    assert _chunk_text("") == []
    assert _chunk_text("   ") == []
    assert _chunk_text(None) == []  # type: ignore[arg-type]


def test_chunk_text_short() -> None:
    text = "This is a short text that fits in one chunk."
    chunks = _chunk_text(text, chunk_size=500)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_splits_long() -> None:
    text = "word " * 500
    chunks = _chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 220
        assert len(chunk) > 0


def test_chunk_text_respects_double_newline() -> None:
    para1 = "This is paragraph one with enough text to be a block.\n\n"
    para2 = "This is paragraph two with more content to fill it.\n\n"
    para3 = "This is paragraph three."
    text = para1 + para2 + para3
    chunks = _chunk_text(text, chunk_size=70, overlap=10)
    assert len(chunks) >= 1


def test_chunk_text_preserves_words() -> None:
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    chunks = _chunk_text(text, chunk_size=30, overlap=5)
    for chunk in chunks:
        words = chunk.split()
        assert all(len(w) > 0 for w in words)


@pytest.mark.asyncio
async def test_rag_embedding_service_init() -> None:
    assert rag_embedding_service.provider == "ollama"
    assert rag_embedding_service.model == "nomic-embed-text:v1.5"
    assert rag_embedding_service.vector_size == 768


@pytest.mark.asyncio
async def test_rag_embedding_embed_empty_text() -> None:
    vectors = await rag_embedding_service.embed_batch([])
    assert vectors == []


@pytest.mark.asyncio
async def test_rag_embedding_embed_short_text(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(*args, **kwargs):
        class Response:
            status_code = 200

            @staticmethod
            def json():
                return {"embeddings": [[0.1] * 768]}

            @staticmethod
            def raise_for_status():
                pass

            text = "ok"

        return Response()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        post = staticmethod(fake_post)

    monkeypatch.setattr("services.rag_embedding_service.httpx.AsyncClient", lambda timeout: FakeClient())
    vector = await rag_embedding_service.embed("hola mundo")
    assert len(vector) == 768


@pytest.mark.asyncio
async def test_rag_embedding_embed_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    count = 0

    async def fake_post(*args, **kwargs):
        nonlocal count
        count += 1

        class Response:
            status_code = 200

            @staticmethod
            def json():
                return {"embeddings": [[float(count)] * 768]}

            @staticmethod
            def raise_for_status():
                pass

            text = "ok"

        return Response()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        post = staticmethod(fake_post)

    monkeypatch.setattr("services.rag_embedding_service.httpx.AsyncClient", lambda timeout: FakeClient())
    vectors = await rag_embedding_service.embed_batch(["a", "b"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 768
    assert len(vectors[1]) == 768


@pytest.mark.asyncio
async def test_qdrant_memory_upsert_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    result = await qdrant_memory_service.upsert_memory(
        organization_id="o1",
        project_id="p1",
        source_type=SOURCE_TYPE_SCRIPT,
        source_id="s1",
        source_table="projects",
        title="Test",
        chunks=[],
        embedding_vectors=[],
    )
    assert result == 0

    result = await qdrant_memory_service.upsert_memory(
        organization_id="o1",
        project_id="p1",
        source_type=SOURCE_TYPE_SCRIPT,
        source_id="s1",
        source_table="projects",
        title="Test",
        chunks=["text"],
        embedding_vectors=[],
    )
    assert result == 0


@pytest.mark.asyncio
async def test_qdrant_memory_upsert_count_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="same length"):
        await qdrant_memory_service.upsert_memory(
            organization_id="o1",
            project_id="p1",
            source_type=SOURCE_TYPE_SCRIPT,
            source_id="s1",
            source_table="projects",
            title="Test",
            chunks=["a", "b"],
            embedding_vectors=[[0.1] * 768],
        )


@pytest.mark.asyncio
async def test_qdrant_memory_upsert_calls_qdrant(monkeypatch: pytest.MonkeyPatch) -> None:
    upserted_points: list[dict[str, Any]] = []

    async def fake_upsert(*, collection: str, points: list[dict[str, Any]]) -> bool:
        nonlocal upserted_points
        upserted_points = points
        return True

    monkeypatch.setattr("services.qdrant_memory_service.qdrant_service.upsert_points", fake_upsert)

    result = await qdrant_memory_service.upsert_memory(
        organization_id="o1",
        project_id="p1",
        source_type=SOURCE_TYPE_SCRIPT,
        source_id="s1",
        source_table="projects",
        title="Test Script",
        chunks=["chunk one", "chunk two"],
        embedding_vectors=[[0.1] * 768, [0.2] * 768],
        tags=["script"],
    )
    assert result == 2
    assert len(upserted_points) == 2
    assert upserted_points[0]["payload"]["chunk_index"] == 0
    assert upserted_points[1]["payload"]["chunk_index"] == 1
    assert upserted_points[0]["payload"]["text"] == "chunk one"
    assert upserted_points[1]["payload"]["text"] == "chunk two"


@pytest.mark.asyncio
async def test_qdrant_memory_search(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search(*, collection: str, query_vector: list[float], limit: int, filter_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
        return [
            {"id": "abc", "score": 0.95, "payload": {"source_type": "script_text", "source_id": "p1", "source_table": "projects", "title": "T", "text": "some text", "chunk_index": 0, "chunk_count": 1, "tags": []}},
        ]

    monkeypatch.setattr("services.qdrant_memory_service.qdrant_service.semantic_search", fake_search)
    results = await qdrant_memory_service.search(
        organization_id="o1",
        project_id="p1",
        query_vector=[0.1] * 768,
        limit=5,
    )
    assert len(results) == 1
    assert results[0]["id"] == "abc"
    assert results[0]["score"] == 0.95


@pytest.mark.asyncio
async def test_qdrant_memory_search_no_results(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search(*, collection: str, query_vector: list[float], limit: int, filter_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
        return []

    monkeypatch.setattr("services.qdrant_memory_service.qdrant_service.semantic_search", fake_search)
    results = await qdrant_memory_service.search(
        organization_id="o1",
        project_id="p1",
        query_vector=[0.1] * 768,
        limit=5,
    )
    assert results == []
