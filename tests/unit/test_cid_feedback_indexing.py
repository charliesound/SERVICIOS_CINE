from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.client_feedback import CIDClientFeedback, CIDFeedbackMemoryEntry
from services.cid_feedback_indexing_service import (
    SOURCE_TYPE_FEEDBACK,
    SOURCE_TABLE_FEEDBACK,
    NON_INDEXABLE_TYPES,
    build_feedback_text,
    is_feedback_indexable,
    already_indexed,
    compute_feedback_point_id,
    cid_feedback_indexing_service,
)


def _make_feedback(**overrides: Any) -> CIDClientFeedback:
    data: dict[str, Any] = dict(
        id="fb-test-1",
        organization_id="org-1",
        project_id="proj-1",
        user_id="user-1",
        feedback_type="answer_helpful",
        feedback_scope="project_feedback",
        original_question="What is a dolly shot?",
        original_answer="A dolly shot is when the camera moves.",
        corrected_answer="A dolly shot is a tracking shot where the camera is mounted on a wheeled platform (dolly) and moves along tracks.",
        feedback_text=None,
        source_ids=None,
        source_types=None,
        approved_for_memory=True,
        approved_by_user_id="user-admin",
        confidence=0.95,
        status="approved",
        model_used="llama3",
        prompt_version="v1",
        answer_version="v1",
        metadata_json=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    data.update(overrides)
    return CIDClientFeedback(**data)


class TestBuildFeedbackText:
    def test_with_corrected_answer(self) -> None:
        fb = _make_feedback()
        text = build_feedback_text(fb)
        assert "Pregunta: What is a dolly shot?" in text
        assert "Respuesta corregida:" in text

    def test_with_feedback_text_fallback(self) -> None:
        fb = _make_feedback(corrected_answer=None, feedback_text="The answer was too vague.")
        text = build_feedback_text(fb)
        assert "Pregunta: What is a dolly shot?" in text
        assert "The answer was too vague." in text
        assert "Respuesta corregida" not in text

    def test_with_original_answer_fallback(self) -> None:
        fb = _make_feedback(corrected_answer=None, feedback_text=None)
        text = build_feedback_text(fb)
        assert "Respuesta original:" in text
        assert "camera moves" in text

    def test_with_no_text_builds_empty(self) -> None:
        fb = _make_feedback(
            original_question=None, original_answer=None,
            corrected_answer=None, feedback_text=None,
        )
        assert build_feedback_text(fb) == ""


class TestIsFeedbackIndexable:
    def test_approved_with_memory_flag(self) -> None:
        assert is_feedback_indexable(_make_feedback()) is True

    def test_rejected_not_indexable(self) -> None:
        assert is_feedback_indexable(_make_feedback(status="rejected")) is False

    def test_pending_not_indexable(self) -> None:
        assert is_feedback_indexable(_make_feedback(status="pending")) is False

    def test_archived_not_indexable(self) -> None:
        assert is_feedback_indexable(_make_feedback(status="archived")) is False

    def test_not_approved_for_memory(self) -> None:
        assert is_feedback_indexable(_make_feedback(approved_for_memory=False)) is False

    def test_source_blacklist_not_indexable(self) -> None:
        assert is_feedback_indexable(_make_feedback(feedback_type="source_blacklist")) is False

    def test_no_text_content_not_indexable(self) -> None:
        fb = _make_feedback(
            original_question=None, original_answer=None,
            corrected_answer=None, feedback_text=None,
        )
        assert is_feedback_indexable(fb) is False

    def test_all_non_indexable_types(self) -> None:
        for t in NON_INDEXABLE_TYPES:
            assert is_feedback_indexable(_make_feedback(feedback_type=t)) is False


@pytest.mark.asyncio
async def test_already_indexed_no_entry() -> None:
    class FakeResult:
        scalar_one_or_none = lambda self: None

    class FakeSession:
        async def execute(self, stmt):
            return FakeResult()

    assert await already_indexed(FakeSession(), "fb-1") is False


@pytest.mark.asyncio
async def test_already_indexed_has_entry() -> None:
    entry = CIDFeedbackMemoryEntry(
        id="entry-1",
        feedback_id="fb-1",
        organization_id="org-1",
        project_id="proj-1",
        source_type=SOURCE_TYPE_FEEDBACK,
        source_id="fb-1",
        qdrant_point_id="point-abc",
        indexed_at=datetime.utcnow(),
    )

    class FakeResult:
        scalar_one_or_none = lambda self: entry

    class FakeSession:
        async def execute(self, stmt):
            return FakeResult()

    assert await already_indexed(FakeSession(), "fb-1") is True


class TestComputeFeedbackPointId:
    def test_deterministic(self) -> None:
        fb = _make_feedback(id="fb-abc")
        assert compute_feedback_point_id(fb) == compute_feedback_point_id(fb)

    def test_version5_uuid(self) -> None:
        fb = _make_feedback(id="fb-uuid-test")
        parsed = uuid.UUID(compute_feedback_point_id(fb))
        assert parsed.version == 5

    def test_differs_by_feedback_id(self) -> None:
        fb1 = _make_feedback(id="fb-a")
        fb2 = _make_feedback(id="fb-b")
        assert compute_feedback_point_id(fb1) != compute_feedback_point_id(fb2)


class TestIndexSingleFeedback:

    @pytest.mark.asyncio
    async def test_not_indexable_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback(status="pending")
        result = await cid_feedback_indexing_service.index_single_feedback(None, fb)
        assert result["indexed"] is False
        assert result["reason"] == "feedback not indexable"

    @pytest.mark.asyncio
    async def test_already_indexed_skips(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback()

        async def fake_already(*_a, **_kw):
            return True

        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.already_indexed",
            fake_already,
        )
        result = await cid_feedback_indexing_service.index_single_feedback(None, fb)
        assert result["indexed"] is False
        assert result["reason"] == "already indexed"

    @pytest.mark.asyncio
    async def test_successful_index(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback(id="fb-success")

        async def fake_already(*_a, **_kw):
            return False

        async def fake_embed(_text):
            return [0.1] * 768

        async def fake_upsert(**kwargs):
            return 1

        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.already_indexed",
            fake_already,
        )
        monkeypatch.setattr(
            "services.rag_embedding_service.rag_embedding_service.embed",
            fake_embed,
        )
        monkeypatch.setattr(
            "services.qdrant_memory_service.qdrant_memory_service.upsert_memory",
            fake_upsert,
        )

        committed = False

        class FakeDB:
            def add(self, obj):
                self._added = obj

            async def commit(self):
                nonlocal committed
                committed = True

        result = await cid_feedback_indexing_service.index_single_feedback(
            FakeDB(), fb,
        )
        assert result["indexed"] is True
        assert isinstance(result["point_id"], str)
        assert isinstance(result["entry_id"], str)
        assert committed is True


class TestIndexApprovedFeedbacks:

    @pytest.mark.asyncio
    async def test_batch_indexes_only_indexable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb1 = _make_feedback(id="fb-batch-ok")
        fb2 = _make_feedback(id="fb-batch-pending", status="pending")

        class _FakeScalars:
            def all(self):
                return [fb1, fb2]

        class _FakeResult:
            def scalars(self):
                return _FakeScalars()

        class FakeSession:
            async def execute(self, stmt):
                return _FakeResult()

        async def fake_index_single(db, feedback):
            if feedback.id == "fb-batch-ok":
                return {"indexed": True, "point_id": "pt-ok", "entry_id": "e-ok"}
            return {"indexed": False, "reason": "feedback not indexable"}

        monkeypatch.setattr(
            cid_feedback_indexing_service,
            "index_single_feedback",
            fake_index_single,
        )
        result = await cid_feedback_indexing_service.index_approved_feedbacks(
            FakeSession(), "org-1", "proj-1",
        )
        assert result["organization_id"] == "org-1"
        assert result["project_id"] == "proj-1"
        assert result["total_candidates"] == 2
        assert result["indexed_count"] == 1
        assert len(result["results"]) == 2


class TestConstants:
    def test_source_type(self) -> None:
        assert SOURCE_TYPE_FEEDBACK == "client_feedback"

    def test_source_table(self) -> None:
        assert SOURCE_TABLE_FEEDBACK == "cid_client_feedback"

    def test_non_indexable_contains_blacklist(self) -> None:
        assert "source_blacklist" in NON_INDEXABLE_TYPES
