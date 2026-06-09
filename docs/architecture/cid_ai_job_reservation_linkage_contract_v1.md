# CID AI Job Reservation Linkage Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Scope: mandatory binding between AIJob and concrete ledger reservation entry for consume/release operations

## 1. Purpose

Define the mandatory link between `AIJob` and a concrete accounting reservation entry.

Its purpose is to:

- require `reservation_entry_id` for every consume and release operation;
- prevent consume/release against aggregated reserved balance without concrete reference;
- prepare the ledger, gateway, and orchestration layers for safe settlement;
- ensure that settlement operations are traceable to a specific reservation record.

This phase is documentary only. No implementation is created.

## 2. Out of Scope

This contract does not:

- implement the changes;
- create or modify Alembic migrations;
- create endpoints;
- create workers;
- create provider adapters;
- execute real ComfyUI, GPU, or external provider workloads.

## 3. Related Entities

### 3.1 `AIJob`

The job record that references a reservation via `reservation_entry_id`. The job is the authoritative source for which reservation it owns.

### 3.2 `CreditLedgerService`

The accounting authority. Must evolve to support lookup and validation against a concrete reservation entry.

### 3.3 `AIJobAccountingGateway`

The adapter between orchestration and the credit layer. Enforces reservation linkage at the gateway boundary.

### 3.4 `AIJobRepository`

Owns persistence for `AIJob`. Provides locked access to the job row during settlement.

### 3.5 `AIJobOrchestrationService`

Coordinates the business flow. Calls the gateway for settlement and the repository for persistence.

## 4. Central Rule

Every consume and release operation must include `reservation_entry_id`.

Required rules:

- `consume` requires `reservation_entry_id`;
- `release` requires `reservation_entry_id`;
- if `reservation_entry_id` is missing, the operation must fail;
- consuming or releasing by `organization_id` + amount alone is not permitted.

This rule prevents blind settlement against an aggregated balance and ensures every settlement is traceable.

## 5. Mandatory Reservation Validations

Before consuming or releasing, the system must verify all of the following:

1. the reservation entry exists;
2. it belongs to the same `organization_id`;
3. it belongs to the same `job_id`;
4. it corresponds to the correct attempt number if applicable;
5. its entry type is `reserve`;
6. it has not been previously consumed;
7. it has not been previously released;
8. the requested settlement amount does not exceed the available reserved amount;
9. the current state of the job permits the operation.

If any of these validations fails, the operation must be rejected with a clear error.

## 6. AI Job States

The reservation linkage interacts with the following job states:

- `reserved`: reservation created, awaiting execution. consume/release are not expected here.
- `running`: job is executing. consume or release may follow.
- `succeeded`: job completed successfully. consume is expected.
- `failed`: job failed. release or partial consume + release may follow.
- `cancel_requested`: cancellation in progress. release is expected.
- `cancelled`: job cancelled. release or expired reservation may follow.
- `consume_pending`: consume operation in progress.
- `consumed`: reservation fully consumed. no further settlement allowed.
- `release_pending`: release operation in progress.
- `released`: reservation fully released. no further settlement allowed.
- `expired`: reservation expired. release or cleanup may follow.

The gateway must validate that the job state permits the requested settlement action.

## 7. Partial Settlement

The contract must define partial settlement behavior:

- consuming less than the reserved amount and releasing the remainder is allowed;
- releasing the entire reservation is allowed;
- partial consume due to failure is allowed;
- double consume is blocked;
- double release is blocked.

When partial settlement occurs, the remaining reserved amount must be clearly tracked on the reservation entry.

## 8. Idempotency

Idempotency keys for settlement operations follow the tenant-safe convention:

- `ai_job:{organization_id}:{job_id}:consume`
- `ai_job:{organization_id}:{job_id}:release`

Expected behavior:

- retry with the same effective key and same payload produces an idempotent replay;
- retry with the same key but different payload produces a conflict;
- consume after release must fail;
- release after consume must fail, unless a partial-settlement policy explicitly allows releasing the surplus.

## 9. Minimum Metadata

Every consume and release entry must record:

- `organization_id`
- `job_id`
- `reservation_entry_id`
- `reservation_amount`
- `settlement_amount`
- `settlement_action`
- `operation_type`
- `project_id`
- `user_id`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `attempt_number`

This metadata ensures full auditability of every settlement operation.

## 10. Future Changes

### 10.1 Ledger Changes

- ledger lookup must support querying by `reservation_entry_id`;
- validation of tenant and job ownership must run before settlement;
- a settlement metadata field or model may be added.

### 10.2 Gateway Changes

- `consume_reserved_credits_for_job` must enforce `reservation_entry_id`;
- `release_reserved_credits_for_job` must enforce `reservation_entry_id`;
- both must run the full validation checklist before delegating to the ledger.

### 10.3 Repository and Orchestration Changes

- repository must provide locked access to the job during settlement;
- orchestration must coordinate repository, gateway, and ledger in a single transaction;
- `AIJob` must persist `reservation_entry_id` as a mandatory field after reservation.

### 10.4 Index and Constraint Recommendation

A unique constraint or index on `reservation_entry_id` in the ledger is recommended to enforce single-use semantics.

## 11. Future Test Requirements

Future implementation must include tests proving:

- consume fails without `reservation_entry_id`;
- release fails without `reservation_entry_id`;
- consume fails when the reservation belongs to a different tenant;
- release fails when the reservation belongs to a different job;
- consume after release fails;
- release after consume fails (or only releases surplus if partial-settlement policy is defined);
- retry of consume with same key does not duplicate;
- retry of release with same key does not duplicate;
- partial consume followed by release of surplus succeeds;
- double consume is blocked;
- double release is blocked.

## 12. Recommended Roadmap

1. reservation linkage contract
2. ledger reservation lookup implementation
3. gateway consume/release with `reservation_entry_id`
4. orchestration async integration
5. PostgreSQL-specific tests
6. internal endpoints
7. workers
