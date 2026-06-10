# CID AI Job Worker Mock Execution Wrapper Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOB.WORKER.MOCK.EXECUTION.WRAPPER.CONTRACT.1
Scope: canonical contract for the future `AIJobWorkerMockExecutionService` idempotency wrapper

Companion docs:

- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md`
- `docs/architecture/cid_ai_job_execution_attempt_model_repository_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future contract for `AIJobWorkerMockExecutionService`, a wrapper service that will apply persistent idempotency by `execution_attempt_id` before delegating to `AIJobWorkerMockService`.

The wrapper exists to:

- protect the internal mock worker trigger from duplicate retries;
- decide whether a request is a first execution, terminal replay, conflict, or already in progress;
- persist and update `AIJobExecutionAttempt` records through `AIJobExecutionAttemptRepository`;
- call `AIJobWorkerMockService` only when the request is the first valid execution for the attempt key;
- prevent duplicate worker execution, duplicate consume settlement, and duplicate release settlement;
- keep retry behavior deterministic, tenant-safe, and auditable.

This phase is documentary only. It does not create the wrapper service, update dependencies, update routes, modify the worker mock, or add runtime tests.

## 2. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md`
- `docs/architecture/cid_ai_job_execution_attempt_model_repository_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `src/models/ai_job_execution_attempt.py`
- `src/repositories/ai_job_execution_attempt_repository.py`
- `src/services/ai_job_worker_mock_service.py`
- `src/routes/internal_ai_job_worker_mock_routes.py`
- `src/schemas/ai_job_worker_mock_api_schema.py`
- `src/dependencies/ai_job_worker_mock.py`
- `src/services/ai_job_async_orchestration_service.py`

Observed relevant facts:

- The current internal trigger route calls `AIJobWorkerMockService.execute(db, command)` directly.
- `AIJobWorkerMockService` is intentionally stateless and passes `execution_attempt_id` as settlement `caller_key`.
- `AIJobWorkerMockService` composes `AIJobAsyncOrchestrationService`; it does not call low-level credit services directly.
- `AIJobExecutionAttempt` now exists as a dedicated table-backed ORM model.
- `AIJobExecutionAttemptRepository` exposes tenant-scoped methods: `create`, `get`, `get_for_update`, `save`, `find_by_key`, and `list_for_job`.
- `AIJobExecutionAttemptRepository.create()` flushes and does not catch unique constraint errors; the future wrapper must interpret first-writer conflicts.
- `AIJobExecutionAttemptRepository.get_for_update()` uses PostgreSQL row locking.
- The trigger request schema forbids extra fields and does not accept `organization_id` or `requested_by` from the body.
- The trigger route derives `organization_id` from `TenantContext` and `requested_by` from `tenant.user_id` or `internal_trigger`.
- `AIJobAsyncOrchestrationService` remains the authority for job transitions and settlement entry linkage.

## 3. Relationship with Existing Pieces

### 3.1 Internal Trigger

The current internal trigger is the HTTP entry point:

- `POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute`
- `include_in_schema=False`
- `auth_method == "internal_api_key"` only

Today it calls the worker mock directly. In the future implementation phase, it must call the wrapper instead.

### 3.2 Worker Mock Service

`AIJobWorkerMockService` remains stateless. It owns simulated execution only:

- success flow: enqueue, start, succeed, mark consume pending, consume;
- failure flow: enqueue, start, fail, mark release pending, release;
- cancel flow: cancel, mark release pending, release for already `cancel_requested` jobs.

The wrapper must not move execution transition logic out of the worker mock. The wrapper decides whether execution is allowed and records the attempt state around the worker call.

### 3.3 Attempt Repository

`AIJobExecutionAttemptRepository` persists and locks attempt records. It does not decide replay, conflict, or HTTP behavior.

The wrapper is responsible for:

- computing fingerprints;
- inserting attempts;
- interpreting unique constraint errors;
- comparing stored fingerprints;
- deciding replay, conflict, or in-progress responses;
- updating attempt records after worker execution.

### 3.4 Orchestration and Ledger

`AIJobAsyncOrchestrationService` remains the authority for AI Job lifecycle transitions and settlement linkage. The ledger remains the accounting authority.

The attempt store does not replace ledger idempotency. It prevents duplicate execution before settlement. Ledger idempotency remains a second line of defense during consume or release settlement.

## 4. Scope

In scope for this contract:

- future wrapper service name and location;
- dependencies and session ownership rules;
- public service surface;
- fingerprint contract;
- first execution flow;
- unique conflict, replay, in-progress, and invalid-state flows;
- replay result shape;
- error classes and future HTTP mapping;
- transaction and concurrency rules;
- future route and dependency integration rules;
- future test requirements and acceptance criteria.

## 5. Non-Scope

This contract does not:

- create `AIJobWorkerMockExecutionService` in code;
- modify the internal trigger route;
- modify dependency wiring;
- modify `AIJobWorkerMockService`;
- modify `AIJobExecutionAttempt`, its migration, or its repository;
- modify orchestration, accounting gateway, ledger, or costing services;
- create runtime tests;
- connect a real queue;
- connect a real provider;
- touch frontend, Docker, Stripe, checkout, ComfyUI runtime, or runtime configuration.

## 6. Future Name and Location

Recommended service:

```python
AIJobWorkerMockExecutionService
```

Recommended future file:

```text
src/services/ai_job_worker_mock_execution_service.py
```

The service should be implemented as a thin orchestration wrapper around `AIJobWorkerMockService`, not as a replacement for it.

## 7. Future Dependencies

Required constructor dependencies:

```python
class AIJobWorkerMockExecutionService:
    def __init__(
        self,
        *,
        worker_service: AIJobWorkerMockService,
        attempt_repository: AIJobExecutionAttemptRepository,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None: ...
```

Rules:

- `AsyncSession` is received by the public `execute(...)` method from the route or use-case layer.
- The wrapper does not instantiate a session.
- The wrapper does not use `AsyncSessionLocal`.
- The wrapper does not call `commit()`.
- The wrapper may rely on repository `flush()` behavior to detect unique constraint conflicts.
- The wrapper does not import or call low-level ledger, gate, gateway, or costing services directly.
- The wrapper delegates execution only to `AIJobWorkerMockService`.

## 8. Public Service Surface

### 8.1 Result Type Decision

The wrapper should return an enriched wrapper result rather than returning `AIJobWorkerMockResult` directly. This keeps replay metadata explicit while preserving the worker result payload.

Recommended dataclass:

```python
@dataclass(frozen=True)
class AIJobWorkerMockExecutionResult:
    result: AIJobWorkerMockResult
    replay: bool
    attempt_status: str
    execution_attempt_id: str
    fingerprint_version: str = "v1"
```

Rationale:

- First execution can return `replay=False` with the worker result.
- Terminal replay can return `replay=True` with a result reconstructed from the stored attempt.
- The future route can still map `result` to the existing response schema while optionally adding replay metadata in a later schema phase.

### 8.2 Optional Replay Result Type

An additional internal type may be useful for replay reconstruction:

```python
@dataclass(frozen=True)
class AIJobWorkerMockExecutionReplayResult:
    organization_id: str
    job_id: str
    execution_attempt_id: str
    mode: str
    result_status: str
    consumed_credits: int | None
    released_credits: int | None
    consume_entry_id: str | None
    release_entry_id: str | None
    replay: bool = True
```

This type is optional. V1 may reconstruct `AIJobWorkerMockResult` directly and wrap it in `AIJobWorkerMockExecutionResult`.

### 8.3 Main Method

```python
async def execute(
    self,
    session: AsyncSession,
    command: AIJobWorkerMockCommand,
) -> AIJobWorkerMockExecutionResult: ...
```

The method must not mutate route state directly. It returns a typed result or raises a typed error.

## 9. Future Errors

Recommended hierarchy:

```python
class AIJobWorkerMockExecutionError(Exception): ...

class AIJobWorkerMockExecutionConflictError(AIJobWorkerMockExecutionError): ...

class AIJobWorkerMockExecutionInProgressError(AIJobWorkerMockExecutionConflictError): ...

class AIJobWorkerMockExecutionFingerprintMismatchError(AIJobWorkerMockExecutionConflictError): ...

class AIJobWorkerMockExecutionReplayError(AIJobWorkerMockExecutionError): ...

class AIJobWorkerMockExecutionInvalidStateError(AIJobWorkerMockExecutionConflictError): ...
```

Rules:

- Fingerprint mismatch is a conflict.
- In-progress replay is a conflict in V1.
- Unknown attempt status is an invalid state.
- Unexpected repository failures should be wrapped or propagated as service errors.
- Worker mock errors remain worker errors and should be mapped by the route as they are today, unless the implementation phase defines a more specific wrapper mapping.

## 10. Fingerprint Contract

Future function:

```python
def compute_execution_attempt_fingerprint(command: AIJobWorkerMockCommand) -> str: ...
```

### 10.1 Included Fields

The fingerprint is SHA-256 over canonical JSON for:

- `mode`
- `simulated_duration_ms`
- `mock_output_metadata`
- `mock_error_code`
- `mock_error_message`
- `actual_credits`
- `release_credits`

### 10.2 Excluded Fields

The following fields are excluded:

- `organization_id` (part of tenant-scoped key)
- `job_id` (part of tenant-scoped key)
- `execution_attempt_id` (part of tenant-scoped key)
- `requested_by` (audit actor, not semantic payload)
- timestamps

### 10.3 Canonical JSON Rules

The fingerprint payload must be deterministic:

- sort keys at every object level;
- compact separators;
- ASCII-safe encoding;
- omit `None` values;
- preserve integers as numbers;
- do not include raw request bodies or secrets.

Pseudocode:

```python
payload = {
    "mode": command.mode,
    "simulated_duration_ms": command.simulated_duration_ms,
    "mock_output_metadata": command.mock_output_metadata,
    "mock_error_code": command.mock_error_code,
    "mock_error_message": command.mock_error_message,
    "actual_credits": command.actual_credits,
    "release_credits": command.release_credits,
}
payload = {key: value for key, value in payload.items() if value is not None}
canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

Fingerprint version for V1: `v1`.

## 11. First Execution Flow

Required sequence:

1. Receive `session` and `AIJobWorkerMockCommand` from the caller.
2. Validate command enough to compute a deterministic fingerprint or rely on worker validation if the route schema has already validated the command.
3. Compute `fingerprint` using version `v1`.
4. Create `AIJobExecutionAttempt` with:
   - `organization_id`
   - `job_id`
   - `execution_attempt_id`
   - `mode`
   - `status="in_progress"`
   - `fingerprint`
   - `fingerprint_version="v1"`
   - `requested_by`
   - `started_at`
5. Call `attempt_repository.create(attempt)`.
6. If create/flush succeeds, call `worker_service.execute(session, command)` exactly once.
7. Map the worker result to the attempt record:
   - `mode="success"` -> `status="succeeded"`
   - `mode="failure"` -> `status="failed"`
   - `mode="cancel"` -> `status="cancelled"`
   - `result_status=result.status`
   - `consume_entry_id=result.consume_entry_id`
   - `release_entry_id=result.release_entry_id`
   - `consumed_credits=result.consumed_credits`
   - `released_credits=result.released_credits`
   - `finished_at=now`
8. Call `attempt_repository.save(attempt)`.
9. Return `AIJobWorkerMockExecutionResult(result=result, replay=False, ...)`.

The wrapper must not commit. Commit remains owned by the route, use-case, task runner, or test harness.

## 12. Unique Conflict, Replay, and In-Progress Flow

If `attempt_repository.create(attempt)` raises an integrity error caused by the unique attempt constraint:

1. Load the existing attempt with `attempt_repository.get_for_update(organization_id, job_id, execution_attempt_id)`.
2. If no existing attempt is found, raise `AIJobWorkerMockExecutionReplayError` because the unique conflict cannot be reconciled.
3. Compare stored `fingerprint` and `fingerprint_version` with the incoming fingerprint.
4. If fingerprint differs, raise `AIJobWorkerMockExecutionFingerprintMismatchError`.
5. If fingerprint matches and status is terminal, return replay from the stored attempt.
6. If fingerprint matches and status is `in_progress`, raise `AIJobWorkerMockExecutionInProgressError` in V1.
7. If status is unknown, raise `AIJobWorkerMockExecutionInvalidStateError`.

The wrapper must not call `AIJobWorkerMockService` on replay, fingerprint mismatch, in-progress conflict, or invalid state.

## 13. Replay Result Reconstruction

Replay is reconstructed from `AIJobExecutionAttempt`, not from the worker or orchestration layer.

Minimum replay fields:

- `organization_id`
- `job_id`
- `execution_attempt_id`
- `mode`
- `status` / `result_status`
- `consumed_credits`
- `released_credits`
- `consume_entry_id`
- `release_entry_id`
- `replay=True`

Recommended reconstruction:

```python
result = AIJobWorkerMockResult(
    organization_id=attempt.organization_id,
    job_id=attempt.job_id,
    mode=attempt.mode,
    status=attempt.result_status or attempt.status,
    consumed_credits=attempt.consumed_credits,
    released_credits=attempt.released_credits,
    consume_entry_id=attempt.consume_entry_id,
    release_entry_id=attempt.release_entry_id,
    output_metadata=safe_output_metadata,
    error_metadata=safe_error_metadata,
)
```

Metadata for replay should be minimal and safe. V1 may omit output/error metadata from replay if it is not stored on the attempt record.

## 14. Future HTTP Mapping

The future route integration should map wrapper errors as follows:

| Condition | Future HTTP status | Notes |
|---|---:|---|
| Fingerprint mismatch | 409 | Same key, different payload |
| In progress | 409 | Existing attempt not terminal |
| Invalid attempt state | 409 | Stored status unsupported |
| Replay reconstruction failure | 500 | Internal consistency problem |
| Repository unexpected error | 500 | Non-leaking service error |
| Worker mock validation error | 400 | Preserve current mapping where possible |
| Worker mock settlement error | 409 | Preserve current mapping where possible |
| Tenant-scoped not found | 404 | Preserve not-found behavior |
| Orchestration invalid state | 409 | Preserve current mapping |

Normal terminal replay should return `200 OK`.

## 15. Error Handling and Attempt Status Policy

### 15.1 Atomicity First

For V1, prefer full transaction atomicity:

- attempt insert;
- worker execution;
- job transitions;
- settlement;
- attempt update.

All of these should commit or roll back together. If the surrounding transaction rolls back, no attempt record remains.

### 15.2 Worker Errors

If the worker raises before settlement or during settlement, V1 should allow the outer transaction to roll back unless the implementation phase explicitly chooses to persist a terminal conflict.

Recommended V1 behavior:

- expected validation errors before worker side effects -> rollback, no persisted attempt;
- expected idempotency conflicts before worker call -> no worker call, no settlement;
- worker/settlement errors after first insert -> rollback whole transaction;
- do not persist partial state unless a later contract defines durable failure audit.

### 15.3 Stale In-Progress Attempts

Stale `in_progress` cleanup is out of scope for V1. It requires a separate operational policy for timeout, retry, and dead-letter behavior.

## 16. Transactions

Rules:

- `AsyncSession` is shared across wrapper, attempt repository, worker mock, orchestration, gateway, and ledger boundaries.
- The wrapper does not create or close sessions.
- The wrapper does not call `commit()`.
- The route/use-case/task runner owns commit/rollback.
- Insert-first with the unique constraint is the first-writer mechanism.
- `get_for_update` is required on replay path before making replay/conflict decisions.
- No fallback or dialect branching is permitted for locking behavior.

## 17. Concurrency

Two simultaneous calls with the same `(organization_id, job_id, execution_attempt_id)` must behave as follows:

1. One request inserts the attempt and proceeds to execute.
2. The other request encounters a unique constraint conflict and enters replay/conflict handling.
3. If the first request is still `in_progress`, the second request receives an in-progress conflict.
4. If the first request has completed and committed, the second request replays if the fingerprint matches.
5. If the fingerprint differs, the second request receives a fingerprint conflict.

The foundation is PostgreSQL unique constraint enforcement plus row locking on replay. Real concurrent integration tests are deferred to a later phase.

## 18. Future Route Integration

Future `internal_ai_job_worker_mock_routes.py` changes must:

- inject `AIJobWorkerMockExecutionService` instead of `AIJobWorkerMockService` directly;
- keep `internal_api_key` only;
- keep `include_in_schema=False`;
- keep `organization_id` derived from `TenantContext`;
- keep `requested_by` derived from `tenant.user_id` or `internal_trigger`;
- keep request body `extra="forbid"`;
- keep the endpoint off public frontend surfaces;
- map wrapper result to the internal response schema.

The route integration phase must update route tests to prove that the wrapper is called and the worker is not injected directly into the route handler.

## 19. Future Dependency Integration

Recommended dependency factory:

```python
def get_ai_job_worker_mock_execution_service(
    db: AsyncSession = Depends(get_db),
    worker_service: AIJobWorkerMockService = Depends(get_ai_job_worker_mock_service),
) -> AIJobWorkerMockExecutionService:
    attempt_repository = AIJobExecutionAttemptRepository(db)
    return AIJobWorkerMockExecutionService(
        worker_service=worker_service,
        attempt_repository=attempt_repository,
    )
```

Rules:

- The repository must receive the same route `AsyncSession` used by the worker path.
- The dependency must not open an independent session.
- The dependency must not commit.
- The dependency must not import low-level accounting services.

## 20. Future Tests

### 20.1 Unit Wrapper Tests

Future wrapper tests must prove:

- first execution creates attempt and calls worker once;
- successful result marks attempt `succeeded`;
- failure mode marks attempt `failed`;
- cancel mode marks attempt `cancelled`;
- terminal replay with same fingerprint returns stored result and does not call worker;
- fingerprint mismatch raises conflict and does not call worker;
- `in_progress` raises conflict and does not call worker;
- unique constraint integrity error triggers replay path;
- unexpected integrity errors are not swallowed;
- worker error handling follows the atomicity policy;
- wrapper does not call `commit()`;
- wrapper does not use `AsyncSessionLocal`;
- wrapper does not directly import or call ledger, gate, gateway, or costing services.

### 20.2 Route Integration Tests

Route integration tests belong to the future route phase. They must prove:

- route calls wrapper, not worker directly;
- terminal replay maps to `200 OK`;
- fingerprint conflict maps to `409`;
- in-progress conflict maps to `409`;
- internal-only policy remains enforced;
- normal JWT callers remain rejected;
- no frontend files are touched.

### 20.3 PostgreSQL Integration Tests

Later integration tests must prove:

- concurrent insert: exactly one first execution wins;
- same payload either replays or receives in-progress conflict according to timing;
- different payload conflicts;
- no duplicate consume settlement;
- no duplicate release settlement.

## 21. Acceptance Criteria for Future Implementation

The future wrapper implementation is acceptable only when:

- `AIJobWorkerMockExecutionService` exists and is covered by unit tests;
- first execution creates an attempt before calling the worker;
- terminal replay never calls the worker;
- fingerprint mismatch never calls the worker;
- in-progress retry never calls the worker in V1;
- attempt update captures result status, settlement ids, credits, and finish timestamp;
- wrapper path cannot duplicate consume or release settlement;
- wrapper does not own session lifecycle or commit;
- wrapper has no direct low-level accounting imports;
- existing worker mock tests still pass;
- route tests are updated only in the route integration phase.

## 22. Roadmap

Recommended order:

1. This contract.
2. Implement `AIJobWorkerMockExecutionService` and fingerprint helper.
3. Add wrapper unit tests.
4. Add dependency factory `get_ai_job_worker_mock_execution_service`.
5. Update internal trigger route to use the wrapper.
6. Update route tests for replay/conflict/in-progress behavior.
7. Add PostgreSQL concurrency tests.
8. Add `request_cancel` orchestration in a separate phase if needed.
9. Add real queue, worker process, and provider adapters in later phases.

## 23. Pending Risks

- Stale `in_progress` attempts need a future cleanup/retry policy.
- Replay metadata is minimal in V1 unless stored explicitly on the attempt record.
- Real concurrent behavior still requires PostgreSQL integration tests.
- The trigger still calls the worker directly until the future route integration phase.
