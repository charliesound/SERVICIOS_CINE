# CID AI Job Status Model Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical status model for AI jobs in CID SaaS, including lifecycle, auditability, and credit-aligned state transitions
Companion docs:
- `docs/architecture/cid_ai_job_costing_contract_v1.md`
- `docs/architecture/cid_billing_models_v1.md`
- `docs/architecture/cid_saas_model_contract_v1.md`
- `docs/architecture/cid_roles_permissions_matrix_v1.md`
- `docs/architecture/cid_plans_modules_matrix_v1.md`
- `src/services/credit_ledger_service.py`
- `src/services/credit_gate_service.py`
- `src/services/ai_job_costing_service.py`

## 1. Purpose of the Contract

This contract defines how CID represents, audits, and transitions AI jobs. Its purpose is to:

- define a canonical lifecycle for AI job state;
- prepare future ORM tables and internal models without implementing them yet;
- connect job state to credit estimation, reservation, consumption, and release;
- ensure that future workers, provider adapters, and internal endpoints share one state language.

This phase does not implement tables, workers, queues, or public APIs. It defines the future shape of the system.

## 2. Principles

- No costly AI job starts without prior reservation.
- Every job has a stable `job_id`.
- Every job belongs to one `organization_id`.
- `project_id` may be optional depending on the operation.
- `user_id` identifies who launched or requested the job.
- Job state and accounting state must not contradict each other.
- Every relevant transition must be auditable.
- CID remains the source of truth for job-credit reconciliation, even when execution is delegated to providers, GPU-on-demand, ComfyUI workflows, or future local agents.

## 3. Canonical Proposed States

The canonical status catalog is:

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

## 4. State Semantics

### 4.1 `created`

- Meaning: the job identity exists but costing has not yet been completed.
- Entered when: CID creates a job request record or in-memory job envelope.
- Allows: estimation, validation, permission checks.
- Blocks: execution, provider dispatch, credit consumption.
- Credit relation: no reservation yet.

### 4.2 `estimated`

- Meaning: `operation_type` and estimated credits are known.
- Entered when: `CreditGateService` or equivalent costing logic returns a canonical estimate.
- Allows: credit availability check and reservation attempt.
- Blocks: execution before reservation.
- Credit relation: estimate known, no credit mutation yet.

### 4.3 `credit_checked`

- Meaning: availability was checked against current balance.
- Entered when: CID completes preflight availability validation.
- Allows: reservation.
- Blocks: execution if reservation has not been completed.
- Credit relation: no mutation yet; still advisory.

### 4.4 `reserved`

- Meaning: credits were successfully reserved for the job.
- Entered when: `reservation_entry_id` exists and reservation succeeds.
- Allows: queueing, expiration handling, cancellation before execution.
- Blocks: direct consume without execution result path.
- Credit relation: `reserved_active` increased and reservation ledger entry exists.

### 4.5 `queued`

- Meaning: the reserved job is waiting for runtime execution.
- Entered when: dispatch to queue/router/provider pipeline is accepted.
- Allows: worker pickup, cancellation, expiry, retry orchestration before run.
- Blocks: release without cancellation/expiry/failure path, consume without result.
- Credit relation: reservation must still exist.

### 4.6 `running`

- Meaning: execution has started in worker, provider, workflow, or runtime.
- Entered when: actual processing begins.
- Allows: success/failure/partial-success/cancel-request transitions.
- Blocks: new reservation for the same execution attempt unless explicitly split.
- Credit relation: reservation must still exist and remain matched to the job.

### 4.7 `succeeded`

- Meaning: execution finished with an acceptable successful result.
- Entered when: the runtime produces a usable output.
- Allows: consume workflow.
- Blocks: release as the default path.
- Credit relation: should move next to `consume_pending`.

### 4.8 `partial_succeeded`

- Meaning: execution produced an incomplete but potentially usable output.
- Entered when: partial result exists and may be accepted.
- Allows: product-policy or user acceptance decision, then consume if accepted.
- Blocks: direct final success semantics until acceptance is clear.
- Credit relation: may later consume, otherwise may release.

### 4.9 `failed`

- Meaning: execution failed without accepted successful completion.
- Entered when: provider/workflow/worker returns failure or runtime abort.
- Allows: release or retry policy evaluation.
- Blocks: normal consume path.
- Credit relation: should move toward `release_pending`, except if partial accepted flow is explicitly documented in future.

### 4.10 `cancel_requested`

- Meaning: user or system requested cancellation during a queued or running job.
- Entered when: cancel action is registered.
- Allows: cooperative cancellation handling and final resolution.
- Blocks: new execution start for the same attempt.
- Credit relation: reservation still exists until final outcome is resolved.

### 4.11 `cancelled`

- Meaning: the job was effectively cancelled.
- Entered when: queue/worker/provider confirms cancellation or CID decides execution will not continue.
- Allows: release workflow.
- Blocks: normal consume path.
- Credit relation: should move to `release_pending`.

### 4.12 `consume_pending`

- Meaning: the job is successful enough to charge, but accounting consumption is not yet finalized.
- Entered when: successful or accepted partial result exists before final consume mutation.
- Allows: safe idempotent consume.
- Blocks: release.
- Credit relation: next expected mutation is `consume_entry_id`.

### 4.13 `consumed`

- Meaning: reservation became final charged usage.
- Entered when: `consume_entry_id` exists and consumption succeeds.
- Allows: audit, result display, downstream delivery workflows.
- Blocks: release and double consume.
- Credit relation: credits have been charged and reservation has been settled.

### 4.14 `release_pending`

- Meaning: the job must release credits but release is not yet finalized.
- Entered when: failure, cancellation, or expiration require accounting cleanup.
- Allows: safe idempotent release.
- Blocks: consume.
- Credit relation: next expected mutation is `release_entry_id`.

### 4.15 `released`

- Meaning: reserved credits were released back to available balance.
- Entered when: `release_entry_id` exists and release succeeds.
- Allows: audit and optional new job creation.
- Blocks: later consume of the same attempt.
- Credit relation: reservation is settled without charge.

### 4.16 `retry_pending`

- Meaning: the failed job attempt is awaiting retry orchestration.
- Entered when: retry policy marks the attempt recoverable.
- Allows: requeueing under controlled idempotency policy.
- Blocks: blind replay without retry policy.
- Credit relation: depends on retry strategy; reservation may be reused or released/recreated.

### 4.17 `expired`

- Meaning: reserved job did not start or did not complete in the allowed lifetime.
- Entered when: reservation timeout or queue lifetime timeout is reached.
- Allows: release workflow.
- Blocks: normal execution continuation.
- Credit relation: should move to `release_pending`.

## 5. Allowed Transitions

Canonical allowed transitions include:

- `created -> estimated`
- `estimated -> credit_checked`
- `credit_checked -> reserved`
- `reserved -> queued`
- `queued -> running`
- `running -> succeeded`
- `running -> partial_succeeded`
- `running -> failed`
- `running -> cancel_requested`
- `cancel_requested -> cancelled`
- `succeeded -> consume_pending -> consumed`
- `partial_succeeded -> consume_pending -> consumed` when partial result is accepted
- `failed -> release_pending -> released`
- `cancelled -> release_pending -> released`
- `failed -> retry_pending -> queued` when retry policy explicitly allows it
- `reserved -> expired -> release_pending -> released`

## 6. Forbidden Transitions

The following transitions are prohibited:

- `created -> running`
- `estimated -> running`
- `queued -> consumed`
- `failed -> consumed` unless a separate explicit accepted-partial intermediate policy exists
- `released -> consumed`
- `consumed -> released` except future audited administrative correction
- double consume
- double release
- retry without explicit idempotency policy

## 7. Relationship with Credits

### 7.1 States that require reservation

Before a costly job reaches `queued` or `running`, it must already be `reserved`.

### 7.2 States that may consume

Only successful result paths may consume:

- `succeeded -> consume_pending -> consumed`
- `partial_succeeded -> consume_pending -> consumed` if partial result is accepted

### 7.3 States that must release

Release is expected after:

- `failed`
- `cancelled`
- `expired`

through the path:

- `release_pending -> released`

### 7.4 Ledger-entry timing

- `reservation_entry_id` is created when the job reaches `reserved`.
- `consume_entry_id` is created when the job reaches `consumed`.
- `release_entry_id` is created when the job reaches `released`.

### 7.5 Preventing double consume

CID must prevent double consume by combining:

- job-state validation;
- idempotent consume operations;
- one successful `consume_entry_id` per attempt;
- worker/provider callback deduplication.

### 7.6 Preventing negative balance

CID avoids negative balance by:

- reserving before execution;
- consuming only from reservation-backed jobs;
- releasing instead of over-consuming on failed paths;
- disallowing additional execution once the reserved budget is exhausted unless a new estimate and reservation are created;
- avoiding silent overrun unless a future explicit Enterprise override exists.

## 8. Future Minimum Job Fields

Future AI job model fields should include at least:

- `id`
- `organization_id`
- `project_id`
- `user_id`
- `operation_type`
- `status`
- `estimated_credits`
- `reserved_credits`
- `consumed_credits`
- `released_credits`
- `reservation_entry_id`
- `consume_entry_id`
- `release_entry_id`
- `idempotency_key`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`
- `output_asset_ids`
- `error_code`
- `failure_reason`
- `attempt_number`
- `parent_job_id`
- `created_at`
- `reserved_at`
- `queued_at`
- `started_at`
- `finished_at`
- `cancelled_at`
- `consumed_at`
- `released_at`
- `expires_at`
- `metadata`

These fields are a future model target, not an implementation in this phase.

## 9. Runtime Families

The status model must support all runtime families below without changing the state vocabulary:

- text / LLM
- image generation
- video generation
- transcription
- sound sync
- DaVinci Bridge
- ComfyUI workflow
- external API
- GPU-on-demand
- future local agent

One state machine, multiple execution families.

## 10. Idempotency

Idempotency must cover:

- job creation
- reservation
- consumption
- release
- retries
- duplicated provider callbacks
- worker crash/restart

Rules:

- creating the same job twice must not silently generate contradictory states;
- reservation must not be duplicated for the same idempotent launch;
- consume must not happen more than once per accepted attempt;
- release must not happen more than once per settled failed/cancelled attempt;
- duplicated provider callbacks must be mapped to current known state and ignored or reconciled safely;
- worker restart must resume or reconcile the last durable state instead of replaying blindly.

## 11. Cancellations

### 11.1 Before reservation

- The job may be cancelled while still in `created`, `estimated`, or `credit_checked`.
- No release is needed because no reservation exists.

### 11.2 After reservation but before execution

- Typical path: `reserved -> cancel_requested -> cancelled -> release_pending -> released`

### 11.3 During execution

- Typical path: `running -> cancel_requested -> cancelled`
- Final accounting depends on whether any accepted result exists. Default path is release.

### 11.4 After partial result

- If partial result is not accepted, release.
- If partial result is accepted, use `consume_pending -> consumed`.

### 11.5 After success but before consume

- If success already produced accepted value, cancellation should not erase accounting obligation.
- Typical path remains `succeeded -> consume_pending -> consumed`.

## 12. Retries

Retries must distinguish:

- same logical job, new attempt;
- same attempt resumed after transient interruption;
- completely new job request.

Guidelines:

- Use `attempt_number` to represent successive execution attempts.
- Use `parent_job_id` to link derivative attempts or retry jobs if separate records are preferred later.
- Reuse reservation only if retry remains within the same authorized reserved scope and the first attempt did not already settle accounting.
- Create a new reservation if retry materially changes scope, duration, or cost.
- Release the old reservation first if the original attempt is abandoned and the retry needs a fresh accounting boundary.

## 13. ComfyUI

For ComfyUI:

- a job is a versioned workflow execution, not a loose prompt;
- `workflow_id`, `workflow_version`, and `workflow_hash` must identify the executable pipeline;
- model packs and custom nodes must be traceable through metadata;
- outputs must remain linked to the job record and the accounting entries;
- prompts alone must not define the whole job identity if no workflow contract exists.

## 14. DaVinci Bridge

For DaVinci Bridge:

- a job may represent package generation, analysis, sync, or export;
- future sync modes may include timecode or clapboard/slate strategies;
- jobs should reference clips, audio assets, sequences, or exports through metadata;
- outputs must remain auditable and linked to job state and accounting state.

## 15. Security and Permissions

- Plan and module gates decide capability visibility.
- Roles and permissions decide who can launch, cancel, approve, or retry.
- Credits decide whether costly execution may proceed.
- Suspended organizations must not launch new costly jobs.

This yields a four-part decision:

1. the feature is available in plan/module terms;
2. the actor has permission to perform the action;
3. the organization is in an allowed operational/billing state;
4. the organization has sufficient credits and a valid reservation path.

## 16. Roadmap

Future implementation milestones:

- `AIJob` ORM model spec -> future implementation
- future migration
- status service
- job reservation wrapper
- worker queue
- provider adapters
- internal endpoints
- frontend usage and job history UI
- admin and reconciliation tools

## 17. Final Rule

The final rule is:

- no costly job runs without reservation;
- no successful costly job remains unconsumed;
- no failed or cancelled reserved job remains unreleased;
- no status transition should contradict the accounting trail.

This contract defines the future language of AI job state in CID. It does not yet implement tables, workers, or queues, but all those future pieces must conform to this model.
