from __future__ import annotations

import contextlib
import re
import sys
import uuid
from pathlib import Path
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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
        return self._value


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
        filters = {}
        for clause in self._flatten_where(where):
            left = getattr(clause, "left", None)
            right = getattr(clause, "right", None)
            if left is not None and right is not None:
                col_name = getattr(left, "name", None)
                val = getattr(right, "value", None)
                if col_name and val is not None:
                    filters[col_name] = val
        for job_id, job in self._store.items():
            match = True
            for col_name, val in filters.items():
                if col_name == "organization_id":
                    actual = self._original_org.get(job_id, job.organization_id)
                else:
                    actual = getattr(job, col_name, None)
                if actual != val:
                    match = False
                    break
            if match:
                import copy
                return FakeScalarResult(copy.copy(job))
        return FakeScalarResult(None)

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
