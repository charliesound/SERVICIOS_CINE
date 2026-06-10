# CID AI Job Worker Mock Execution Wrapper PostgreSQL Concurrency Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOB.WORKER.MOCK.EXECUTION.WRAPPER.POSTGRES.CONCURRENCY.CONTRACT.1
Scope: future PostgreSQL integration tests for `AIJobWorkerMockExecutionService` and the internal mock worker trigger

Companion docs:

- `docs/architecture/cid_ai_job_worker_mock_execution_wrapper_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md`
- `docs/architecture/cid_ai_job_execution_attempt_model_repository_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future PostgreSQL integration tests required to validate persisted idempotency by `execution_attempt_id` for the CID AI Job mock worker wrapper.

The future tests must prove behavior that unit tests and fake repositories cannot prove:

- the real unique constraint on `(organization_id, job_id, execution_attempt_id)` is enforced;
- `AIJobExecutionAttemptRepository.get_for_update()` uses real row locking semantics;
- two concurrent calls with the same effective key cannot both execute the worker;
- terminal attempts can be replayed without calling the worker again;
- conflicting fingerprints are rejected without calling the worker;
- in-progress attempts are treated conservatively;
- duplicate settlement is prevented indirectly because the wrapper calls the worker at most once for a given key.

The goal is to validate the database-backed concurrency contract, not to re-test all worker transition logic.

## 2. Scope

In scope for future implementation:

- PostgreSQL integration tests.
- `AIJobWorkerMockExecutionService`.
- `AIJobExecutionAttemptRepository`.
- `AIJobExecutionAttempt` persistence and constraints.
- The real unique constraint `(organization_id, job_id, execution_attempt_id)`.
- Real `FOR UPDATE` behavior through `get_for_update()`.
- Concurrency with independent sessions and transactions.
- A controlled fake worker service that returns `AIJobWorkerMockResult`.
- Optional route-level coverage for `POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute` after the wrapper integration.

This phase creates only this contract. It does not implement tests.

## 3. Non-Scope

Out of scope for this phase and for the first future integration-test phase:

- Creating tests in this phase.
- Changing runtime application code.
- Changing models, migrations, repositories, services, dependencies, or routes.
- Changing the worker queue, real worker process, or external provider integrations.
- Changing ledger, gateway, gate, costing, or accounting behavior.
- Testing real settlement side effects against the ledger.
- Changing UI or public API behavior.
- Changing container, deployment, or runtime configuration.

## 4. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `docs/architecture/cid_ai_job_worker_mock_execution_wrapper_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md`
- `docs/architecture/cid_ai_job_execution_attempt_model_repository_contract_v1.md`
- `src/services/ai_job_worker_mock_execution_service.py`
- `src/services/ai_job_worker_mock_service.py`
- `src/repositories/ai_job_execution_attempt_repository.py`
- `src/models/ai_job_execution_attempt.py`
- `src/routes/internal_ai_job_worker_mock_routes.py`
- `tests/unit/test_ai_job_worker_mock_execution_service.py`
- `tests/unit/test_ai_job_worker_mock_routes.py`
- `tests/unit/test_postgres_test_harness.py`

Observed facts:

- The wrapper uses an insert-first strategy and catches only the expected unique-attempt `IntegrityError`.
- The wrapper compares the incoming fingerprint with the stored fingerprint before replaying.
- The wrapper returns `replay=True` only for terminal attempt statuses that can be reconstructed safely.
- The wrapper raises an in-progress conflict for matching `in_progress` attempts.
- The repository flushes on `create()` and `save()` and does not call `commit()`.
- The repository uses tenant-scoped lookup methods and `with_for_update()` for `get_for_update()`.
- The model declares the unique constraint named `uq_ai_job_execution_attempts_org_job_attempt`.
- The internal route now depends on `AIJobWorkerMockExecutionService` and maps wrapper errors to safe HTTP responses.
- The existing PostgreSQL harness validates safe test DSNs and provides explicit skip behavior when a real PostgreSQL test database is unavailable.

## 5. Prerequisites

Future tests must run only against a real PostgreSQL test database.

Required prerequisites:

- A configured PostgreSQL test database using the repository's existing harness pattern.
- `TEST_DATABASE_URL` when the integration harness requires it.
- `DATABASE_URL` only when needed by import-time configuration, and only with a PostgreSQL test DSN.
- Schema available through applied migrations or a fixture-created test schema when the harness supports that pattern.
- Explicit skip behavior when the PostgreSQL test database is not configured.
- No compatibility backend, in-memory backend, or local file-backed substitute.

Future tests must not silently pass against anything other than PostgreSQL.

## 6. Objects Under Test

Primary objects:

- `AIJobWorkerMockExecutionService`
- `AIJobExecutionAttemptRepository`
- `AIJobExecutionAttempt`
- Unique constraint `(organization_id, job_id, execution_attempt_id)`
- `AIJobExecutionAttemptRepository.get_for_update()`

Optional object:

- Internal route `POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute` after route-level database wiring is practical in the integration harness.

The `AIJobWorkerMockService` itself should be represented by a controlled fake worker for these tests. These tests verify whether the wrapper calls the worker, not the worker's orchestration internals.

## 7. Isolation Strategy

Every future test must be isolated and deterministic.

Rules:

- Generate unique `organization_id`, `job_id`, and `execution_attempt_id` per test.
- Use unique attempt keys even across parametrized cases.
- Clean rows created by the test at the end, or use a per-test transaction rollback pattern when compatible with concurrency checks.
- Never touch production-like data or shared seeded data.
- Do not depend on global IDs shared across tests.
- Avoid test ordering dependencies.
- Keep fake worker state local to the test.
- Assert final row counts by the composite key, not by table-wide assumptions.

If the future harness creates a temporary schema per test module, tests may rely on schema teardown. If it uses a shared test schema, tests must delete only the rows they created.

## 8. Concurrency Design

Future concurrency tests must use independent sessions.

Recommended design:

- Create two separate async sessions from the same PostgreSQL test engine.
- Use `asyncio.gather()` only after both tasks have clear coordination points.
- Use `asyncio.Event` to coordinate critical phases.
- Use a controlled fake worker that can pause until released by the test.
- Add explicit timeouts around waits and gathered tasks to prevent hung tests.
- Avoid fragile sleeps. If a short sleep is unavoidable, it must have a documented reason and be bounded by a timeout.

Preferred event flow for same-key concurrency:

1. Session A calls the wrapper.
2. Session A inserts the attempt and enters the fake worker.
3. The fake worker signals `worker_entered` and waits on `release_worker`.
4. Session B calls the wrapper with the same key.
5. The test observes whether Session B receives an in-progress conflict, waits for the unique constraint to resolve, or receives replay after Session A completes.
6. The test releases Session A.
7. Both tasks finish or fail within a bounded timeout.
8. The test asserts one attempt row and one worker call.

Important PostgreSQL nuance:

- A concurrent insert for the same unique key may block until the first transaction commits or rolls back.
- The exact visible outcome can depend on when Session A flushes, commits, or rolls back.
- A test that requires a guaranteed in-progress row should preinsert and commit an `in_progress` attempt, then call the wrapper in a separate session.
- A test that verifies concurrent first-writer behavior should accept either a replay or an in-progress conflict for the second caller, depending on timing, but must always assert one worker call and one attempt row.

## 9. Future Test Cases

### A. First Execution Persists Attempt

Flow:

- Build a command with a unique composite key.
- Execute the wrapper once with a fake worker returning a terminal `AIJobWorkerMockResult`.
- Query `AIJobExecutionAttempt` by `(organization_id, job_id, execution_attempt_id)`.

Assertions:

- Exactly one row exists for the composite key.
- Attempt status matches the command mode: `succeeded`, `failed`, or `cancelled`.
- `fingerprint` is a 64-character hex value.
- `fingerprint_version` is `v1`.
- `result_status` and settlement fields are persisted from the fake worker result.
- `started_at` and `finished_at` are populated.
- Fake worker was called exactly once.
- The wrapper result has `replay=False`.

### B. Terminal Replay With Same Fingerprint

Flow:

- Execute once to terminal, or preinsert a terminal attempt with a matching fingerprint and result fields.
- Execute again with the same command and same composite key.

Assertions:

- The second wrapper result has `replay=True`.
- The second call does not call the fake worker.
- No second attempt row is created.
- The reconstructed result matches stored `result_status`, credits, and settlement entry ids.
- `get_for_update()` is exercised through the replay path.

### C. Fingerprint Mismatch

Flow:

- Create or execute a terminal attempt using payload A.
- Execute again with the same composite key and payload B.

Payload B may differ by:

- `mode`
- `mock_output_metadata`
- `mock_error_code`
- `mock_error_message`
- `actual_credits`
- `release_credits`

Assertions:

- The wrapper raises `AIJobWorkerMockExecutionFingerprintMismatchError`.
- The fake worker is not called for the second request.
- Exactly one attempt row remains for the key.
- The stored terminal attempt is not mutated by the conflicting request.

### D. In-Progress Conflict

Flow option 1, deterministic V1 baseline:

- Preinsert an `in_progress` attempt with the expected fingerprint.
- Commit the preinserted row.
- Execute the wrapper with the same command in a new session.

Assertions:

- The wrapper raises `AIJobWorkerMockExecutionInProgressError`.
- The fake worker is not called.
- Exactly one attempt row exists.
- The row remains `in_progress`.

Flow option 2, advanced lock behavior:

- Session A locks an `in_progress` row with `get_for_update()` and keeps the transaction open.
- Session B attempts the same key.
- Use a short statement timeout or task timeout to verify controlled blocking behavior.

Option 2 should be implemented only if the harness can set timeouts safely and clean up reliably.

### E. Concurrent Same Key, Same Payload

Flow:

- Run two wrapper calls concurrently with the same command and same composite key.
- Use independent sessions and a fake worker coordinated by events.

Allowed second-call outcomes in V1:

- replay after the first transaction completes;
- in-progress conflict while the first execution is still active.

Required assertions:

- Exactly one fake worker call.
- Exactly one attempt row for the composite key.
- No duplicate settlement fields are produced.
- The terminal row is coherent if Session A completes.
- No deadlock or hung task.

### F. Concurrent Same Key, Different Payload

Flow:

- Run two wrapper calls concurrently with the same composite key but different payloads.
- Coordinate so one caller can become the first writer.

Assertions:

- At most one fake worker call.
- Exactly one attempt row.
- The conflicting caller raises `AIJobWorkerMockExecutionFingerprintMismatchError` or maps to route-level `409` if tested through HTTP.
- The persisted row corresponds to the first writer's fingerprint.
- No duplicate settlement fields are produced.

### G. `get_for_update()` Row Lock Behavior

Flow:

- Insert an attempt row.
- Session A calls `get_for_update()` for the row and keeps the transaction open.
- Session B attempts to call `get_for_update()` for the same row.

Assertions:

- Session B does not make a contradictory decision while Session A owns the row lock.
- The test completes under an explicit timeout.
- Cleanup releases any held transaction.

This case may be deferred if the current harness does not expose safe statement timeout controls.

### H. Optional Route-Level Integration

Flow:

- Configure the route with the real wrapper and real attempt repository.
- Use a controlled fake worker dependency.
- Call the internal endpoint twice with the same attempt key.

Assertions:

- The first response returns `replay=False`.
- A terminal retry returns `replay=True` or a safe conflict according to timing.
- A fingerprint mismatch maps to `409`.
- The endpoint remains `internal_api_key` only.
- `organization_id` comes from `TenantContext`.
- `job_id` comes from the path.
- No public endpoint or UI path is involved.

This route-level test may be deferred if dependency override plus real database setup makes the test too broad for the first concurrency phase.

## 10. Worker Policy For Future Tests

The future tests must not call a real renderer, real provider, or external paid service.

Use a controlled fake worker service with these properties:

- It exposes `execute(session, command)`.
- It counts calls.
- It stores received commands for assertions.
- It returns an `AIJobWorkerMockResult` with deterministic fields.
- It can wait on `asyncio.Event` to simulate a slow execution.
- It does not touch ledger, gateway, gate, costing, orchestration, queues, or external APIs.

Recommended fake worker fields:

- `calls: list[AIJobWorkerMockCommand]`
- `worker_entered: asyncio.Event | None`
- `release_worker: asyncio.Event | None`
- `result_factory: Callable[[AIJobWorkerMockCommand], AIJobWorkerMockResult]`

## 11. Ledger And Settlement Policy

These concurrency tests must not require real ledger writes.

Rules:

- The primary assertion is that the wrapper does not call the worker more than once for the same effective key.
- Duplicate settlement prevention is validated indirectly by worker-call count.
- Real ledger settlement idempotency remains a separate future test phase.
- No low-level accounting service imports should be introduced in these tests.
- The fake worker may return `consume_entry_id`, `release_entry_id`, `consumed_credits`, and `released_credits` as plain deterministic values.

## 12. PostgreSQL Risks

Known risks for future tests:

- Concurrent unique-key inserts can block until the first transaction finishes.
- `FOR UPDATE` can block if another transaction holds the row lock.
- A test can deadlock if two sessions wait on each other without timeouts.
- Flaky sleeps can hide real races or create intermittent failures.
- Transaction rollback can remove rows that another session expects to observe.
- Connection pool limits can affect concurrency tests if too small.

Mitigations:

- Use explicit event coordination.
- Use bounded `asyncio.wait_for()` around tasks and event waits.
- Prefer deterministic preinserted rows for in-progress conflict tests.
- Keep transaction scopes short and visible in the test.
- Always release events and close sessions in cleanup paths.
- Verify final row count after all tasks have completed.

## 13. Future Test Location

Recommended future file:

```text
tests/integration/test_ai_job_worker_mock_execution_wrapper_postgres_concurrency.py
```

If the repository has a more specific existing integration layout at implementation time, use that pattern. These tests must not be placed under `tests/unit`.

## 14. Markers And Skip Policy

Future tests must follow the existing PostgreSQL harness pattern.

Rules:

- Use the repository's existing PostgreSQL test configuration helpers.
- Skip clearly when no real PostgreSQL test DSN is configured.
- Do not create fallback storage.
- Do not make CI fail solely because a real PostgreSQL test database is absent, if the current harness policy is skip-safe.
- Do fail fast if a configured DSN is not PostgreSQL or is not explicitly test-safe.

The skip message should make clear that these are real PostgreSQL integration checks.

## 15. Future Validations

When the tests are implemented, the validation set should include:

- The specific PostgreSQL concurrency integration test file.
- Existing wrapper unit tests.
- Existing route unit tests.
- Existing worker mock unit tests.
- Existing attempt repository tests.
- Existing configuration tests.
- Diff whitespace checks.
- Repository guard scripts.
- A focused grep confirming no UI imports and no direct low-level accounting imports in the new tests.

No future validation should require a public endpoint, UI build, real worker queue, external provider, or production-like data.

## 16. Acceptance Criteria For Future Implementation

The future implementation is acceptable only if it demonstrates all of the following:

- One and only one execution can occur for a given `(organization_id, job_id, execution_attempt_id)` key.
- Terminal retry with the same fingerprint returns replay without calling the worker.
- Fingerprint mismatch returns conflict without calling the worker.
- In-progress retry returns conflict without calling the worker in the deterministic baseline case.
- The real PostgreSQL unique constraint is exercised.
- `get_for_update()` is exercised on the replay/conflict path.
- Concurrent same-key calls never produce two attempt rows.
- Concurrent same-key calls never call the worker twice.
- Tests use only PostgreSQL and no alternate backend.
- Tests skip safely when no real PostgreSQL test database is configured.
- Tests do not touch runtime code, model definitions, migrations, public endpoints, UI, or external services.
- Guards pass.

## 17. Roadmap

Recommended follow-up order:

1. Implement PostgreSQL integration tests for the wrapper service with a fake worker.
2. Add deterministic preinserted-row tests for replay, mismatch, and in-progress conflict.
3. Add concurrent same-key tests with independent sessions and event-coordinated fake worker.
4. Add route-level PostgreSQL tests only if dependency override and database setup remain simple.
5. Add stale `in_progress` hardening if product requirements define retry-after-timeout behavior.
6. Add `request_cancel_ai_job` coverage when that feature exists.
7. Add separate real settlement idempotency tests if future phases connect more layers.

## 18. Constraints For Future Authors

Future authors must keep these tests narrow.

- Do not import low-level accounting services.
- Do not instantiate internal sessions inside the wrapper.
- Do not call `commit()` from the wrapper.
- Do not rely on global mutable IDs.
- Do not depend on real worker queues or external services.
- Do not broaden route tests into public API or UI coverage.
- Do not modify allowlists or guard scripts to make these tests pass.
