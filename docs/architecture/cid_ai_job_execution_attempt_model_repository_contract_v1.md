# CID AI Job Execution Attempt Model and Repository Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOB.EXECUTION.ATTEMPT.MODEL.CONTRACT.1
Scope: canonical contract for the future `AIJobExecutionAttempt` ORM model, `ai_job_execution_attempts` table, and async repository

Companion docs:

- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md`
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the canonical contract for the future `AIJobExecutionAttempt` ORM model, its backing table `ai_job_execution_attempts`, and the async repository that will encapsulate its persistence.

The contract exists to:

- fix the logical schema, constraints, indexes, and field contract before any ORM or Alembic code is written;
- define the tenant-safe identity `(organization_id, job_id, execution_attempt_id)` as the single source of truth for execution attempt idempotency;
- separate the attempt persistence concerns from the `AIJob` model (which currently stores `attempt_number` and namespaced `job_metadata.execution.execution_attempt_id`);
- prepare the repository boundary that the future `AIJobWorkerMockExecutionService` (idempotency wrapper) will use to persist, detect, and replay execution attempts;
- keep the attempt store independent from the ledger idempotency layer — both layers are required, neither replaces the other.

This phase is documentary only. It does not create the model, table, migration, repository, service wrapper, route updates, or tests.

## 2. Relationship with the Idempotency Hardening Contract

This document descends from `cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md` and elaborates the model and repository sections of that contract into a standalone, implementation-ready specification.

Key relationships:

- The idempotency hardening contract defines the overall strategy: identity, fingerprint, replay, conflict, two-layer separation, concurrency rules.
- This contract defines the concrete model columns, types, constraints, indexes, FK policy, repository methods, error classes, and test requirements.
- The hardening contract defines `AIJobWorkerMockExecutionService` (the idempotency wrapper); this contract defines the repository that wrapper will depend on.
- Both contracts are compatible and complementary. This contract does not replace the hardening contract.
- Implementation order: model + migration → repository → wrapper service → route update. Each phase must have its own contract or explicit scope.

## 3. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `src/models/ai_job.py` — existing AIJob ORM model with `attempt_number`, `job_metadata`, and timestamp columns
- `src/models/billing.py` — CreditLedgerEntry with global `UniqueConstraint("idempotency_key")`
- `src/repositories/ai_job_repository.py` — tenant-safe async repository with `get`, `get_for_update`, `save`, `list_for_organization`, `find_by_idempotency_key`
- `src/repositories/__init__.py` — empty package init
- `src/services/ai_job_worker_mock_service.py` — stateless mock worker, `execution_attempt_id` passed as `caller_key`
- `src/routes/internal_ai_job_worker_mock_routes.py` — internal trigger endpoint, `include_in_schema=False`, `internal_api_key` only
- `src/schemas/ai_job_worker_mock_api_schema.py` — Pydantic request/response with `extra="forbid"`
- `docs/architecture/cid_ai_jobs_worker_mock_idempotency_hardening_contract_v1.md` — source contract for idempotency hardening
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md` — internal trigger contract
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md` — worker mock contract
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md` — AIJob repository contract
- `docs/architecture/cid_postgresql_only_policy_v1.md` — PostgreSQL-only policy

Observed relevant facts:

- `AIJob` has `attempt_number: int` and `job_metadata: dict` (JSON column aliased from `metadata`). Execution attempt id is currently stored under `job_metadata["execution"]["execution_attempt_id"]`.
- `AIJob` has no dedicated attempt tracking table.
- `AIJobRepository` receives `AsyncSession` at construction time and shares it across methods. It never calls `commit()`; it may call `flush()`.
- `AIJobRepository.get_for_update(organization_id, job_id)` uses `stmt.with_for_update()`.
- `AIJobRepository` has no method without `organization_id` — all reads are tenant-scoped by construction.
- `AIJobRepository.save()` includes `_check_tenant_mutation` to prevent silent `organization_id` reassignment.
- `repositories/__init__.py` is empty — new repository modules will be auto-discovered by import pattern.
- `CreditLedgerEntry.idempotency_key` has a global unique constraint (not tenant-scoped). This is a known gap tracked in `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`.
- The worker mock service is stateless — it does not persist attempt replay state. This is the gap this model+repository contract addresses.
- The internal trigger route constructs `AIJobWorkerMockCommand` from tenant context and calls `worker.execute(db, command)` directly — no idempotency wrapper yet.
- The idempotency hardening contract already defines fingerprint computation, replay behavior, conflict rules, and the insert-first concurrency strategy.

## 4. Scope

### 4.1 In Scope

- The future `AIJobExecutionAttempt` ORM model class.
- The future `ai_job_execution_attempts` PostgreSQL table.
- Column definitions, types, nullability, defaults, and purposes.
- Primary key, unique constraints, check constraints, foreign keys, and indexes.
- The tenant-safe identity `(organization_id, job_id, execution_attempt_id)` as the unique logical key.
- The future `AIJobExecutionAttemptRepository` async repository.
- Repository method contracts (signatures, parameters, return types, semantics).
- Repository error classes.
- Future test requirements (unit, model/contract, PostgreSQL integration).
- Future migration rules and constraints.
- Relationship with the idempotency wrapper, worker mock, orchestration, and ledger.

### 4.2 Out of Scope (Not Implemented in This Phase)

- The actual `AIJobExecutionAttempt` model class in `src/models/`.
- The Alembic migration for `ai_job_execution_attempts`.
- The `AIJobExecutionAttemptRepository` class in `src/repositories/`.
- The `AIJobWorkerMockExecutionService` idempotency wrapper.
- Route handler updates to use the idempotency wrapper.
- Any change to runtime application code.
- Any change to existing models (`AIJob`, `CreditLedgerEntry`, etc.).
- Any change to existing repositories.
- Any change to existing routes, services, dependencies, or schemas.
- Any change to frontend, Docker, Stripe, ComfyUI, or runtime configuration.
- Any change to guard scripts or CI/CD configuration.

## 5. Future Table

### 5.1 Table Name

```
ai_job_execution_attempts
```

### 5.2 Table Type

This is a dedicated PostgreSQL table. It is not a JSON field inside `ai_jobs`, not a view, not a composite type.

Rationale:

- Dedicated table enables proper constraints, indexes, foreign keys, and query performance.
- The attempt record has its own lifecycle and access patterns distinct from the job record.
- JSON storage inside `ai_jobs.job_metadata` would prevent unique constraints, efficient indexing, and row-level locking for attempts.
- Separation keeps the `AIJob` model focused on job-level state and the attempt model focused on execution-level state.

### 5.3 Relationship to ai_jobs

- Each `ai_job` may have zero or more `ai_job_execution_attempts`.
- The relationship is identified by `job_id` (foreign key to `ai_jobs.id`).
- The relationship is tenant-scoped: both tables carry `organization_id`.
- The unique constraint `(organization_id, job_id, execution_attempt_id)` ensures that an attempt id is unique per job per tenant.

## 6. Tenant-Safe Identity

### 6.1 Logical Key

The effective idempotency key for an execution attempt is:

```
(organization_id, job_id, execution_attempt_id)
```

### 6.2 Unique Constraint

```sql
UNIQUE (organization_id, job_id, execution_attempt_id)
```

This constraint is the single source of truth for first-writer-wins semantics. It enforces at the database level that the same `execution_attempt_id` cannot be reused for the same job in the same tenant.

### 6.3 Rules

- There must be no `get(execution_attempt_id)` method — no global lookup by `execution_attempt_id` alone.
- There must be no `get(job_id, execution_attempt_id)` without `organization_id`.
- Every read method must include `organization_id` as a mandatory filter parameter.
- `execution_attempt_id` alone does not identify any row globally.
- The same `execution_attempt_id` used across different tenants or different jobs is a completely independent row (allowed by the unique constraint because the composite key differs).

### 6.4 Cross-Tenant Isolation

- Two tenants using the same `execution_attempt_id` string produce two independent rows (different `organization_id`).
- A retry for job A in tenant 1 cannot accidentally replay a result from job A in tenant 2.
- Tenant isolation is enforced at the unique constraint level and at the query filter level (defense in depth).

## 7. Recommended Columns

### 7.1 Required Columns

| Column | Type | Nullable | Default | Purpose |
|---|---|---|---|---|
| `id` | `String(36)` | NOT NULL | UUID4 hex | Internal primary key |
| `organization_id` | `String(36)` | NOT NULL | — | Tenant scope |
| `job_id` | `String(36)` | NOT NULL | — | FK to `ai_jobs.id` |
| `execution_attempt_id` | `String(255)` | NOT NULL | — | External idempotency key |
| `mode` | `String(20)` | NOT NULL | — | `success`, `failure`, or `cancel` |
| `status` | `String(20)` | NOT NULL | `in_progress` | Attempt lifecycle status |
| `fingerprint` | `String(64)` | NOT NULL | — | SHA-256 hex of canonical payload |
| `fingerprint_version` | `String(10)` | NOT NULL | `v1` | Schema version for fingerprint |
| `created_at` | `DateTime` | NOT NULL | `utcnow` | Row creation timestamp |
| `updated_at` | `DateTime` | NOT NULL | `utcnow` | Row last-update timestamp |

### 7.2 Optional Columns

| Column | Type | Nullable | Default | Purpose |
|---|---|---|---|---|
| `requested_by` | `String(100)` | YES | `None` | Identity of the actor who triggered this attempt |
| `result_status` | `String(40)` | YES | `None` | Final job status after attempt (e.g., `consumed`, `released`) |
| `consume_entry_id` | `String(36)` | YES | `None` | Ledger consume entry id if settlement succeeded |
| `release_entry_id` | `String(36)` | YES | `None` | Ledger release entry id if settlement succeeded |
| `consumed_credits` | `Integer` | YES | `None` | Credits consumed by this attempt |
| `released_credits` | `Integer` | YES | `None` | Credits released by this attempt |
| `error_code` | `String(100)` | YES | `None` | Machine-readable error code if failed |
| `error_message_safe` | `Text` | YES | `None` | Human-readable safe error description |
| `started_at` | `DateTime` | YES | `None` | When attempt execution began |
| `finished_at` | `DateTime` | YES | `None` | When attempt reached terminal status |
| `metadata_json` | `JSON` | YES | `None` | Safe, size-limited metadata for diagnostics |

### 7.3 Column Decision Rationale

**Why `fingerprint` is required (not optional):**
- Fingerprint is the only mechanism to detect semantic changes between retries.
- Without a fingerprint, the system cannot tell if a retry carries the same payload or a different one.
- `fingerprint_version` ensures forward compatibility when the payload schema evolves.

**Why `payload_digest` is not included by default:**
- `payload_digest` (SHA-256 of raw request body) was considered in the hardening contract for audit purposes.
- In V1, `fingerprint` (SHA-256 of canonical payload fields) provides sufficient conflict detection.
- `payload_digest` can be added in a future phase if operational audit requires raw-body traceability.
- The hardening contract discusses `payload_digest`; this contract explicitly omits it for V1 to keep the model minimal.

**Why `metadata_json` is optional and limited:**
- Provides extensibility for future non-sensitive metadata without schema changes.
- Size must be bounded at the application layer (recommended max 4 KB).
- Must never store secrets, tokens, credentials, or raw provider payloads.

**Why `updated_at` is included:**
- Useful for detecting stale `in_progress` rows and for operational monitoring.
- Must be updated on every status change via `onupdate=_utcnow`.

### 7.4 Updated_at Pattern

`updated_at` must be automatically updated on row modification. Recommended SQLAlchemy pattern:

```python
updated_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
)
```

## 8. Permitted States

### 8.1 Attempt States

The `status` column tracks the execution attempt lifecycle. These states are independent of `AIJob.status`.

| State | Meaning | Terminal |
|---|---|---|
| `in_progress` | Attempt created but not yet completed | No |
| `succeeded` | Attempt completed with `mode=success`, consume settled | Yes |
| `failed` | Attempt completed with `mode=failure`, release settled | Yes |
| `cancelled` | Attempt completed with `mode=cancel`, release settled | Yes |
| `conflicted` | Attempt rejected by conflict detection | Yes |

### 8.2 State Transition Rules

- `in_progress` → `succeeded` (consume settled successfully)
- `in_progress` → `failed` (release settled after failure flow)
- `in_progress` → `cancelled` (release settled after cancel flow)
- `in_progress` → `conflicted` (explicit rejection, e.g., fingerprint mismatch detected late)
- Terminal states (`succeeded`, `failed`, `cancelled`, `conflicted`) are immutable — no further transitions.

### 8.3 Relationship with AIJob.status

- `AIJobExecutionAttempt.status` does not replace `AIJob.status`.
- The job lifecycle (created → estimated → reserved → queued → running → succeeded/failed → consumed/released) is tracked on `AIJob.status`.
- The attempt lifecycle (in_progress → succeeded/failed/cancelled/conflicted) is tracked on `AIJobExecutionAttempt.status`.
- These are related but independent: a `succeeded` attempt implies the job reached a terminal settlement state, but the job status tells you which one (`consumed` for success, `released` for failure/cancel).
- The `result_status` column on the attempt record stores the final job status after settlement for fast reference.

### 8.4 No Synthetic States

- Do not invent attempt states that are not documented here without a prior status-contract phase.
- `pending`, `retrying`, `expired`, `aborted`, `skipped`, and `unknown` are not valid attempt states for V1.
- If a future phase requires new attempt states, they must be added to this contract before implementation.

## 9. Permitted Modes

The `mode` column records the execution mode requested for this attempt.

Permitted values:

| Mode | Meaning |
|---|---|
| `success` | Simulated success execution with consume settlement |
| `failure` | Simulated failure execution with release settlement |
| `cancel` | Cancellation of an already `cancel_requested` job with release settlement |

Rules:

- `mode` must be one of the three values above.
- `mode` is set at attempt creation and never changes.
- A retry that changes `mode` is always a fingerprint conflict (handled at the wrapper level).

## 10. Constraints

### 10.1 Primary Key

```sql
PRIMARY KEY (id)
```

- `id` is a UUID4 hex string (36 characters).
- Internal only; never exposed to external callers.

### 10.2 Unique Constraint (Tenant-Safe Identity)

```sql
UNIQUE (organization_id, job_id, execution_attempt_id)
```

- Enforces the effective idempotency key at the database level.
- Prevents duplicate attempt records for the same key.
- Serves as the first-writer-wins mechanism for concurrent insert attempts.

### 10.3 Check Constraints

```sql
CHECK (mode IN ('success', 'failure', 'cancel'))
```

- Ensures only valid execution modes are stored.

```sql
CHECK (status IN ('in_progress', 'succeeded', 'failed', 'cancelled', 'conflicted'))
```

- Ensures only valid attempt lifecycle states are stored.

```sql
CHECK (consumed_credits IS NULL OR consumed_credits > 0)
```

- Ensures consumed credits are positive when present (default is NULL).

```sql
CHECK (released_credits IS NULL OR released_credits > 0)
```

- Ensures released credits are positive when present (default is NULL).

```sql
CHECK (finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at)
```

- Ensures temporal consistency: `finished_at` must not precede `started_at`.

### 10.4 Foreign Key

```sql
FOREIGN KEY (job_id) REFERENCES ai_jobs(id)
```

- Establishes referential integrity at the row level.
- Prevents orphaned attempt records referencing non-existent jobs.

**Important FK rules:**

- The FK on `job_id` alone does not enforce tenant safety. A row with `organization_id=X, job_id=A` could theoretically reference a job that belongs to `organization_id=Y`.
- Tenant-safe validation must be enforced at the repository and service layers: every attempt lookup must filter by both `organization_id` and `job_id`.
- A future improvement could use a composite FK `(organization_id, job_id) REFERENCES ai_jobs(organization_id, id)`, but this requires a composite unique constraint on `ai_jobs(organization_id, id)` or making `(organization_id, id)` the PK. This is a larger schema change and is **not** required for V1.
- Documented here as a future improvement, not a V1 blocker.

### 10.5 Not-Null Constraints

All columns listed as required (Section 7.1) have NOT NULL enforced at the database level.

## 11. Indexes

### 11.1 Required Indexes

```sql
-- Primary key lookup (automatic with PK)
PRIMARY KEY (id)

-- Tenant-scoped lookup by job (most common access pattern)
CREATE INDEX ix_ai_job_exec_attempts_org_job
    ON ai_job_execution_attempts (organization_id, job_id);

-- Tenant-scoped lookup by job with creation ordering (history queries)
CREATE INDEX ix_ai_job_exec_attempts_org_job_created
    ON ai_job_execution_attempts (organization_id, job_id, created_at DESC);

-- Tenant-scoped lookup by status (stale attempt detection, admin queries)
CREATE INDEX ix_ai_job_exec_attempts_org_status_created
    ON ai_job_execution_attempts (organization_id, status, created_at DESC);
```

### 11.2 Optional Indexes

```sql
-- Lookup by execution_attempt_id for internal audit (rare)
CREATE INDEX ix_ai_job_exec_attempts_org_attempt
    ON ai_job_execution_attempts (organization_id, execution_attempt_id);
```

This index is optional for V1. It enables efficient cross-job audit queries like "find all attempts with this `execution_attempt_id` for this tenant". Without it, such queries would require a full scan filtered by `organization_id`.

### 11.3 Index Rules

- All user-facing indexes are prefixed with `organization_id` — no global indexes except the primary key.
- Avoid indexes on `execution_attempt_id` alone (global lookup).
- The unique constraint `(organization_id, job_id, execution_attempt_id)` automatically creates a backing index for equality lookups on that combination.

## 12. Fingerprint Storage

### 12.1 Storage Fields

The attempt record stores two fingerprint-related fields:

| Field | Type | Length | Purpose |
|---|---|---|---|
| `fingerprint` | `String(64)` | 64 hex chars | SHA-256 of canonical payload (see Section 15 of hardening contract) |
| `fingerprint_version` | `String(10)` | e.g., `v1` | Schema version for fingerprint computation |

### 12.2 Fingerprint Behavior

- Computed at the `AIJobWorkerMockExecutionService` layer before inserting the attempt record.
- Stored once at creation; never updated.
- On replay, the incoming request's fingerprint is compared with the stored fingerprint.
- Schema version `v1` covers the fields defined in the hardening contract: `mode`, `simulated_duration_ms`, `mock_output_metadata`, `mock_error_code`, `mock_error_message`, `actual_credits`, `release_credits`.

### 12.3 What Is NOT Stored

- The raw request body is not stored in V1 (no `payload_digest` column).
- Full request payloads are not stored by default — only the fingerprint hash.
- `metadata_json` may store safe, size-limited diagnostics but must not contain credentials, tokens, secrets, or raw provider payloads.

## 13. Future Repository

### 13.1 Name and Location

```
AIJobExecutionAttemptRepository
```

```
src/repositories/ai_job_execution_attempt_repository.py
```

### 13.2 Repository Pattern

The repository follows the same conventions as `AIJobRepository`:

- Receives `AsyncSession` at construction time.
- Shares the session with orchestration, gateway, and other repositories.
- Never calls `commit()`.
- May call `flush()` when constraint visibility is required (especially for insert-first unique violation detection).
- Never instantiates `AsyncSessionLocal`.
- All methods require `organization_id` — no tenantless access.
- No fallback or dialect branching.

### 13.3 Required Methods

#### `async create(session: AsyncSession, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt`

Inserts a new attempt record and flushes. On success, returns the persisted attempt with `id` populated.

If a unique constraint violation occurs on `(organization_id, job_id, execution_attempt_id)`, the implementation must allow the caller to catch and handle the `IntegrityError`. The repository should not silently swallow unique violations.

**Signature:**

```python
async def create(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
    self._session.add(attempt)
    await self._session.flush()
    return attempt
```

#### `async get(session, organization_id: str, job_id: str, execution_attempt_id: str) -> AIJobExecutionAttempt | None`

Tenant-scoped lookup by the effective key.

Returns the attempt record or `None` if not found within the tenant scope.

**Signature:**

```python
async def get(
    self,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
) -> AIJobExecutionAttempt | None:
    stmt = (
        select(AIJobExecutionAttempt)
        .where(AIJobExecutionAttempt.organization_id == organization_id)
        .where(AIJobExecutionAttempt.job_id == job_id)
        .where(AIJobExecutionAttempt.execution_attempt_id == execution_attempt_id)
    )
    result = await self._session.execute(stmt)
    return result.scalar_one_or_none()
```

#### `async get_for_update(session, organization_id: str, job_id: str, execution_attempt_id: str) -> AIJobExecutionAttempt | None`

Tenant-scoped lookup with PostgreSQL row locking (`SELECT ... FOR UPDATE`).

Used on the replay path after a unique violation is detected, to prevent race conditions between the insert attempt and the replay decision.

**Signature:**

```python
async def get_for_update(
    self,
    organization_id: str,
    job_id: str,
    execution_attempt_id: str,
) -> AIJobExecutionAttempt | None:
    stmt = (
        select(AIJobExecutionAttempt)
        .where(AIJobExecutionAttempt.organization_id == organization_id)
        .where(AIJobExecutionAttempt.job_id == job_id)
        .where(AIJobExecutionAttempt.execution_attempt_id == execution_attempt_id)
        .with_for_update()
    )
    result = await self._session.execute(stmt)
    return result.scalar_one_or_none()
```

#### `async save(session, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt`

Persists changes to an existing attempt record and flushes.

The implementation must guard against tenant reassignment, following the same pattern as `AIJobRepository.save()`.

**Signature:**

```python
async def save(self, attempt: AIJobExecutionAttempt) -> AIJobExecutionAttempt:
    if attempt.organization_id is None:
        raise AIJobExecutionAttemptRepositoryError("organization_id must not be None")
    self._session.add(attempt)
    await self._session.flush()
    return attempt
```

#### `async find_by_key(session, organization_id: str, job_id: str, execution_attempt_id: str) -> AIJobExecutionAttempt | None`

Semantic alias for `get()`. Intended for explicit readability in idempotency-check code paths.

For V1, this may be an alias or a separate method. The purpose is code clarity: `find_by_key` conveys "I am checking if this key already exists" rather than "I am loading an attempt by its composite key."

**Recommended implementation:** either an alias to `get()` or a separate query with identical semantics. Both are acceptable for V1.

#### `async list_for_job(session, organization_id: str, job_id: str, *, limit: int = 50, cursor: str | None = None) -> tuple[list[AIJobExecutionAttempt], str | None]`

Lists execution attempts for a specific job, ordered by creation time descending (newest first).

Cursor-based pagination, following the same pattern as `AIJobRepository.list_for_organization()`.

**Signature:**

```python
async def list_for_job(
    self,
    organization_id: str,
    job_id: str,
    *,
    limit: int = 50,
    cursor: str | None = None,
) -> tuple[list[AIJobExecutionAttempt], str | None]:
    safe_limit = min(max(int(limit or 50), 1), 100)
    stmt = (
        select(AIJobExecutionAttempt)
        .where(AIJobExecutionAttempt.organization_id == organization_id)
        .where(AIJobExecutionAttempt.job_id == job_id)
    )
    if cursor:
        stmt = stmt.where(AIJobExecutionAttempt.id < cursor)
    stmt = stmt.order_by(AIJobExecutionAttempt.created_at.desc()).limit(safe_limit + 1)
    result = await self._session.execute(stmt)
    rows = list(result.scalars().all())
    next_cursor = rows[safe_limit].id if len(rows) > safe_limit else None
    return rows[:safe_limit], next_cursor
```

### 13.4 Optional Convenience Methods

These methods are **optional** for V1. They may be added if the idempotency wrapper or route layer requires them to reduce boilerplate.

#### `async mark_succeeded(session, attempt_id: str, *, consume_entry_id: str, consumed_credits: int, result_status: str) -> AIJobExecutionAttempt`

Loads the attempt by `id` (internal PK), updates status to `succeeded`, sets settlement fields and `finished_at`.

**Constraint:** this method must be used only when the caller already verified tenant scope. Prefer updating through the standard `get_for_update` + `save` pattern for tenant safety.

#### `async mark_failed(session, attempt_id: str, *, release_entry_id: str, released_credits: int, error_code: str | None, error_message_safe: str | None) -> AIJobExecutionAttempt`

Same as `mark_succeeded` but for failure settlement.

#### `async mark_cancelled(session, attempt_id: str, *, release_entry_id: str, released_credits: int, error_message_safe: str | None) -> AIJobExecutionAttempt`

Same as `mark_succeeded` but for cancel settlement.

#### `async mark_conflicted(session, attempt_id: str, *, error_message_safe: str | None) -> AIJobExecutionAttempt`

Marks an attempt as conflicted without settlement fields.

**V1 Recommendation:** Skip convenience methods in V1. The idempotency wrapper should use `get_for_update` + `save` explicitly for clarity and control.

### 13.5 Repository Rules

- Every method receives and uses the shared `AsyncSession` passed at construction time.
- No method accepts `organization_id` as optional — it is always required.
- No method accepts `execution_attempt_id` without `organization_id` and `job_id`.
- No method uses `AsyncSessionLocal`.
- No method calls `commit()`.
- `flush()` is allowed for constraint detection and id generation.
- No fallback or dialect branching for locking (`with_for_update()` is PostgreSQL-only).

## 14. Repository Concurrency

### 14.1 Insert-First Strategy

The repository supports the insert-first strategy defined in the hardening contract:

1. Caller calls `create(attempt)` to insert the attempt record.
2. If unique constraint is violated (`IntegrityError`), caller catches the error and switches to replay/conflict path.
3. On replay path, caller calls `get_for_update(key)` to lock and read the existing record.
4. Caller compares fingerprints, decides replay or conflict.

### 14.2 IntegrityError Handling

The repository does **not** catch `IntegrityError` internally. It propagates the error to the caller (the idempotency wrapper service), which is responsible for:

- Inspecting the error to determine if it is a unique violation (PostgreSQL error code 23505).
- If unique violation: proceeding to the replay/conflict path.
- If other integrity error: raising or propagating as appropriate.

### 14.3 Row Locking on Replay

`get_for_update()` must use PostgreSQL `SELECT ... FOR UPDATE` to lock the existing attempt row before the replay/conflict decision. This prevents the race condition described in Section 11.3 of the hardening contract.

### 14.4 No Dialect Fallback

- `with_for_update()` is a PostgreSQL feature.
- No dialect checks, no dialect branching, no fallback to `SELECT ...` without lock.
- The repository contract is PostgreSQL-only.

## 15. Future Error Classes

### 15.1 Error Class Hierarchy

```python
class AIJobExecutionAttemptRepositoryError(Exception):
    """Base error for AIJobExecutionAttemptRepository operations."""

class AIJobExecutionAttemptNotFoundError(AIJobExecutionAttemptRepositoryError):
    """Raised when a tenant-scoped attempt lookup returns no row."""

class AIJobExecutionAttemptConflictError(AIJobExecutionAttemptRepositoryError):
    """Raised when an idempotency conflict is detected at the repository level."""

class AIJobExecutionAttemptAlreadyInProgressError(AIJobExecutionAttemptRepositoryError):
    """Raised when a retry arrives while the existing attempt is still in_progress."""

class AIJobExecutionAttemptFingerprintMismatchError(AIJobExecutionAttemptRepositoryError):
    """Raised when a retry carries a different fingerprint than the stored attempt."""

class AIJobExecutionAttemptInvalidStateError(AIJobExecutionAttemptRepositoryError):
    """Raised when an attempt operation is invalid for the current attempt status."""
```

### 15.2 Error Usage Rules

- `AIJobExecutionAttemptRepositoryError` is the base class for all repository errors.
- The repository itself raises `AIJobExecutionAttemptRepositoryError` for internal failures (e.g., `organization_id is None` during `save()`).
- `AIJobExecutionAttemptNotFoundError`, `AIJobExecutionAttemptConflictError`, and fingerprint/state errors may be raised by the idempotency wrapper service, not necessarily by the repository directly.
- The idempotency wrapper maps repository-level errors and logical decisions into these typed errors for route-level error mapping.

## 16. Relationship with the Idempotency Wrapper

### 16.1 Separation of Concerns

- The repository only persists, reads, locks, and updates attempt records.
- The repository does **not** decide replay vs. conflict.
- The repository does **not** compute fingerprints.
- The repository does **not** call the worker mock service.
- `AIJobWorkerMockExecutionService` (the future idempotency wrapper) uses the repository to persist state and make replay/conflict decisions.

### 16.2 Expected Wrapper Flow

```python
class AIJobWorkerMockExecutionService:
    def __init__(self, worker_service, attempt_repo):
        ...

    async def execute(self, session, command):
        fingerprint = compute_fingerprint(command)

        # Insert-first
        attempt = AIJobExecutionAttempt(
            organization_id=command.organization_id,
            job_id=command.job_id,
            execution_attempt_id=command.execution_attempt_id,
            mode=command.mode,
            fingerprint=fingerprint,
            fingerprint_version="v1",
        )
        try:
            await self.attempt_repo.create(attempt)
        except IntegrityError as exc:
            if not is_unique_violation(exc):
                raise
            # Replay path
            existing = await self.attempt_repo.get_for_update(
                session,
                command.organization_id,
                command.job_id,
                command.execution_attempt_id,
            )
            if existing is None:
                raise AIJobExecutionAttemptRepositoryError(...)
            if existing.fingerprint != fingerprint:
                raise AIJobExecutionAttemptFingerprintMismatchError(...)
            if existing.status == "in_progress":
                raise AIJobExecutionAttemptAlreadyInProgressError(...)
            # Replay terminal result
            return self._build_replay_result(existing)

        # First-wins execution
        result = await self.worker_service.execute(session, command)
        await self._update_attempt(session, attempt, result)
        return result
```

### 16.3 Worker Mock Remains Stateless

`AIJobWorkerMockService` does not change. It continues to receive the shared session and command, execute transitions, and return results. It does not know about the attempt store, fingerprint, or replay logic.

## 17. Relationship with the Ledger

### 17.1 Two-Layer Separation

The attempt store and the ledger are independent idempotency layers:

| Aspect | Attempt Store | Ledger |
|---|---|---|
| What it protects | Execution replay (same attempt id) | Settlement replay (same idempotency key) |
| Key scope | `(org, job, attempt_id)` | `(org, job, action, caller_key)` |
| When it fires | Before execution | During settlement |
| Error type | `IntegrityError` on insert | `DuplicateIdempotencyKeyError` |
| Layer | New (this contract) | Existing (`CreditLedgerService`) |

### 17.2 Settlement References

The attempt record stores `consume_entry_id` and `release_entry_id` as references to the ledger entries created during settlement. These are foreign keys in a logical sense only:

- The attempt record references the ledger entry by its `id` (UUID4 hex string).
- There is no database-level FK constraint from `ai_job_execution_attempts.consume_entry_id` to `credit_ledger_entries.id` in V1.
- A future phase may add FK constraints if the operational benefit outweighs the migration complexity.
- Both `consume_entry_id` and `release_entry_id` are optional (NULL before settlement).

### 17.3 Known Ledger Gap

`CreditLedgerEntry.idempotency_key` currently has a global `UniqueConstraint("idempotency_key")` without `organization_id`. This gap is tracked in `cid_credit_ledger_idempotency_tenant_scope_contract_v1.md` and must be resolved in a separate phase. The attempt store does not depend on the ledger gap being resolved first.

## 18. Future Migration Rules

### 18.1 Migration Phase

The `ai_job_execution_attempts` table must be created via Alembic migration in a dedicated implementation phase. Rules:

1. The migration must be PostgreSQL-only with no compatibility backend branches.
2. The migration must create the table with all columns, constraints, and indexes defined in this contract.
3. The migration must have a safe downgrade that drops the table.
4. The migration must not modify existing tables (`ai_jobs`, `credit_ledger_entries`, etc.).
5. The migration must be validated against a PostgreSQL instance before commit.

### 18.2 Data Safety

- The `ai_job_execution_attempts` table starts empty.
- No existing data is migrated or transformed.
- No existing `job_metadata["execution"]["execution_attempt_id"]` values are backfilled into the new table.
- Future execution attempts populate the table from scratch.

### 18.3 Guard Compatibility

The migration and model files must pass the existing repository policy guards:

- Repository policy guards must pass for all new files.
- `guard_wsl_repo.sh`: no Windows paths, secrets, or nested copies.

## 19. Future Test Requirements

### 19.1 Unit Tests for Repository

| Test | Description |
|---|---|
| `create` succeeds | Insert a new attempt, verify `id` and timestamps are populated |
| `create` unique violation | Insert duplicate `(org, job, attempt_id)`, expect `IntegrityError` |
| `get` tenant-scoped | Lookup by correct key, returns the attempt |
| `get` wrong tenant | Lookup with same key but different `organization_id`, returns `None` |
| `get` wrong job | Lookup with same key but different `job_id`, returns `None` |
| `get` not found | Lookup with non-existent key, returns `None` |
| `get_for_update` tenant-scoped | Lookup by correct key, returns attempt with lock applied |
| `get_for_update` not found | Lookup with non-existent key, returns `None` |
| `save` updates fields | Modify status and fingerprint, save, verify persistence |
| `save` rejects None organization_id | Attempt to save with `organization_id=None`, expect error |
| `find_by_key` | Alias for `get`, same semantics |
| `list_for_job` tenant-scoped | Returns attempts for the correct job, ordered by `created_at DESC` |
| `list_for_job` cursor pagination | Returns next cursor when more rows exist |
| `list_for_job` empty | Returns empty list for job with no attempts |
| `list_for_job` cross-tenant isolation | Same `job_id` in different tenant returns empty |

### 19.2 Model/Contract Tests

| Test | Description |
|---|---|
| Canonical attempt states | All valid states are accepted by the check constraint |
| Invalid attempt states rejected | Invalid state string is rejected by the check constraint |
| Canonical modes | All valid modes are accepted by the check constraint |
| Invalid modes rejected | Invalid mode string is rejected by the check constraint |
| Fingerprint is 64 hex chars | Stored fingerprint matches SHA-256 format |
| No fallback | Repository code contains no alternate backend imports, checks, or dialect branching |
| No `AsyncSessionLocal` | Repository code does not import or use `AsyncSessionLocal` |
| No `commit()` | Repository code does not call `commit()` |
| All methods require `organization_id` | No method signature accepts `organization_id` as optional |

### 19.3 PostgreSQL Integration Tests (Future Phase)

| Test | Description |
|---|---|
| Unique constraint enforcement | Two inserts with same `(org, job, attempt_id)` — second fails |
| Same attempt id, different job | Insert with same attempt id but different job — allowed |
| Same attempt id, different tenant | Insert with same attempt id but different org — allowed |
| Concurrent insert race | Two concurrent inserts for same key — exactly one succeeds |
| Row lock with `FOR UPDATE` | `get_for_update` blocks concurrent write until transaction ends |
| Check constraint validation | Invalid `mode` or `status` is rejected at the database level |

### 19.4 Test Infrastructure Rules

- Unit tests must use fake/spy repositories, not real databases.
- PostgreSQL integration tests must use a real PostgreSQL instance (or testcontainers).
- No in-memory compatibility backend is permitted for integration tests.
- Tests must clean up created rows after each test (transaction rollback or explicit deletion).

## 20. Acceptance Criteria for Future Implementation

The future model and repository implementation is acceptable only when:

1. The `AIJobExecutionAttempt` ORM model exists with all required columns, constraints, and indexes as defined in Section 7.
2. The `UniqueConstraint("organization_id", "job_id", "execution_attempt_id")` is enforced at the database level.
3. All check constraints (mode, status, credits, timestamps) are present.
4. The FK to `ai_jobs(id)` is present.
5. Required indexes are present.
6. No method on `AIJobExecutionAttemptRepository` accepts or performs a lookup without `organization_id`.
7. No method uses `AsyncSessionLocal` or calls `commit()`.
8. No fallback or dialect branching exists in the repository code.
9. `get_for_update` uses `stmt.with_for_update()` (PostgreSQL row locking).
10. All unit tests in Section 19.1 pass.
11. All model/contract tests in Section 19.2 pass.
12. The migration (in its phase) creates the table with all constraints and indexes.
13. The migration passes repository policy guards.
14. No runtime code (routes, services, dependencies, schemas) is modified by the model+repository phase.
15. The worker mock service remains unchanged.
16. The internal trigger route remains unchanged.
17. No real provider, ComfyUI, GPU, payment, frontend, Docker, or runtime configuration changes are introduced.

## 21. Risks and Open Questions

### 21.1 Composite FK to ai_jobs(organization_id, id)

Adding a composite FK `(organization_id, job_id) REFERENCES ai_jobs(organization_id, id)` would enforce tenant-safe referential integrity at the database level. This requires either:

- Making `(organization_id, id)` the primary key of `ai_jobs`, or
- Adding a unique constraint on `ai_jobs(organization_id, id)`.

Both options are schema changes that affect the existing `AIJob` model and its relationships. This is deferred to a future phase.

**Risk:** Without a composite FK, an orphaned row could theoretically reference a job from a different tenant. The risk is mitigated by: (a) `organization_id` is set from trusted tenant context, never from client input; (b) all repository queries filter by both `organization_id` and `job_id`.

### 21.2 Stale in_progress Attempts

The contract defines `in_progress` → conflict on retry (Strategy A in the hardening contract). Stale attempt detection (e.g., attempts stuck `in_progress` for > 5 minutes) is not addressed in V1.

**Risk:** A worker crash could leave an attempt `in_progress` indefinitely, blocking retries. Mitigation: the caller (internal trigger) is synchronous within a request lifecycle. If the request fails, the transaction rolls back and the attempt insert is also rolled back. Stale detection is only needed if the process crashes after the insert but before the transaction commits or rolls back — a narrow window.

### 21.3 payload_digest Exclusion

`payload_digest` is not included in V1. If operational forensics later requires tracing the exact request body that produced an attempt, `payload_digest` would need to be added.

**Risk:** Low. The fingerprint provides conflict detection. `payload_digest` is a forensic tool, not a correctness requirement.

### 21.4 Ledger Global UniqueConstraint

`CreditLedgerEntry` still has a global `UniqueConstraint("idempotency_key")`. This means the ledger layer is not fully tenant-safe for idempotency. The attempt store partially compensates by blocking duplicate execution attempts early, but settlement could still collide if two different tenants somehow produce the same ledger idempotency key.

**Risk:** Low for the AI Jobs flow because the gateway derives keys as `ai_job:{organization_id}:{job_id}:{action}:{caller_key}`, which embeds `organization_id`. Two tenants with the same `job_id` and same `caller_key` would get different keys because the `organization_id` differs. The risk is for non-AI-Jobs flows that pass raw keys without tenant context.

### 21.5 Implementation Order

The recommended implementation order is:

1. `AIJobExecutionAttempt` ORM model (this contract).
2. Alembic migration for `ai_job_execution_attempts`.
3. `AIJobExecutionAttemptRepository` (this contract).
4. `AIJobWorkerMockExecutionService` (idempotency wrapper, scoped in hardening contract).
5. Update internal trigger route to use idempotency wrapper.
6. Unit tests for all new code.
7. PostgreSQL integration tests (separate phase or combined with step 4).

The model+repository must be implemented before the idempotency wrapper, because the wrapper depends on the repository. Steps 4 and 5 may be in a separate phase or combined.
