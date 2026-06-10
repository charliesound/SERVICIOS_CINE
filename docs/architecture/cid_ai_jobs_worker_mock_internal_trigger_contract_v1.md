# CID AI Jobs Worker Mock Internal Trigger Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-10
Phase: CID.SAAS.AI.JOBS.WORKER.MOCK.INTERNAL.TRIGGER.CONTRACT.1
Scope: canonical contract for a future internal/admin trigger for the CID AI Jobs mock worker

Companion docs:

- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_worker_mock_internal_trigger_contract_v1.md` (this document)
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future contract for triggering the CID AI Jobs mock worker from an internal, admin, or server-to-server context.

The trigger exists to:

- allow controlled execution of the full AI Job lifecycle through the backend-only mock worker;
- validate create, estimate, check, reserve, execute, consume, release, status, and history flows end-to-end;
- support internal testing and beta validation before real workers, queues, and providers are connected;
- keep mock execution strictly outside the public frontend and outside normal user authorization;
- prevent unauthorized or accidental credit consumption, credit release, or job execution by non-internal actors.

This phase is documentary only. It does not implement the trigger endpoint, create routes, add frontend UI, connect providers, mutate models, create Alembic migrations, or change runtime configuration.

## 2. Read-Only Audit Surface

Read-only audit performed before writing this contract:

- `src/services/ai_job_worker_mock_service.py`
- `src/services/ai_job_async_orchestration_service.py`
- `src/routes/ai_job_routes.py`
- `src/dependencies/ai_job_orchestration.py`
- `src/schemas/ai_job_api_schema.py`
- `docs/architecture/cid_ai_jobs_worker_mock_contract_v1.md`
- `docs/architecture/cid_ai_jobs_execution_transitions_contract_v1.md`
- `docs/architecture/cid_ai_jobs_api_endpoints_contract_v1.md`

Observed relevant implementation facts:

- `AIJobWorkerMockService` is implemented and receives `AIJobAsyncOrchestrationService` at construction time.
- `AIJobWorkerMockService.execute(session, command)` composes orchestration methods only; it never calls `CreditLedgerService`, `CreditGateService`, `AIJobCostingService`, or any external provider.
- `AIJobWorkerMockService` does not create its own session, does not use `AsyncSessionLocal`, and does not call `commit()` internally.
- `AIJobWorkerMockService` uses `_require_loaded_job(...)` to guard against missing jobs returned from `get_ai_job(...)`.
- `AIJobWorkerMockCommand` is a frozen dataclass with `organization_id`, `job_id`, `requested_by`, `execution_attempt_id`, `mode`, and optional credit/metadata fields.
- `AIJobWorkerMockResult` is a frozen dataclass with `organization_id`, `job_id`, `mode`, `status`, settlement fields, and metadata.
- `AIJobAsyncOrchestrationService.get_ai_job(session, organization_id, job_id)` raises `AIJobAsyncNotFoundError` if the job is not found within the tenant scope.
- `AIJobAsyncOrchestrationService` exposes execution transition methods: `enqueue_ai_job`, `start_ai_job`, `succeed_ai_job`, `fail_ai_job`, `cancel_ai_job`, `mark_consume_pending`, `mark_release_pending`.
- `AIJobAsyncOrchestrationService` exposes settlement methods: `consume_ai_job_credits`, `release_ai_job_credits`.
- `ai_job_routes.py` already gates consume and release endpoints with `_ensure_internal_caller(tenant)` requiring `auth_method == "internal_api_key"`.
- `ai_job_routes.py` already gates credit override fields with `_ensure_credit_override_allowed(...)`.
- `ai_job_routes.py` already rejects `organization_id` query override via `_reject_forged_organization_query(request)`.
- Route handlers derive `organization_id` from `TenantContext` and never accept it from client body, path, or query.
- `AIJobRepository` does not expose a global `get(job_id)` contract.
- `AIJobWorkerMockService` success flow: `get -> enqueue -> start -> succeed -> mark_consume_pending -> consume`.
- `AIJobWorkerMockService` failure flow: `get -> enqueue -> start -> fail -> mark_release_pending -> release`.
- `AIJobWorkerMockService` cancel flow: `get -> cancel -> mark_release_pending -> release` (only for jobs already in `cancel_requested` status).
- `AIJobWorkerMockService` cancel mode validates `status == "cancel_requested"` before proceeding.
- `AIJobWorkerMockService` resolve_credits uses explicit credits if provided, otherwise falls back to `reserved_credits` from the loaded job.
- `AIJobWorkerMockService` validates `simulated_duration_ms` between 0 and 60000 inclusive.
- `AIJobWorkerMockService` validates metadata is JSON-safe.
- `AIJobWorkerMockService` validates all required text fields are non-empty strings.
- Current route prefix is `/api/v1/ai-jobs`.
- Existing internal-only consume and release endpoints live at `/api/v1/ai-jobs/{job_id}/consume` and `/api/v1/ai-jobs/{job_id}/release`.
- Dependency wiring for `AIJobAsyncOrchestrationService` lives in `src/dependencies/ai_job_orchestration.py`.

## 3. Scope

In scope for this contract:

- the concept of an internal/admin/S2S trigger for the mock worker;
- access policy definition for who may trigger mock execution;
- the separation of the mock trigger from public AI Jobs endpoints;
- a proposed future endpoint path and method;
- a proposed future command/request schema derived from `AIJobWorkerMockCommand`;
- the expected internal flow from trigger to worker mock to settlement;
- tenant-safety, locking, and session ownership rules;
- observability and audit logging requirements;
- future test requirements;
- roadmap for implementation.

Out of implementation scope for this contract phase:

- actual endpoint implementation;
- actual route registration;
- actual schema or Pydantic model creation;
- actual dependency or DI wiring changes;
- actual worker execution logic (already implemented in `AIJobWorkerMockService`);
- real worker process;
- real async queue;
- real provider adapter;
- frontend integration or UI changes;
- Alembic migrations;
- model changes;
- database schema changes;
- Stripe or payment integration;
- ComfyUI runtime or GPU consumption;
- runtime configuration changes.

## 4. Non-Scope

The mock worker trigger must not:

- be exposed through the public frontend;
- be callable by normal JWT-authenticated users;
- be callable by normal organization members;
- be callable by normal project roles;
- allow arbitrary tenant impersonation from public callers;
- allow arbitrary credit amount manipulation from public callers;
- create real provider connections;
- consume GPU capacity;
- process real images or create real assets;
- call ComfyUI runtime;
- call OpenAI, Anthropic, Ollama, or any other AI provider;
- integrate Stripe, checkout, billing purchase flows, or payment flows;
- create or modify Alembic migrations;
- create or modify database models;
- mutate runtime configuration;
- act as a substitute for a real worker trigger contract.

## 5. Access Policy

### 5.1 Allowed Callers

The future mock worker trigger must be restricted to internal or explicitly authorized callers only.

Permitted callers:

- internal API key / S2S callers using `auth_method == "internal_api_key"`;
- global technical admin if the existing authorization model supports it;
- explicitly authorized internal admin if a future policy defines that role.

The trigger must reuse or extend the existing internal caller policy. It must not create a bypass or a parallel authorization path.

### 5.2 Prohibited Callers

The future mock worker trigger must reject:

- the public frontend application;
- normal JWT-authenticated users;
- normal organization members;
- normal project roles;
- any caller whose `auth_method` is not explicitly authorized for internal trigger use;
- any caller that attempts to supply `organization_id` from a public query, body, or header.

### 5.3 Authorization Enforcement Point

Authorization must be enforced at the route or use-case layer before the worker mock service is invoked.

Required enforcement:

- the trigger endpoint or use-case must verify internal/admin/S2S caller identity before constructing `AIJobWorkerMockCommand`;
- if the caller is not authorized, the request must be rejected with a clear, non-leaking error;
- authorization must not be deferred to the worker mock service or orchestration service;
- authorization must not be bypassed by query parameters, headers, or path tricks.

### 5.4 Separation from Public Endpoints

The mock worker trigger must live on a separate path from the public AI Jobs endpoints.

Recommended separation:

- public endpoints remain under `/api/v1/ai-jobs/...`;
- mock worker trigger must use a distinct prefix such as `/api/v1/internal/ai-jobs/...` or `/api/v1/admin/ai-jobs/...`;
- the mock trigger must not be listed in public API documentation or public OpenAPI tags;
- the mock trigger must not appear in frontend route declarations, navigation, or UI.

## 6. Proposed Future Endpoint

### 6.1 Method and Path

Proposed future endpoint (not implemented in this phase):

- `POST /api/v1/internal/ai-jobs/{job_id}/mock-worker/execute`

or alternatively:

- `POST /api/v1/admin/ai-jobs/{job_id}/mock-worker/execute`

The final prefix must follow the existing internal/admin endpoint convention if one exists. If no convention exists, the prefix must be documented and approved before implementation.

### 6.2 Path Parameters

| Parameter | Type | Source | Notes |
|---|---|---|---|
| `job_id` | `str` | path | tenant-scoped job identifier |

`job_id` must come from the URL path. It must not come from the request body or query parameters.

### 6.3 Request Body

Proposed future request body:

| Field | Type | Required | Notes |
|---|---|---|---|
| `mode` | `Literal["success", "failure", "cancel"]` | yes | execution mode |
| `execution_attempt_id` | `str` | yes | stable idempotency key for this execution attempt |
| `simulated_duration_ms` | `int \| None` | no | optional simulated delay, bounded 0-60000 |
| `mock_output_metadata` | `dict[str, Any] \| None` | no | optional mock output for success mode |
| `mock_error_code` | `str \| None` | no | optional error code for failure/cancel mode |
| `mock_error_message` | `str \| None` | no | optional safe error message for failure/cancel mode |
| `actual_credits` | `int \| None` | no | internal/admin only credit override for success settlement |
| `release_credits` | `int \| None` | no | internal/admin only credit override for failure/cancel settlement |

### 6.4 Fields Prohibited from Request Body

The following fields must never be accepted from the trigger request body:

- `organization_id` (derived from secure internal context, never from the client)
- `requested_by` (derived from the authenticated internal actor if possible)
- `reservation_entry_id` (read from the persisted tenant-scoped job)
- `consume_entry_id` (set by settlement flow)
- `release_entry_id` (set by settlement flow)
- `status` (determined by transition logic)
- lifecycle timestamps
- ledger entry ids
- arbitrary account or tenant identifiers

### 6.5 organization_id Resolution

`organization_id` must come from one of the following trusted sources, in order of preference:

1. the authenticated internal caller's tenant context (preferred);
2. a validated internal-use-only body field if the internal caller explicitly operates across tenants under a documented admin policy.

`organization_id` must never come from:

- public query parameters;
- public headers;
- public path segments;
- unvalidated body fields.

If `organization_id` is supplied in the body by an internal caller, the route must validate it against the caller's authorized scope before passing it to the worker command.

### 6.6 requested_by Derivation

`requested_by` should be derived from the authenticated internal actor identity if available.

If the internal caller provides an explicit `requested_by` value, it must be validated as a non-empty string and logged for audit purposes.

If the internal caller does not provide `requested_by`, a default such as `"internal_trigger"` or `"admin_trigger"` may be used.

### 6.7 Response Shape

The trigger endpoint must return a minimal internal result. It must not expose raw provider payloads, internal ledger internals, or sensitive metadata.

Proposed response minimum:

```json
{
  "job_id": "string",
  "organization_id": "string",
  "mode": "success | failure | cancel",
  "status": "string",
  "consumed_credits": 0,
  "released_credits": 0,
  "consume_entry_id": "string | null",
  "release_entry_id": "string | null"
}
```

The response may be extended for internal diagnostics but must never include secrets, tokens, credentials, raw provider payloads, or private runtime artifacts.

## 7. Proposed Future Command Construction

### 7.1 Command Derivation

The trigger route or use-case must construct `AIJobWorkerMockCommand` from validated inputs and trusted context.

Recommended construction:

```python
command = AIJobWorkerMockCommand(
    organization_id=tenant.organization_id,
    job_id=job_id,
    requested_by=resolved_requested_by,
    execution_attempt_id=payload.execution_attempt_id,
    mode=payload.mode,
    simulated_duration_ms=payload.simulated_duration_ms,
    mock_output_metadata=payload.mock_output_metadata,
    mock_error_code=payload.mock_error_code,
    mock_error_message=payload.mock_error_message,
    actual_credits=payload.actual_credits,
    release_credits=payload.release_credits,
)
```

### 7.2 Credit Override Policy

`actual_credits` and `release_credits` are sensitive settlement fields.

Rules:

- these fields must never be accepted from public frontend callers;
- these fields may be accepted only from internal API key / S2S callers or explicitly authorized admin callers;
- the trigger route must apply the same `_ensure_credit_override_allowed(...)` policy or an equivalent validation before passing these values to the worker command;
- if the caller is not authorized to override credits, the trigger must reject the request or ignore the override and fall back to `reserved_credits` from the persisted job;
- the worker mock service already implements this fallback behavior via `_resolve_credits(...)`.

### 7.3 Execution Attempt Idempotency

`execution_attempt_id` is the primary idempotency key for the worker mock execution.

Rules:

- `execution_attempt_id` must be a non-empty string;
- retrying the same trigger with the same `execution_attempt_id` must not duplicate consume or release settlement;
- retrying the same trigger with the same `execution_attempt_id` and a different payload must produce a conflict or be safely rejected;
- the same `execution_attempt_id` must not be reused for a different tenant or job.

## 8. Internal Flow

### 8.1 Trigger-to-Worker Flow

The expected future internal flow:

1. internal/admin/S2S caller authenticates with internal API key or equivalent policy;
2. trigger route or use-case validates authorization;
3. trigger route or use-case resolves `organization_id` from trusted context;
4. trigger route or use-case extracts `job_id` from the URL path;
5. trigger route or use-case validates the request body schema;
6. trigger route or use-case applies credit override policy if `actual_credits` or `release_credits` are present;
7. trigger route or use-case constructs `AIJobWorkerMockCommand`;
8. trigger route or use-case obtains or receives `AsyncSession` from the dependency or use-case layer;
9. trigger route or use-case instantiates or injects `AIJobWorkerMockService` with `AIJobAsyncOrchestrationService`;
10. trigger route or use-case calls `worker.execute(session, command)`;
11. worker mock service executes the validated flow (success, failure, or cancel);
12. worker mock service returns `AIJobWorkerMockResult`;
13. trigger route or use-case commits the transaction outside the worker service if the pattern requires it;
14. trigger route or use-case maps `AIJobWorkerMockResult` to the internal response shape;
15. trigger route or use-case returns the minimal internal result.

### 8.2 Session and Transaction Ownership

The trigger endpoint or use-case must own the `AsyncSession` and the transaction boundary.

Rules:

- `AsyncSession` must be received from the dependency injection layer or the outer use-case;
- the worker mock service must not create its own session;
- the worker mock service must not call `commit()`;
- commit must happen outside the worker mock service, in the route handler, use-case, task runner, or test harness;
- rollback must happen if any step in the flow fails;
- the same `AsyncSession` must be shared across orchestration, repository, gateway, and settlement boundaries for one business operation.

### 8.3 Commit Location

Recommended commit location:

- the route handler or use-case layer that invokes `worker.execute(session, command)` owns the transaction commit;
- if the trigger is implemented as a background task or cron, the task runner owns the commit;
- in tests, the test harness owns the commit or uses a rollback-based assertion pattern.

### 8.4 Error Handling

The trigger must map worker mock errors and orchestration errors to clear, non-leaking HTTP responses.

Expected mappings:

- `AIJobWorkerMockError` / `AIJobWorkerMockInvalidModeError` -> `400 Bad Request`
- `AIJobWorkerMockSettlementError` -> `400 Bad Request` or `409 Conflict` depending on cause
- `AIJobAsyncNotFoundError` -> `404 Not Found` (tenant-scoped, no cross-tenant leak)
- `AIJobAsyncInvalidStateError` -> `409 Conflict`
- `AIJobAsyncAccountingError` -> `400 Bad Request` or `409 Conflict`
- `AIJobAsyncOrchestrationError` -> `400 Bad Request` for caller errors, `500 Internal Server Error` for unexpected failures
- authorization failures -> `403 Forbidden`
- missing authentication -> `401 Unauthorized`

## 9. Tenant-Safety Rules

### 9.1 Mandatory Tenant Scoping

- `organization_id` is required for every worker mock command.
- `job_id` is never used without `organization_id`.
- No global `get(job_id)` is permitted.
- The trigger must not accept `organization_id` from public frontend input.
- The trigger must not mutate jobs across tenants.
- A job loaded for one `organization_id` must return not found or forbidden if a command references another tenant.

### 9.2 Cross-Tenant Protection

- Cross-tenant worker commands must result in a secure not-found or forbidden response.
- The trigger must not reveal whether a job exists in another tenant.
- Tenant isolation must be enforced at the repository boundary through `organization_id` in all queries.

### 9.3 No Tenant Impersonation

- Normal users must not be able to impersonate another tenant.
- Normal users must not be able to supply `organization_id` to execute jobs in another tenant's scope.
- Internal callers that operate across tenants must be explicitly authorized and audited.

## 10. Accounting Rules

### 10.1 Settlement Delegation

- The trigger must not call `CreditLedgerService` directly.
- The trigger must not call `CreditGateService` directly.
- The trigger must not call `AIJobCostingService` directly.
- The trigger must use `AIJobWorkerMockService` which composes `AIJobAsyncOrchestrationService`.
- `AIJobAsyncOrchestrationService` delegates settlement to `AIJobAccountingGateway`.

### 10.2 Settlement Flow

- Success path: `consume_ai_job_credits(session, AIJobAsyncConsumeRequest(...))`.
- Failure path: `release_ai_job_credits(session, AIJobAsyncReleaseRequest(...))`.
- Cancel path: `release_ai_job_credits(session, AIJobAsyncReleaseRequest(...))`.
- `caller_key` must equal `execution_attempt_id` or a deterministic derived key.
- `reservation_entry_id` must come from the persisted tenant-scoped job, never from the request.

### 10.3 Double Settlement Prevention

- Double consume must be blocked.
- Double release must be blocked.
- Consume after full release must fail.
- Release after full consume must fail unless a future partial-settlement policy explicitly permits releasing surplus.

### 10.4 Credit Override Restrictions

- `actual_credits` and `release_credits` overrides must never come from public frontend callers.
- If provided by an authorized internal caller, they must be validated as positive integers.
- If not provided, the worker mock service must fall back to `reserved_credits` from the persisted job.
- The trigger route must not bypass the credit override policy.

## 11. Observability

### 11.1 Audit Logging

Every trigger invocation must be auditable with at minimum:

- `organization_id`
- `job_id`
- `mode`
- `execution_attempt_id`
- `requested_by`
- outcome (success or failure)
- timestamp

### 11.2 Log Safety

- Do not log secrets, tokens, API keys, credentials, raw provider payloads, private prompt payloads, private uploads, or sensitive runtime artifacts.
- Log only JSON-safe, size-limited metadata.
- Error messages in logs must be safe for internal diagnostics without exposing internal stack traces to clients.

### 11.3 Status and History Visibility

After a trigger invocation:

- `GET /api/v1/ai-jobs/{job_id}` must reflect the latest canonical status.
- `GET /api/v1/ai-jobs/{job_id}/history` must reflect mock execution timestamps where available.
- Mock metadata must be namespaced and must not overwrite accounting fields.

## 12. Future Test Requirements

### 12.1 Authorization Tests

- trigger rejects normal JWT user.
- trigger rejects normal organization member.
- trigger rejects normal project role.
- trigger accepts internal API key caller.
- trigger accepts authorized admin caller if that policy is defined.
- trigger rejects unauthorized caller with `403`.

### 12.2 Tenant-Safety Tests

- `organization_id` cannot come from public query.
- `organization_id` cannot come from public body.
- cross-tenant job lookup returns not found or forbidden.
- trigger does not mutate jobs across tenants.

### 12.3 Command Validation Tests

- `mode` is required and must be `success`, `failure`, or `cancel`.
- `execution_attempt_id` is required and must be a non-empty string.
- `simulated_duration_ms` must be within bounds if provided.
- `mock_output_metadata` must be JSON-safe if provided.
- `mock_error_code` and `mock_error_message` must be safe strings if provided.
- invalid mode is rejected.
- missing `execution_attempt_id` is rejected.

### 12.4 Worker Mock Flow Tests

- success mode calls worker mock and consumes reserved credits.
- failure mode calls worker mock and releases reserved credits.
- cancel mode calls worker mock and releases reserved credits for `cancel_requested` jobs.
- cancel mode rejects jobs not in `cancel_requested` status.
- worker mock service is invoked with the correct `AIJobWorkerMockCommand`.
- worker mock result is returned to the caller.
- transaction commits after successful worker mock execution.
- transaction rolls back on worker mock failure.

### 12.5 Accounting Tests

- `actual_credits` override is accepted only from authorized internal callers.
- `release_credits` override is accepted only from authorized internal callers.
- credit override from normal user is rejected.
- credit override from public frontend is rejected.
- default credit resolution uses `reserved_credits` from the persisted job.
- `caller_key == execution_attempt_id` in consume and release.
- no double consume.
- no double release.
- no `CreditLedgerService` direct call.
- no `CreditGateService` direct call.

### 12.6 Isolation Tests

- no frontend files are touched.
- no ComfyUI imports exist.
- no real provider imports exist.
- no `AsyncSessionLocal` usage.
- no internal `commit()` in worker mock service.
- no `CreditLedgerService` / `CreditGateService` / `AIJobCostingService` direct calls from trigger or worker.

## 13. Roadmap

### 13.1 Immediate (After This Contract)

1. Implement the internal trigger endpoint as a new route module or an extension of the existing internal route surface.
2. Add Pydantic request/response schemas for the trigger.
3. Add dependency wiring for `AIJobWorkerMockService` injection.
4. Register the trigger route in the application factory.
5. Add unit tests for authorization, tenant-safety, command validation, flow, and accounting.

### 13.2 Short-Term

6. Add smoke tests for the full mock worker trigger flow.
7. Add an optional manual trigger command or script for operational testing if useful.
8. Harden idempotency by persisting execution attempt replay state beyond the current `caller_key` passthrough.

### 13.3 Medium-Term

9. Implement real worker process.
10. Implement real async queue.
11. Implement real provider adapters (ComfyUI, OpenAI, Anthropic, Ollama, etc.).
12. Connect frontend read-only surfaces for job status and history.

### 13.4 Long-Term

13. Frontend integration for public create/estimate/check/reserve/read/list/history flows.
14. Real credit consumption through verified provider execution.
15. Stripe integration for purchasable credits.

## 14. Acceptance Criteria for Future Implementation

The future mock worker trigger implementation is acceptable only when:

- the trigger is internal/admin/S2S only and is not exposed in the public frontend;
- normal JWT users cannot trigger mock execution;
- normal organization members cannot trigger mock execution;
- `organization_id` is derived from trusted internal context, never from public input;
- `job_id` comes from the URL path;
- `mode`, `execution_attempt_id`, and other required fields are validated before worker invocation;
- credit override fields (`actual_credits`, `release_credits`) are accepted only from authorized internal callers;
- the trigger uses `AIJobWorkerMockService` which composes `AIJobAsyncOrchestrationService`;
- there are no direct calls to `CreditLedgerService`, `CreditGateService`, or `AIJobCostingService`;
- there is no `AsyncSessionLocal` usage in the trigger or worker mock service;
- there is no `commit()` inside the worker mock service;
- tenant isolation is enforced through `organization_id` in all queries;
- cross-tenant access returns not found or forbidden;
- double settlement is blocked;
- all required tests pass;
- no real provider, ComfyUI, GPU, payment, Alembic, model, or frontend changes are introduced by the trigger implementation phase unless explicitly scoped.
