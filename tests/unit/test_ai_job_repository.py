from __future__ import annotations

import contextlib
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)

from models.ai_job import AIJob
from repositories.ai_job_repository import (
    AIJobRepository,
    AIJobRepositoryError,
    AIJobTenantMutationError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_job(
    organization_id: str = "org-aaa",
    job_id: str | None = None,
    idempotency_key: str | None = None,
    status: str = "created",
) -> AIJob:
    return AIJob(
        id=job_id or uuid.uuid4().hex,
        organization_id=organization_id,
        operation_type="comfyui.text_to_image",
        status=status,
        idempotency_key=idempotency_key,
    )


class FakeScalarResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        if isinstance(self._value, list):
            return self._value[0] if self._value else None
        return self._value

    def scalars(self):
        return self

    def all(self) -> list[Any]:
        if isinstance(self._value, list):
            return self._value
        if self._value is None:
            return []
        return [self._value]


class FakeAsyncSession:
    """Minimal fake AsyncSession for repository unit tests."""

    def __init__(self) -> None:
        self.added: list[AIJob] = []
        self.flushes: int = 0
        self.commits: int = 0
        self._store: dict[str, AIJob] = {}
        self._original_org: dict[str, str] = {}

    async def execute(self, stmt):
        cls_name = type(stmt).__name__
        if cls_name == "Select":
            if stmt.column_descriptions:
                model = stmt.column_descriptions[0].get("entity")
                if model is AIJob:
                    if len(stmt.selected_columns) == 1:
                        return self._execute_select_column(stmt)
                    return self._execute_select(stmt)
        return FakeScalarResult(None)

    def _execute_select_column(self, stmt):
        col = stmt.selected_columns[0]
        col_name = getattr(col, "name", None)
        where = stmt.whereclause
        if where is None:
            return FakeScalarResult(None)
        filters = {}
        for clause in self._flatten_where(where):
            left = getattr(clause, "left", None)
            right = getattr(clause, "right", None)
            if left is not None and right is not None:
                cname = getattr(left, "name", None)
                val = getattr(right, "value", None)
                if cname and val is not None:
                    filters[cname] = val
        for job_id, job in self._store.items():
            match = True
            for cname, val in filters.items():
                if cname == "organization_id":
                    actual = self._original_org.get(job_id, job.organization_id)
                else:
                    actual = getattr(job, cname, None)
                if actual != val:
                    match = False
                    break
            if match:
                return FakeScalarResult(getattr(job, col_name, None))
        return FakeScalarResult(None)

    def _execute_select(self, stmt):
        where = stmt.whereclause
        if where is None:
            return FakeScalarResult(None)
        filters = []
        for clause in self._flatten_where(where):
            left = getattr(clause, "left", None)
            right = getattr(clause, "right", None)
            if left is not None and right is not None:
                col_name = getattr(left, "name", None)
                if col_name:
                    op_name = getattr(clause.operator, "__name__", "") or "eq"

                    if op_name in ("in_op", "in_"):
                        vals = getattr(right, "value", None)
                        if isinstance(vals, (list, tuple, set, frozenset)):
                            filters.append((col_name, set(vals), "in_"))
                    elif op_name in ("is_not",) and type(right).__name__ == "Null":
                        filters.append((col_name, None, "is_not"))
                    elif op_name in ("is_", "eq") and type(right).__name__ == "Null":
                        filters.append((col_name, None, "is_"))
                    else:
                        val = getattr(right, "value", None)
                        if val is not None:
                            filters.append((col_name, val, op_name))
        matches = []
        for job_id, job in self._store.items():
            match = True
            for col_name, val, op_name in filters:
                if col_name == "organization_id":
                    actual = self._original_org.get(job_id, job.organization_id)
                else:
                    actual = getattr(job, col_name, None)

                if op_name in ("in_",):
                    if actual not in val:
                        match = False
                        break
                elif op_name in ("is_not",):
                    if actual is None:
                        match = False
                        break
                elif op_name in ("is_",):
                    if actual is not None:
                        match = False
                        break
                elif op_name in ("eq",) and actual != val:
                    match = False
                    break
                elif op_name in ("ne",) and actual == val:
                    match = False
                    break
                elif op_name in ("lt",) and not (actual < val):
                    match = False
                    break
                elif op_name in ("le",) and not (actual <= val):
                    match = False
                    break
                elif op_name in ("gt",) and not (actual > val):
                    match = False
                    break
                elif op_name in ("ge",) and not (actual >= val):
                    match = False
                    break
            if match:
                import copy
                matches.append(copy.copy(job))

        order_by_clauses = getattr(stmt, "_order_by_clauses", None) or ()
        if order_by_clauses:
            sort_cols = []
            for clause in order_by_clauses:
                element = getattr(clause, "element", None)
                col_name = getattr(element, "name", None)
                if col_name:
                    sort_cols.append(col_name)
            if sort_cols:
                all_desc = all(
                    getattr(clause.modifier, '__name__', '') == 'desc_op'
                    for clause in order_by_clauses
                ) if order_by_clauses else False

                def _sort_key(item):
                    return tuple(getattr(item, c, None) or "" for c in sort_cols)
                matches.sort(key=_sort_key, reverse=all_desc)
        else:
            matches.sort(key=lambda item: item.id, reverse=True)

        limit_clause = getattr(stmt, "_limit_clause", None)
        limit = getattr(limit_clause, "value", None)
        if limit is not None:
            matches = matches[:limit]
        return FakeScalarResult(matches)

    @staticmethod
    def _flatten_where(clause) -> list:
        clauses = []
        if hasattr(clause, "clauses"):
            for c in clause.clauses:
                clauses.extend(FakeAsyncSession._flatten_where(c))
        else:
            clauses.append(clause)
        return clauses

    async def flush(self) -> None:
        self.flushes += 1
        for obj in self.added:
            if isinstance(obj, AIJob) and obj.id:
                import copy
                if obj.id not in self._store:
                    self._original_org[obj.id] = obj.organization_id
                self._store[obj.id] = copy.copy(obj)

    async def commit(self) -> None:
        self.commits += 1

    def add(self, obj) -> None:
        self.added.append(obj)

    @property
    @contextlib.asynccontextmanager
    async def no_autoflush(self) -> AsyncIterator[None]:
        yield


# ---------------------------------------------------------------------------
# Tests: create
# ---------------------------------------------------------------------------

class TestRepositoryCreate:
    @pytest.mark.asyncio
    async def test_create_persists_job(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        result = await repo.create(job)
        assert result is not None and result.id == job.id
        assert result.id in session._store
        assert session.flushes == 1

    @pytest.mark.asyncio
    async def test_create_does_not_commit(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        await repo.create(job)
        assert session.commits == 0


# ---------------------------------------------------------------------------
# Tests: get (tenant-scoped)
# ---------------------------------------------------------------------------

class TestRepositoryGet:
    @pytest.mark.asyncio
    async def test_get_returns_job_in_same_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        result = await repo.get("org-aaa", job.id)
        assert result is not None and result.id == job.id

    @pytest.mark.asyncio
    async def test_get_returns_none_for_different_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        result = await repo.get("org-bbb", job.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_none_for_nonexistent_job(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        result = await repo.get("org-aaa", "nonexistent")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: get_for_update (tenant-scoped + lock)
# ---------------------------------------------------------------------------

class TestRepositoryGetForUpdate:
    @pytest.mark.asyncio
    async def test_get_for_update_returns_job_in_same_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        result = await repo.get_for_update("org-aaa", job.id)
        assert result is not None and result.id == job.id

    @pytest.mark.asyncio
    async def test_get_for_update_returns_none_for_different_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        result = await repo.get_for_update("org-bbb", job.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_for_update_applies_with_for_update(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        captured_stmts: list = []
        original_execute = session.execute

        async def capturing_execute(stmt):
            captured_stmts.append(stmt)
            return await original_execute(stmt)

        session.execute = capturing_execute
        await repo.get_for_update("org-aaa", job.id)
        assert len(captured_stmts) == 1
        stmt = captured_stmts[0]
        assert stmt._for_update_arg is not None


# ---------------------------------------------------------------------------
# Tests: save (tenant mutation guard)
# ---------------------------------------------------------------------------

class TestRepositorySave:
    @pytest.mark.asyncio
    async def test_save_new_job(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        result = await repo.save(job)
        assert result is not None and result.id == job.id
        assert job.id in session._store

    @pytest.mark.asyncio
    async def test_save_existing_job_same_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        job.status = "reserved"
        result = await repo.save(job)
        assert result.status == "reserved"

    @pytest.mark.asyncio
    async def test_save_rejects_tenant_reassignment(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        job.organization_id = "org-bbb"
        with pytest.raises(AIJobTenantMutationError, match="Cannot reassign"):
            await repo.save(job)

    @pytest.mark.asyncio
    async def test_save_does_not_commit(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        await repo.save(job)
        assert session.commits == 0

    @pytest.mark.asyncio
    async def test_save_rejects_none_organization_id(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        job.organization_id = None
        with pytest.raises(AIJobRepositoryError, match="organization_id must not be None"):
            await repo.save(job)


# ---------------------------------------------------------------------------
# Tests: find_by_idempotency_key (tenant-scoped)
# ---------------------------------------------------------------------------

class TestRepositoryFindByIdempotencyKey:
    @pytest.mark.asyncio
    async def test_finds_job_by_idempotency_key(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa", idempotency_key="key-123")
        await repo.create(job)
        result = await repo.find_by_idempotency_key("org-aaa", "key-123")
        assert result is not None and result.id == job.id

    @pytest.mark.asyncio
    async def test_returns_none_for_different_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa", idempotency_key="key-123")
        await repo.create(job)
        result = await repo.find_by_idempotency_key("org-bbb", "key-123")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_key(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        result = await repo.find_by_idempotency_key("org-aaa", "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_same_key_different_tenants_no_collision(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job_a = _new_job(organization_id="org-aaa", idempotency_key="shared-key")
        job_b = _new_job(organization_id="org-bbb", idempotency_key="shared-key")
        await repo.create(job_a)
        await repo.create(job_b)
        result_a = await repo.find_by_idempotency_key("org-aaa", "shared-key")
        result_b = await repo.find_by_idempotency_key("org-bbb", "shared-key")
        assert result_a is not None and result_a.id == job_a.id
        assert result_b is not None and result_b.id == job_b.id
        assert result_a.id != result_b.id


# ---------------------------------------------------------------------------
# Tests: list_for_organization (tenant-scoped filters + cursor)
# ---------------------------------------------------------------------------

class TestRepositoryListForOrganization:
    @pytest.mark.asyncio
    async def test_lists_only_jobs_for_requested_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job_a = _new_job(organization_id="org-aaa", job_id="job-002")
        job_b = _new_job(organization_id="org-bbb", job_id="job-003")
        await repo.create(job_a)
        await repo.create(job_b)

        jobs, next_cursor = await repo.list_for_organization("org-aaa")

        assert [job.id for job in jobs] == ["job-002"]
        assert next_cursor is None

    @pytest.mark.asyncio
    async def test_list_applies_status_project_operation_and_date_filters(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        keep = _new_job(organization_id="org-aaa", job_id="job-003", status="reserved")
        keep.project_id = "project-1"
        keep.operation_type = "image_generation"
        keep.created_at = datetime(2026, 6, 9, 12, 0, 0)
        wrong_status = _new_job(organization_id="org-aaa", job_id="job-004", status="created")
        wrong_status.project_id = "project-1"
        wrong_status.operation_type = "image_generation"
        wrong_status.created_at = datetime(2026, 6, 9, 12, 0, 0)
        old_job = _new_job(organization_id="org-aaa", job_id="job-005", status="reserved")
        old_job.project_id = "project-1"
        old_job.operation_type = "image_generation"
        old_job.created_at = datetime(2026, 6, 1, 12, 0, 0)
        await repo.create(keep)
        await repo.create(wrong_status)
        await repo.create(old_job)

        jobs, _next_cursor = await repo.list_for_organization(
            "org-aaa",
            status="reserved",
            project_id="project-1",
            operation_type="image_generation",
            created_after=datetime(2026, 6, 8, 0, 0, 0),
            created_before=datetime(2026, 6, 10, 0, 0, 0),
        )

        assert [job.id for job in jobs] == ["job-003"]

    @pytest.mark.asyncio
    async def test_list_returns_next_cursor_when_more_rows_exist(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for job_id in ["job-001", "job-002", "job-003"]:
            await repo.create(_new_job(organization_id="org-aaa", job_id=job_id))

        jobs, next_cursor = await repo.list_for_organization("org-aaa", limit=2)

        assert [job.id for job in jobs] == ["job-003", "job-002"]
        assert next_cursor == "job-001"

    @pytest.mark.asyncio
    async def test_list_applies_cursor(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for job_id in ["job-001", "job-002", "job-003"]:
            await repo.create(_new_job(organization_id="org-aaa", job_id=job_id))

        jobs, next_cursor = await repo.list_for_organization("org-aaa", cursor="job-003")

        assert [job.id for job in jobs] == ["job-002", "job-001"]
        assert next_cursor is None


# ---------------------------------------------------------------------------
# Tests: contract compliance
# ---------------------------------------------------------------------------

class TestRepositoryContractCompliance:
    @pytest.mark.asyncio
    async def test_repository_does_not_commit(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        await repo.create(job)
        await repo.save(job)
        await repo.get(job.organization_id, job.id)
        await repo.get_for_update(job.organization_id, job.id)
        await repo.find_by_idempotency_key(job.organization_id, "any")
        assert session.commits == 0

    @pytest.mark.asyncio
    async def test_repository_allows_flush(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job()
        await repo.create(job)
        assert session.flushes >= 1

    @pytest.mark.asyncio
    async def test_all_reads_filter_by_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-aaa")
        await repo.create(job)
        assert await repo.get("org-bbb", job.id) is None
        assert await repo.get_for_update("org-bbb", job.id) is None
        assert await repo.find_by_idempotency_key("org-bbb", "key") is None


# ---------------------------------------------------------------------------
# Tests: source inspection
# ---------------------------------------------------------------------------

class TestRepositorySourceInspection:
    def test_source_does_not_call_commit(self) -> None:
        import repositories.ai_job_repository as mod
        raw = Path(mod.__file__).read_text()
        cleaned = re.sub(r'""".*?"""', '', raw, flags=re.DOTALL)
        cleaned = re.sub(r"'''.*?'''", '', cleaned, flags=re.DOTALL)
        assert "commit()" not in cleaned

    def test_source_does_not_import_async_session_local(self) -> None:
        import repositories.ai_job_repository as mod
        source = Path(mod.__file__).read_text()
        assert "AsyncSessionLocal" not in source

    def test_source_does_not_import_get_db(self) -> None:
        import repositories.ai_job_repository as mod
        source = Path(mod.__file__).read_text()
        assert "get_db" not in source

    def test_source_has_no_is_sqlite_method(self) -> None:
        import repositories.ai_job_repository as mod
        raw = Path(mod.__file__).read_text()
        cleaned = re.sub(r'""".*?"""', '', raw, flags=re.DOTALL)
        cleaned = re.sub(r"'''.*?'''", '', cleaned, flags=re.DOTALL)
        assert "_is_sqlite" not in cleaned


# ---------------------------------------------------------------------------
# Tests: exception hierarchy
# ---------------------------------------------------------------------------

class TestRepositoryExceptions:
    def test_tenant_mutation_error_is_subclass(self) -> None:
        assert issubclass(AIJobTenantMutationError, AIJobRepositoryError)

    def test_repository_error_is_subclass_of_exception(self) -> None:
        assert issubclass(AIJobRepositoryError, Exception)


# ---------------------------------------------------------------------------
# Tests: list_cancelled_credit_release_candidates
# ---------------------------------------------------------------------------

class TestRepositoryListCancelledCreditReleaseCandidates:
    """Behavioral tests for the reconciliation candidate selector."""

    @pytest.mark.asyncio
    async def test_returns_eligible_job(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancel_requested")
        job.reservation_entry_id = "res-1"
        job.reserved_credits = 8
        job.consumed_credits = 0
        job.consume_entry_id = None
        job.release_entry_id = None
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert len(candidates) == 1
        assert candidates[0].id == job.id

    @pytest.mark.asyncio
    async def test_excludes_wrong_tenant(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(organization_id="org-bbb", status="cancelled")
        job.reservation_entry_id = "res-1"
        job.reserved_credits = 8
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_non_eligible_status(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="created")
        job.reservation_entry_id = "res-1"
        job.reserved_credits = 8
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_missing_reservation_entry(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancelled")
        job.reservation_entry_id = None
        job.reserved_credits = 8
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_already_released(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancelled")
        job.reservation_entry_id = "res-1"
        job.release_entry_id = "rel-1"
        job.reserved_credits = 8
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_already_consumed(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancelled")
        job.reservation_entry_id = "res-1"
        job.consume_entry_id = "con-1"
        job.reserved_credits = 8
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_non_zero_consumed_credits(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancelled")
        job.reservation_entry_id = "res-1"
        job.reserved_credits = 8
        job.consumed_credits = 1
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_excludes_zero_reserved_credits(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job = _new_job(status="cancelled")
        job.reservation_entry_id = "res-1"
        job.reserved_credits = 0
        await repo.create(job)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert candidates == []

    @pytest.mark.asyncio
    async def test_returns_multiple_eligible_statuses(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for i, status in enumerate(["cancel_requested", "cancelled", "release_pending"]):
            j = _new_job(job_id=f"job-{i}", organization_id="org-aaa", status=status)
            j.reservation_entry_id = f"res-{i}"
            j.reserved_credits = 8
            j.consumed_credits = 0
            await repo.create(j)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert len(candidates) == 3

    @pytest.mark.asyncio
    async def test_respects_limit(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for i in range(5):
            j = _new_job(job_id=f"job-{i}", organization_id="org-aaa", status="cancelled")
            j.reservation_entry_id = f"res-{i}"
            j.reserved_credits = 8
            j.consumed_credits = 0
            j.created_at = datetime(2026, 6, 9, 10, i, 0)
            await repo.create(j)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=2
        )

        assert len(candidates) == 2

    @pytest.mark.asyncio
    async def test_orders_by_created_at_asc_then_id_asc(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        job_a = _new_job(job_id="job-a", organization_id="org-aaa", status="cancelled")
        job_a.reservation_entry_id = "res-a"
        job_a.reserved_credits = 8
        job_a.consumed_credits = 0
        job_a.created_at = datetime(2026, 6, 9, 12, 0, 0)
        await repo.create(job_a)
        job_b = _new_job(job_id="job-b", organization_id="org-aaa", status="cancelled")
        job_b.reservation_entry_id = "res-b"
        job_b.reserved_credits = 8
        job_b.consumed_credits = 0
        job_b.created_at = datetime(2026, 6, 9, 11, 0, 0)
        await repo.create(job_b)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=10
        )

        assert len(candidates) == 2
        assert [c.id for c in candidates] == ["job-b", "job-a"]

    @pytest.mark.asyncio
    async def test_safe_limit_caps_at_100(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for i in range(150):
            j = _new_job(job_id=f"job-{i:03d}", organization_id="org-aaa", status="cancelled")
            j.reservation_entry_id = f"res-{i}"
            j.reserved_credits = 8
            j.consumed_credits = 0
            await repo.create(j)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=200
        )

        assert len(candidates) == 100

    @pytest.mark.asyncio
    async def test_safe_limit_floors_at_one(self) -> None:
        session = FakeAsyncSession()
        repo = AIJobRepository(session)
        for i in range(3):
            j = _new_job(job_id=f"job-{i}", organization_id="org-aaa", status="cancelled")
            j.reservation_entry_id = f"res-{i}"
            j.reserved_credits = 8
            j.consumed_credits = 0
            await repo.create(j)

        candidates = await repo.list_cancelled_credit_release_candidates(
            "org-aaa", limit=0
        )

        assert len(candidates) == 1
