from __future__ import annotations

import contextlib
import inspect
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

import pytest
from sqlalchemy.exc import IntegrityError

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)

from models.ai_job_execution_attempt import (
    AIJobExecutionAttempt,
    ATTEMPT_MODE_SUCCESS,
    ATTEMPT_STATUS_IN_PROGRESS,
)
from repositories.ai_job_execution_attempt_repository import (
    AIJobExecutionAttemptRepository,
    AIJobExecutionAttemptRepositoryError,
)


def _new_attempt(
    organization_id: str = "org-aaa",
    job_id: str = "job-aaa",
    execution_attempt_id: str | None = None,
    created_at: datetime | None = None,
) -> AIJobExecutionAttempt:
    now = created_at or datetime.utcnow()
    return AIJobExecutionAttempt(
        id=uuid.uuid4().hex,
        organization_id=organization_id,
        job_id=job_id,
        execution_attempt_id=execution_attempt_id or uuid.uuid4().hex,
        mode=ATTEMPT_MODE_SUCCESS,
        status=ATTEMPT_STATUS_IN_PROGRESS,
        fingerprint="a" * 64,
        fingerprint_version="v1",
        created_at=now,
        updated_at=now,
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
    def __init__(self) -> None:
        self.added: list[AIJobExecutionAttempt] = []
        self.flushes = 0
        self.commits = 0
        self.last_stmt = None
        self._store: dict[str, AIJobExecutionAttempt] = {}
        self._original_org: dict[str, str] = {}

    async def execute(self, stmt):
        self.last_stmt = stmt
        if getattr(stmt, "column_descriptions", None):
            description = stmt.column_descriptions[0]
            entity = description.get("entity")
            if entity is AIJobExecutionAttempt:
                if len(stmt.selected_columns) == 1:
                    return self._execute_select_column(stmt)
                return self._execute_select(stmt)
        return FakeScalarResult(None)

    def _execute_select_column(self, stmt):
        column = stmt.selected_columns[0]
        column_name = getattr(column, "name", None)
        filters = self._filters_from_where(stmt.whereclause)
        for attempt_id, attempt in self._store.items():
            if self._matches(attempt_id, attempt, filters):
                if column_name == "organization_id":
                    return FakeScalarResult(self._original_org.get(attempt_id, attempt.organization_id))
                return FakeScalarResult(getattr(attempt, column_name, None))
        return FakeScalarResult(None)

    def _execute_select(self, stmt):
        filters = self._filters_from_where(stmt.whereclause)
        matches = []
        for attempt_id, attempt in self._store.items():
            if self._matches(attempt_id, attempt, filters):
                matches.append(attempt)
        matches.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        limit_clause = getattr(stmt, "_limit_clause", None)
        limit = getattr(limit_clause, "value", None)
        if limit is not None:
            matches = matches[:limit]
        return FakeScalarResult(matches)

    def _matches(self, attempt_id: str, attempt: AIJobExecutionAttempt, filters: list[tuple[str, Any, str]]) -> bool:
        for column_name, value, operator_name in filters:
            if column_name == "organization_id":
                actual = self._original_org.get(attempt_id, attempt.organization_id)
            else:
                actual = getattr(attempt, column_name, None)
            if operator_name == "eq" and actual != value:
                return False
            if operator_name == "lt" and not (actual < value):
                return False
        return True

    @classmethod
    def _filters_from_where(cls, clause) -> list[tuple[str, Any, str]]:
        filters = []
        for item in cls._flatten_where(clause):
            left = getattr(item, "left", None)
            right = getattr(item, "right", None)
            if left is None or right is None:
                continue
            column_name = getattr(left, "name", None)
            value = getattr(right, "value", None)
            operator_name = getattr(item.operator, "__name__", "eq")
            if column_name and value is not None:
                filters.append((column_name, value, operator_name))
        return filters

    @classmethod
    def _flatten_where(cls, clause) -> list:
        if clause is None:
            return []
        if hasattr(clause, "clauses"):
            flattened = []
            for item in clause.clauses:
                flattened.extend(cls._flatten_where(item))
            return flattened
        return [clause]

    async def flush(self) -> None:
        self.flushes += 1
        for attempt in self.added:
            if isinstance(attempt, AIJobExecutionAttempt) and attempt.id:
                if attempt.id not in self._store:
                    self._original_org[attempt.id] = attempt.organization_id
                self._store[attempt.id] = attempt

    async def commit(self) -> None:
        self.commits += 1

    def add(self, obj) -> None:
        self.added.append(obj)

    @property
    @contextlib.contextmanager
    def no_autoflush(self) -> Iterator[None]:
        yield


class IntegrityErrorSession(FakeAsyncSession):
    async def flush(self) -> None:
        raise IntegrityError("statement", "params", Exception("duplicate"))


@pytest.mark.asyncio
async def test_create_adds_and_flushes_attempt() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt()

    result = await repo.create(attempt)

    assert result is attempt
    assert attempt.id in session._store
    assert session.flushes == 1
    assert session.commits == 0


@pytest.mark.asyncio
async def test_create_rejects_missing_organization_id() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt()
    attempt.organization_id = ""

    with pytest.raises(AIJobExecutionAttemptRepositoryError, match="organization_id"):
        await repo.create(attempt)


@pytest.mark.asyncio
async def test_create_does_not_swallow_integrity_error() -> None:
    session = IntegrityErrorSession()
    repo = AIJobExecutionAttemptRepository(session)

    with pytest.raises(IntegrityError):
        await repo.create(_new_attempt())


@pytest.mark.asyncio
async def test_get_filters_by_tenant_job_and_attempt_id() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt(
        organization_id="org-aaa",
        job_id="job-aaa",
        execution_attempt_id="attempt-aaa",
    )
    await repo.create(attempt)

    result = await repo.get("org-aaa", "job-aaa", "attempt-aaa")


    assert result is attempt


@pytest.mark.asyncio
async def test_get_returns_none_for_tenant_mismatch() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt(organization_id="org-aaa", job_id="job-aaa")
    await repo.create(attempt)

    result = await repo.get("org-bbb", "job-aaa", attempt.execution_attempt_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_for_update_uses_row_locking() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt()
    await repo.create(attempt)

    result = await repo.get_for_update(
        attempt.organization_id,
        attempt.job_id,
        attempt.execution_attempt_id,
    )

    assert result is attempt
    assert getattr(session.last_stmt, "_for_update_arg", None) is not None


@pytest.mark.asyncio
async def test_find_by_key_aliases_get_semantics() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt(execution_attempt_id="attempt-aaa")
    await repo.create(attempt)

    result = await repo.find_by_key(
        attempt.organization_id,
        attempt.job_id,
        "attempt-aaa",
    )

    assert result is attempt


@pytest.mark.asyncio
async def test_save_flushes_and_does_not_commit() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt()
    await repo.create(attempt)
    session.flushes = 0

    result = await repo.save(attempt)

    assert result is attempt
    assert session.flushes == 1
    assert session.commits == 0


@pytest.mark.asyncio
async def test_save_rejects_missing_organization_id() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    attempt = _new_attempt()
    attempt.organization_id = ""

    with pytest.raises(AIJobExecutionAttemptRepositoryError, match="organization_id"):
        await repo.save(attempt)


@pytest.mark.asyncio
async def test_list_for_job_filters_by_tenant_and_job() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    matching = _new_attempt("org-aaa", "job-aaa")
    other_job = _new_attempt("org-aaa", "job-bbb")
    other_tenant = _new_attempt("org-bbb", "job-aaa")
    await repo.create(matching)
    await repo.create(other_job)
    await repo.create(other_tenant)

    rows, next_cursor = await repo.list_for_job("org-aaa", "job-aaa")

    assert rows == [matching]
    assert next_cursor is None


@pytest.mark.asyncio
async def test_list_for_job_clamps_limit_and_returns_next_cursor() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    base = datetime.utcnow()
    attempts = [
        _new_attempt("org-aaa", "job-aaa", created_at=base + timedelta(seconds=index))
        for index in range(3)
    ]
    for attempt in attempts:
        await repo.create(attempt)

    rows, next_cursor = await repo.list_for_job("org-aaa", "job-aaa", limit=1)

    assert len(rows) == 1
    assert next_cursor == attempts[1].id


@pytest.mark.asyncio
async def test_list_for_job_clamps_limit_to_100() -> None:
    session = FakeAsyncSession()
    repo = AIJobExecutionAttemptRepository(session)
    await repo.create(_new_attempt("org-aaa", "job-aaa"))

    await repo.list_for_job("org-aaa", "job-aaa", limit=500)

    assert getattr(session.last_stmt._limit_clause, "value", None) == 101


def test_no_tenantless_lookup_methods_exist() -> None:
    for method_name in ("get", "get_for_update", "find_by_key", "list_for_job"):
        signature = inspect.signature(getattr(AIJobExecutionAttemptRepository, method_name))
        assert "organization_id" in signature.parameters


def test_repository_does_not_import_session_factory_or_call_commit() -> None:
    import repositories.ai_job_execution_attempt_repository as module

    source = inspect.getsource(module)
    assert "AsyncSessionLocal" not in source
    assert ".commit(" not in source
