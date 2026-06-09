# CID AI Job Repository Async Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical future async repository contract for `AIJob` persistence, tenant-safe lookup, locking, and transaction coordination
Companion docs:
- `docs/architecture/cid_ai_job_orchestration_service_contract_v1.md`
- `docs/architecture/cid_ai_job_model_contract_v1.md`
- `docs/architecture/cid_ai_job_status_model_contract_v1.md`
- `src/models/ai_job.py`
- `src/services/ai_job_orchestration_service.py`
- `src/services/ai_job_transition_service.py`
- `src/services/credit_ledger_service.py`

## 1. Purpose

This document defines the future async repository contract for `AIJob`.

Its purpose is to:

- define one canonical persistence boundary for `AIJob` reads and writes;
- prevent future endpoints, workers, provider adapters, and internal tools from querying or mutating `AIJob` rows ad hoc;
- guarantee tenant-safe access patterns at the repository boundary;
- prepare row locking and transaction coordination for future orchestration with the credit ledger;
- make the future async orchestration layer explicit before real ORM integration starts.

This phase is documentary only. It does not implement repository code, routes, workers, migrations, or runtime integrations.

## 2. Out of Scope

This contract does not:

- create endpoints;
- create workers or queue runtimes;
- create provider adapters;
- execute real ComfyUI, GPU, or external provider workloads;
- modify `AIJob` schema or Alembic migrations;
- implement the repository yet;
- change `AIJobOrchestrationService` behavior in code in this phase.

## 3. Relationship with Other Services

### 3.1 `AIJob`

`AIJob` remains the persisted job envelope and audit record. The repository is the canonical persistence boundary for loading and saving that model.

### 3.2 `AIJobOrchestrationService`

The future orchestration service should depend on the repository rather than directly on ORM/session details. Mutating orchestration flows should load jobs through tenant-safe repository methods and use row locking where needed.

### 3.3 `AIJobTransitionService`

`AIJobTransitionService` remains the status transition authority. The repository does not validate business transitions by itself; it provides the locked and tenant-scoped persistence context in which those transitions are applied.

### 3.4 Future `AIJobAccountingGateway`

The future async accounting gateway should share the same `AsyncSession` as the repository so that job-state mutation and ledger mutation can participate in one transaction.

### 3.5 `CreditLedgerService`

`CreditLedgerService` remains the accounting authority. The repository exists to coordinate `AIJob` persistence with ledger mutation safely, not to replace ledger logic.

## 4. Minimum Future Repository Methods

The future async repository should expose, at minimum, the following conceptual methods:

- `async create(job: AIJob) -> AIJob`
- `async get(organization_id: str, job_id: str) -> AIJob | None`
- `async get_for_update(organization_id: str, job_id: str) -> AIJob | None`
- `async save(job: AIJob) -> AIJob`
- `async find_by_idempotency_key(organization_id: str, idempotency_key: str) -> AIJob | None`

These methods define the minimum contract needed by future orchestration and accounting integration. Additional helper methods may exist later, but they should not weaken tenant-safety or transaction rules defined here.

## 5. Critical Tenant Rule

The real repository must be tenant-safe by construction.

Required rules:

- there must be no real repository method equivalent to `get(job_id)` without `organization_id`;
- all repository reads must filter by `organization_id` in the query itself;
- cross-tenant access attempts must return `None` or not-found behavior;
- repository code must not load by `job_id` first and filter by tenant later in Python;
- `find_by_idempotency_key(...)` must also be tenant-scoped.

This rule exists to keep the tenant perimeter enforced at the persistence boundary rather than relying on caller discipline.

## 6. Locking Contract

`get_for_update(...)` is required for mutating orchestration paths that are sensitive to races.

Primary use cases include transitions involving jobs currently in:

- `reserved`
- `queued`
- `running`
- `cancel_requested`
- `consume_pending`
- `release_pending`

Expected behavior by backend:

- PostgreSQL: use `SELECT ... FOR UPDATE` or equivalent row-level lock.
- SQLite and lightweight test backends: provide controlled degradation without real row locking while keeping the same repository contract.

The contract must remain explicit that SQLite fallback is a test convenience, not proof of production locking semantics.

## 7. Transaction Rules

The repository must not own transaction finalization.

Required rules:

- the repository does not call `commit()`;
- the surrounding application/service layer owns transaction boundaries;
- the repository may call `flush()` when ids, constraints, or immediate visibility are needed;
- the repository must be able to share one `AsyncSession` with orchestration and accounting services.

This allows one business operation to coordinate `AIJob` persistence and ledger mutation inside the same transactional context.

## 8. Future Atomicity Model

The following sequence should eventually run in one transaction for mutating accounting flows:

1. load the job through `get_for_update(organization_id, job_id)`;
2. validate the lifecycle transition through `AIJobTransitionService`;
3. execute the required ledger mutation;
4. update `AIJob` fields such as status, timestamps, and linked ledger entry ids;
5. flush;
6. commit outside the repository.

This ordering is important because it reduces the risk of:

- ledger mutation succeeding while `AIJob` state is not persisted;
- `AIJob` state changing to `reserved`, `consumed`, or `released` before the authoritative ledger mutation exists;
- concurrent consume/release races on the same job attempt.

The repository contract alone does not solve all atomicity issues, but it is a required prerequisite for doing so safely.

## 9. Idempotency Contract

`find_by_idempotency_key(...)` must always be scoped by:

- `organization_id`
- `idempotency_key`

Global idempotency by key alone is forbidden for the repository contract.

The repository should be compatible with future derived keys such as:

- `ai_job:{organization_id}:{job_id}:reserve`
- `ai_job:{organization_id}:{job_id}:consume`
- `ai_job:{organization_id}:{job_id}:release`

This prepares the orchestration layer for tenant-safe retries and duplicated callback handling without allowing collisions between organizations.

## 10. Protection Against Tenant Mutation

`save(job)` must not allow silent tenant reassignment.

Required rule:

- if the persisted row belongs to one `organization_id`, the repository must reject attempts to save the same job under a different `organization_id`.

The exact error type can be defined in implementation, but the contract requires failure, not silent reassignment.

This protects against accidental or malicious cross-tenant mutation in higher layers.

## 11. Future Test Requirements

Future implementation must be covered by tests that prove the repository contract, including at least:

- `get(...)` filters by tenant;
- `get_for_update(...)` filters by tenant;
- `find_by_idempotency_key(...)` does not collide cross-tenant;
- `save(...)` rejects changes to `organization_id`;
- repository methods do not call `commit()`;
- repository methods may use `flush()` when required;
- PostgreSQL-backed tests verify contractual locking behavior;
- SQLite/test fallback is explicit and controlled even without real row locks.

Recommended future test layers:

- pure repository tests with fake/session spy coverage for commit/flush behavior;
- lightweight integration tests with temporary DB/session;
- PostgreSQL-specific tests for real `FOR UPDATE` semantics when available.

## 12. Recommended Roadmap

Recommended implementation order:

1. repository async contract
2. repository async implementation
3. accounting gateway async contract and implementation
4. ledger tenant-safe idempotency adjustment
5. reservation linkage contract and implementation
6. orchestration async integration
7. internal endpoints
8. workers

This order is recommended because orchestration should not be connected to real accounting until the persistence boundary is tenant-safe, lock-aware, and transaction-compatible.

## 13. Delivery Note

This document defines the contract only. It does not implement any repository, does not change backend runtime behavior, and does not authorize direct use of ORM/session internals by future callers outside the repository boundary.
