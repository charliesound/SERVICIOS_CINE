# CID AI Job Cancellation Credit Release Orchestration Contract v1

## Status

- Based on HEAD `4a521be` (`test: clean CID credit ledger datetime warnings`).
- Pre-implementation architecture contract.
- Documentation-only. This document does not change runtime behavior.
- Defines how later phases should connect AI Job cancellation with internal reserved-credit release.
- PostgreSQL-only.

## Problem

AI Job cancellation and internal reserved-credit release now exist as separate backend capabilities:

- Public cancellation endpoint: `POST /api/v1/ai-jobs/{job_id}/cancel`.
- Public cancellation route delegates only to `AIJobAsyncOrchestrationService.request_cancel_ai_job(...)`.
- Internal release operation: `AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)`.
- Credit ledger settlement validates reservation linkage and tenant scope.

The missing contract is when, where, and under which guarantees the backend invokes `release_cancelled_ai_job_reserved_credits(...)` after cancellation. The connection must not let clients force credit return, must avoid double release, and must keep AI Job state and ledger settlement coherent under retries and partial failures.

## Main Principle

Clients must never be able to force credit return. Credit release must be an internal backend decision derived from trusted tenant context, AI Job state, reservation linkage, and ledger settlement state.

The public cancel endpoint expresses cancellation intent only. It must not accept release controls or directly expose a public refund-like operation.

## Current Runtime Boundaries

### Public Cancel Route

`src/routes/ai_job_routes.py` currently exposes:

```http
POST /api/v1/ai-jobs/{job_id}/cancel
```

It:

- Uses `require_write_permission`.
- Rejects forged `organization_id` query values.
- Builds `AIJobAsyncCancelRequest` with `organization_id` from `tenant.organization_id`.
- Derives `requested_by` from `tenant.user_id` or `internal_trigger`.
- Calls only `service.request_cancel_ai_job(...)`.
- Does not call `release_cancelled_ai_job_reserved_credits(...)`.
- Does not create attempts, run a worker, or settle credits.

`AIJobCancelRequest` in `src/schemas/ai_job_api_schema.py` has `extra="forbid"` and only accepts:

- `reason`
- `metadata`

It does not accept `release_credits`, `release_pending`, `release_required`, `organization_id`, `job_id`, or `requested_by`.

### Internal Release Service

`AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)` currently:

- Loads the job with the tenant-scoped `repository.get_for_update(organization_id, job_id)` path.
- No-ops idempotently when there is no `reservation_entry_id`.
- No-ops idempotently when `release_entry_id` already exists.
- Rejects release after consumption through `consume_entry_id` or positive `consumed_credits`.
- Allows only `cancel_requested`, `cancelled`, and `release_pending` states.
- Uses `reserved_credits` from the job as release amount.
- Uses deterministic caller key `cancel:<reservation_entry_id>`.
- Calls `accounting_gateway.release_reserved_credits_for_job(...)`.
- Stores `release_entry_id` and `released_credits` after verified release or duplicate-key reconciliation.
- Advances through real AI Job states to `released`.

### Ledger Settlement

`CreditLedgerService.release_reserved_credits(...)` currently:

- Requires positive amount.
- Uses `organization_id` when finding balances and linked reservations.
- Validates `reservation_entry_id` when present.
- Rejects wrong tenant, wrong job, wrong entry type/status, over-release, and already-settled reservations.
- Decrements `reserved_active` exactly when release is written.
- Creates `credit_release` with settlement metadata.
- Raises `DuplicateIdempotencyKeyError` on duplicate idempotency key; the service layer must reconcile safely.

## Orchestration Options

### Option A: Release Synchronously Inside `request_cancel_ai_job()`

Description: `request_cancel_ai_job(...)` would perform cancellation state transition and immediately invoke `release_cancelled_ai_job_reserved_credits(...)` when a reservation exists.

Advantages:

- Single service-level entry point for cancel and settlement.
- Callers cannot forget to invoke release.
- Can share the same job row lock if designed carefully.
- Easier to reason about from an API consumer perspective when release succeeds.

Risks:

- Couples user-facing cancellation latency to ledger work.
- Makes public cancellation semantically heavier even if the route still hides release controls.
- Partial failure can leave cancellation committed but release not completed unless one transaction encloses both actions.
- If cancellation and release are combined too eagerly, `running` jobs may be settled before execution has actually stopped.
- Requires careful handling of `cancel_requested` because that state means cooperative stop is pending, not necessarily safe final cancellation.

Latency impact:

- Higher request latency because ledger lookup/write happens during cancellation.

Consistency impact:

- Strong if one transaction covers cancel and release for pre-finalized jobs.
- Unsafe if release is attempted while execution may still complete or consume credits.

Double-release risk:

- Low only if deterministic idempotency and `release_entry_id` checks remain mandatory.

Error handling:

- If ledger fails, API must decide whether to return cancellation success with release pending, or fail the whole request.
- Failing the whole request after cancellation state mutation can confuse clients unless transaction boundaries are strict.

Observability:

- Requires structured logs for both cancellation and settlement in one request flow.

Idempotency:

- Must distinguish idempotent cancel replay from idempotent release replay.
- Must never retry release from public payload fields.

### Option B: Release Synchronously From The API Route After `request_cancel_ai_job()`

Description: the route would call `request_cancel_ai_job(...)`, inspect the result, and then call `release_cancelled_ai_job_reserved_credits(...)`.

Advantages:

- Minimal service changes if implemented later.
- Easy to sequence in one route handler.
- Keeps `request_cancel_ai_job(...)` focused on cancellation intent.

Risks:

- Places orchestration logic in the FastAPI adapter, violating the current route-thin pattern.
- Increases chance that future routes diverge from service rules.
- Makes public HTTP request directly responsible for ledger settlement.
- Harder to keep cancellation and release in one transaction if route performs two service calls.
- Easier to accidentally expose release status as client-controllable behavior.

Latency impact:

- Higher HTTP latency.

Consistency impact:

- Medium to weak unless route and service share an explicit transaction boundary.

Double-release risk:

- Controlled by the internal service, but route-level orchestration can accidentally call it in unsafe states if tests are incomplete.

Error handling:

- Route must map release errors without leaking ledger internals.
- Route must avoid returning a response that implies credits were released when settlement failed.

Observability:

- Route logging would need to include both cancellation and release outcomes.

Idempotency:

- Still relies on the service and ledger, but the API layer would become part of the idempotency path.

### Option C: Release Asynchronously By Internal Worker Or Background Job

Description: public cancellation records intent. A trusted internal worker or background job observes eligible jobs and invokes `release_cancelled_ai_job_reserved_credits(...)` after cancellation is final enough for settlement.

Advantages:

- Keeps public cancellation endpoint simple and low latency.
- Keeps clients unable to force credit return.
- Allows retries with deterministic idempotency independent of client retries.
- Fits cooperative cancellation: `reserved`, `queued`, and `running` jobs can move to `cancel_requested` first, then settle after stop/finalization.
- Can isolate ledger failures from user-facing cancellation responses.
- Allows operational monitoring and reconciliation.

Risks:

- Requires an internal worker/background mechanism in a later phase.
- Requires clear retry ownership and observability.
- Without a worker, jobs can remain in `cancel_requested` or `release_pending` until a manual/internal process runs.
- Requires guards to prevent consume after cancellation intent when execution races exist.

Latency impact:

- Low for public API. Release happens after the request path.

Consistency impact:

- Eventual consistency between cancellation intent and ledger release.
- Strong settlement consistency remains inside `release_cancelled_ai_job_reserved_credits(...)` and ledger transaction.

Double-release risk:

- Low if the worker always uses the internal service and deterministic caller key.

Error handling:

- Release failure leaves job in a retryable internal state.
- Worker can retry safely and alert after repeated failures.

Observability:

- Requires internal logs/metrics for pending, released, retry, and failed settlement outcomes.

Idempotency:

- Natural fit: repeated worker runs should converge on one ledger release and one `release_entry_id`.

### Option D: Controlled Internal Admin/Reconciliation Operation

Description: cancellation remains separate from release. A trusted internal/admin command or reconciliation process invokes `release_cancelled_ai_job_reserved_credits(...)` for eligible jobs.

Advantages:

- Safest immediate operational bridge without exposing new public API behavior.
- Useful for repair after partial failures or before a full worker exists.
- Can be built with strict internal authentication and audit logging in later phases.

Risks:

- Manual or scheduled reconciliation can lag behind cancellation.
- Requires operational discipline and dashboards/alerts.
- Not ideal as the only long-term settlement mechanism.

Latency impact:

- None on public API path.

Consistency impact:

- Eventual consistency; depends on reconciliation frequency.

Double-release risk:

- Low when using the internal service, job row locking, and deterministic idempotency.

Error handling:

- Reconciliation can record errors and retry safely.

Observability:

- Strong if each run reports scanned, eligible, released, idempotent, skipped, and failed counts.

Idempotency:

- Same as worker approach; repeated runs must be safe.

## Recommendation

Recommended path for the current repository state: Option C as the target architecture, with Option D as the smallest safe stepping stone.

Do not connect release directly in the public route. Do not let the public request payload influence release. Keep `POST /api/v1/ai-jobs/{job_id}/cancel` as a cancellation-intent endpoint.

Recommended phased approach:

1. Keep public cancel route unchanged.
2. Add a small internal orchestration phase that marks eligible cancelled jobs for release using real states only.
3. Invoke `release_cancelled_ai_job_reserved_credits(...)` from a trusted internal worker/background process or reconciliation command.
4. Use deterministic idempotency and row locking already present in the internal service.
5. Return public cancellation results based on cancellation state, not on client-requested release.

Why this is safest now:

- `running` cancellation is cooperative. Release should not be tied to the user HTTP request before execution is known to be stopped.
- The internal release service is already idempotent and tenant-scoped.
- Route tests already assert the public cancel route does not call the release service.
- Ledger failures can be retried without making public cancel responses ambiguous.

If a later phase chooses synchronous service orchestration for pre-reservation or already-finalized jobs, it must still keep release out of route logic and must define transaction behavior explicitly.

## Proposed Flow

### Pre-Reservation Cancellation

Statuses:

- `created`
- `estimated`
- `credit_checked`

Flow:

1. Public route calls `request_cancel_ai_job(...)`.
2. Service transitions directly to `cancelled`.
3. No release is required because no `reservation_entry_id` exists.
4. Any later internal release sweep must treat missing `reservation_entry_id` as idempotent no-op.

### Post-Reservation Cancellation Intent

Statuses:

- `reserved`
- `queued`
- `running`

Flow:

1. Public route calls `request_cancel_ai_job(...)`.
2. Service transitions to `cancel_requested`.
3. Public response may indicate `cancel_requested`.
4. Credits remain reserved until internal cancellation finalization confirms release is safe.
5. A later internal worker/background process handles final cancellation and release.

### Internal Finalization And Release

Eligible release states for the current internal service:

- `cancel_requested`
- `cancelled`
- `release_pending`

Recommended future worker flow:

1. Load the job with trusted tenant scope and row locking.
2. Confirm execution has stopped or never started.
3. Move through real AI Job states only: `cancel_requested -> cancelled -> release_pending -> released`.
4. Call `release_cancelled_ai_job_reserved_credits(...)`.
5. On success, persist `release_entry_id`, `released_credits`, and final `released` status.
6. On idempotent replay, return success without another ledger entry.
7. On failure before ledger release, keep the job in a retryable state such as `cancel_requested`, `cancelled`, or `release_pending` depending on the point of failure.

### Release Success

Expected durable state:

- `AIJob.status == "released"`.
- `AIJob.release_entry_id` set.
- `AIJob.released_credits` equals `AIJob.reserved_credits`.
- Ledger has one linked `credit_release` settlement for `reservation_entry_id`.
- `CreditBalance.reserved_active` was decremented once by the ledger.

### Release Idempotent Replay

Expected behavior:

- Existing `release_entry_id` returns no-op success.
- Duplicate idempotency with valid existing entry is reconciled by service.
- No additional ledger entry is created.
- Public clients cannot trigger the replay directly.

### Release Failure

Expected safe behavior:

- No response may claim release if `release_entry_id` was not persisted.
- If ledger write failed before settlement, retry with the same deterministic key.
- If ledger wrote but job update failed, the next retry must reconcile duplicate idempotency or existing settlement.
- If duplicate idempotency lacks an existing entry id, surface controlled accounting error and alert.

## States And Ownership

Do not introduce new states.

AI Job lifecycle states currently include:

- `cancel_requested`: AI Job cancellation intent accepted; execution may still need cooperative stop.
- `cancelled`: AI Job execution is cancelled/finalized, but reserved-credit settlement may still be pending.
- `release_pending`: AI Job accounting release is required or in progress.
- `released`: AI Job terminal accounting state after release settlement.

Ledger states/entry types currently include:

- `credit_reserve` with status `reserved`.
- `credit_release` with status `available`.
- `credit_consume` with status `consumed`.

`release_pending` and `released` are AI Job lifecycle states. Ledger release is represented by a `credit_release` entry and settlement metadata, not by an AI Job state alone.

## Error Handling Contract

| Condition | Required behavior |
|---|---|
| Ledger failure before release entry exists | Keep or return to retryable internal state; do not set `release_entry_id`; retry with same deterministic key. |
| Duplicate idempotency without `existing_entry_id` | Raise controlled accounting error; do not claim release success; alert for investigation. |
| Job consumed between cancel and release | Reject release; never release consumed credits; preserve consume settlement. |
| Job not found | Treat as tenant-scoped not found; do not leak cross-tenant existence. |
| Tenant mismatch | Same as not found for public-facing paths; internal paths must log trusted context only. |
| State not eligible | Reject release and do not call ledger. |
| Concurrent release attempts | Row lock plus deterministic idempotency must converge to one release. |
| Concurrent consume and release | Ledger reservation settlement must allow only one winner; loser must receive controlled conflict/error. |
| Retry after partial failure | Safe retry must not create duplicate ledger entries and must reconcile valid existing settlement. |

## Public API Contract

`POST /api/v1/ai-jobs/{job_id}/cancel` must remain a cancellation-intent endpoint.

It must not accept:

- `release_credits`
- `release_pending`
- `release_required`
- `organization_id`
- `job_id` in the request body
- `requested_by`
- Any equivalent release-forcing flag

It must not expose a public release endpoint for cancellation settlement.

It may return release-related information only if the information comes from trusted persisted backend state and cannot be influenced by the request payload. If exposed later, fields must be read-only status indicators, not commands.

## Internal Components For Later Phases

Potential internal components:

- Internal orchestration method that decides whether a cancelled job should move to release processing.
- Internal worker/background job that processes `cancel_requested`, `cancelled`, or `release_pending` jobs.
- Reconciliation command for jobs with reservation linkage but missing `release_entry_id`.
- Internal scheduler to retry failed release settlements.
- Admin-only operation for audited repair, not public refund control.
- Internal event/outbox record for cancellation accepted and release required.

None of these are implemented by this document.

## Idempotency And Concurrency

### Double Cancel

`request_cancel_ai_job(...)` is already idempotent for `cancel_requested` and `cancelled`. Future orchestration must preserve that behavior and must not turn a cancel replay into a client-triggered release command.

### Double Release

Release must be invoked only through `release_cancelled_ai_job_reserved_credits(...)` or a later wrapper with equivalent guarantees:

- Check `release_entry_id` first.
- Use `reservation_entry_id`.
- Use deterministic caller key.
- Reconcile duplicate idempotency safely.
- Persist `release_entry_id` exactly once.

### Release After Consume

Release must be rejected when:

- `consume_entry_id` exists.
- `consumed_credits > 0`.
- Ledger reservation already has a consume settlement.

### Consume After Cancel Requested

Future worker integration must guard execution/consume paths after cancellation intent. A job in `cancel_requested` should not be consumed unless a later explicit policy defines a safe race winner and tests it.

### Worker And Cancellation Race

For `running` jobs, cancellation is cooperative. The worker must observe `cancel_requested`, stop safely, and only then allow release processing. If execution succeeds first and consumption becomes required, cancellation release must not run.

### Retry After Partial Error

Retries must use the same deterministic release key for the same `organization_id`, `job_id`, and `reservation_entry_id`. A retry that sees an existing valid release must converge to idempotent success.

## Tests Required For Next Implementation

Minimum service tests:

- `request_cancel_ai_job(...)` still does not call release until orchestration phase explicitly changes it.
- Future internal orchestration does not accept release amount from public payload.
- `reserved` cancellation leaves a state that internal release can process safely.
- `queued` cancellation leaves a state that internal release can process safely after finalization.
- `running` cancellation does not release before execution is stopped.
- Release failure leaves job retryable and does not set `release_entry_id`.
- Re-run after release does not create a second ledger entry.
- Duplicate idempotency with valid existing entry reconciles.
- Duplicate idempotency without existing entry raises controlled error.
- Consumption settlement blocks release.
- Release settlement blocks later consumption.

Minimum route/API tests:

- Public cancel route still rejects `release_credits`.
- Public cancel route still rejects `release_pending`.
- Public cancel route still rejects `release_required`.
- Public cancel route still rejects `organization_id` in body/query.
- Public cancel route does not call `release_cancelled_ai_job_reserved_credits(...)` unless a future contract explicitly changes that.
- No public release endpoint is added for cancellation settlement.

Minimum worker/background tests for later phases:

- Worker does not consume a job that is already `cancel_requested`.
- Worker finalizes `cancel_requested -> cancelled -> release_pending -> released` for reserved jobs.
- Worker retry after ledger duplicate converges to one `release_entry_id`.
- Worker logs and retries ledger failure without double settlement.
- Concurrent worker runs produce one ledger release.

Minimum integration tests:

- Concurrent release/release for one reservation creates one release settlement.
- Concurrent consume/release for one reservation creates one settlement and controlled conflict for the loser.
- Tenant mismatch cannot release another tenant's reservation.
- `reserved_active` decreases once and only once.

## Risks

- Coupling the public API to ledger settlement can increase latency and expose users to accounting transient failures.
- Synchronous release in the HTTP path can create ambiguous responses if cancellation succeeds but ledger settlement fails.
- Double settlement risk exists if any future path bypasses reservation-linked release or deterministic idempotency.
- `cancelled` versus `released` can become ambiguous unless docs and response fields distinguish execution cancellation from accounting settlement.
- There is no real queue/worker integration yet, so automatic release orchestration must not be assumed.
- Running-job cancellation remains cooperative; premature release could conflict with execution success or consumption.
- Lack of outbox/reconciliation can leave partial failures requiring manual operational repair.
- Exposing release flags in public payloads would create a refund-control surface and must remain forbidden.

## Recommended Next Phase

Recommended next implementation phase:

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.ORCHESTRATION.SERVICE.PHASE4.IMPLEMENTATION.1
```

Scope for that phase should be small:

- Keep the public cancel route unchanged.
- Add an internal orchestration function or internal worker-adapter function only.
- Use `release_cancelled_ai_job_reserved_credits(...)` as the only release path.
- Add focused unit tests for retry, failure, and idempotency.
- Add PostgreSQL concurrency integration tests before enabling any automatic worker path.

Related future contract phase:

```text
CID.SAAS.AI.JOB.CANCELLATION.WORKER.CANCELLED.GUARD.CONTRACT.AUDIT.1
```

This should define how execution workers stop or skip consumption after `cancel_requested`.
