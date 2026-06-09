# CID AI Job Orchestration Service Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical future internal orchestration service for AI jobs in CID SaaS, aligned with job model, lifecycle, credit accounting, and auditability
Companion docs:
- `docs/architecture/cid_ai_job_model_contract_v1.md`
- `docs/architecture/cid_ai_job_status_model_contract_v1.md`
- `docs/architecture/cid_ai_job_costing_contract_v1.md`
- `src/models/ai_job.py`
- `src/services/ai_job_transition_service.py`
- `src/services/ai_job_status_service.py`
- `src/services/ai_job_costing_service.py`
- `src/services/credit_gate_service.py`
- `src/services/credit_ledger_service.py`

## 1. Purpose

This contract defines how CID should eventually orchestrate the lifecycle of an `AIJob`. Its purpose is to:

- define one canonical internal path to create, estimate, reserve, queue, update, consume, release, cancel, expire, and retry AI jobs;
- prevent each future endpoint, worker, provider adapter, or internal tool from implementing its own lifecycle logic;
- keep `CreditLedgerService` as the accounting authority while `AIJob` remains the orchestration and audit envelope;
- make future runtime integrations converge on one predictable lifecycle and reconciliation policy.

## 2. Scope

This phase is specification only. It:

- does not implement `AIJobOrchestrationService` yet;
- does not create endpoints;
- does not execute real AI workloads;
- does not create a worker or queue runtime;
- does not create provider adapters or callback handlers;
- does not modify migrations or the database schema.

## 3. Future Service

Recommended future name:

- `AIJobOrchestrationService`

This service is expected to be an internal backend boundary, not a public API surface.

## 4. Responsibility

The future orchestration service should own the coordination of:

- creating the initial job envelope;
- invoking costing logic and normalizing canonical operation metadata;
- checking available credits;
- reserving credits before costly execution;
- applying lifecycle transitions through `AIJobTransitionService`;
- preparing jobs for queue dispatch;
- recording success, failure, cancellation, retry, and expiration outcomes;
- consuming or releasing credits according to the canonical accounting contract;
- reconciling `AIJob` state with linked ledger entries.

The orchestration service should coordinate other services, not replace them. In particular:

- `AIJobTransitionService` remains the transition rule helper;
- `AIJobCostingService` remains the job-costing facade;
- `CreditGateService` remains the credit-gating facade;
- `CreditLedgerService` remains the accounting authority.

## 5. Out of Scope

The future orchestration service should not directly implement:

- real ComfyUI execution;
- real DaVinci control;
- provider-specific adapters;
- HTTP callback endpoints;
- frontend workflows;
- Stripe or external billing;
- real workers or queue backends.

Those concerns may call the orchestration service later, but should not bypass it.

## 6. Canonical Lifecycle

The service should support the canonical lifecycle below.

### 6.1 `create`

- Create an `AIJob` envelope with `status="created"`.
- Persist tenant, project, user, operation, idempotency, and base metadata.
- No credit mutation yet.

### 6.2 `estimate`

- Normalize `operation_type`.
- Derive `estimated_credits` using the canonical costing path.
- Transition to `estimated`.
- Record `estimated_at`.

### 6.3 `check credits`

- Run credit availability preflight for the target organization.
- Transition to `credit_checked`.
- Record `credit_checked_at`.
- No credit mutation yet.

### 6.4 `reserve`

- Reserve credits before costly execution begins.
- Create and store `reservation_entry_id`.
- Transition to `reserved`.
- Record `reserved_at`.

### 6.5 `queue`

- Move the reserved job into a queue-ready state.
- Transition to `queued`.
- Record `queued_at`.
- No execution should begin before this stage is valid.

### 6.6 `start`

- Mark runtime execution as actually started.
- Transition to `running`.
- Record `started_at`.

### 6.7 `succeed`

- Mark execution as successfully completed with usable output.
- Transition to `succeeded`.
- Record `finished_at`.
- Next expected stage is `consume_pending`.

### 6.8 `partial_succeed`

- Mark execution as partially completed with potentially usable output.
- Transition to `partial_succeeded`.
- Record `finished_at`.
- Product or policy must determine whether the result is billable or releasable.

### 6.9 `fail`

- Mark execution as failed.
- Transition to `failed`.
- Record `finished_at`.
- Expected next path is `release_pending` or `retry_pending`.

### 6.10 `cancel_requested`

- Register cancellation intent from user or system.
- Allow this from `reserved`, `queued`, and `running`.
- Transition to `cancel_requested`.
- Record `cancel_requested_at`.

### 6.11 `cancelled`

- Mark the job as effectively cancelled.
- Transition to `cancelled`.
- Record `cancelled_at`.
- Expected next path is `release_pending`.

### 6.12 `consume_pending`

- Move a successful or accepted partial result to the billable pre-consume state.
- Transition to `consume_pending`.
- Record `consume_pending_at`.
- No consumption happens yet.

### 6.13 `consumed`

- Execute final credit consumption.
- Create and store `consume_entry_id`.
- Transition to `consumed`.
- Record `consumed_at`.
- This is terminal.

### 6.14 `release_pending`

- Move a failed, cancelled, or expired job to release preparation.
- Transition to `release_pending`.
- Record `release_pending_at`.
- No release happens yet.

### 6.15 `released`

- Execute final credit release.
- Create and store `release_entry_id`.
- Transition to `released`.
- Record `released_at`.
- This is terminal.

### 6.16 `retry_pending`

- Mark a failed attempt as awaiting retry orchestration.
- Preserve lineage through `attempt_number` and `parent_job_id`.
- Do not assume reservation reuse.

### 6.17 `expired`

- Mark a reservation, queued job, or provider-backed run as expired.
- Transition to `expired`.
- Record `expires_at`.
- Expected canonical path is `expired -> release_pending -> released`.

## 7. Recommended Future Methods

The future service should likely expose internal methods equivalent to:

- `create_ai_job(...)`
- `estimate_ai_job(...)`
- `check_ai_job_credits(...)`
- `reserve_ai_job_credits(...)`
- `queue_ai_job(...)`
- `mark_ai_job_running(...)`
- `mark_ai_job_succeeded(...)`
- `mark_ai_job_partial_succeeded(...)`
- `mark_ai_job_failed(...)`
- `request_ai_job_cancel(...)`
- `mark_ai_job_cancelled(...)`
- `consume_ai_job_credits(...)`
- `release_ai_job_credits(...)`
- `expire_ai_job(...)`
- `retry_ai_job(...)`
- `reconcile_ai_job_accounting(...)`

The final implementation may choose different exact names, but it should preserve these conceptual boundaries.

## 8. Accounting Rules

- `CreditLedgerService` is the accounting authority.
- `AIJob` never replaces the ledger.
- Reserving credits must create `reservation_entry_id`.
- Consuming credits must create `consume_entry_id`.
- Releasing credits must create `release_entry_id`.
- No double consume.
- No double release.
- No costly execution without a valid reservation.
- `consume_pending` does not consume yet.
- `release_pending` does not release yet.

The orchestration service should treat ledger mutations as authoritative side effects that must be reflected back into `AIJob`.

## 9. Transition Rules

- Every state change must pass through `AIJobTransitionService`.
- No caller should write arbitrary status strings directly.
- `consumed` and `released` are terminal settled states.
- Cancellation must be allowed from `reserved`, `queued`, and `running`.
- Expiration must follow `expired -> release_pending -> released`.
- Transition timestamps should follow the timestamp-field mapping already defined by `AIJobTransitionService`.

## 10. Idempotency

The future service should define idempotent behavior for:

- repeated create requests;
- repeated reserve/consume/release requests;
- duplicated provider callbacks;
- network retries;
- repeated admin reconciliation actions.

Recommended policy:

- use `idempotency_key` whenever a mutating step may be retried;
- align job-level idempotency with ledger-level idempotency where possible;
- never allow idempotency to mask contradictory state transitions;
- preserve enough metadata to explain why a duplicate request was accepted, ignored, or rejected.

## 11. Concurrency

The future implementation should protect against:

- two workers consuming the same reservation;
- one path consuming while another path releases;
- duplicated callback and worker completion races;
- cancellation racing with success/failure completion.

Recommended design principles:

- state transitions must be atomic;
- ledger mutation and job-state update should be transactionally coordinated where possible;
- logical locking or row-level locking will likely be needed in the eventual repository layer;
- reconciliation must exist for mid-flight partial failures.

## 12. Error Handling

The orchestration service should define policy for at least:

- failure before reservation;
- failure after reservation but before queueing;
- failure while queued;
- failure during runtime execution;
- failure after success but before consumption;
- failure during consume;
- failure during release;
- provider-originated errors and malformed callback payloads.

Errors should be recorded in `error_code`, `failure_reason`, metadata, and status transitions without bypassing accounting rules.

## 13. Cancellation Rules

The service should document behavior for:

- cancellation before reservation;
- cancellation after reservation but before execution;
- cancellation while queued;
- cancellation while running;
- cancellation after partial success;
- cancellation after nominal success but before final consume.

The eventual implementation should make clear whether a partial result is accepted, billable, releasable, or quarantined for manual review.

## 14. Retry Rules

Retries should use:

- `attempt_number`;
- `parent_job_id`;
- explicit retry orchestration logic.

Recommended policy:

- create a new reservation if cost, scope, provider, or workflow meaningfully changes;
- do not reuse reservations unless a documented explicit policy allows it;
- treat `retry_pending` as orchestration state, not as silent auto-replay.

## 15. Expiration Rules

The service should support expiration due to:

- reservation timeout;
- queue timeout;
- provider timeout;
- stale execution state that requires release follow-up.

Expiration should normally flow into pending release and then final release.

## 16. ComfyUI Alignment

For future ComfyUI-backed execution, the orchestration service should:

- treat jobs as reproducible workflow runs;
- preserve `workflow_id`, `workflow_version`, and `workflow_hash`;
- preserve outputs as assets linked to the job;
- preserve model and workflow metadata needed for audit and replay analysis.

This phase does not execute ComfyUI.

## 17. DaVinci Bridge Alignment

For future DaVinci Bridge use cases, the orchestration service should support jobs representing:

- analysis;
- sync;
- preparation;
- export packaging.

It should preserve metadata about clips, audio, sequences, and local agent context without assuming direct control of DaVinci in this phase.

## 18. Provider Callbacks

The future design should anticipate:

- `provider_job_id`;
- late callbacks;
- duplicated callbacks;
- callbacks incompatible with the current state;
- quarantine and reconciliation paths for impossible or suspicious provider events.

The orchestration service should be the place where callback-driven state changes are validated against the canonical state machine.

## 19. Security

- `organization_id` is the hard perimeter.
- `project_id` provides additional scoping where applicable.
- Permissions must govern who may create, cancel, retry, inspect, or reconcile jobs.
- Plan and module gates should determine whether an operation is allowed at all.
- Credit gates must run before costly execution begins.

No future provider integration should bypass tenant and permission checks.

## 20. Audit Requirements

The orchestration service should preserve auditability for:

- initiating user or system actor;
- estimated, reserved, consumed, and released credits;
- provider, workflow, model, and assets;
- errors and failure reasons;
- lifecycle timings;
- linked ledger references;
- idempotency key usage.

Audit must explain both what happened and why it was allowed to happen.

## 21. Future Internal API Shapes

The eventual service will likely need conceptual request/response structures equivalent to:

- `AIJobCreateRequest`
- `AIJobReserveRequest`
- `AIJobQueueRequest`
- `AIJobCompletionRequest`
- `AIJobFailureRequest`
- `AIJobCancelRequest`
- `AIJobRetryRequest`
- `AIJobOrchestrationResult`

These are conceptual interface shapes for now. This phase does not require Pydantic schemas or runtime classes.

## 22. Roadmap

Recommended implementation sequence:

1. Implement `AIJobOrchestrationService`.
2. Add unit tests with fake repository/session boundaries.
3. Introduce a repository layer for job persistence and locking.
4. Add internal/admin service surfaces.
5. Integrate a worker queue.
6. Add provider adapters.
7. Add reconciliation tooling.
8. Add UI history and operational audit views.
9. Add metrics and cost dashboards.

## 23. Phase Boundary

This contract is documentary only. In this phase CID does not:

- implement `AIJobOrchestrationService`;
- create endpoints;
- create workers;
- create real queue logic;
- create provider adapters;
- create callback execution paths;
- execute ComfyUI or other AI runtimes.

That boundary is intentional so the orchestration design can stabilize before executable code is introduced.
