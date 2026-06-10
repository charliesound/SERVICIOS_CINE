# CID PostgreSQL Test Harness Concurrency Timeouts Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.POSTGRES.TEST.HARNESS.CONCURRENCY.TIMEOUTS.CONTRACT.1
Scope: future PostgreSQL test harness hardening for real locking and concurrency tests

Companion docs:

- `docs/architecture/cid_ai_job_worker_mock_execution_wrapper_postgres_concurrency_contract_v1.md`
- `docs/architecture/cid_postgresql_only_tests_quarantine_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future contract for hardening the PostgreSQL test harness so integration tests can safely exercise real locking and concurrency behavior.

The harness hardening exists to:

- avoid deadlocks, fragile sleeps, and indefinitely hung async tasks;
- support tests for concurrent unique-key inserts;
- support tests for `FOR UPDATE` row locks;
- support blocked transaction assertions with bounded failure modes;
- enable deterministic replay-versus-in-progress checks for idempotent workers;
- keep all locking tests scoped to explicitly test-safe PostgreSQL databases.

The immediate driver is the deferred same-key concurrency case in `tests/integration/test_ai_job_worker_mock_execution_wrapper_postgres_concurrency.py`.

## 2. Scope

In scope for this contract:

- Future PostgreSQL test harness hardening.
- Future helpers for PostgreSQL `statement_timeout` and `lock_timeout`.
- Future helpers for Python async timeouts.
- Future helpers for independent sessions from the same test engine.
- Future cleanup helpers for concurrent tasks and sessions.
- Future PostgreSQL integration tests that need real transaction and lock behavior.

This is a contract-only phase. No harness code or tests are implemented here.

## 3. Non-Scope

Out of scope:

- Implementing harness changes in this phase.
- Implementing new concurrency tests in this phase.
- Changing runtime application code.
- Changing models, migrations, services, repositories, dependencies, or routes.
- Changing container, deployment, or production configuration.
- Changing public API behavior.
- Changing UI code.
- Changing allowlists or guard scripts.

## 4. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `tests/helpers/postgres_test_harness.py`
- `tests/unit/test_postgres_test_harness.py`
- `tests/integration/test_ai_job_worker_mock_execution_wrapper_postgres_concurrency.py`
- `docs/architecture/cid_ai_job_worker_mock_execution_wrapper_postgres_concurrency_contract_v1.md`
- `docs/architecture/cid_postgresql_only_tests_quarantine_v1.md`
- `pytest.ini`
- `directivas/cid_wsl_only_agent_rules.md`

Observed facts:

- The current harness validates `TEST_DATABASE_URL`, rejects unsafe DSNs, creates a temporary schema, builds selected tables from `Base.metadata`, and disposes the engine after teardown.
- The current harness uses `NullPool`, `async_sessionmaker`, and schema-local `search_path` settings.
- The current harness does not expose helpers for per-session PostgreSQL timeouts.
- The current harness does not expose helpers for opening coordinated independent sessions.
- The current wrapper PostgreSQL integration test implements deterministic first execution, terminal replay, fingerprint mismatch, and in-progress conflict coverage.
- The same-key concurrent first-writer test is currently skipped because blocked unique-key inserts need explicit timeout controls.
- `pytest.ini` already defines `postgres_required` and `postgres_validated` markers.
- The quarantine document classifies PostgreSQL harness tests as valid for new SaaS persistence and concurrency gates.

## 5. Current Problem

PostgreSQL exposes real concurrency semantics that unit tests and fake repositories cannot emulate safely.

Current risks:

- A concurrent insert for the same unique key can block until the first transaction commits or rolls back.
- A `FOR UPDATE` query can block while another transaction holds the row lock.
- Without PostgreSQL-side timeouts, a blocked statement can wait longer than the test process should allow.
- Without Python-side timeouts, an async task or event wait can hang indefinitely.
- Sleeps are not deterministic synchronization and can create flaky tests.
- A failed concurrent task can leave sessions or transactions open unless cleanup is centralized.

The harness must provide bounded, explicit, test-scoped controls before enabling broader locking tests.

## 6. Future Harness Requirements

### 6.1 PostgreSQL Statement And Lock Timeouts

The future harness must support per-session or per-transaction timeout settings:

- `statement_timeout`
- `lock_timeout`

Rules:

- Timeouts must apply only to test sessions or test transactions.
- Timeouts must never be written as global database settings.
- Helpers must use scoped SQL such as `SET LOCAL` when inside an active transaction, or reset session settings before close when session-level settings are used.
- Timeout values must be explicit in each test or helper call.
- Timeout values must be short enough to fail fast but long enough to avoid false positives on normal local or CI latency.
- Helper errors must include the operation label and timeout values.

### 6.2 Python Async Timeouts

The future harness must provide a helper to wrap critical awaits.

Requirements:

- Use `asyncio.wait_for` internally.
- Accept an operation label.
- Raise an assertion-style error with a clear message when the timeout expires.
- Preserve original exceptions for non-timeout failures.
- Be usable for database awaits, task gathers, and event waits.

### 6.3 Independent Sessions

The future harness must provide a safe way to open multiple independent sessions from the same `session_factory`.

Requirements:

- Support two or more sessions.
- Ensure each session is closed.
- Ensure failed concurrent tasks trigger rollback and close.
- Make transaction ownership explicit in tests.
- Avoid sharing one session across concurrent tasks.

### 6.4 Coordination Primitives

The future harness should standardize event-based coordination.

Recommended approach:

- Use `asyncio.Event` for barriers such as `worker_entered`, `insert_started`, `lock_acquired`, and `release_worker`.
- Provide optional helper classes for common barrier patterns.
- Avoid sleeps as the primary synchronization mechanism.
- Permit a tiny bounded sleep only as a last-resort yield point, documented inline and wrapped by a timeout.

### 6.5 Expected Blocking Classification

Future helpers should make it possible for tests to distinguish:

- expected blocking that resolves before timeout;
- expected timeout caused by lock contention;
- unexpected deadlock or database error;
- expected unique-key violation;
- expected replay result;
- expected in-progress conflict.

The helper layer should not hide database exceptions. It should attach context and let the test assert the expected class or outcome.

### 6.6 DSN Safety

Future hardening must preserve current DSN safety rules.

Requirements:

- Continue validating that the DSN is explicitly test-safe.
- Continue skipping clearly when no PostgreSQL test DSN is configured.
- Never run locking tests against production-like hosts or database names.
- Never introduce a local compatibility fallback.
- Keep temporary schema teardown mandatory.

## 7. Proposed Future Helpers

### 7.1 `set_local_postgres_timeouts`

Proposed signature:

```python
async def set_local_postgres_timeouts(
    session: AsyncSession,
    *,
    statement_timeout_ms: int,
    lock_timeout_ms: int,
) -> None: ...
```

Semantics:

- Applies timeout settings to the current transaction using `SET LOCAL`.
- Requires an active transaction or starts one explicitly by the caller's session context.
- Validates positive integer values.
- Does not commit.
- Does not close the session.

### 7.2 `postgres_session_with_timeouts`

Proposed signature:

```python
@asynccontextmanager
async def postgres_session_with_timeouts(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    statement_timeout_ms: int,
    lock_timeout_ms: int,
) -> AsyncIterator[AsyncSession]: ...
```

Semantics:

- Opens one session.
- Applies scoped timeouts.
- Rolls back on error.
- Closes the session in `finally`.
- Does not commit automatically.

### 7.3 `run_with_async_timeout`

Proposed signature:

```python
async def run_with_async_timeout(
    awaitable: Awaitable[T],
    *,
    timeout_seconds: float,
    label: str,
) -> T: ...
```

Semantics:

- Wraps `asyncio.wait_for`.
- Includes `label` in timeout messages.
- Re-raises non-timeout exceptions unchanged.
- Should be used around critical awaits, event waits, and task gathers.

### 7.4 `open_independent_sessions`

Proposed signature:

```python
@asynccontextmanager
async def open_independent_sessions(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    count: int = 2,
) -> AsyncIterator[tuple[AsyncSession, ...]]: ...
```

Semantics:

- Opens `count` independent sessions.
- Validates `count >= 2`.
- Rolls back and closes every session in cleanup.
- Does not commit automatically.
- Leaves transaction boundaries explicit to each test.

### 7.5 `cleanup_concurrent_tasks`

Proposed signature:

```python
async def cleanup_concurrent_tasks(
    tasks: Iterable[asyncio.Task[Any]],
    *,
    timeout_seconds: float,
) -> None: ...
```

Semantics:

- Cancels unfinished tasks.
- Awaits task cancellation under a timeout.
- Suppresses only expected cancellation exceptions.
- Does not suppress assertion failures or database failures from completed tasks.

### 7.6 Local Assertion Helpers

Some assertions should remain in integration test files rather than global harness code.

Examples:

- `assert_single_row_by_key(...)`
- `load_attempt_by_key(...)`
- `count_attempts_by_key(...)`

These helpers are domain-specific and should stay close to the wrapper tests unless multiple PostgreSQL integration files reuse them.

## 8. Rules For Future Locking Tests

Future PostgreSQL locking tests must follow these rules:

- Use independent sessions for independent concurrent actors.
- Use `asyncio.Event` or explicit database locks for coordination.
- Do not use sleeps as the primary synchronization mechanism.
- Use both PostgreSQL-side and Python-side timeouts.
- Close every session.
- Roll back every open transaction during cleanup.
- Cancel unfinished tasks if one task fails.
- Use test-level commits only when visibility across sessions is required.
- Document each test-level commit that is needed for cross-session visibility.
- Never call commit from runtime services under test.
- Assert final row counts after all tasks complete.
- Keep tests skip-safe when PostgreSQL is not configured.

## 9. Future Application To Mock Worker Wrapper

The harness hardening should enable these currently deferred wrapper tests:

### 9.1 Same Key, Same Payload

Goal:

- Two independent sessions call the wrapper with the same `(organization_id, job_id, execution_attempt_id)` and the same fingerprint.

Expected accepted outcomes:

- One caller executes first and the other replays after completion.
- Or one caller executes first and the other receives an in-progress conflict while the first transaction is active.

Hard assertions:

- Fake worker is called at most once.
- Exactly one attempt row exists.
- No task hangs.
- No broad table cleanup is required.

### 9.2 Same Key, Different Payload

Goal:

- Two independent sessions call the wrapper with the same key and different fingerprints.

Expected outcome:

- One request may execute.
- The conflicting request must fail with fingerprint conflict or route-level conflict mapping.

Hard assertions:

- Fake worker is called at most once.
- Exactly one attempt row exists.
- The stored fingerprint belongs to the first writer.
- No second settlement-like result is created.

### 9.3 Blocked `get_for_update`

Goal:

- Session A locks an attempt row.
- Session B attempts to lock the same row.

Expected outcome:

- Session B either waits and then proceeds after release, or hits an expected lock timeout.
- The result is classified explicitly by the test.

Hard assertions:

- No contradictory replay/conflict decision occurs while the lock is held.
- All sessions close and all tasks finish under bounded time.

## 10. Acceptance Criteria For Future Implementation

The future harness hardening is acceptable only if:

- It provides scoped PostgreSQL statement and lock timeout helpers.
- It provides Python async timeout helpers with clear labels.
- It provides safe independent-session management.
- It provides cleanup for concurrent tasks.
- Timeout settings are limited to test scope.
- A blocked test fails quickly with an actionable message.
- Failed tests do not leave persistent locks, tasks, or sessions behind.
- Tests skip clearly when no safe PostgreSQL test DSN is configured.
- No local compatibility fallback is introduced.
- Repository guards pass.

## 11. Roadmap

Recommended implementation order:

1. Implement the minimal timeout helpers in `tests/helpers/postgres_test_harness.py`.
2. Add harness unit tests for timeout SQL generation, validation, async timeout behavior, and cleanup behavior.
3. Add a PostgreSQL integration test proving `lock_timeout` works against a held row lock.
4. Enable the real same-key/same-payload wrapper concurrency test.
5. Add the same-key/different-payload wrapper concurrency test.
6. Add route-level concurrency tests only if wrapper-level coverage leaves an HTTP mapping gap.
7. Clean up unrelated warnings separately.

## 12. Constraints For Future Authors

Future authors must keep this harness hardening test-only.

- Do not import runtime application factories into the harness.
- Do not change application database configuration.
- Do not change models or migrations for test convenience.
- Do not broaden the harness to public API or UI concerns.
- Do not hide database errors that tests need to assert.
- Do not modify guard scripts or allowlists to make tests pass.
