# CID AI Jobs Worker Mock Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOBS.WORKER.MOCK.CONTRACT.1
Scope: canonical contract for a future backend-controlled mock worker for CID AI Jobs

Companion docs:

- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future contract for a mock async worker for CID AI Jobs.

The mock worker exists to:

- simulate async AI Job execution without connecting to a real AI provider;
- validate the complete create, estimate, check, reserve, execute, consume, release, status, and history cycle;
- support tests and internal beta validation before real workers, queues, and providers are connected;
- exercise accounting settlement boundaries through the existing AI Job orchestration layer.

This phase is documentary only. It does not implement the worker, create endpoints, mutate runtime configuration, alter database models, or connect real providers.

## 2. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `src/services/ai_job_async_orchestration_service.py`
- `src/routes/ai_job_routes.py`
- `src/repositories/ai_job_repository.py`
- `src/services/ai_job_accounting_gateway.py`
- `src/services/ai_job_status_service.py`
- `src/services/ai_job_transition_service.py`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`

Observed relevant behavior:

- route handlers call `AIJobAsyncOrchestrationService` rather than low-level credit services;
- consume and release HTTP endpoints are internal-only in route policy;
- repository reads and mutation loads require `organization_id` plus `job_id`;
- repository mutation loads use `get_for_update(organization_id, job_id)`;
- repository does not expose a global `get(job_id)` contract;
- orchestration settlement methods require `reservation_entry_id` from the persisted job;
- gateway idempotency key shape is `ai_job:{organization_id}:{job_id}:{action}[:caller_key]`;
- gateway is the adapter to credit services and must receive the shared `AsyncSession` from above;
- orchestration currently exposes consume and release methods, but does not yet expose worker-specific execution transitions.

## 3. Scope

The future mock worker is in scope only as a backend-controlled execution simulator.

In scope:

- a backend service or use-case layer that receives a tenant-scoped worker command;
- simulated success, failure, and cancellation execution modes;
- orchestration-driven consume and release settlement;
- deterministic mock output and mock error metadata;
- tests that verify lifecycle, accounting, idempotency, and tenant isolation;
- optional internal/admin trigger in a future phase, if explicitly authorized.

Out of immediate implementation scope for this contract phase:

- real worker process;
- real async queue;
- real provider adapter;
- public API trigger;
- frontend integration.

## 4. Non-Scope

The mock worker must not:

- process real images;
- generate real assets;
- consume GPU capacity;
- call ComfyUI runtime;
- call OpenAI, Anthropic, Ollama, or any other AI provider;
- integrate Stripe, checkout, billing purchase flows, or payment flows;
- create or modify Alembic migrations;
- create or modify database models;
- mutate runtime configuration;
- act as a substitute for a real provider result contract.

## 5. Canonical Job States

The following status names were audited as canonical in the current status service:

- `created`
- `estimated`
- `credit_checked`
- `reserved`
- `queued`
- `running`
- `succeeded`
- `partial_succeeded`
- `failed`
- `cancel_requested`
- `cancelled`
- `consume_pending`
- `consumed`
- `release_pending`
- `released`
- `retry_pending`
- `expired`

Accounting terminal states currently audited:

- `consumed`
- `released`

Execution states currently audited:

- `queued`
- `running`
- `succeeded`
- `partial_succeeded`
- `failed`
- `cancel_requested`
- `cancelled`

Important naming rule:

- `finished` and `completed` are not currently canonical job statuses.
- `finished_at` is a timestamp field used for `succeeded`, `partial_succeeded`, and `failed` transitions.
- Any future use of `finished` or `completed` as a status requires an explicit status-contract update before implementation.

Future required implementation gap:

- The current orchestration service settles directly from the job's current status into `consumed` or `released` through transition validation.
- A mock worker implementation must add or use explicit orchestration methods for execution transitions such as `reserved -> queued`, `queued -> running`, `running -> succeeded`, `running -> failed`, `cancel_requested -> cancelled`, `succeeded -> consume_pending -> consumed`, and `failed/cancelled/expired -> release_pending -> released`.
- The worker contract must not silently mutate `AIJob.status` outside transition validation.

## 6. High-Level Worker Responsibility

The mock worker owns simulated execution only.

It may:

- load a tenant-scoped job through the orchestration or repository boundary defined for worker execution;
- validate that the job has an existing reservation before execution settlement;
- mark simulated execution progress using canonical lifecycle transitions once the future service surface exists;
- attach mock output or mock error metadata to the job metadata if the future implementation explicitly defines that write;
- call `AIJobAsyncOrchestrationService.consume_ai_job_credits(...)` for success settlement;
- call `AIJobAsyncOrchestrationService.release_ai_job_credits(...)` for failure, cancellation, expiration, or cleanup settlement.

It must not:

- call `CreditLedgerService` directly;
- call `CreditGateService` directly;
- calculate arbitrary credits from worker inputs;
- accept `reservation_entry_id` from the command as authority;
- mutate jobs across tenants;
- bypass lifecycle transition validation;
- create its own database session;
- commit internally.

## 7. Happy Path: Simulated Success

Required conceptual flow:

1. Receive `AIJobWorkerMockCommand` with `organization_id`, `job_id`, `execution_attempt_id`, and `mode="success"`.
2. Validate caller is internal/S2S or admin-internal according to future trigger policy.
3. Load the job tenant-safe using `organization_id` plus `job_id`; never use a global `job_id` lookup.
4. Lock the job row for mutation through the repository/orchestration mutation path.
5. Validate the job belongs to `organization_id` and has `reservation_entry_id` persisted.
6. Validate the current status permits mock execution.
7. Transition the job to `queued` if the job is still in `reserved` and queueing is modeled in the future service surface.
8. Transition the job to `running` when simulated execution starts.
9. Optionally wait for `simulated_duration_ms` without blocking critical production resources.
10. Transition the job to `succeeded` when the simulated result is OK.
11. Persist `mock_output_metadata` under a namespaced metadata key such as `mock_worker.output`, if defined by the implementation phase.
12. Call `AIJobAsyncOrchestrationService.consume_ai_job_credits(...)` with `organization_id`, `job_id`, `actual_credits` from trusted policy, and `caller_key=execution_attempt_id` or a derived caller key.
13. Persist `consume_entry_id`, `consumed_credits`, status, and timestamps through existing orchestration and repository boundaries.

Credit rule:

- The mock worker must not compute arbitrary credit amounts from untrusted command data.
- If `actual_credits` is needed, the value must come from an internal policy defined by the future implementation, normally bounded by the persisted reservation or estimate.
- Frontend callers must never supply settlement amounts.

## 8. Failure Path: Simulated Error

Required conceptual flow:

1. Receive `AIJobWorkerMockCommand` with `organization_id`, `job_id`, `execution_attempt_id`, and `mode="failure"`.
2. Validate caller is internal/S2S or admin-internal according to future trigger policy.
3. Load and lock the job tenant-safe using `organization_id` plus `job_id`.
4. Validate the job has a persisted `reservation_entry_id`.
5. Validate the current status permits mock execution or failure settlement.
6. Transition to `queued` and `running` if those lifecycle boundaries are part of the simulated path.
7. Transition the job to `failed` when the simulated error occurs.
8. Persist mock error metadata under a namespaced metadata key such as `mock_worker.error`, including `mock_error_code` and safe `mock_error_message` if defined by the implementation phase.
9. Call `AIJobAsyncOrchestrationService.release_ai_job_credits(...)` with `organization_id`, `job_id`, `release_credits` from trusted policy, and `caller_key=execution_attempt_id` or a derived caller key.
10. Persist `release_entry_id`, `released_credits`, status, and timestamps through existing orchestration and repository boundaries.

Failure settlement rule:

- A simulated failure must not leave credits reserved indefinitely.
- If release fails due to a transient accounting error, the future implementation must leave the job in a state that is visible for retry or operator intervention, such as `release_pending`, without double-releasing on retry.

## 9. Cancellation Path

Cancellation applies only if future worker implementation authorizes a cancel command or consumes an already-cancelled state.

Cancellation before execution:

- If a reserved job is cancelled before `running`, transition through `cancel_requested` and `cancelled` if required by transition service.
- Release the reservation through `AIJobAsyncOrchestrationService.release_ai_job_credits(...)`.
- Use the same `execution_attempt_id` or cancel-specific caller key for idempotent release.

Cancellation during mock execution:

- If a job is already `running`, the cancel command must not interrupt real provider work because no real provider exists in mock mode.
- The mock worker may mark `cancel_requested`, then `cancelled`, then settle with release if the transition path is valid.
- If the mock work has already settled as `consumed` or `released`, cancellation must be rejected as too late or treated as an idempotent no-op only if the future contract explicitly defines that behavior.

Cancellation safety:

- Release is required when a reservation exists and the job does not consume credits.
- Release must use the persisted `reservation_entry_id` from the job.
- Double release must be blocked by idempotency and reservation-linkage validation.

## 10. Tenant-Safe Rules

Mandatory rules:

- `organization_id` is required on every worker command.
- `job_id` is never used without `organization_id`.
- No global `get(job_id)` is permitted.
- The worker must not accept `organization_id` from public frontend input.
- The worker must not mutate jobs cross-tenant.
- A job loaded for one `organization_id` must return not found or forbidden if a command references another tenant.
- All read and mutation queries must include `AIJob.organization_id == organization_id` at the persistence boundary.
- Mutation paths must use row locking equivalent to the existing `get_for_update(organization_id, job_id)` pattern.

## 11. Accounting Rules

Mandatory rules:

- The worker must not call `CreditLedgerService` directly.
- The worker must not call `CreditGateService` directly.
- The worker must not call `AIJobCostingService` directly for settlement.
- The worker must use `AIJobAsyncOrchestrationService` for consume and release.
- `reservation_entry_id` must come from the persisted tenant-scoped job.
- `consume` and `release` must respect tenant-safe idempotency.
- Double consume and double release must be blocked.
- Consume after full release must fail.
- Release after full consume must fail unless a future documented partial-settlement policy permits releasing a surplus.
- Partial settlement must follow `cid_ai_job_accounting_gateway_async_contract_v1.md` and `cid_ai_job_reservation_linkage_contract_v1.md`; it must not be implicitly enabled by the mock worker.

Current known accounting gap:

- Tenant-scoped ledger idempotency is contractually required, but the ledger model evolution is tracked separately.
- The mock worker implementation must not claim full ledger-level tenant-safe idempotency until that phase lands.

## 12. Idempotency Contract

Every worker command must carry a stable idempotency discriminator.

Required command field:

- `execution_attempt_id`

Allowed settlement caller key:

- `caller_key=execution_attempt_id`
- or a deterministic derived key such as `mock:{execution_attempt_id}:consume` and `mock:{execution_attempt_id}:release`

Rules:

- Retrying the same worker command must not duplicate consume or release ledger entries.
- Retrying success after success must return the already settled result or fail safely without duplicate settlement.
- Retrying failure after failure must return the already released result or fail safely without duplicate settlement.
- Retrying success after release must fail as a conflicting settlement.
- Retrying failure after consume must fail as a conflicting settlement.
- Reusing one `execution_attempt_id` for a different job or tenant must be rejected.
- The implementation must store enough metadata to compare replay payloads safely.

## 13. Future Command Model

Conceptual dataclass or schema:

```python
class AIJobWorkerMockCommand:
    organization_id: str
    job_id: str
    requested_by: str
    execution_attempt_id: str
    mode: Literal["success", "failure", "cancel"]
    simulated_duration_ms: int | None = None
    mock_output_metadata: dict[str, Any] | None = None
    mock_error_code: str | None = None
    mock_error_message: str | None = None
```

Field rules:

- `organization_id` is mandatory and must come from trusted internal context.
- `job_id` is mandatory and must be tenant-scoped.
- `requested_by` identifies internal actor, admin, worker id, or test harness.
- `execution_attempt_id` is mandatory for idempotency.
- `mode` is one of `success`, `failure`, or `cancel`.
- `simulated_duration_ms` is optional, bounded, and must not block request workers in production paths.
- `mock_output_metadata` must be JSON-safe, size-limited, and namespaced.
- `mock_error_code` and `mock_error_message` must be safe for logs and API history; no secrets or provider internals.

## 14. Future Result Model

Conceptual dataclass or schema:

```python
class AIJobWorkerMockResult:
    job_id: str
    organization_id: str
    status: str
    consumed_credits: int | None
    released_credits: int | None
    consume_entry_id: str | None
    release_entry_id: str | None
    output_metadata: dict[str, Any] | None
    error_metadata: dict[str, Any] | None
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    cancelled_at: datetime | None
    consumed_at: datetime | None
    released_at: datetime | None
```

Result rules:

- `job_id` and `organization_id` are always present.
- `status` must be one of the canonical statuses.
- Success settlement returns `consume_entry_id` and `consumed_credits` when consumption is completed.
- Failure and cancellation settlement return `release_entry_id` and `released_credits` when release is completed.
- Metadata must be safe to expose through internal diagnostics and safe subsets of history.
- Timestamps must reflect canonical transition timestamp fields.

## 15. Security Requirements

Mandatory security rules:

- The mock worker is internal/S2S only.
- No public frontend endpoint may execute mock worker commands.
- Existing consume and release paths remain internal-only.
- If a manual trigger is exposed later, it must be admin/internal only.
- Manual trigger requests must not accept arbitrary tenant impersonation from public callers.
- Worker commands must be auditable by `requested_by`, `organization_id`, `job_id`, and `execution_attempt_id`.
- Error metadata must not include secrets, tokens, credentials, raw provider payloads, or private runtime artifacts.
- The worker must preserve tenant isolation even in admin-triggered paths.

## 16. Transaction and Session Contract

The future implementation must follow the current async session rules:

- `AsyncSession` is received from the caller above the worker service.
- The worker service does not instantiate its own session.
- The worker service does not use `AsyncSessionLocal`.
- The worker service does not call `commit()` internally.
- Repository, orchestration, gateway, and ledger share the same session for one business operation.
- Repository mutation loads use row locking.
- Flush may happen inside repository/gateway boundaries where existing contracts permit it.
- Transaction ownership remains with the outer use-case, route, task runner, or test harness.

Recommended atomic sequence for one worker settlement:

1. validate command and caller;
2. open or receive shared async session from the outer layer;
3. load tenant-scoped job for update;
4. validate status and reservation linkage;
5. apply execution transition metadata through orchestration-approved methods;
6. call consume or release through `AIJobAsyncOrchestrationService`;
7. persist job metadata and ledger ids through repository save/flush;
8. commit outside the worker service.

## 17. History and Status Contract

The mock worker must make execution visible through existing read surfaces.

Required future behavior:

- `GET /api/v1/ai-jobs/{job_id}` shows the latest canonical status.
- `GET /api/v1/ai-jobs/{job_id}/history` reflects mock execution timestamps where available.
- History entries use existing timestamp fields: `queued_at`, `started_at`, `finished_at`, `cancel_requested_at`, `cancelled_at`, `consume_pending_at`, `consumed_at`, `release_pending_at`, and `released_at`.
- Mock metadata is namespaced so it does not overwrite accounting fields.

Future gap:

- The current history implementation derives events from timestamp fields on `AIJob`; a richer event table is not part of this phase.
- If future worker requirements need detailed per-attempt logs, define a separate event/audit contract before adding storage.

## 18. Future Test Requirements

Future implementation must include tests proving:

- happy path consumes one existing reservation;
- failure path releases one existing reservation;
- cancel before execution releases safely when a reservation exists;
- cancel during mock execution releases safely when no consumption occurred;
- idempotent retry does not duplicate consume settlement;
- idempotent retry does not duplicate release settlement;
- success after release is blocked;
- failure after consume is blocked;
- cross-tenant worker command is blocked;
- missing reservation is blocked;
- non-internal caller is blocked;
- worker does not call `CreditLedgerService` directly;
- worker does not call `CreditGateService` directly;
- worker does not use `AsyncSessionLocal`;
- worker does not call `commit()` internally;
- status and history reflect mock queued, running, success, failure, cancellation, consume, and release transitions;
- mock output metadata is persisted only on success paths;
- mock error metadata is persisted only on failure or cancellation paths;
- no real provider, ComfyUI runtime, GPU, payment, or frontend integration is triggered.

Recommended test layers:

- unit tests with fake repository, orchestration, and gateway boundaries;
- route tests only if a future internal/admin trigger endpoint is explicitly added;
- PostgreSQL integration tests if a future phase authorizes database-backed worker execution validation.

## 19. Roadmap After This Contract

Recommended order:

1. Implement `AIJobWorkerMockCommand` and `AIJobWorkerMockResult` schemas or dataclasses.
2. Implement backend-only mock worker service with fake execution modes.
3. Add orchestration methods for execution transitions if missing.
4. Add unit tests for happy path, failure path, cancellation, idempotency, and tenant isolation.
5. Add an optional internal/admin trigger endpoint only if explicitly scoped.
6. Add PostgreSQL integration tests if operationally approved.
7. Implement real worker process after mock worker behavior is stable.
8. Add real queue integration after worker process semantics are stable.
9. Add real provider adapters after accounting and lifecycle contracts are validated.
10. Connect Command Center or frontend read-only surfaces after backend worker behavior is stable.

## 20. Acceptance Criteria for Future Implementation

The future mock worker implementation is acceptable only when:

- it is backend-controlled and internal/S2S only;
- it never calls real AI providers;
- it never calls ComfyUI runtime;
- it never bypasses tenant-scoped job lookup;
- it never bypasses `AIJobAsyncOrchestrationService` for consume or release;
- it never calls low-level credit services directly;
- it preserves idempotency under worker retries;
- it blocks double settlement;
- it releases reserved credits after failure or cancellation;
- it exposes status and history through existing tenant-safe read surfaces;
- all required tests pass without real provider connections.
