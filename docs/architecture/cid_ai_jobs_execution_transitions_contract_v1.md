# CID AI Jobs Execution Transitions Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOBS.EXECUTION.TRANSITIONS.CONTRACT.1
Scope: canonical contract for future AI Job execution lifecycle transitions

Companion docs:

- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines how future execution transitions must be added to CID AI Jobs.

The contract exists to:

- define safe execution lifecycle transitions after credit reservation;
- prevent workers, endpoints, provider adapters, or external services from mutating `AIJob.status` directly;
- prepare the implementation of the mock worker and then the real worker;
- keep execution status changes tenant-safe, locked, timestamped, and auditable;
- keep accounting settlement through the existing AI Job orchestration and gateway boundaries.

This phase is documentary only. It does not implement orchestration methods, workers, endpoints, queues, provider adapters, models, migrations, or runtime behavior.

## 2. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `src/services/ai_job_async_orchestration_service.py`
- `src/services/ai_job_status_service.py`
- `src/services/ai_job_transition_service.py`
- `src/models/ai_job.py`
- `src/repositories/ai_job_repository.py`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`

Observed current implementation facts:

- `AIJobAsyncOrchestrationService` currently implements create, estimate, check, reserve, consume, release, read, list, and history methods.
- Worker-specific execution transition methods do not currently exist.
- Current settlement methods call `_load_job_for_mutation(organization_id, job_id)` and use repository `get_for_update(organization_id, job_id)`.
- Current transition application uses `build_ai_job_transition_plan(from_status, to_status)` before `_apply_transition(...)` mutates status and timestamps.
- `AIJobRepository` exposes tenant-scoped `get`, `get_for_update`, `list_for_organization`, and `find_by_idempotency_key`; it does not expose global `get(job_id)`.
- `AIJobRepository.save(...)` may flush and must not commit.
- `AIJob` currently includes `queued_at`, `started_at`, `finished_at`, `cancel_requested_at`, `cancelled_at`, `consume_pending_at`, `consumed_at`, `release_pending_at`, `released_at`, and `expires_at`.
- `AIJob` does not currently include `expired_at` or `retry_pending_at` columns.
- History currently derives events from available timestamp fields; it currently labels `finished_at` as `finished`, which is not a canonical status.

## 3. Scope

In scope for this contract:

- canonical execution states;
- allowed execution transitions;
- recommended future `AIJobAsyncOrchestrationService` methods;
- timestamp rules;
- metadata rules;
- idempotency rules for worker-driven transitions;
- settlement relationship with consume and release;
- tenant-safe lookup and mutation locking;
- test requirements for the future implementation.

## 4. Non-Scope

This contract does not:

- implement a worker;
- implement new endpoints;
- change route behavior;
- change repository, orchestration, gateway, ledger, or model code;
- create or modify Alembic migrations;
- connect a real queue;
- connect ComfyUI runtime;
- connect OpenAI, Anthropic, Ollama, or any real AI provider;
- process real images or create real assets;
- touch Stripe, checkout, billing purchase flows, Docker, frontend, or runtime configuration.

## 5. Canonical States

The following statuses were audited as canonical in `AI_JOB_STATUSES`:

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

Non-canonical names:

- `finished` is not a canonical status.
- `completed` is not a canonical status.
- `finished_at` is a timestamp field, not a state.

Future implementations must not introduce `finished` or `completed` as runtime statuses without a prior explicit status-contract and model/migration phase.

## 6. Existing Allowed Transition Map

The audited status service currently allows these transitions:

- `created -> estimated`
- `estimated -> credit_checked`
- `credit_checked -> reserved`
- `reserved -> queued`
- `reserved -> cancel_requested`
- `reserved -> expired`
- `queued -> running`
- `queued -> cancel_requested`
- `running -> succeeded`
- `running -> partial_succeeded`
- `running -> failed`
- `running -> cancel_requested`
- `succeeded -> consume_pending`
- `partial_succeeded -> consume_pending`
- `failed -> release_pending`
- `failed -> retry_pending`
- `cancel_requested -> cancelled`
- `cancelled -> release_pending`
- `consume_pending -> consumed`
- `release_pending -> released`
- `retry_pending -> queued`
- `expired -> release_pending`

The future execution implementation must use this map or a stricter successor contract. It must not create an implicit transition path by assigning `AIJob.status` directly.

## 7. Proposed Execution Transitions

The future execution surface should support the following execution transitions:

- `reserved -> queued`
- `queued -> running`
- `running -> succeeded`
- `running -> partial_succeeded`
- `running -> failed`
- `reserved -> cancel_requested`
- `queued -> cancel_requested`
- `running -> cancel_requested`
- `cancel_requested -> cancelled`
- `reserved -> expired` when expiration is policy-authorized
- `queued -> expired` only if a future status-contract update adds this transition
- `running -> expired` only if a future status-contract update adds this transition
- `failed -> release_pending`
- `cancelled -> release_pending`
- `expired -> release_pending`
- `succeeded -> consume_pending`
- `partial_succeeded -> consume_pending`
- `consume_pending -> consumed`
- `release_pending -> released`

Important gap:

- `queued -> expired` and `running -> expired` are requested as conceptual expiration paths, but they are not currently allowed by the audited status service.
- A future implementation must either restrict expiration to `reserved -> expired` or explicitly update the transition contract and tests before enabling other expiration paths.

## 8. Settlement Rules

Execution transitions and accounting settlement are related but separate boundaries.

Consumption rules:

- Consume is allowed only after `succeeded`, `partial_succeeded`, or `consume_pending`.
- The recommended state path is `succeeded -> consume_pending -> consumed` or `partial_succeeded -> consume_pending -> consumed`.
- `consume_ai_job_credits(...)` must continue to use `AIJobAsyncOrchestrationService`.
- `reservation_entry_id` must come from the persisted tenant-scoped job.
- Worker code must not call `CreditLedgerService` or `CreditGateService` directly.

Release rules:

- Release is allowed only after `failed`, `cancelled`, `expired`, or `release_pending`.
- The recommended state path is `failed -> release_pending -> released`, `cancelled -> release_pending -> released`, or `expired -> release_pending -> released`.
- `release_ai_job_credits(...)` must continue to use `AIJobAsyncOrchestrationService`.
- `reservation_entry_id` must come from the persisted tenant-scoped job.
- Worker code must not call `CreditLedgerService` or `CreditGateService` directly.

Double settlement rules:

- Double consume must be blocked.
- Double release must be blocked.
- Consume after full release must fail.
- Release after full consume must fail unless a future partial-settlement policy explicitly allows releasing surplus.
- Partial settlement must follow the accounting gateway and reservation linkage contracts; it must not be introduced implicitly by execution transitions.

## 9. Recommended Future Orchestration Methods

The following methods are recommended future surface on `AIJobAsyncOrchestrationService`. They do not currently exist and must not be treated as implemented until a future code phase adds them.

Recommended full surface:

```python
async def enqueue_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    metadata: dict | None = None,
): ...

async def start_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    metadata: dict | None = None,
): ...

async def succeed_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    output_metadata: dict | None = None,
): ...

async def partially_succeed_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    output_metadata: dict | None = None,
): ...

async def fail_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    error_metadata: dict | None = None,
): ...

async def request_cancel_ai_job(
    session,
    organization_id: str,
    job_id: str,
    requested_by: str,
    reason: str | None = None,
): ...

async def cancel_ai_job(
    session,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
    reason: str | None = None,
): ...

async def expire_ai_job(
    session,
    organization_id: str,
    job_id: str,
    reason: str | None = None,
): ...

async def mark_consume_pending(...): ...

async def mark_release_pending(...): ...
```

Minimum V1 recommended to unblock the mock worker:

- `enqueue_ai_job(...)`
- `start_ai_job(...)`
- `succeed_ai_job(...)`
- `fail_ai_job(...)`
- `cancel_ai_job(...)` if the V1 mock worker includes cancel mode
- `mark_consume_pending(...)`
- `mark_release_pending(...)`

Optional after V1:

- `partially_succeed_ai_job(...)`
- `request_cancel_ai_job(...)`
- `expire_ai_job(...)`
- retry-specific methods for `retry_pending -> queued`

## 10. Orchestration Method Rules

Every future execution method must:

- receive `AsyncSession` from the caller;
- require `organization_id` and `job_id`;
- load the job through `get_for_update(organization_id, job_id)` or an equivalent tenant-scoped locked repository path;
- validate the current status and target status through `AIJobTransitionService` or an equivalent centralized transition helper;
- apply status, timestamp, and metadata atomically;
- persist through repository `save`/flush;
- avoid internal `commit()`;
- return a result containing the job and transition plan;
- map invalid transition to a typed orchestration error;
- return not found for missing or cross-tenant jobs without exposing cross-tenant existence.

Direct status mutation rule:

- Code outside orchestration transition helpers must not do `job.status = ...`.
- The only acceptable direct assignment is inside a validated helper equivalent to current `_apply_transition(...)`, after a transition plan has been built.

## 11. Tenant-Safe Rules

Mandatory rules:

- `organization_id` is required for every execution transition.
- `job_id` is never used without `organization_id`.
- Mutation methods use `get_for_update(organization_id, job_id)`.
- Cross-tenant jobs return tenant-scoped not found behavior.
- No global `get(job_id)` is permitted.
- Worker commands, provider callbacks, admin triggers, and tests must not bypass tenant-scoped lookup.
- The worker cannot mutate jobs cross-tenant even when invoked by internal tooling.

## 12. Locking and Transaction Rules

Mandatory rules:

- `AsyncSession` is received from the caller above orchestration.
- `AsyncSessionLocal` is forbidden inside execution transition methods.
- Internal `commit()` is forbidden inside repository, orchestration, gateway, and worker service boundaries.
- Repository `save`/flush is allowed where existing contracts permit it.
- A status change must be atomic with its timestamp and metadata changes.
- Settlement transitions must be atomic with their ledger entry id and credit amount updates.
- The outer use-case, task runner, route, or test harness owns transaction commit/rollback.

Recommended atomic sequence for an execution transition:

1. validate caller and command;
2. receive shared `AsyncSession`;
3. load the job through `get_for_update(organization_id, job_id)`;
4. validate current status and target status;
5. build transition plan;
6. apply status and timestamp;
7. merge namespaced metadata;
8. repository save/flush;
9. return transition result;
10. commit outside orchestration.

## 13. Timestamp Rules

Audited timestamp mapping:

- `queued` uses `queued_at`.
- `running` uses `started_at`.
- `succeeded` uses `finished_at`.
- `partial_succeeded` uses `finished_at`.
- `failed` uses `finished_at`.
- `cancel_requested` uses `cancel_requested_at`.
- `cancelled` uses `cancelled_at`.
- `consume_pending` uses `consume_pending_at`.
- `consumed` uses `consumed_at`.
- `release_pending` uses `release_pending_at`.
- `released` uses `released_at`.
- `expired` currently maps to `expires_at` in `AIJobTransitionService` and `AIJob`.

Future model gaps:

- `expired_at` does not currently exist. Do not invent it at runtime in V1.
- `retry_pending_at` does not currently exist. Do not invent it at runtime in V1.
- If exact transition time for expiration or retry pending is required, add an explicit future model and migration phase.

History rule:

- History must reflect canonical statuses.
- A future history update should map `finished_at` to the concrete current status that produced it (`succeeded`, `partial_succeeded`, or `failed`) rather than the non-canonical label `finished`.

## 14. Metadata Rules

Execution metadata must be namespaced and safe.

Required metadata conventions:

- `execution_attempt_id` must be stored under a namespaced key when no dedicated column exists.
- Use `execution.execution_attempt_id` or `mock_worker.execution_attempt_id` for mock worker attempts.
- Use `mock_worker.output` for mock success output metadata.
- Use `mock_worker.error` for mock failure or cancellation error metadata.
- Real provider metadata must use a separate namespace such as `provider.execution` or a future provider-specific contract.
- Mock metadata and provider metadata must not overwrite accounting fields.

Security rules:

- Do not store secrets, tokens, API keys, credentials, raw provider payloads, private prompt payloads, private uploads, or sensitive runtime artifacts.
- Store only JSON-safe, size-limited metadata.
- Error messages must be safe for logs and internal history.
- Public responses may redact internal metadata while preserving status and traceability.

## 15. Idempotency Rules

Worker-driven transitions require stable idempotency.

Mandatory rules:

- `execution_attempt_id` is required for worker-driven transitions.
- Repeating the same transition with the same `execution_attempt_id` and same payload must be safe.
- Repeating the same transition with the same `execution_attempt_id` and different payload must produce a conflict.
- The same `execution_attempt_id` must not be reused for another tenant or job.
- Settlement `caller_key` must derive from `execution_attempt_id` or another stable documented key.
- Idempotency metadata must be sufficient to compare replay payloads.

Recommended key forms:

- `execution:{execution_attempt_id}:enqueue`
- `execution:{execution_attempt_id}:start`
- `execution:{execution_attempt_id}:succeed`
- `execution:{execution_attempt_id}:fail`
- `execution:{execution_attempt_id}:cancel`
- `execution:{execution_attempt_id}:consume`
- `execution:{execution_attempt_id}:release`

Accounting key note:

- Gateway settlement keys continue to follow `ai_job:{organization_id}:{job_id}:consume[:caller_key]` and `ai_job:{organization_id}:{job_id}:release[:caller_key]`.
- The execution layer supplies the stable `caller_key`; the gateway derives the final ledger idempotency key.

## 16. AIJobTransitionService Integration

All future execution transitions must integrate with `AIJobTransitionService` or a strict successor.

Required behavior:

- validate canonical `from_status` and `to_status` before mutation;
- reject unknown statuses;
- reject disallowed transitions;
- build a transition plan with accounting action and timestamp field;
- apply the status only after the transition plan is valid;
- expose the transition plan in mutation results where useful for tests and diagnostics.

Forbidden behavior:

- direct `job.status = ...` in workers;
- direct `job.status = ...` in endpoints;
- direct `job.status = ...` in provider adapters;
- direct timestamp mutation without a matching validated transition;
- adding runtime status names that are not present in the canonical status service.

## 17. AIJobStatusService Integration

Future implementation must:

- use canonical status constants from `AIJobStatusService`;
- validate status names with the status service;
- keep `AI_JOB_ALLOWED_STATUS_TRANSITIONS` as the source of truth or update it through a documented status-contract phase;
- avoid `finished` and `completed` as status names;
- keep derived history aligned with canonical statuses;
- update tests whenever the status map changes.

## 18. Future Test Requirements

Future implementation must include tests proving:

- `reserved -> queued` succeeds;
- `queued -> running` succeeds;
- `running -> succeeded` succeeds;
- `running -> partial_succeeded` succeeds when implemented;
- `running -> failed` succeeds;
- `reserved -> cancel_requested` succeeds when cancel is implemented;
- `queued -> cancel_requested` succeeds when cancel is implemented;
- `running -> cancel_requested` succeeds when cancel is implemented;
- `cancel_requested -> cancelled` succeeds when cancel is implemented;
- invalid transitions are blocked;
- cross-tenant mutation is blocked with tenant-scoped not found behavior;
- timestamps are set on the correct fields;
- metadata is namespaced and does not overwrite accounting fields;
- idempotent retry with the same `execution_attempt_id` is safe;
- replay with changed payload conflicts;
- the same `execution_attempt_id` cannot be reused for another tenant or job;
- no direct status mutation occurs outside orchestration helper paths;
- no `AsyncSessionLocal` usage exists in execution transition methods;
- no internal `commit()` exists in execution transition methods;
- consume is only reachable after `succeeded`, `partial_succeeded`, or `consume_pending`;
- release is only reachable after `failed`, `cancelled`, `expired`, or `release_pending`;
- worker code does not call `CreditLedgerService` or `CreditGateService` directly;
- history/read surfaces reflect canonical status and timestamps after execution transitions.

## 19. Roadmap After This Contract

Recommended order:

1. Implement execution transition methods in `AIJobAsyncOrchestrationService`.
2. Add unit tests for transition validation, timestamps, metadata, idempotency, and tenant isolation.
3. Add tests proving no direct status mutation outside validated helper paths.
4. Implement mock worker service using the new orchestration methods.
5. Add an optional internal/admin trigger only if explicitly scoped.
6. Add PostgreSQL integration tests if operationally authorized.
7. Implement a real worker process.
8. Add a real queue.
9. Add real provider adapters.
10. Connect Command Center/frontend read surfaces after backend behavior is stable.

## 20. Acceptance Criteria for Future Implementation

Future execution transition implementation is acceptable only when:

- all status changes pass through validated orchestration helpers;
- tenant-scoped locked lookup is used for every mutation;
- timestamps match the audited transition mapping;
- metadata is namespaced and safe;
- worker-driven transitions are idempotent by `execution_attempt_id`;
- settlement remains delegated to `AIJobAsyncOrchestrationService` and `AIJobAccountingGateway`;
- double settlement is blocked;
- no real provider, queue, frontend, Docker, Stripe, Alembic, or runtime/config changes are introduced by the transition implementation phase unless explicitly scoped.
