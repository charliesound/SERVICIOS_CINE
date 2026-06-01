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
    MEMORY_TYPE_FEEDBACK,
    MEMORY_TYPE_COMMON_QUESTION,
    build_feedback_text,
    is_feedback_indexable,
    already_indexed,
    compute_feedback_point_id,
    compute_canonical_hash,
    normalize_canonical_text,
    determine_memory_type,
    build_variant_questions,
    find_existing_by_hash,
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


# ── Normalization ────────────────────────────────────────────────────────────

class TestNormalizeCanonicalText:
    def test_lowercase(self) -> None:
        assert normalize_canonical_text("HELLO World") == "hello world"

    def test_trim(self) -> None:
        assert normalize_canonical_text("  hello  ") == "hello"

    def test_collapse_spaces(self) -> None:
        assert normalize_canonical_text("hello   world") == "hello world"

    def test_remove_punctuation(self) -> None:
        result = normalize_canonical_text("\u00bfQu\u00e9 es un dolly? \u00a1Explica!")
        assert "?" not in result
        assert "!" not in result
        assert "qu\u00e9 es un dolly explica" in result

    def test_empty(self) -> None:
        assert normalize_canonical_text("") == ""
        assert normalize_canonical_text("   ") == ""

    def test_preserves_spanish_accents(self) -> None:
        result = normalize_canonical_text("acci\u00f3n y efectos")
        assert "acci\u00f3n" in result


# ── Canonical Hash ───────────────────────────────────────────────────────────

class TestComputeCanonicalHash:
    def test_stable_hash(self) -> None:
        h1 = compute_canonical_hash("What is a dolly shot?")
        h2 = compute_canonical_hash("What is a dolly shot?")
        assert h1 == h2

    def test_case_insensitive(self) -> None:
        h1 = compute_canonical_hash("What is a Dolly Shot")
        h2 = compute_canonical_hash("what is a dolly shot")
        assert h1 == h2

    def test_whitespace_insensitive(self) -> None:
        h1 = compute_canonical_hash("dolly  shot")
        h2 = compute_canonical_hash("dolly shot")
        assert h1 == h2

    def test_punctuation_insensitive(self) -> None:
        h1 = compute_canonical_hash("\u00bfQue es un dolly? \u00a1Explica!")
        h2 = compute_canonical_hash("Que es un dolly Explica")
        assert h1 == h2

    def test_different_text_different_hash(self) -> None:
        h1 = compute_canonical_hash("What is a dolly shot")
        h2 = compute_canonical_hash("What is a crane shot")
        assert h1 != h2

    def test_empty_text(self) -> None:
        assert compute_canonical_hash("") == compute_canonical_hash("")


# ── Memory Type ──────────────────────────────────────────────────────────────

class TestDetermineMemoryType:
    def test_with_corrected_answer_is_client_feedback(self) -> None:
        fb = _make_feedback()
        assert determine_memory_type(fb) == MEMORY_TYPE_FEEDBACK

    def test_with_feedback_text_is_client_feedback(self) -> None:
        fb = _make_feedback(corrected_answer=None, feedback_text="too vague")
        assert determine_memory_type(fb) == MEMORY_TYPE_FEEDBACK

    def test_only_question_is_common_question(self) -> None:
        fb = _make_feedback(
            corrected_answer=None, feedback_text=None,
            original_answer="Good answer.",
        )
        assert determine_memory_type(fb) == MEMORY_TYPE_COMMON_QUESTION


# ── Variant Questions ────────────────────────────────────────────────────────

class TestBuildVariantQuestions:
    def test_with_question(self) -> None:
        fb = _make_feedback(original_question="What is a dolly?")
        assert build_variant_questions(fb) == ["What is a dolly?"]

    def test_without_question(self) -> None:
        fb = _make_feedback(original_question=None)
        assert build_variant_questions(fb) == []


# ── BuildFeedbackText ────────────────────────────────────────────────────────

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


# ── IsFeedbackIndexable ──────────────────────────────────────────────────────

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


# ── AlreadyIndexed ───────────────────────────────────────────────────────────

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


# ── ComputeFeedbackPointId ───────────────────────────────────────────────────

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


# ── FindExistingByHash ───────────────────────────────────────────────────────

class TestFindExistingByHash:
    @pytest.mark.asyncio
    async def test_no_match_returns_none(self) -> None:
        class FakeScalars:
            def all(self):
                return []

        class FakeResult:
            def scalars(self):
                return FakeScalars()

        class FakeSession:
            async def execute(self, stmt):
                return FakeResult()

        result = await find_existing_by_hash(FakeSession(), "abc123", "org-1", "proj-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_match_returns_entry(self) -> None:
        entry = CIDFeedbackMemoryEntry(
            id="entry-match",
            feedback_id="fb-orig",
            organization_id="org-1",
            project_id="proj-1",
            source_type=SOURCE_TYPE_FEEDBACK,
            source_id="fb-orig",
            qdrant_point_id="point-abc",
            metadata_json={"canonical_hash": "abc123"},
            indexed_at=datetime.utcnow(),
        )

        class FakeScalars:
            def all(self):
                return [entry]

        class FakeResult:
            def scalars(self):
                return FakeScalars()

        class FakeSession:
            async def execute(self, stmt):
                return FakeResult()

        result = await find_existing_by_hash(FakeSession(), "abc123", "org-1", "proj-1")
        assert result is not None
        assert result.id == "entry-match"

    @pytest.mark.asyncio
    async def test_org_isolation(self) -> None:
        class FakeScalars:
            def all(self):
                return []

        class FakeResult:
            def scalars(self):
                return FakeScalars()

        class FakeSession:
            async def execute(self, stmt):
                return FakeResult()

        result = await find_existing_by_hash(FakeSession(), "abc123", "org-1", "proj-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_project_isolation(self) -> None:
        class FakeScalars:
            def all(self):
                return []

        class FakeResult:
            def scalars(self):
                return FakeScalars()

        class FakeSession:
            async def execute(self, stmt):
                return FakeResult()

        result = await find_existing_by_hash(FakeSession(), "abc123", "org-1", "proj-1")
        assert result is None


# ── IndexSingleFeedback ──────────────────────────────────────────────────────

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
    async def test_dedup_exact_skips_upsert(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback(id="fb-dedup-new")

        existing_entry = CIDFeedbackMemoryEntry(
            id="entry-existing",
            feedback_id="fb-orig",
            organization_id="org-1",
            project_id="proj-1",
            source_type=SOURCE_TYPE_FEEDBACK,
            source_id="fb-orig",
            qdrant_point_id="point-existing",
            metadata_json={"canonical_hash": compute_canonical_hash(build_feedback_text(_make_feedback()))},
            indexed_at=datetime.utcnow(),
        )

        async def fake_already(*_a, **_kw):
            return False

        async def fake_find_hash(*_a, **_kw):
            return existing_entry

        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.already_indexed",
            fake_already,
        )
        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.find_existing_by_hash",
            fake_find_hash,
        )

        added = []

        class FakeDB:
            def add(self, obj):
                added.append(obj)

            async def commit(self):
                pass

        result = await cid_feedback_indexing_service.index_single_feedback(FakeDB(), fb)
        assert result["indexed"] is True
        assert result["dedup"] is True
        assert result["point_id"] == "point-existing"
        assert len(added) == 1
        meta = added[0].metadata_json or {}
        assert meta.get("is_duplicate") is True
        assert meta.get("original_entry_id") == "entry-existing"
        assert meta.get("canonical_hash") is not None

    @pytest.mark.asyncio
    async def test_dedup_isolates_by_org(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback(id="fb-other-org", organization_id="org-2")

        async def fake_already(*_a, **_kw):
            return False

        async def fake_find_hash(*_a, **_kw):
            return None

        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.already_indexed",
            fake_already,
        )
        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.find_existing_by_hash",
            fake_find_hash,
        )

        async def fake_embed(_text):
            return [0.1] * 768

        async def fake_upsert(**kw):
            return 1

        monkeypatch.setattr(
            "services.rag_embedding_service.rag_embedding_service.embed",
            fake_embed,
        )
        monkeypatch.setattr(
            "services.qdrant_memory_service.qdrant_memory_service.upsert_memory",
            fake_upsert,
        )

        class FakeDB:
            def add(self, obj):
                pass

            async def commit(self):
                pass

        result = await cid_feedback_indexing_service.index_single_feedback(FakeDB(), fb)
        assert result["indexed"] is True
        assert result.get("dedup") is False

    @pytest.mark.asyncio
    async def test_successful_index_includes_new_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fb = _make_feedback(id="fb-success", original_question="What is a dolly?")

        async def fake_already(*_a, **_kw):
            return False

        async def fake_find_hash(*_a, **_kw):
            return None

        async def fake_embed(_text):
            return [0.1] * 768

        captured_metadata = {}

        async def fake_upsert(**kw):
            nonlocal captured_metadata
            captured_metadata = kw.get("metadata", {})
            return 1

        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.already_indexed",
            fake_already,
        )
        monkeypatch.setattr(
            "services.cid_feedback_indexing_service.find_existing_by_hash",
            fake_find_hash,
        )
        monkeypatch.setattr(
            "services.rag_embedding_service.rag_embedding_service.embed",
            fake_embed,
        )
        monkeypatch.setattr(
            "services.qdrant_memory_service.qdrant_memory_service.upsert_memory",
            fake_upsert,
        )

        class FakeDB:
            def add(self, obj):
                self._added = obj

            async def commit(self):
                pass

        result = await cid_feedback_indexing_service.index_single_feedback(FakeDB(), fb)
        assert result["indexed"] is True
        assert result.get("dedup") is False

        assert "canonical_hash" in captured_metadata
        assert captured_metadata["memory_type"] == MEMORY_TYPE_FEEDBACK
        assert captured_metadata["occurrence_count"] == 1
        assert captured_metadata["variant_questions"] == ["What is a dolly?"]

        added = getattr(FakeDB, "_added", None)
        if added:
            entry_meta = added.metadata_json or {}
            assert "canonical_hash" in entry_meta
            assert entry_meta["memory_type"] == MEMORY_TYPE_FEEDBACK
            assert entry_meta["occurrence_count"] == 1
            assert entry_meta["variant_questions"] == ["What is a dolly?"]


# ── IndexApprovedFeedbacks ───────────────────────────────────────────────────

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
                return {"indexed": True, "dedup": False, "point_id": "pt-ok", "entry_id": "e-ok"}
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
        assert result["dedup_count"] == 0
        assert len(result["results"]) == 2


# ── Constants ────────────────────────────────────────────────────────────────

class TestConstants:
    def test_source_type(self) -> None:
        assert SOURCE_TYPE_FEEDBACK == "client_feedback"

    def test_source_table(self) -> None:
        assert SOURCE_TABLE_FEEDBACK == "cid_client_feedback"

    def test_memory_type_constants(self) -> None:
        assert MEMORY_TYPE_FEEDBACK == "client_feedback"
        assert MEMORY_TYPE_COMMON_QUESTION == "common_question"

    def test_non_indexable_contains_blacklist(self) -> None:
        assert "source_blacklist" in NON_INDEXABLE_TYPES
