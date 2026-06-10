# CID AI Jobs Worker Mock Idempotency Hardening Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOBS.WORKER.MOCK.IDEMPOTENCY.HARDENING.CONTRACT.1
Scope: canonical contract for persistent execution_attempt_id-based idempotency for the CID AI Jobs mock worker trigger

Companion docs:

- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md`
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`
- `docs/architecture/cid_database_canonical_policy_v1.md`

## 1. Purpose

This document defines the future design for persistent idempotency based on `execution_attempt_id` for the CID AI Jobs mock worker execution trigger.

The idempotency hardening exists to:

- prevent duplicate settlement (consume or release) when the same worker command is retried;
- prevent duplicate execution transitions when the same `execution_attempt_id` is reused;
- detect conflicting payloads reusing the same `execution_attempt_id`;
- reject cross-tenant and cross-job reuse attempts;
- provide a deterministic replay path for terminals and a safe conflict path for active attempts;
- integrate with the existing trigger, worker mock, orchestration, accounting gateway, and ledger idempotency layers.

This phase is documentary only. It does not implement the model, migration, repository, service, route updates, or integration tests.

## 2. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `src/services/ai_job_worker_mock_service.py`
- `src/routes/internal_ai_job_worker_mock_routes.py`
- `src/schemas/ai_job_worker_mock_api_schema.py`
- `src/dependencies/ai_job_worker_mock.py`
- `src/services/ai_job_async_orchestration_service.py`
- `src/services/ai_job_accounting_gateway.py`
- `src/services/credit_ledger_service.py`
- `src/repositories/ai_job_repository.py`
- `src/models/ai_job.py`
- `src/models/billing.py`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md`
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`

Observed relevant implementation facts:

- `AIJobWorkerMockService.execute(session, command)` receives `execution_attempt_id` in the command and passes it as `caller_key` to settlement methods, but does not persist attempt replay state.
- The V1 worker mock service is stateless: retrying the same `execution_attempt_id` will re-execute the full flow and rely on downstream ledger idempotency to prevent duplicate settlement.
- The internal trigger route (`POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute`) constructs `AIJobWorkerMockCommand` from the request and tenant context, then calls `worker.execute(db, command)`.
- `AIJobAsyncExecutionTransitionRequest.execution_attempt_id` is stored in `job.job_metadata["execution"]["execution_attempt_id"]` via `_build_execution_metadata()`.
- The accounting gateway builds idempotency keys as `ai_job:{organization_id}:{job_id}:{action}[:caller_key]` and the caller key is the `execution_attempt_id`.
- `CreditLedgerService._get_existing_entry_by_idempotency_key` does a global lookup on `idempotency_key` without `organization_id` filtering at the query level. The `CreditLedgerEntry` model has `UniqueConstraint("idempotency_key")` globally, not tenant-scoped.
- `AIJobRepository` does not have an execution attempt table or repository.
- `AIJob` model has `attempt_number` (integer) and `job_metadata` (JSON) but no dedicated attempt tracking table.
- `credit_ledger_entries` has a global `UniqueConstraint("idempotency_key")` — this is a known gap documented in `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`.

## 3. Problem Statement

### 3.1 Current V1 Behavior

The current V1 mock worker passes `execution_attempt_id` as the `caller_key` to ledger settlement. This provides downstream idempotency at the ledger level: if the same `execution_attempt_id` reaches `consume` or `release`, the ledger's `DuplicateIdempotencyKeyError` prevents double settlement.

However, V1 has the following gaps:

1. **No attempt replay store.** If the trigger is called twice with the same `execution_attempt_id`, the worker mock service re-executes the full orchestration flow (enqueue, start, succeed, mark consume pending, consume). The orchestration transitions are not themselves idempotent — they may fail or produce unexpected state because the job is already in a later status.

2. **No payload fingerprint.** A retry with the same `execution_attempt_id` but a different payload (different `mode`, different `mock_output_metadata`, different credit amounts) is not detected until it hits the ledger idempotency check, and even then only for settlement — not for execution transitions.

3. **Cross-tenant or cross-job reuse of `execution_attempt_id` is not explicitly enforced.** The V1 worker validates `organization_id` and `job_id` per call, but there is no persistent record that would detect reuse of the same `execution_attempt_id` for a different tenant or job across separate requests.

4. **In-progress concurrency is not handled.** If two concurrent requests arrive with the same `execution_attempt_id`, both may pass the initial check before either persists a result, leading to a race.

5. **No replay for terminal results.** If a retry arrives after the first attempt completed (terminal status), the service attempts to execute transitions that are now invalid because the job is already in a terminal state.

### 3.2 Scope Boundaries

This contract defines the future idempotency layer. It does not change downstream ledger idempotency. The two-layer design is intentional:

- **Attempt store layer** (this contract): deduplicates, fingerprints, and controls replay for the worker mock execution attempt itself.
- **Ledger layer** (existing + `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`): deduplicates settlement entries by `idempotency_key`.

Both layers are required. Neither layer alone is sufficient.

## 4. Canonical Identity: Effective Idempotency Key

### 4.1 Key Structure

The effective idempotency key for a worker mock execution attempt is:

```
(organization_id, job_id, execution_attempt_id)
```

All three components are mandatory. None may be null, empty, or defaulted.

### 4.2 Why Not execution_attempt_id Alone

`execution_attempt_id` alone is insufficient because:

- A caller might accidentally reuse the same UUID across two different jobs in the same tenant.
- A caller might reuse the same UUID across two different tenants (e.g., a test harness with a fixed attempt id).
- Without `organization_id` and `job_id` in the key, a retry for the right attempt but wrong job would not be detected.

Adding `organization_id` and `job_id` makes the key tenant-scoped and job-scoped, consistent with the rest of the CID idempotency policy.

### 4.3 Key Derivation

The future implementation should derive a deterministic, stored key for database lookup. The recommended format is:

```
mock_exec:{organization_id}:{job_id}:{execution_attempt_id}
```

This format is a plain string suitable for a unique index or unique constraint.

### 4.4 Relationship to Gateway/Ledger Keys

The gateway derives ledger keys as `ai_job:{organization_id}:{job_id}:{action}[:caller_key]`. The attempt store key is different and independent:

- Attempt store key: `mock_exec:{organization_id}:{job_id}:{execution_attempt_id}` — used for attempt replay and conflict detection.
- Gateway settle key: `ai_job:{organization_id}:{job_id}:consume:{execution_attempt_id}` (or `:release:`) — used for ledger idempotency.

The attempt store check happens first (before execution). The ledger check happens during settlement. Both must pass for a clean execution.

## 5. Payload Fingerprint

### 5.1 Purpose

A payload fingerprint enables the system to detect when the same `execution_attempt_id` is retried with a different request body. This prevents:

- silent corruption from a retry that changes `mode` (e.g., first call was `success`, retry is `failure`);
- silent credit manipulation from a retry that changes `actual_credits` or `release_credits`;
- silent metadata mutation from a retry that changes `mock_output_metadata` or `mock_error_*` fields.

### 5.2 Fingerprint Specification

The fingerprint must be a SHA-256 hex digest over a canonical JSON representation of select request fields.

**Fields included in the fingerprint:**

| Field | Type | Reason |
|---|---|---|
| `mode` | string | Changing execution mode between retries is a conflict |
| `simulated_duration_ms` | int or null | Affects observable behavior |
| `mock_output_metadata` | dict or null | Changing output shape is a conflict |
| `mock_error_code` | string or null | Changing error semantics is a conflict |
| `mock_error_message` | string or null | Changing error messaging is a conflict |
| `actual_credits` | int or null | Changing credit amount is a conflict |
| `release_credits` | int or null | Changing release amount is a conflict |

**Fields excluded from the fingerprint:**

| Field | Reason |
|---|---|
| `organization_id` | Part of the key, not the payload |
| `job_id` | Part of the key, not the payload |
| `execution_attempt_id` | Part of the key, not the payload |
| `requested_by` | Convenience field, may differ on retry from different actors |

### 5.3 Canonical JSON Requirements

The canonical JSON form must:

- serialize to a UTF-8 byte string;
- sort keys alphabetically at all nesting levels;
- omit keys with `null` values;
- use compact encoding (no whitespace);
- encode integers as JSON numbers (not strings);
- encode strings as JSON strings.

Pseudocode:

```python
import hashlib, json

def compute_fingerprint(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

### 5.4 Schema Versioning

The fingerprint specification is versioned. The version number must be stored alongside the fingerprint in the attempt record.

Initial version: `v1` as defined above.

When the fingerprint specification changes (fields added, removed, or format updated), the version increments. The implementation must handle multiple versions during migration windows.

### 5.5 Comparison Rule

On retry:
1. Look up the existing attempt record by `(organization_id, job_id, execution_attempt_id)`.
2. Compute the fingerprint of the incoming request.
3. Compare with the stored fingerprint.
4. If fingerprints match under the same schema version: proceed with replay (terminal) or safe retry (in-progress).
5. If fingerprints differ: raise a conflict error (`409 Conflict`).

## 6. Future Attempt States

### 6.1 Canonical Attempt States

The execution attempt record must track its own status independently of the job status.

Proposed attempt states:

| State | Meaning |
|---|---|
| `in_progress` | The attempt has been created but not yet completed or settled |
| `succeeded` | The attempt completed with `mode=success`, consume settled |
| `failed` | The attempt completed with `mode=failure`, release settled |
| `cancelled` | The attempt completed with `mode=cancel`, release settled |
| `conflicted` | The attempt was explicitly rejected due to a conflict (fingerprint mismatch) |

### 6.2 State Transition Map

```
created -> in_progress  (first insert succeeds)
in_progress -> succeeded (consume settled)
in_progress -> failed    (release settled)
in_progress -> cancelled (release settled)
any -> conflicted        (rejected by conflict detection)
```

### 6.3 Terminal States

Terminal attempt states are: `succeeded`, `failed`, `cancelled`, `conflicted`.

A retry for a terminal state must not re-execute execution transitions or settlement. It must return the stored result (replay).

### 6.4 Non-Terminal States

`in_progress` means the attempt was created but the execution flow did not complete (possibly crashed, timed out, or is still running).

A retry for `in_progress` must either:
- block with a `409 Conflict` if the previous attempt may still be running (conservative);
- or skip re-execution if the attempt can be proven dead and the caller re-authorizes.

The conservative choice (block with 409) is recommended for V1.

## 7. Future Model/Table Recommendation

### 7.1 Recommended Table: ai_job_execution_attempts

A new table to store execution attempt records, separate from the `ai_jobs` table.

### 7.2 Recommended Columns

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `String(36)` | PK, default UUID4 hex | Internal primary key |
| `organization_id` | `String(36)` | NOT NULL, indexed | Tenant scope |
| `job_id` | `String(36)` | NOT NULL, FK to ai_jobs(id) | Job this attempt belongs to |
| `execution_attempt_id` | `String(255)` | NOT NULL | External attempt idempotency key |
| `mode` | `String(20)` | NOT NULL | `success`, `failure`, or `cancel` |
| `status` | `String(20)` | NOT NULL, default `in_progress` | Attempt lifecycle status |
| `fingerprint` | `String(64)` | NOT NULL | SHA-256 hex digest |
| `fingerprint_version` | `String(10)` | NOT NULL, default `v1` | Schema version for fingerprint |
| `payload_digest` | `String(64)` | NOT NULL | SHA-256 of the raw request body for audit |
| `requested_by` | `String(100)` | NULLABLE | Who triggered this attempt |
| `result_status` | `String(20)` | NULLABLE | Final job status after attempt completion |
| `consume_entry_id` | `String(36)` | NULLABLE | Ledger consume entry id if settled |
| `release_entry_id` | `String(36)` | NULLABLE | Ledger release entry id if settled |
| `consumed_credits` | `Integer` | NULLABLE | Credits consumed in this attempt |
| `released_credits` | `Integer` | NULLABLE | Credits released in this attempt |
| `error_message` | `Text` | NULLABLE | Safe error description if attempt failed |
| `started_at` | `DateTime` | NULLABLE | When the attempt began execution |
| `finished_at` | `DateTime` | NULLABLE | When the attempt reached terminal status |
| `created_at` | `DateTime` | NOT NULL, default now | Row creation timestamp |

### 7.3 Recommended Indexes and Constraints

```sql
-- Primary key
PRIMARY KEY (id)

-- Unique constraint: the effective idempotency key
UNIQUE (organization_id, job_id, execution_attempt_id)

-- Foreign key to ai_jobs
FOREIGN KEY (job_id) REFERENCES ai_jobs(id)

-- Lookup by job for history
INDEX (job_id, created_at)

-- Lookup by organization for admin queries
INDEX (organization_id, created_at)

-- Lookup by status for retry/dead-letter processing
INDEX (status, created_at)
```

### 7.4 Check Constraints

```sql
-- Ensure mode is valid
CHECK (mode IN ('success', 'failure', 'cancel'))

-- Ensure status is valid
CHECK (status IN ('in_progress', 'succeeded', 'failed', 'cancelled', 'conflicted'))

-- Ensure finish timestamp is consistent
CHECK (finished_at IS NULL OR finished_at >= started_at)
```

### 7.5 ORM Model Recommendation

```python
class AIJobExecutionAttempt(Base):
    __tablename__ = "ai_job_execution_attempts"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "job_id", "execution_attempt_id",
            name="uq_ai_job_exec_attempt_org_job_attempt",
        ),
        CheckConstraint(
            "mode IN ('success', 'failure', 'cancel')",
            name="ck_ai_job_exec_attempts_mode",
        ),
        CheckConstraint(
            "status IN ('in_progress', 'succeeded', 'failed', 'cancelled', 'conflicted')",
            name="ck_ai_job_exec_attempts_status",
        ),
        Index("ix_ai_job_exec_attempts_job_created", "job_id", "created_at"),
        Index("ix_ai_job_exec_attempts_org_created", "organization_id", "created_at"),
        Index("ix_ai_job_exec_attempts_status_created", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_hex)
    organization_id: Mapped[str] = mapped_column(String(36), nullable=False)
    job_id: Mapped[str] = mapped_column(String(36), nullable=False)
    execution_attempt_id: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    fingerprint_version: Mapped[str] = mapped_column(String(10), nullable=False, default="v1")
    payload_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    result_status: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    consume_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    release_entry_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    consumed_credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    released_credits: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
```

## 8. Replay Behavior

### 8.1 When Replay Applies

Replay applies when a retry arrives and the existing attempt record is in a **terminal state** (`succeeded`, `failed`, `cancelled`, `conflicted`).

### 8.2 Terminal Replay Matrix

| Attempt Record | Incoming Request | Behavior | HTTP Status |
|---|---|---|---|
| `succeeded` | same `mode=success`, same fingerprint | Return stored result, no re-execution | `200 OK` |
| `succeeded` | different `mode` or different fingerprint | Conflict: fingerprint mismatch | `409 Conflict` |
| `failed` | same `mode=failure`, same fingerprint | Return stored result, no re-execution | `200 OK` |
| `failed` | different `mode` or different fingerprint | Conflict: fingerprint mismatch | `409 Conflict` |
| `cancelled` | same `mode=cancel`, same fingerprint | Return stored result, no re-execution | `200 OK` |
| `cancelled` | different `mode` or different fingerprint | Conflict: fingerprint mismatch | `409 Conflict` |
| `conflicted` | any | Return stored conflict result or re-conflict | `409 Conflict` |

### 8.3 Replay Response Shape

On replay, the response must include all fields that the original success response included, plus an indication that this is a replay.

Proposed additional field:

```json
{
  "replay": true,
  "original_status": "succeeded",
  "original_timestamp": "2026-06-10T12:00:00Z"
}
```

### 8.4 Replay without Re-execution

When replay is detected:

1. Do not call `AIJobWorkerMockService.execute()`.
2. Do not call any orchestration method.
3. Do not call any gateway or ledger method.
4. Return the stored result directly from the attempt record.

This ensures that replays are safe, fast, and do not double-settle even if downstream idempotency were compromised.

## 9. In-Progress Conflict Behavior

### 9.1 When Conflict Applies

Conflict applies when a retry arrives and the existing attempt record is in a **non-terminal state** (`in_progress`).

### 9.2 In-Progress Conflict Strategy

Three strategies considered:

**Strategy A: Block (Conservative)**

Return `409 Conflict` with a message indicating the attempt is still in progress. This is the safest choice for V1.

```
409 Conflict
{
  "detail": "Execution attempt is already in progress",
  "execution_attempt_id": "...",
  "status": "in_progress"
}
```

**Strategy B: Wait and Re-evaluate**

Wait for a configurable timeout for the in-progress attempt to complete, then re-evaluate. This is more complex and not recommended for V1.

**Strategy C: Force Re-execution (Dangerous)**

Allow re-execution if the caller provides a force flag. This risks duplicate settlement if the original attempt completes after the re-execution starts. Not recommended.

**V1 Recommendation: Strategy A (Block).**

### 9.3 Stale Attempt Detection

If the attempt record remains `in_progress` beyond a reasonable timeout (e.g., 5 minutes), it may be considered stale. Stale attempt handling is out of scope for this contract V1 but should be addressed in a future phase.

## 10. Settlement Behavior

### 10.1 Two-Layer Idempotency

Settlement idempotency operates at two independent layers:

1. **Attempt store layer** (this contract): detects attempt replay before any execution or settlement occurs.
2. **Ledger layer** (`CreditLedgerService` + `CreditLedgerEntry`): detects duplicate settlement entries by `idempotency_key` at the moment of ledger insertion.

Both layers must be in place for full protection.

### 10.2 Settlement Write to Attempt Record

When settlement completes (consume or release), the attempt record must be updated with:

- `status` → `succeeded`, `failed`, or `cancelled`
- `result_status` → final job status (e.g., `consumed`, `released`)
- `consume_entry_id` or `release_entry_id` → ledger entry id
- `consumed_credits` or `released_credits` → actual settlement amount
- `finished_at` → current timestamp

### 10.3 Atomicity Constraint

The attempt record update must happen in the **same database transaction** as the job status update and the ledger entry insertion. If any step fails, the entire transaction rolls back, and the attempt record remains `in_progress` (or is rolled back if the attempt record insert is also in the same transaction).

### 10.4 Settlement Failure Recording

If settlement fails (e.g., `DuplicateIdempotencyKeyError` from ledger, or insufficient credits), the attempt record should be updated to record the failure:

- `status` → `conflicted` if the conflict is persistent
- `error_message` → safe description of the settlement failure

But the attempt record must not be left `in_progress` if the settlement failure is permanent.

## 11. Transaction and Concurrency Rules

### 11.1 Insert-First Strategy

The recommended concurrency strategy is **insert-first with unique constraint**.

Flow:

1. Begin transaction (caller owns the session).
2. Attempt to insert a new `AIJobExecutionAttempt` row with the unique key `(organization_id, job_id, execution_attempt_id)`.
3. If the insert succeeds (no unique violation):
   - Proceed with execution (load job, validate, transition, settle).
   - Update the attempt record with result data.
   - Commit.
4. If the insert fails with a unique violation:
   - A previous attempt exists for this key.
   - Select the existing row for read.
   - Compare fingerprints.
   - If terminal and fingerprint matches: replay (return stored result).
   - If terminal and fingerprint differs: conflict (409).
   - If in-progress: conflict (409).

### 11.2 Why Insert-First

- The PostgreSQL unique constraint is the single source of truth for first-writer wins.
- No separate locking step is needed for the initial insert.
- The insert is fast and avoids table-level contention.
- Subsequent reads for replay/conflict can use `SELECT FOR UPDATE` to lock the row during the decision.

### 11.3 SELECT FOR UPDATE on Replay

When a unique violation is detected on insert, the retry path must use `SELECT FOR UPDATE` to lock the existing attempt row before making the replay/conflict decision. This prevents a race where:

1. Request A inserts attempt record (in_progress).
2. Request B sees unique violation, reads attempt record (in_progress).
3. Request A completes and updates attempt to `succeeded`.
4. Request B (which already read `in_progress`) incorrectly returns a conflict when it should replay.

Using `SELECT FOR UPDATE` ensures Request B sees Request A's committed result.

### 11.4 Deadlock Consideration

Because the insert is first (no existing row to lock), there is no lock ordering conflict between the insert step and the `SELECT FOR UPDATE` step. The insert acquires an insert lock on the index page; the subsequent `SELECT FOR UPDATE` on replay acquires a row-level lock. These are compatible because the insert creates the row, and the replay reads an already-existing row.

No special deadlock handling is required for V1 beyond normal PostgreSQL deadlock detection.

### 11.5 Session and Transaction Ownership

The attempt insert, job mutation, gateway call, ledger insert, and attempt update must all share the same `AsyncSession` and transaction.

Rules:

- `AsyncSession` is received from the outer layer (route handler, use-case, or test harness).
- The attempt repository and the job repository share the same session.
- The worker mock service receives the shared session.
- Commit happens only in the outer layer (route handler or use-case).
- No internal `commit()` is permitted in repositories or services.

### 11.6 Reproducible Error on Constraint Violation

PostgreSQL raises `UniqueViolation` (23505) for unique constraint violations. The future implementation must catch this specific error (or use SQLAlchemy's `IntegrityError` inspection) to distinguish first-wins from other database errors.

Recommended pattern:

```python
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation  # or async equivalent

try:
    session.add(attempt)
    await session.flush()
except IntegrityError as exc:
    if _is_unique_violation(exc):
        # handle replay or conflict
    raise
```

## 12. Integration with Existing Layers

### 12.1 Integration with Internal Trigger Route

The internal trigger route (`POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute`) is the entry point for the idempotency layer.

Future flow with idempotency wrapper:

```
route handler
  -> idempotency wrapper service (new)
     -> insert attempt record (insert-first)
     -> on first-wins:
        -> worker mock service
           -> orchestration transitions
           -> gateway settlement
        -> update attempt record with result
     -> on replay:
        -> return stored result
  -> commit
  -> return response
```

The route handler must be updated to call the idempotency wrapper service instead of calling the worker mock service directly.

### 12.2 Integration with AIJobWorkerMockService

The worker mock service remains stateless. It does not know about the attempt store. The idempotency wrapper calls `worker.execute(session, command)` only after the attempt record is inserted.

The worker mock service already receives `execution_attempt_id` and passes it as `caller_key`. No changes to the worker mock service are required for the idempotency wrapper.

### 12.3 Integration with AIJobAsyncOrchestrationService

The orchestration service does not need to change. It continues to receive the shared session and execute transitions through its existing methods.

### 12.4 Integration with AIJobAccountingGateway

The gateway continues to build ledger idempotency keys using `build_idempotency_key(action=..., organization_id=..., job_id=..., caller_key=execution_attempt_id)`. The attempted store layer is upstream of the gateway.

### 12.5 Integration with CreditLedgerService

The ledger's existing `DuplicateIdempotencyKeyError` remains the second line of defense. The ledger idempotency is independent of the attempt store idempotency.

Known gap: The ledger currently uses a global `UniqueConstraint("idempotency_key")`. This is tracked in `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md` and must be resolved in a separate phase.

### 12.6 Integration with Existing Worker Mock Tests

Existing tests for the worker mock service (`tests/unit/test_ai_job_worker_mock_service.py`) should continue to pass without changes. The idempotency wrapper tests are additive.

Existing route tests (`tests/unit/test_ai_job_worker_mock_routes.py`) must be updated or extended to cover idempotency wrapper behavior.

## 13. Proposed Service Layer

### 13.1 AIJobWorkerMockExecutionService (Idempotency Wrapper)

A new service that wraps the worker mock service with attempt-store idempotency.

Proposed interface:

```python
class AIJobWorkerMockExecutionService:
    def __init__(self, worker_service: AIJobWorkerMockService, attempt_repo: AIJobExecutionAttemptRepository):
        ...

    async def execute(
        self,
        session: AsyncSession,
        command: AIJobWorkerMockCommand,
    ) -> AIJobWorkerMockExecuteResult:
        # 1. Compute fingerprint from command
        # 2. Insert attempt record (insert-first)
        # 3. On success: delegate to worker_service.execute(session, command)
        # 4. On success: update attempt record with result
        # 5. On unique violation: SELECT FOR UPDATE, replay or conflict
        # 6. Return result
        ...
```

### 13.2 AIJobExecutionAttemptRepository

A new repository for the `ai_job_execution_attempts` table.

Required methods:

```python
class AIJobExecutionAttemptRepository:
    async def create(self, session: AsyncSession, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
        # Inserts and flushes. Raises IntegrityError on unique violation.
        ...

    async def get_for_update(
        self, session: AsyncSession, organization_id: str, job_id: str, execution_attempt_id: str
    ) -> AIJobExecutionAttempt | None:
        # SELECT FOR UPDATE by (organization_id, job_id, execution_attempt_id)
        ...

    async def update(
        self, session: AsyncSession, attempt: AIJobExecutionAttempt
    ) -> AIJobExecutionAttempt:
        # Merge and flush
        ...
```

### 13.3 Route Handler Update

The route handler must be updated to inject `AIJobWorkerMockExecutionService` instead of `AIJobWorkerMockService` directly.

```python
@router.post("/{job_id}/mock-worker/execute", ...)
async def execute_mock_worker_endpoint(
    ...,
    execution_service: AIJobWorkerMockExecutionService = Depends(...),
):
    ...
    result = await execution_service.execute(db, command)
    ...
```

## 14. Future Test Requirements

### 14.1 Unit Tests for Attempt Repository

- `create` succeeds and returns the attempt record.
- `create` raises `IntegrityError` on duplicate `(organization_id, job_id, execution_attempt_id)`.
- `get_for_update` returns the existing attempt when the key exists.
- `get_for_update` returns `None` when the key does not exist.
- `update` persists status, result fields, and `finished_at`.

### 14.2 Unit Tests for Idempotency Wrapper Service

- First execution with a new `execution_attempt_id` proceeds to worker mock and succeeds.
- First execution with a new `execution_attempt_id` proceeds to worker mock and fails (worker error propagated).
- Retry with a terminal `succeeded` attempt and matching fingerprint returns replay result (no re-execution).
- Retry with a terminal `failed` attempt and matching fingerprint returns replay result (no re-execution).
- Retry with a terminal `cancelled` attempt and matching fingerprint returns replay result (no re-execution).
- Retry with a terminal attempt and different fingerprint raises `409 Conflict`.
- Retry with an `in_progress` attempt raises `409 Conflict` (blocked).
- Replay response includes `replay: true` flag.

### 14.3 Conflict Detection Tests

- Different `mode` on retry: conflict.
- Different `mock_output_metadata` on retry: conflict.
- Different `mock_error_code` on retry: conflict.
- Different `actual_credits` on retry: conflict.
- Different `release_credits` on retry: conflict.
- Same `execution_attempt_id` for a different `job_id`: treated as a different key (no conflict, new attempt record created).
- Same `execution_attempt_id` for a different `organization_id`: treated as a different key (no conflict, new attempt record created).

### 14.4 Route Integration Tests

- Route returns `200 OK` for the first execution with a valid request.
- Route returns `409 Conflict` on retry with the same `execution_attempt_id` while the first is still `in_progress`.
- Route returns `200 OK` with replay on retry with the same `execution_attempt_id` after the first completed.
- Route returns `409 Conflict` on retry with the same `execution_attempt_id` but different payload.
- Route returns `409 Conflict` on retry with the same `execution_attempt_id` but different `mode`.

### 14.5 PostgreSQL Integration Tests (Unique Constraint)

- Inserting two attempt records with the same `(organization_id, job_id, execution_attempt_id)` in a single transaction fails with unique violation.
- Concurrent inserts from two connections for the same `(organization_id, job_id, execution_attempt_id)` — only one succeeds.
- Unique constraint allows the same `execution_attempt_id` for different `job_id` values.
- Unique constraint allows the same `execution_attempt_id` for different `organization_id` values.

### 14.6 Fingerprint Determinism Tests

- The same payload always produces the same fingerprint.
- The same payload with different key ordering in JSON produces the same fingerprint.
- `null` values are consistently excluded.
- `requested_by` changes do not affect the fingerprint.
- Schema version is stored correctly.

### 14.7 Isolation and Safety Tests

- Worker mock service is not called during replay (verified via spy/mock).
- Orchestration service is not called during replay (verified via spy/mock).
- Gateway is not called during replay (verified via spy/mock).
- Ledger is not called during replay (verified via spy/mock).
- No `AsyncSessionLocal` usage in idempotency wrapper.
- No internal `commit()` in idempotency wrapper or attempt repository.
- No `CreditLedgerService` or `CreditGateService` direct calls from idempotency wrapper.

## 15. Fingerprint Implementation Details

### 15.1 Computing the Fingerprint

The fingerprint function receives the validated command fields and returns a SHA-256 hex digest.

```python
import hashlib, json
from dataclasses import asdict

def compute_attempt_fingerprint(command: AIJobWorkerMockCommand) -> str:
    payload = {
        "mode": command.mode,
        "simulated_duration_ms": command.simulated_duration_ms,
        "mock_output_metadata": command.mock_output_metadata,
        "mock_error_code": command.mock_error_code,
        "mock_error_message": command.mock_error_message,
        "actual_credits": command.actual_credits,
        "release_credits": command.release_credits,
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

### 15.2 Computing the Payload Digest

The payload digest is a SHA-256 of the raw request body bytes. This is for audit purposes, not for comparison. It helps operators identify what was originally sent.

```python
def compute_payload_digest(raw_body: bytes) -> str:
    return hashlib.sha256(raw_body).hexdigest()
```

### 15.3 Storing the Fingerprint

The fingerprint is stored as a `String(64)` column (SHA-256 produces 64 hex characters). The `fingerprint_version` column stores the schema version (`"v1"`).

## 16. Edge Cases

### 16.1 Requested_by Changes on Retry

`requested_by` is explicitly excluded from the fingerprint. This means a retry from a different internal actor with the same payload is considered idempotent.

Rationale: `requested_by` is an audit field, not a semantic field. Changing it does not affect the business outcome of the execution.

### 16.2 Additional Metadata on Retry

If the future API adds optional metadata fields beyond those listed in the fingerprint spec, they must be explicitly included or excluded from the fingerprint. If included, the fingerprint version must be incremented.

### 16.3 Attempt Record without Settlement

If a worker mock execution completes its orchestration transitions but fails during settlement (e.g., ledger error), the attempt record must reflect the failure:

- If the error is transient and the transaction rolls back: the attempt record insert is also rolled back, and the retry will attempt a fresh insert (clean slate).
- If the error is non-transient and the transaction commits with partial state: this is a design smell and must be avoided. The entire flow (attempt insert + execution + settlement + attempt update) must be atomic.

### 16.4 Gateway Idempotency Key Collision

If two different `execution_attempt_id` values produce the same gateway settlement key (unlikely with the current `build_idempotency_key` which includes `caller_key`), the ledger's `DuplicateIdempotencyKeyError` blocks the duplicate. The attempt store adds an additional check earlier in the flow.

### 16.5 Unique Constraint across Tables

The `ai_job_execution_attempts` table has its own unique constraint. It does not conflict with any constraint on `ai_jobs` or `credit_ledger_entries`.

### 16.6 Migration of Existing Data

The attempt table starts empty. No migration of existing historical data is required. Future execution attempts will populate the table from scratch.

### 16.7 Large Payloads

The `payload_digest` column stores only the SHA-256 hash (64 bytes equivalent). The raw body is not stored in the database. If raw body storage is needed for audit, it should be in a separate audit log, not in the attempt record.

## 17. Non-Scope for This Contract

This contract explicitly does not scope the following items. They are deferred to future phases:

- The actual `AIJobExecutionAttempt` model implementation.
- The Alembic migration for `ai_job_execution_attempts`.
- The `AIJobExecutionAttemptRepository` implementation.
- The `AIJobWorkerMockExecutionService` (idempotency wrapper) implementation.
- The route handler update to use the idempotency wrapper.
- The fingerprint computation functions.
- PostgreSQL integration tests for unique constraints and concurrent attempt creation.
- Stale attempt detection and cleanup.
- Dead-letter queue for stuck `in_progress` attempts.
- `CreditLedgerEntry` tenant-scoped unique constraint (tracked in separate contract).

## 18. Roadmap

### 18.1 Implementation Phase (Future)

1. Create `AIJobExecutionAttempt` ORM model in `src/models/ai_job_execution_attempt.py`.
2. Add Alembic migration for `ai_job_execution_attempts` table.
3. Create `AIJobExecutionAttemptRepository` in `src/repositories/ai_job_execution_attempt_repository.py`.
4. Implement `compute_attempt_fingerprint` and `compute_payload_digest` utilities.
5. Implement `AIJobWorkerMockExecutionService` (idempotency wrapper) in a new service module or as an extension of the existing worker mock service.
6. Update the internal trigger route to inject and use `AIJobWorkerMockExecutionService`.
7. Add unit tests for the new repository, service, and route behavior.
8. Add PostgreSQL integration tests for unique constraint and concurrent attempt creation.
9. Keep repository policy guards passing for all future implementation phases.
10. Update `AGENTS.md` if new module conventions are established.

### 18.2 Hardening Phase (Future)

11. Implement stale attempt detection and cleanup (periodic job or TTL).
12. Add dead-letter or retry queue for stuck `in_progress` attempts.
13. Add tenant-scoped unique constraint to `CreditLedgerEntry.idempotency_key` (tracked in `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`).

### 18.3 Ordering with Other Contracts

The idempotency hardening implementation must happen **after** the internal trigger route is stable and tested. It may happen **in parallel with or before** the ledger tenant-scope implementation, since the attempt store is independent of the ledger constraint.

## 19. Acceptance Criteria for Future Implementation

The future idempotency hardening implementation is acceptable only when:

- The `AIJobExecutionAttempt` model exists with the correct columns, constraints, and indexes as defined in Section 7.
- The unique constraint on `(organization_id, job_id, execution_attempt_id)` is enforced at the database level.
- The insert-first strategy is implemented correctly, with `IntegrityError` catch for first-winner detection.
- `SELECT FOR UPDATE` is used on replay paths to prevent race conditions.
- Terminal replays return the stored result without re-execution.
- `in_progress` replays return `409 Conflict`.
- Fingerprint mismatches on terminal attempts return `409 Conflict`.
- The fingerprint is deterministic and schema-versioned.
- All required tests in Section 14 pass.
- The worker mock service remains stateless (no changes to `AIJobWorkerMockService`).
- The orchestration service remains unchanged.
- The accounting gateway remains unchanged.
- The ledger remains unchanged by this phase.
- No `AsyncSessionLocal` or internal `commit()` exists in new code.
- No real provider, ComfyUI runtime, GPU, payment, Alembic (beyond the migration for this table), or frontend changes are introduced by the implementation phase unless explicitly scoped.
