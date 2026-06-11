# CID AI Job Cancellation Contract v1

## Objective
Define the technical contract for cancelling AI Jobs (by user or system) before implementing the runtime. This covers status transitions, credit release semantics, concurrency guarantees, idempotency, and the future API surface.

## Current State of Cancellation Code

### What exists
- **AIJob model** (`src/models/ai_job.py:98-99`): `cancel_requested_at` (nullable `DateTime`) and `cancelled_at` (nullable `DateTime`) columns present.
- **Status constants** (`src/services/ai_job_status_service.py:13-14`): `AI_JOB_STATUS_CANCEL_REQUESTED = "cancel_requested"` and `AI_JOB_STATUS_CANCELLED = "cancelled"` defined.
- **Allowed transitions** (`src/services/ai_job_status_service.py:100-127`):
  - `RESERVED -> CANCEL_REQUESTED`
  - `QUEUED -> CANCEL_REQUESTED`
  - `RUNNING -> CANCEL_REQUESTED`
  - `CANCEL_REQUESTED -> CANCELLED`
  - `CANCELLED -> RELEASE_PENDING`
- **Timestamp mapping** (`src/services/ai_job_transition_service.py:45-46`): `cancel_requested_at` mapped for `CANCEL_REQUESTED`, `cancelled_at` mapped for `CANCELLED`.
- **History events** (`src/services/ai_job_async_orchestration_service.py:714-715`): `cancel_requested`/`cancelled` events with timestamps included in history derivation.
- **`cancel_ai_job()` in orchestration service** (`src/services/ai_job_async_orchestration_service.py:510-521`): exists but transitions directly to `CANCELLED` — does NOT set `cancel_requested` first.
- **`_execute_cancel()` in mock worker** (`src/services/ai_job_worker_mock_service.py:197-245`): requires `status=="cancel_requested"` as precondition (line 209), then calls `cancel_ai_job()`, `mark_release_pending()`, and `release_ai_job_credits()`.
- **Attempt model** (`src/models/ai_job_execution_attempt.py:16,29`): `ATTEMPT_STATUS_CANCELLED`, `ATTEMPT_MODE_CANCEL` defined.
- **Wrapper execution service** (`src/services/ai_job_worker_mock_execution_service.py:31-35,209-210`): `ATTEMPT_STATUS_CANCELLED` included in `TERMINAL_REPLAY_STATUSES`; `_apply_worker_result()` handles `mode="cancel"` setting `attempt.status = ATTEMPT_STATUS_CANCELLED`.
- **Release idempotency** (`src/services/ai_job_accounting_gateway.py:74-91`): `build_idempotency_key()` constructs `ai_job:<org>:<job>:release:<caller_key>`; release is idempotent via ledger idempotency_key unique constraint.

### What is missing / broken
1. **No `request_cancel_ai_job()` service method** — `cancel_ai_job()` jumps directly to `CANCELLED` without an intermediate `cancel_requested` phase.
2. **`cancel_ai_job()` skips `cancel_requested` status** — the allowed transition graph expects `cancel_requested` first, but the orchestration service bypasses it.
3. **No cancel route for AI Jobs** — the mock trigger route (`internal_ai_job_worker_mock_routes.py`) only has `POST /mock-worker/execute`; no cancel endpoint exists.
4. **No cancel endpoint in mock trigger schema** — `AIJobWorkerMockExecuteRequest` has no cancel-specific fields or separate schema.
5. **`cancel_requested` cannot be set** — no code path sets `status=cancel_requested`; the column `cancel_requested_at` is always `NULL` in practice.
6. **`_execute_cancel()` has unreachable precondition** — requires `status=="cancel_requested"` (line 209) but nothing sets it, making the cancel codepath dead.

## Proposed Cancellation Policy

### Two-Phase Cancellation Flow

```
cancel_requested -> CANCELLED -> RELEASE_PENDING -> RELEASED
```

Phase 1 (`request_cancel_ai_job`): Validates job is in a cancelable state and transitions to `cancel_requested`. Sets `cancel_requested_at` timestamp. Does NOT modify credits.

Phase 2 (worker mock or real worker): Detects `cancel_requested`, stops execution, transitions to `CANCELLED`, then `RELEASE_PENDING`, then releases credits to `RELEASED`.

### Cancelable Statuses

| Current Status | Cancelable? | Phase 1 Target | Credit Action |
|---|---|---|---|
| `created` | YES | `CANCELLED` (direct) | None (no reservation) |
| `estimated` | YES | `CANCELLED` (direct) | None (no reservation) |
| `credit_checked` | YES | `CANCELLED` (direct) | None (no reservation) |
| `reserved` | YES | `cancel_requested` | Release reserved credits in Phase 2 |
| `queued` | YES | `cancel_requested` | Release reserved credits in Phase 2 |
| `running` | YES | `cancel_requested` | Release reserved credits in Phase 2 |
| `cancel_requested` | YES (idempotent) | No-op | No-op |
| `succeeded` | NO (409 Conflict) | — | — |
| `partial_succeeded` | NO (409 Conflict) | — | — |
| `failed` | NO (409 Conflict) | — | — |
| `cancelled` | YES (idempotent) | No-op | No-op |
| `consume_pending` | NO (409 Conflict) | — | — |
| `consumed` | NO (409 Conflict) | — | — |
| `release_pending` | NO (409 Conflict) | — | — |
| `released` | NO (409 Conflict) | — | — |
| `retry_pending` | NO (409 Conflict) | — | — |
| `expired` | NO (409 Conflict) | — | — |

### Pre-Reservation Cancel (created / estimated / credit_checked)

Transition directly to `CANCELLED` without `cancel_requested`. No credit release needed because no reservation exists.

### Post-Reservation Cancel (reserved / queued / running)

Two-phase:
1. `request_cancel_ai_job`: transition to `cancel_requested`. Sets `cancel_requested_at`.
2. Cancel handler (worker mock): transition to `CANCELLED`, `RELEASE_PENDING`, then `release_reserved_credits()` with idempotency_key `ai_job:<org>:<job>:release:<execution_attempt_id>`.

### Post-Consumption Cancel

Jobs that have already succeeded, consumed, released, or expired are NOT cancelable. No automatic refund; separate compensation policy required.

### Terminal Jobs

`SUCCEEDED` / `FAILED` / `CONSUMED` / `RELEASED` / `EXPIRED`: return 409 Conflict.

## Credits Policy for Cancellation

### Release Trigger
Credit release happens during the `CANCELLED -> RELEASE_PENDING -> RELEASED` transition sequence, NOT during `request_cancel_ai_job`.

### Idempotency Key for Release
```
ai_job:<organization_id>:<job_id>:release:<execution_attempt_id>
```
Built by `AIJobAccountingGateway.build_idempotency_key(action="release", ...)` with `caller_key=execution_attempt_id`.

### Idempotency Guarantee
`CreditLedgerService.release_reserved_credits()` is idempotent by `idempotency_key` (unique constraint on CreditLedgerEntry). Replaying the same release key returns the same `CreditReleaseResult` with the existing `ledger_entry_id`.

### Credit Amount
Default: `reserved_credits` from the job. Caller can override via `release_credits` parameter in cancel command.

## Concurrency Guarantees

### Insert-First Strategy
The wrapper execution service (`AIJobWorkerMockExecutionService.execute()`) uses `session.begin_nested()` savepoint for attempt creation. On `IntegrityError` (unique constraint violation on `uq_ai_job_execution_attempts_org_job_attempt`), the savepoint rolls back and the handler retrieves the existing attempt for replay or conflict detection.

### FOR UPDATE Lock
`_load_job_for_mutation()` in orchestration service uses `repository.get_for_update()` which applies `SELECT ... FOR UPDATE` — preventing concurrent status transitions on the same job row.

### Same-Payload Replay
Same `(organization_id, job_id, execution_attempt_id)` with identical fingerprint is idempotent: terminal replay returns the stored result, in-progress raises 409.

### Same-Key Different-Payload
Same `(organization_id, job_id, execution_attempt_id)` with different fingerprint raises 409 FingerprintMismatch.

### Cancel Idempotency
Cancel idempotency key: `(organization_id, job_id, execution_attempt_id)` with mode="cancel" in fingerprint. Replaying cancel with same attempt id returns stored terminal result.

### Concurrent Cancel vs. Execution
- If both arrive with different execution_attempt_ids: both succeed independently (two distinct attempts).
- If both arrive with same execution_attempt_id: insert-first wins, second gets replay or conflict.
- If cancel arrives while execution is running with different attempt_id: job status conflict (cancel requires `cancel_requested`, execution requires `QUEUED`/`RUNNING`). FOR UPDATE lock ensures one wins.

## Future API Contract: `request_cancel_ai_job`

### Endpoint
```
POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/cancel
```

### Permission Model
Same as existing mock trigger (`_ensure_internal_caller`): requires `auth_method == "internal_api_key"`. `include_in_schema=False` (internal only).

### Request Schema
```json
{
  "execution_attempt_id": "str (required)",
  "release_credits": "int | null (default: reserved_credits)",
  "mock_error_code": "str | null",
  "mock_error_message": "str | null",
  "requested_by": "str | null (default: from tenant or 'internal_trigger')"
}
```

### Response Schema
```json
{
  "organization_id": "str",
  "job_id": "str",
  "mode": "cancel",
  "status": "str (final job status after cancel flow)",
  "replay": "bool",
  "attempt_status": "str",
  "released_credits": "int | null",
  "release_entry_id": "str | null",
  "error_metadata": "dict | null"
}
```

### Error Codes
| HTTP | Condition |
|---|---|
| 400 | Invalid payload (missing fields, bad types) |
| 404 | Job not found |
| 409 | Job not in cancelable state |
| 409 | Execution attempt conflict (in-progress / fingerprint mismatch) |
| 500 | Replay failure or unexpected error |

### Flow
1. Validate internal caller (`_ensure_internal_caller`).
2. Reject forged `organization_id` in query params.
3. Resolve `requested_by` from tenant or default `"internal_trigger"`.
4. Build `AIJobWorkerMockCommand` with `mode="cancel"`.
5. Call `AIJobWorkerMockExecutionService.execute()` which:
   a. Creates attempt record with mode="cancel" (insert-first).
   b. On first execution: calls `AIJobWorkerMockService._execute_cancel()` which verifies `cancel_requested` status, transitions to CANCELLED, RELEASE_PENDING, then releases credits.
   c. On replay: returns stored result if terminal, raises conflict if in-progress or fingerprint mismatch.

## Decision Table

| Condition | Action | Result |
|---|---|---|
| Job status = created | Direct to CANCELLED | No credit change |
| Job status = estimated | Direct to CANCELLED | No credit change |
| Job status = credit_checked | Direct to CANCELLED | No credit change |
| Job status = reserved | request_cancel -> cancel_requested | Credits released in Phase 2 |
| Job status = queued | request_cancel -> cancel_requested | Credits released in Phase 2 |
| Job status = running | request_cancel -> cancel_requested | Credits released in Phase 2 |
| Job status = cancel_requested | Idempotent no-op | No change |
| Job status = cancelled | Idempotent no-op | No change |
| Job status = succeeded | 409 Conflict | Reject |
| Job status = partial_succeeded | 409 Conflict | Reject |
| Job status = failed | 409 Conflict | Reject |
| Job status = consume_pending | 409 Conflict | Reject |
| Job status = consumed | 409 Conflict | Reject |
| Job status = release_pending | 409 Conflict | Reject |
| Job status = released | 409 Conflict | Reject |
| Job status = retry_pending | 409 Conflict | Reject |
| Job status = expired | 409 Conflict | Reject |
| Same attempt_id, same fingerprint | Replay | Return stored result |
| Same attempt_id, different fingerprint | 409 Conflict | FingerprintMismatch |
| Same attempt_id, in-progress | 409 Conflict | InProgress |
| Concurrent cancel + execute, diff attempt_ids | Both succeed | Two distinct attempts |
| Concurrent cancel + execute, same attempt_id | Insert-first wins | Second gets replay/conflict |

## Risks and Limitations

1. **Cooperative cancellation only**: The cancellation is cooperative, not a hard kill. A RUNNING job that ignores `cancel_requested` will not be forcibly terminated. The worker must poll for `cancel_requested`.

2. **No automatic refund for consumed credits**: Jobs that have already consumed credits are not refunded by cancellation. A separate compensation policy is required for post-consumption refunds.

3. **Mock worker cancel precondition**: `_execute_cancel()` currently requires `status=="cancel_requested"` (line 209). This is correct once `request_cancel_ai_job()` is implemented, but is currently a dead path.

4. **No real queue integration**: The contract covers the mock worker only. Real queue cancel (e.g., Celery, Redis, RabbitMQ) requires a separate contract.

5. **`cancel_ai_job()` skips RELEASE_PENDING**: The current `cancel_ai_job()` in orchestration service transitions directly to `CANCELLED` and does not go through `release_pending`. The mock worker's `_execute_cancel()` handles this externally by calling `mark_release_pending()` then `release_ai_job_credits()` after `cancel_ai_job()`.

## Recommended Next Phases

### Phase 1 — Implement `request_cancel_ai_job()` service method
- Add `request_cancel_ai_job()` to `AIJobAsyncOrchestrationService` that transitions to `cancel_requested` (not directly to `CANCELLED`).
- Validate job is in a cancelable state per the decision table.
- Set `cancel_requested_at` timestamp.
- Pre-reservation cancel (created/estimated/credit_checked): skip `cancel_requested`, go direct to `CANCELLED`.

### Phase 2 — Add cancel route to internal mock trigger
- Add `POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/cancel` route in `internal_ai_job_worker_mock_routes.py`.
- Add cancel request/response schemas.
- Register route with existing guard middleware.

### Phase 3 — Extend wrapper unit tests with mode=cancel coverage
- Unit tests for wrapper with `mode="cancel"`.
- Verify replay works for cancelled attempts.
- Verify fingerprint mismatch for changed cancel payload.
- Verify in-progress conflict for concurrent cancel.

### Phase 4 — Extend PostgreSQL integration tests with mode=cancel coverage
- Integration test: cancel flow end-to-end (request_cancel -> execute cancel).
- Integration test: concurrent same-key cancel idempotency.
- Integration test: cancel after reservation (credit release verification).
- Integration test: cancel on pre-reservation job (no credit release).
- Integration test: cancel conflict on terminal job (409).

### Phase 5 — Credit release integration tests for cancel
- Verify `release_reserved_credits()` called with correct idempotency_key.
- Verify idempotent replay of release during cancel replay.
- Verify cancel with explicit `release_credits` override.

### Phase 6 — Formalize cancel route API contract
- OpenAPI spec for cancel endpoint.
- Document in API reference.

### Phase 7 — Design real queue cancel contract
- Contract for Celery/Redis/RabbitMQ cancel propagation.
- Separate from mock worker scope.
