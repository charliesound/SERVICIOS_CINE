# CID AI Job Model Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: canonical future `AIJob` model for CID SaaS, aligned with status lifecycle, credit gating, ledger reconciliation, and auditability
Companion docs:
- `docs/architecture/cid_ai_job_status_model_contract_v1.md`
- `docs/architecture/cid_ai_job_costing_contract_v1.md`
- `docs/architecture/cid_billing_models_v1.md`
- `docs/architecture/cid_saas_model_contract_v1.md`
- `src/services/ai_job_status_service.py`
- `src/services/ai_job_costing_service.py`
- `src/services/credit_gate_service.py`
- `src/services/credit_ledger_service.py`
- `src/models/billing.py`

## 1. Purpose

This contract defines the future canonical `AIJob` model for CID SaaS. Its purpose is to:

- define one auditable source of truth for AI job identity, lifecycle, and credit-facing state;
- prepare a future ORM model and Alembic migration without implementing them in this phase;
- avoid ad hoc table design for states, credit traces, provider references, and workflow metadata;
- make future workers, internal services, provider adapters, and admin tooling converge on one durable model shape.

This phase is documentary only. It does not implement an ORM table, worker, internal queue, endpoint, migration, or real AI execution.

## 2. Scope

This contract:

- is a specification only;
- does not create the `ai_jobs` table;
- does not create SQLAlchemy ORM code yet;
- does not create workers or provider callbacks;
- does not create public or internal endpoints;
- does not execute ComfyUI, GPU, LLM, or other real AI workloads.

## 3. Entity Definition

`AIJob` represents one auditable unit of costly or potentially costly AI work inside CID. A job may correspond to:

- one single AI execution request;
- one queued attempt of a workflow run;
- one retry attempt derived from a parent job;
- one provider-backed or workflow-backed operation that requires estimate, reserve, consume, or release semantics.

The model exists to connect:

- tenant ownership and access control;
- operation identity and canonical `operation_type`;
- execution state and lifecycle timestamps;
- credit estimation, reservation, consumption, and release;
- provider/workflow/model metadata;
- input and output asset traceability;
- failure and retry audit.

## 4. Future Minimum Fields

The future `AIJob` model should include at least:

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
- `provider_job_id`
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
- `estimated_at`
- `credit_checked_at`
- `reserved_at`
- `queued_at`
- `started_at`
- `finished_at`
- `cancel_requested_at`
- `cancelled_at`
- `consume_pending_at`
- `consumed_at`
- `release_pending_at`
- `released_at`
- `expires_at`
- `metadata`

`provider_job_id` is recommended even though it is not mandatory in the minimum list from the phase brief, because provider callbacks, late reconciliation, and duplicated callback handling will need a stable external run reference.

## 5. Field Types and Rules

### 5.1 Identifiers

- `id`: UUID/string following current project convention. The existing billing models use `String(36)` identifiers, so the initial recommendation is to keep `AIJob.id` aligned with that convention.
- `organization_id`: required UUID/string; mandatory tenant perimeter.
- `project_id`: optional UUID/string; nullable because some AI jobs may be organization-level.
- `user_id`: optional UUID/string in the schema, but operationally recommended whenever a human or service actor initiated the job.
- `parent_job_id`: optional self-reference for retries, splits, or derived attempts.
- `reservation_entry_id`, `consume_entry_id`, `release_entry_id`: optional UUID/string references to `credit_ledger_entries.id`.
- `provider_job_id`: optional string from external provider/runtime namespace; should not be treated as globally unique unless the provider contract guarantees it.

### 5.2 Operation and Status

- `operation_type`: required non-empty string, normalized the same way `CreditGateService` normalizes it today.
- `status`: required non-empty string from the canonical catalog implemented by `AIJobStatusService`.
- `operation_type` must remain aligned with `CreditGateService` canonical operations and future approved expansions.
- `status` must remain aligned with `src/services/ai_job_status_service.py`; no free-form status strings should be trusted.

### 5.3 Credit Fields

- `estimated_credits`: non-negative integer; expected estimate for the attempt.
- `reserved_credits`: non-negative integer; reservation amount held for the attempt.
- `consumed_credits`: non-negative integer; amount ultimately charged.
- `released_credits`: non-negative integer; amount ultimately returned to available balance.

Recommended invariants:

- no credit field may be negative;
- `consumed_credits` and `released_credits` should not both be positive for the same settled attempt unless a future adjustment policy explicitly documents a split settlement;
- in the initial model, `reserved_credits` should normally equal `estimated_credits` at reservation time unless pricing/version policy introduces controlled variance.

### 5.4 Provider and Workflow Fields

- `provider_type`: optional short string such as `openai`, `replicate`, `runpod`, `comfyui`, `internal`.
- `provider_name`: optional human-readable provider/runtime identifier.
- `workflow_id`: optional string identifying the canonical workflow template or route.
- `workflow_version`: optional string for immutable or semver-like versioning.
- `workflow_hash`: optional string for reproducible workflow fingerprinting.
- `model_name`: optional string for the LLM, image, audio, or video model used.

### 5.5 Asset References

- `input_asset_ids`: future JSON/list field or future relational child table.
- `output_asset_ids`: future JSON/list field or future relational child table.

Initial recommendation:

- start with JSONB arrays of string asset ids for speed of implementation and audit portability;
- keep the contract open for later extraction into a relational `ai_job_assets` table if query patterns, referential integrity, or asset-level permissions require it.

This gives an initial model that is simple enough for backend rollout while leaving room for a more normalized design later.

### 5.6 Error and Retry Fields

- `error_code`: optional string; stable machine-facing failure category.
- `failure_reason`: optional text; human-readable explanation or normalized provider failure summary.
- `attempt_number`: non-negative integer; recommended default `1`.
- `idempotency_key`: optional string, but strongly recommended for mutating flows and callback reconciliation.

### 5.7 Timestamps

All timestamps are future datetime columns and should be UTC-based:

- `created_at`
- `estimated_at`
- `credit_checked_at`
- `reserved_at`
- `queued_at`
- `started_at`
- `finished_at`
- `cancel_requested_at`
- `cancelled_at`
- `consume_pending_at`
- `consumed_at`
- `release_pending_at`
- `released_at`
- `expires_at`

Timestamp semantics should reflect actual lifecycle progression, not merely best-effort logging.

### 5.8 Metadata

- `metadata`: future JSONB field for extensible audit payload.
- It should preserve canonical costing metadata already shaped by `AIJobCostingService`, including `operation_type`, `estimated_credits`, `provider_type`, `provider_name`, `workflow_id`, `workflow_version`, `workflow_hash`, `model_name`, `input_asset_ids`, `output_asset_ids`, `job_status`, and `failure_reason`.
- Internal canonical keys should remain protected from unsafe overwrite by arbitrary external metadata.

## 6. Future Relationships

The model should be designed for these future relationships:

- `organization_id` -> tenant / organization ownership boundary;
- `project_id` -> optional project association;
- `user_id` -> actor who launched or requested the job;
- `reservation_entry_id` -> `credit_ledger_entries.id`;
- `consume_entry_id` -> `credit_ledger_entries.id`;
- `release_entry_id` -> `credit_ledger_entries.id`;
- `parent_job_id` -> previous `AIJob.id` for retry or derivation lineage;
- future association with asset records for `input_asset_ids` and `output_asset_ids`;
- future association with versioned ComfyUI workflow descriptors;
- future association with provider-run records, callback logs, or execution envelopes.

The `AIJob` model should reference ledger entries, not replace them. Billing remains authoritative in `credit_ledger_entries`.

## 7. Recommended Future Indexes

Recommended initial indexes:

- primary key on `(id)`
- index on `(organization_id, created_at)`
- index on `(organization_id, status)`
- index on `(organization_id, project_id, created_at)`
- index on `(organization_id, operation_type, created_at)`
- index on `(parent_job_id)`
- index on `(reservation_entry_id)`
- index on `(consume_entry_id)`
- index on `(release_entry_id)`
- index on `(provider_job_id)` when callbacks or reconciliation rely on it

Recommended uniqueness rules:

- partial or composite uniqueness for `idempotency_key` scoped by `organization_id` when `idempotency_key` is present;
- if provider callback routing proves ambiguous, consider composite uniqueness on `(provider_type, provider_job_id)` when both are non-null.

## 8. Future Constraints

The future table/model should enforce or clearly validate:

- `status` must belong to the canonical `AIJobStatusService` catalog;
- all credit fields must be non-negative;
- `organization_id` is required;
- `operation_type` is required;
- `attempt_number` must be positive or zero according to final convention; recommended minimum is `1`;
- no `running` job without prior reservation evidence such as `reserved_at` and `reservation_entry_id`;
- no `consumed` status without `consume_entry_id`;
- no `released` status without `release_entry_id`;
- no double consume for the same attempt;
- no double release for the same attempt;
- `consumed` and `released` are settled terminal outcomes for one attempt;
- `idempotency_key` is optional at schema level but recommended for all mutating operations and callback-driven updates.

Recommended semantic checks:

- `queued_at` should not precede `reserved_at`;
- `started_at` should not precede `queued_at` when a queue stage exists;
- `consumed_at` should not exist before `consume_pending_at`;
- `released_at` should not exist before `release_pending_at`;
- `cancelled_at` should not exist without a prior `cancel_requested_at` unless future policy documents an immediate administrative cancellation path.

## 9. Lifecycle Coverage

The model must be able to register and audit:

### 9.1 Creation

- job envelope created;
- tenant/project/user context assigned;
- base metadata initialized.

### 9.2 Estimation

- `operation_type` normalized;
- `estimated_credits` derived;
- `estimated_at` recorded.

### 9.3 Credit Check

- advisory preflight completed;
- `credit_checked_at` recorded;
- no ledger mutation yet.

### 9.4 Reservation

- reservation created in `credit_ledger_entries`;
- `reservation_entry_id`, `reserved_credits`, and `reserved_at` recorded.

### 9.5 Queueing

- job accepted by queue/router/provider handoff;
- `queued_at` recorded.

### 9.6 Execution

- execution started;
- `started_at` recorded;
- provider/runtime metadata attached.

### 9.7 Success

- successful result available;
- `finished_at` recorded;
- next transition expected toward `consume_pending`.

### 9.8 Failure

- failure metadata recorded;
- `error_code` and `failure_reason` preserved;
- next transition expected toward `release_pending` or `retry_pending`.

### 9.9 Cancellation

- cancellation requested before or during execution;
- `cancel_requested_at` and `cancelled_at` tracked separately;
- release path remains auditable.

### 9.10 Consumption

- `consume_pending_at` and `consumed_at` registered;
- `consume_entry_id` linked to ledger authority.

### 9.11 Release

- `release_pending_at` and `released_at` registered;
- `release_entry_id` linked to ledger authority.

### 9.12 Retry

- `attempt_number` incremented;
- `parent_job_id` or retry lineage preserved;
- reservation reuse or replacement made explicit.

### 9.13 Expiration

- `expires_at` tracked;
- expiration can occur for reservation lifetime or queue lifetime;
- path remains `expired -> release_pending -> released`.

## 10. Relationship with `AIJobStatusService`

- `AIJob.status` must be validated using `AIJobStatusService` helpers.
- Allowed transitions must pass through a future job transition service or equivalent boundary that uses the canonical transition map.
- The current canonical status set includes `created`, `estimated`, `credit_checked`, `reserved`, `queued`, `running`, `succeeded`, `partial_succeeded`, `failed`, `cancel_requested`, `cancelled`, `consume_pending`, `consumed`, `release_pending`, `released`, `retry_pending`, and `expired`.
- The current canonical transition model already covers reservation, queueing, cancellation, consumption, release, retry, and expiry paths.
- The ORM model must not trust free-form status strings written directly by callers.

## 11. Relationship with `AIJobCostingService`

- The model must store enough information to reconstruct estimate, reserve, consume, and release decisions for audit and reconciliation.
- Canonical metadata should preserve provider/workflow/model/assets fields already normalized by `AIJobCostingService`.
- `estimated_credits` must remain traceable to the estimate used at reservation time.
- `job_status` inside metadata should never drift indefinitely from `AIJob.status`; if both exist, the column is authoritative and metadata is supporting audit context.
- Future implementations should reuse canonical metadata keys rather than invent parallel naming.

## 12. Relationship with `CreditLedgerService`

- `CreditLedgerService` remains the accounting authority.
- `AIJob` references ledger entries through `reservation_entry_id`, `consume_entry_id`, and `release_entry_id`; it does not replace the append-only ledger.
- Job state and ledger state must reconcile consistently:
  - reserved job -> reservation ledger entry exists;
  - consumed job -> consume ledger entry exists;
  - released job -> release ledger entry exists.
- Future reconciliation tooling should compare `AIJob.status`, credit fields, and linked ledger entries to detect anomalies.

## 13. ComfyUI Alignment

For ComfyUI-oriented execution, the model should support:

- `workflow_id`, `workflow_version`, and `workflow_hash`;
- metadata for models, LoRAs, custom nodes, and execution presets when applicable;
- reproducible workflow identity rather than raw ad hoc prompt text alone;
- output assets linked back to the job;
- auditability of which workflow version produced which output.

Jobs should represent reproducible workflows, not loose prompt strings without traceability.

## 14. DaVinci Bridge Alignment

For DaVinci Bridge use cases, jobs may represent:

- packaging;
- analysis;
- synchronization;
- export-oriented preparation.

The model should allow:

- clip/audio/sequence references through metadata or asset ids;
- future timecode or clapboard-aligned synchronization metadata;
- auditable outputs tied to one job record;
- provider/runtime distinction between local bridge logic and external AI-backed processing.

## 15. Provider Callbacks and External Runs

The model should anticipate:

- duplicated callbacks;
- late callbacks after timeout or cancellation;
- provider-specific external run ids;
- reconciliation between callback payloads, `idempotency_key`, current `status`, and canonical metadata.

For this reason, `provider_job_id` is recommended as a future field even in the first ORM iteration.

Callback handling should prefer:

- idempotent update semantics;
- explicit transition validation;
- ignoring or quarantining impossible backward transitions;
- audit retention of raw callback identifiers outside the core status field when needed.

## 16. Retries

Retry support should use:

- `attempt_number` to distinguish attempts;
- `parent_job_id` to preserve lineage;
- explicit policy to determine whether a retry reuses an existing reservation or creates a new one.

Recommended rule:

- if scope, cost, workflow, or provider assumptions materially change, create a new reservation path and treat the retry as a distinct auditable attempt;
- reservation reuse should happen only under an explicit policy documented by product and billing logic;
- `retry_pending` should represent orchestration state, not a hidden execution side effect.

## 17. Cancellations

The model must support auditable cancellation paths for:

- cancellation before reservation;
- cancellation after reservation but before execution;
- cancellation while queued;
- cancellation while running;
- cancellation after success but before final consume if product policy allows intervention;
- cancellation with partial result where acceptance and charge policy still need resolution.

Cancellation data should make it possible to answer:

- who requested cancellation;
- when it was requested;
- whether execution had started;
- whether credits were released or ultimately consumed.

## 18. Expiration

The model should support:

- `expires_at` as explicit reservation/queue lifetime boundary;
- expiration of reserved but never started jobs;
- expiration of queued jobs that do not progress in time;
- canonical transition path `expired -> release_pending -> released`.

Expiration should be auditable independently from manual cancellation or active runtime failure.

## 19. Audit Requirements

The future model should allow CID to answer:

- who launched the job;
- when each state transition happened;
- what was estimated, reserved, consumed, and released;
- which provider, workflow, and model were used;
- which assets entered and exited the workflow;
- which errors or failure reasons occurred;
- whether the job was retried, cancelled, expired, consumed, or released.

Audit quality matters for:

- customer support;
- finance reconciliation;
- internal ops;
- provider dispute analysis;
- security investigation;
- enterprise reporting.

## 20. Security and Multitenancy

- `organization_id` is the hard perimeter for tenant isolation.
- `AIJob` must not be readable or mutable across tenants.
- Project scoping should further narrow visibility where applicable.
- Roles and permissions should govern who may launch, cancel, retry, inspect, or reconcile jobs.
- Plan/module entitlements should determine who may access costly AI operations.
- Credit availability remains a prerequisite for execution of gated operations.

The model must be compatible with existing CID multitenant isolation rules and should not allow cross-tenant reconciliation shortcuts.

## 21. Roadmap

Recommended future implementation order:

1. Implement ORM `AIJob` model aligned with this contract.
2. Create a future Alembic migration for `ai_jobs`.
3. Introduce a dedicated job transition service that wraps `AIJobStatusService`.
4. Add internal create/estimate/check/reserve/queue orchestration wrappers.
5. Add worker queue integration.
6. Add provider adapters and callback reconciliation.
7. Add internal endpoints or service surfaces for job inspection and control.
8. Add UI history and usage views.
9. Add admin reconciliation tools for AI job vs. ledger anomalies.

## 22. Phase Boundary

This document is intentionally limited to specification. In this phase CID does not:

- implement the `AIJob` ORM class;
- create a migration;
- create routes or endpoints;
- launch workers;
- dispatch real AI jobs;
- execute ComfyUI runtime flows.

That boundary is deliberate so the model can be reviewed and stabilized before schema and runtime work begin.
