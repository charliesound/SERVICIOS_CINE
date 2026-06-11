# CID AI Job Cancellation Credit Release Contract v1

## Status

- Documentation-only contract for a future implementation phase.
- Based on HEAD `9ae3283` (`test: harden CID AI job cancellation route gating`).
- PostgreSQL-only. Do not introduce alternate database backend behavior.
- No runtime, route, schema, service, model, migration, frontend, Docker, billing, ledger, worker, or queue changes are part of this phase.
- Base lifecycle contracts:
  - `docs/architecture/cid_ai_job_cancellation_contract_v1.md`
  - `docs/architecture/cid_ai_job_cancellation_api_contract_v1.md`

## Problem

The public AI Job cancel API currently records cancellation intent or direct cancellation state, but intentionally does not release reserved credits. This leaves reserved-credit settlement as a later worker/accounting responsibility.

The next implementation phase needs a precise contract for releasing credits after cancellation without double releasing, releasing credits for the wrong tenant/job, or releasing credits that have already been consumed.

## Principle

Credit release after AI Job cancellation must be a server-side accounting settlement, not a client-controlled refund. It must be tenant-scoped, reservation-linked, idempotent, auditable, and mutually exclusive with consumption.

The public cancel route must continue to express only cancellation intent. It must not accept or honor `release_credits`, `release_pending`, `release_required`, `organization_id`, or any release-forcing flag from clients.

## Current AI Job State Policy

| Current status | Cancel API result today | Future release eligibility | Credit action at cancel request |
|---|---|---|---|
| `created` | `cancelled` | No | None; no reservation exists. |
| `estimated` | `cancelled` | No | None; no reservation exists. |
| `credit_checked` | `cancelled` | No | None; no reservation exists. |
| `reserved` | `cancel_requested` | Yes, after `cancelled -> release_pending` | None at request time. |
| `queued` | `cancel_requested` | Yes, after `cancelled -> release_pending` | None at request time. |
| `running` | `cancel_requested` | Yes, after cooperative stop and `cancelled -> release_pending` | None at request time. |
| `cancel_requested` | Idempotent no-op | Not directly; wait for worker/cancel finalization | None. |
| `cancelled` | Idempotent no-op | Yes only if reserved credits are still unsettled | None at request time. |
| `succeeded` | 409 | No cancellation release | Must follow consume flow. |
| `partial_succeeded` | 409 | No cancellation release | Must follow consume flow. |
| `failed` | 409 | Not cancellation-owned; failure release flow may apply | None. |
| `consume_pending` | 409 | No | Must finish consume flow. |
| `consumed` | 409 | No | Never release consumed credits. |
| `release_pending` | 409 | Already in release flow | Existing release worker may continue. |
| `released` | 409 | No | Already settled. |
| `retry_pending` | 409 | No cancellation release | Retry policy owns next step. |
| `expired` | 409 | Not cancellation-owned; expiry release flow may apply | None. |

Relevant current status graph from `src/services/ai_job_status_service.py`:

- `reserved -> cancel_requested`
- `queued -> cancel_requested`
- `running -> cancel_requested`
- `cancel_requested -> cancelled`
- `cancelled -> release_pending`
- `release_pending -> released`

Relevant transition accounting rule from `src/services/ai_job_transition_service.py`:

- Only transitions to `released` carry `ACCOUNTING_ACTION_RELEASE`.
- `cancelled` and `release_pending` mark lifecycle/accounting intent, but do not by themselves write ledger entries.

## Current AI Job And Ledger Relationship

`AIJob` currently stores the accounting linkage needed for future cancellation release:

| AI Job field | Purpose |
|---|---|
| `organization_id` | Tenant boundary for job and ledger operations. |
| `reserved_credits` | Reserved amount intended to be released if cancellation settles before consumption. |
| `consumed_credits` | Amount consumed after successful/partial execution. Must remain zero for cancellation release. |
| `released_credits` | Amount released after failed/cancelled/expired settlement. |
| `reservation_entry_id` | Ledger reservation entry that must be settled. Required for linked release. |
| `consume_entry_id` | Ledger consumption entry. If present, cancellation release must not proceed. |
| `release_entry_id` | Ledger release entry. If present, repeated release should be treated as already settled. |
| `cancel_requested_at` | Cooperative cancellation intent timestamp. |
| `cancelled_at` | Cancellation finalization timestamp. |
| `release_pending_at` | Timestamp for pending credit release. |
| `released_at` | Terminal accounting release timestamp. |

`AIJobAsyncOrchestrationService.release_ai_job_credits()` already performs the intended high-level operation:

- Loads the tenant-scoped job with `repository.get_for_update()`.
- Requires `reservation_entry_id`.
- Transitions `release_pending -> released`.
- Calls `AIJobAccountingGateway.release_reserved_credits_for_job()`.
- Stores `release_entry_id` and `released_credits` on the job.

## Current Ledger Audit

### Reserve

`CreditLedgerService.reserve_credits()` currently:

- Requires a positive integer amount.
- Rejects duplicate `idempotency_key` by looking up existing ledger entries.
- Creates a tenant balance if missing.
- Checks available credits before reserving.
- Increments `CreditBalance.reserved_active`.
- Creates a `credit_reserve` entry with status `reserved`.
- Stores `organization_id`, optional `project_id`, optional `user_id`, optional `job_id`, metadata, reason, and `idempotency_key`.

`AIJobAccountingGateway.reserve_credits_for_job()` builds reservation idempotency keys as:

```text
ai_job:<organization_id>:<job_id>:reserve[:<caller_key>]
```

### Release

`CreditLedgerService.release_reserved_credits()` currently:

- Requires a positive integer amount.
- Rejects duplicate `idempotency_key` by raising `DuplicateIdempotencyKeyError`.
- Reads `reservation_entry_id` from `metadata["reservation_entry_id"]` when provided.
- If reservation-linked, validates that the reservation entry:
  - belongs to the same `organization_id`
  - is a `credit_reserve` entry
  - has status `reserved`
  - has positive amount
  - matches `job_id` when `job_id` is provided
  - has no previous consume/release settlement for the same reservation
  - is not exceeded by the release amount
- Requires an existing `CreditBalance`.
- Decrements `reserved_active`.
- Creates a `credit_release` entry with status `available` and `released_at`.
- Adds settlement metadata including `reservation_entry_id`, `reservation_amount`, `settlement_amount`, `settlement_action`, and `job_id`.

`AIJobAccountingGateway.release_reserved_credits_for_job()` builds release idempotency keys as:

```text
ai_job:<organization_id>:<job_id>:release[:<caller_key>]
```

### Consume

`CreditLedgerService.consume_reserved_credits()` mirrors the linked-reservation checks used by release, then:

- Allocates debits from canonical buckets.
- Debits buckets.
- Decrements `reserved_active`.
- Increments `consumed_period`.
- Creates a `credit_consume` entry with status `consumed` and `consumed_at`.
- Adds settlement metadata with `settlement_action="consume"`.

Consumption and release are mutually exclusive because `_validate_linked_reservation()` rejects any existing settlement for the same reservation.

### Idempotency

The current ledger behavior is duplicate-key rejection, not result replay. A repeated call with the same `idempotency_key` raises `DuplicateIdempotencyKeyError` and exposes the existing ledger entry id.

Future cancellation-release code must not assume the ledger returns a successful result on replay. The orchestration layer must interpret one of these as an already-settled outcome only after verifying it belongs to the same job, same organization, same reservation, same amount, and same release action:

- Existing `AIJob.release_entry_id`.
- Existing duplicate ledger entry from `DuplicateIdempotencyKeyError.existing_entry_id`.
- Existing settlement found for the reservation.

### Metadata

Current AI Job accounting metadata includes:

- `job_id`
- `project_id`
- `user_id`
- `operation_type`
- provider/workflow/model fields
- `input_asset_ids`
- `job_status`
- `reservation_entry_id` for consume/release

Future cancellation release should add only safe audit metadata, for example:

- `settlement_reason="cancelled"`
- `cancelled_at`
- `cancel_requested_at`
- `requested_by` if already server-derived
- `cancellation_release_contract="v1"`

Do not store tokens, credentials, raw request headers, full private prompts, or sensitive user payloads in ledger metadata.

### Scoping

The ledger validates `organization_id` on reservation lookup, and `AIJobAsyncOrchestrationService` loads jobs through tenant-scoped repository methods.

Future release code must derive `organization_id` from the job or trusted tenant context. It must never trust client-supplied `organization_id`.

### Errors

Expected current ledger errors relevant to cancellation release:

| Error | Meaning for cancellation release |
|---|---|
| `InvalidCreditAmountError` | Release amount is missing, non-integer, boolean, zero, or negative. |
| `CreditReservationNotFoundError` | Job has no usable reservation linkage, or reservation belongs to another organization. |
| `CreditBalanceNotFoundError` | Tenant balance is missing despite a reservation. Treat as accounting inconsistency. |
| `CreditLedgerStateError` | Reservation is already settled, wrong type/status/job, amount exceeds reservation, or active reserved balance is insufficient. |
| `DuplicateIdempotencyKeyError` | Idempotency key already exists. Must be reconciled before treating as success. |

### Limits

- Ledger release accepts any positive `amount`; the cancellation release service must choose the amount safely.
- Linked release blocks amounts greater than the reservation amount, but partial release is technically possible today. Cancellation release should default to full reserved amount and should not expose partial release to clients.
- Current idempotency lookup is by key only. The service must validate existing-entry semantics before treating duplicate keys as replay.

## Future Release Operation Contract

Recommended next operation name:

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.SERVICE.PHASE3.IMPLEMENTATION.1
```

Recommended service behavior:

1. Load the AI Job for mutation using `organization_id + job_id` and row locking.
2. Accept release only when job status is `cancelled` or `release_pending`, with reserved credits still unsettled.
3. If status is `cancelled`, transition to `release_pending` before ledger write.
4. Require `reservation_entry_id` and positive `reserved_credits`.
5. Reject release when `consume_entry_id` is set or `consumed_credits > 0`.
6. If `release_entry_id` is already set, verify the referenced release belongs to the same organization/job/reservation and return an idempotent already-released result.
7. Build release amount from `job.reserved_credits`, not from public request data.
8. Build idempotency key through `AIJobAccountingGateway.build_idempotency_key(action="release", organization_id=job.organization_id, job_id=job.id, caller_key=<server-controlled-key>)`.
9. Call `AIJobAccountingGateway.release_reserved_credits_for_job()` with `reservation_entry_id`, `release_credits`, job metadata, and server-controlled `caller_key`.
10. Store `release_entry_id` and `released_credits` from the accounting result.
11. Transition `release_pending -> released` only after a verified ledger release or verified idempotent replay.
12. Commit job state and ledger settlement in the same database transaction.

Recommended server-controlled `caller_key`:

- For worker attempts: `execution_attempt_id`.
- For a cancellation-release sweeper: a deterministic key such as `cancel:<reservation_entry_id>`.
- Do not use a public client-provided key for release settlement.

## Idempotency Contract

Cancellation release must be idempotent across:

- Worker retry after process crash.
- Duplicate worker execution attempt replay.
- API retry that re-requests cancellation while release is already pending.
- Sweeper retry after partial failure.

Required idempotency checks:

| Existing state | Required behavior |
|---|---|
| `release_entry_id` present and valid | Return success as already released. |
| `release_entry_id` present but invalid tenant/job/reservation/action | Raise accounting inconsistency; do not write a new release. |
| Duplicate idempotency key for same release | Verify existing entry, attach if needed, and return success. |
| Duplicate idempotency key for different org/job/reservation/action/amount | Raise conflict/accounting error. |
| Existing consume settlement for reservation | Reject release; never refund through cancellation path. |
| Existing release settlement for reservation but job missing `release_entry_id` | Attach verified release entry and transition to `released`. |

## Concurrency Contract

Future cancellation release must rely on both job row locking and ledger settlement constraints:

- Use the existing repository `get_for_update()` path for AI Job mutation.
- Keep status transition, ledger release, and job release fields in one transaction.
- Do not do read-modify-write in a route adapter.
- Treat concurrent consume-vs-release as mutually exclusive. Whichever linked settlement commits first owns the reservation.
- If a second settlement observes the reservation already settled, it must verify whether the existing settlement is a release for the same cancellation or a consume that blocks release.
- Do not release credits from `running` directly. A running job must first reach `cancel_requested`, then `cancelled`, then `release_pending`.

## Consume vs Release Contract

Cancellation release is valid only before consumption. The following invariants must hold:

- `consume_entry_id` is null.
- `consumed_credits == 0`.
- No ledger `credit_consume` settlement exists for `reservation_entry_id`.
- `release_credits == reserved_credits` unless a future documented partial-release policy is explicitly implemented.
- `released_credits` must not exceed `reserved_credits`.
- Once `consumed`, cancellation release is permanently disallowed. Any customer compensation must be a separate credit-grant or refund policy, not a reservation release.

## API Contract

No public API changes are required for this phase.

Future public cancellation API must remain:

```http
POST /api/v1/ai-jobs/{job_id}/cancel
```

It must continue to:

- Derive `organization_id` from `tenant.organization_id`.
- Derive `requested_by` from trusted server context.
- Forbid forged organization fields.
- Forbid credit release controls in the request body or query.
- Return cancellation/request state, not a promise that credits have already been released.

If a future internal release endpoint or worker command is introduced, it must be internal-only, tenant-scoped, and server-authenticated. It must not be exposed as a public refund endpoint.

## Error Mapping For Future Runtime

Recommended service-to-HTTP mapping if exposed through a route or worker trigger:

| Condition | HTTP / worker result |
|---|---|
| Job not found in tenant | 404 / not found terminal error |
| Job not cancelled or release-pending | 409 / invalid state |
| Missing reservation linkage | 409 / accounting inconsistency |
| Existing consume settlement | 409 / already consumed |
| Existing valid release settlement | 200 replay / already released |
| Duplicate idempotency key with valid same release | 200 replay / already released |
| Duplicate idempotency key with incompatible entry | 409 / idempotency conflict |
| Ledger balance missing or reserved balance inconsistent | 500 or operational accounting error; alert required |
| Unexpected exception | 500; generic external message, detailed server log only |

## Tests Required For The Next Implementation Phase

Minimum unit tests:

- `cancelled -> release_pending -> released` releases full `reserved_credits`.
- `cancel_requested` cannot release until final cancellation reaches `cancelled`.
- Missing `reservation_entry_id` blocks release.
- `consume_entry_id` blocks release.
- `consumed_credits > 0` blocks release.
- Existing valid `release_entry_id` is idempotent.
- Duplicate idempotency key for same release is reconciled safely.
- Duplicate idempotency key for incompatible entry is rejected.
- Existing consume settlement for reservation blocks release.
- Public cancel route rejects `release_credits`, `release_pending`, `release_required`, and forged `organization_id`.

Minimum PostgreSQL integration tests:

- Concurrent release/release for same cancellation produces one ledger release and one idempotent replay.
- Concurrent consume/release for the same reservation produces one settlement and a deterministic conflict for the loser.
- Worker retry after ledger release but before job `release_entry_id` attachment reconciles the existing release.
- Tenant mismatch cannot release another tenant's reservation.
- `reserved_active` decreases exactly once.

Guard validations:

- database regression guard
- `bash scripts/dev/guard_wsl_repo.sh`
- `git diff --check`

## Risks Detected

- The current ledger duplicate-key behavior raises `DuplicateIdempotencyKeyError`; it does not replay a `CreditReleaseResult`. The future service must reconcile duplicates explicitly.
- A cancellation release path that accepts client-provided release amount would permit partial or unintended releases. The amount must be derived server-side from the job reservation.
- A release that bypasses `reservation_entry_id` would rely only on `reserved_active`, which is unsafe for AI Job cancellation. Cancellation release must always be reservation-linked.
- A worker crash between ledger release and job update can leave a valid ledger release without `AIJob.release_entry_id`. The next phase must implement reconciliation.
- Post-consumption customer compensation is a separate billing policy. It must not be implemented as cancellation release.

## Recommended Next Phase

Implement `CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.SERVICE.PHASE3.IMPLEMENTATION.1` as a minimal service-layer phase that:

- Adds no public release controls.
- Uses existing `AIJobAccountingGateway.release_reserved_credits_for_job()`.
- Reconciles duplicate idempotency keys and existing settlements safely.
- Adds focused unit tests and PostgreSQL concurrency tests before exposing any worker/API trigger.
