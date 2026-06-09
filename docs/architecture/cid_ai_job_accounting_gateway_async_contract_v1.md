# CID AI Job Accounting Gateway Async Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Scope: canonical async accounting gateway contract for AI Job credit operations

## 1. Purpose

Define the future `AIJobAccountingGateway` as the sole adapter between AI Job orchestration and the credit layer.

Its purpose is to:

- coordinate credit estimation, reservation, consumption, and release for a concrete `AIJob`;
- keep `CreditLedgerService` as the sole accounting authority;
- prevent orchestration from speaking directly to multiple accounting services in a scattered way;
- provide a single async boundary where session, idempotency, and transaction rules converge.

This phase is documentary only. No implementation is created.

## 2. Out of Scope

This contract does not:

- implement the gateway;
- create endpoints;
- create workers;
- create provider adapters;
- execute real ComfyUI, GPU, or external provider workloads;
- modify Alembic migrations;
- change `CreditLedgerService` internals yet;
- modify `AIJob` schema.

## 3. Component Relationships

### 3.1 `AIJobOrchestrationService`

The future orchestration service calls the gateway exclusively for credit operations. It does not call `AIJobCostingService`, `CreditGateService`, or `CreditLedgerService` directly for job-level credit flows.

### 3.2 `AIJobRepository`

The repository owns persistence for `AIJob`. The gateway and repository share the same `AsyncSession`. Ledger entry ids produced by the gateway are persisted on `AIJob` via the repository.

### 3.3 `AIJobCostingService`

Costing remains the authority for estimating credit cost per operation type, provider, and workflow. The gateway delegates cost estimation to it but does not let it write ledger entries directly.

### 3.4 `CreditGateService`

Gate remains the authority for credit availability checks. The gateway delegates availability checks to it but does not let it perform mutations.

### 3.5 `CreditLedgerService`

Ledger remains the sole accounting authority. The gateway does not replace it. The gateway adapts its calls to the AI Job domain model and enforces job-level idempotency and reservation linkage.

### 3.6 `AIJobTransitionService`

Transition remains the authority for lifecycle validation. The gateway is orthogonal to transition rules; it only produces the ledger entry ids that transition may store on the job.

### 3.7 `AIJob`

`AIJob` does not calculate balances. It stores references to ledger entry ids produced by the gateway.

## 4. Authority Principle

`CreditLedgerService` is the accounting authority.

The gateway:

- coordinates;
- adapts;
- enforces job-level idempotency;
- enforces reservation linkage;
- passes session and metadata through.

The gateway does not:

- own accounting rules;
- calculate balances;
- replace ledger internals.

## 5. Async Session Rule

All gateway methods receive `AsyncSession` from the caller above (orchestration or use case layer).

Required rules:

- the gateway never creates its own session;
- the gateway never calls `commit()`;
- the gateway may call `flush()` when needed for constraint visibility;
- `AIJobRepository`, `AIJobAccountingGateway`, and `CreditLedgerService` must share the same session within one business operation.

This ensures one business operation stays inside one transactional boundary.

## 6. Minimum Async Contract

The future gateway must expose, at minimum, these conceptual methods:

### 6.1 `estimate_credit_cost`

Purpose: compute estimated credits without mutating ledger.

Parameters:
- `organization_id`
- `job_id`
- `operation_type`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`

Returns: `CreditEstimate`

### 6.2 `check_credit_availability`

Purpose: verify that the organization has enough credits without mutating ledger.

Parameters:
- `organization_id`
- `estimated_credits`

Returns: `CreditAvailabilityResult`

### 6.3 `reserve_credits_for_job`

Purpose: create a reservation ledger entry and return its entry id.

Parameters:
- `organization_id`
- `job_id`
- `estimated_credits`
- `idempotency_key`
- `caller_key`
- `project_id`
- `user_id`
- `operation_type`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`

Returns: `ReservationResult` with `reservation_entry_id`

### 6.4 `consume_reserved_credits_for_job`

Purpose: consume reserved credits against a concrete reservation. `reservation_entry_id` is mandatory.

Parameters:
- `organization_id`
- `job_id`
- `reservation_entry_id` (mandatory)
- `actual_credits`
- `idempotency_key`
- `caller_key`
- `project_id`
- `user_id`
- `operation_type`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`
- `output_asset_ids`

Returns: `SettlementResult`

### 6.5 `release_reserved_credits_for_job`

Purpose: release reserved credits back. `reservation_entry_id` is mandatory.

Parameters:
- `organization_id`
- `job_id`
- `reservation_entry_id` (mandatory)
- `release_credits`
- `idempotency_key`
- `caller_key`
- `project_id`
- `user_id`
- `operation_type`

Returns: `SettlementResult`

## 7. Idempotency Contract

Idempotency is always tenant-scoped. Global idempotency by raw key is forbidden.

### 7.1 Derived Keys

Effective keys must be derived as:

- `ai_job:{organization_id}:{job_id}:reserve`
- `ai_job:{organization_id}:{job_id}:consume`
- `ai_job:{organization_id}:{job_id}:release`

### 7.2 Optional Caller Suffix

When `caller_key` is provided:

- `ai_job:{organization_id}:{job_id}:{action}:{caller_key}`

This allows the same job to have multiple reservation/consume/release cycles without collision.

### 7.3 Rules

- Retries with the same effective key must not duplicate ledger entries.
- The same raw key in a different organization must never collide.
- The gateway derives the effective key and passes it through to `CreditLedgerService`.

## 8. Reservation Linkage

### 8.1 Mandatory Field

`consume` and `release` require `reservation_entry_id`. If absent, the gateway must reject the call.

### 8.2 Validation Rules

Before mutating, the gateway must verify that the reservation entry:

- belongs to the same `organization_id`;
- belongs to the same `job_id`;
- has not already been consumed or released (depending on the operation).

### 8.3 Ledger Evolution

The current ledger must evolve to operate against a concrete reservation entry. This contract prepares that boundary without implementing it yet.

## 9. Atomicity Sequence

The following sequence must run in one transaction for mutating operations:

1. repository `get_for_update(organization_id, job_id)` -- lock the job row;
2. transition preview -- validate the lifecycle state is appropriate for the mutation;
3. gateway credit mutation -- reserve, consume, or release via `CreditLedgerService`;
4. update `AIJob` fields -- set `reservation_entry_id`, ledger entry ids, status, timestamps;
5. repository save/flush;
6. commit outside the repository (ownership lies with the orchestration or use case layer).

This sequence reduces the risk of:

- ledger mutation succeeding while `AIJob` state is not persisted;
- `AIJob` state changing before the authoritative ledger entry exists;
- concurrent consume/release races on the same job.

## 10. Expected Errors

The gateway must produce clear, typed errors. Conceptual categories:

| Error | Meaning |
|---|---|
| `insufficient_credits` | Not enough credits for reservation or consumption |
| `reservation_not_found` | `reservation_entry_id` does not exist |
| `idempotency_conflict` | Different payload with same idempotency key |
| `reservation_already_consumed` | Reservation was already consumed |
| `reservation_already_released` | Reservation was already released |
| `cross_tenant_reservation` | Reservation belongs to a different organization |
| `accounting_unavailable` | Ledger or gate service is temporarily unavailable |
| `invalid_amount` | Credit amount is zero, negative, or exceeds policy limits |

These are conceptual categories for the contract. The actual error types and codes are defined during implementation.

## 11. Minimum Accounting Metadata

Every gateway call must pass accounting metadata for auditability:

- `organization_id`
- `project_id`
- `user_id`
- `job_id`
- `operation_type`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`
- `output_asset_ids`
- `estimated_credits`
- `actual_credits`
- `reservation_entry_id`
- `settlement_action`

Not all fields are present in every call. For example, `estimate` does not produce `reservation_entry_id`; `consume` does not produce `estimated_credits`. The contract requires that every relevant field be passed when available.

## 12. Future Test Requirements

Future implementation must be covered by tests proving the contract:

- `estimate` uses costing/gate without mutating ledger;
- `reserve` derives a tenant-safe idempotency key;
- `consume` requires `reservation_entry_id`;
- `release` requires `reservation_entry_id`;
- the same raw key in a different tenant does not collide;
- retry of `reserve` with same key does not duplicate ledger entries;
- retry of `consume` with same key does not duplicate ledger entries;
- `consume` after `release` fails;
- `release` after `consume` fails;
- gateway does not call `commit()`;
- gateway uses the session received from the caller.

Recommended layers:

- unit tests with fake/spy services proving delegation and idempotency key derivation;
- integration tests proving session sharing and flush behavior;
- PostgreSQL-specific tests for real reservation linkage once ledger evolves.

## 13. Recommended Roadmap

1. accounting gateway async contract
2. accounting gateway async implementation with fakes
3. ledger tenant-safe idempotency
4. ledger reservation linkage
5. orchestration async integration
6. internal endpoints
7. workers
8. real provider adapters

This order is recommended because the gateway must be proven with fakes before connecting to real ledger mutations and real provider workloads.
