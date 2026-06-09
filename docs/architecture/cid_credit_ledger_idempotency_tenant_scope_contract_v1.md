# CID Credit Ledger Idempotency Tenant Scope Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Scope: evolve CreditLedgerService idempotency from global key to tenant-safe scope

## 1. Problem Statement

The current `CreditLedgerService` looks up idempotency by `idempotency_key` alone. The key is stored and matched without any tenant context.

This design assumes that idempotency keys are globally unique across all organizations. In practice, external callers, workflow engines, and integration layers may reuse raw keys such as `reserve`, `consume`, or `release` across different tenants.

## 2. Cross-Tenant Collision Risk

If two organizations happen to submit the same raw idempotency key, the current ledger behavior will:

- treat the second request as an idempotent replay of the first;
- return the first request result instead of executing a new independent operation;
- silently mix accounting entries across tenants.

This is a correctness and security issue. Idempotency must be scoped to the organization that owns the ledger entry.

## 3. New Rule

Effective idempotency identity = `organization_id` + `idempotency_key`.

Required changes:

- every idempotency lookup must filter by `organization_id`;
- every idempotency insert must store `organization_id` alongside the key;
- the same raw key in a different organization must be treated as a completely independent operation;
- no idempotency check may run without tenant context.

## 4. AI Job Derived Keys Compatibility

The AI Job accounting gateway already derives tenant-safe keys:

- `ai_job:{organization_id}:{job_id}:reserve`
- `ai_job:{organization_id}:{job_id}:consume`
- `ai_job:{organization_id}:{job_id}:release`

These derived keys already embed `organization_id` in the key string itself. With the new tenant-scoped idempotency rule, the organization context is enforced twice: once in the key derivation and once in the ledger lookup. This is intentional defense-in-depth.

## 5. Raw External Key Policy

When callers pass raw idempotency keys (not derived from AI Job conventions):

- the key must never be used globally without organization context;
- the gateway or caller layer must always pair the raw key with `organization_id`;
- the ledger must reject any idempotency operation that arrives without `organization_id`.

This prevents accidental cross-tenant collisions from external integrations that reuse generic key names.

## 6. Expected Behavior

### 6.1 Same Key, Same Tenant, Same Payload

Idempotent replay. The ledger returns the previous result without creating a new entry.

### 6.2 Same Key, Same Tenant, Different Payload

Conflict. The ledger must reject the request. The same key cannot map to two different operations within one organization.

### 6.3 Same Key, Different Tenant

Independent operation. Each organization operates on its own idempotency namespace. No collision occurs.

## 7. Future Changes

### 7.1 Service Changes

- `CreditLedgerService` must accept and propagate `organization_id` in all idempotency-related methods;
- idempotency lookup queries must include `organization_id` as a filter;
- idempotency insert operations must store `organization_id` as a column;
- callers that currently pass only `idempotency_key` must be updated to pass `organization_id` as well.

### 7.2 Model Changes

- the idempotency record model (or ledger entry model) must include `organization_id` as a persisted field;
- the field must be non-nullable and indexed.

### 7.3 Test Changes

- existing tests must be updated to pass `organization_id` in all idempotency assertions;
- new tests must prove tenant isolation behavior.

## 8. Index and Constraint Recommendation

A unique constraint on the combination of `organization_id` + `idempotency_key` is recommended.

This constraint:

- enforces tenant-scoped uniqueness at the database level;
- prevents silent cross-tenant collisions;
- makes the idempotency guarantee explicit in the schema.

The constraint must be added via Alembic migration during the implementation phase, not in this spec phase.

## 9. Future Test Requirements

Future implementation must include tests proving:

- the same key in two different tenants does not collide;
- the same key in the same tenant does not duplicate ledger entries;
- a different payload with the same key in the same tenant fails with conflict;
- reserve/consume/release operations derive tenant-safe idempotency keys;
- any idempotency operation without `organization_id` is rejected;
- the unique constraint (once applied) prevents duplicate key inserts at the database level.

## 10. Out of Scope

This contract does not:

- implement the changes;
- create or modify Alembic migrations;
- modify service code;
- create endpoints;
- create workers;
- change runtime behavior in this phase.
