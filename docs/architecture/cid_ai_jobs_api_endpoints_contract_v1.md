# CID AI Jobs API Endpoints Contract v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-09
Owners: CID Architecture / CID Product / CID Business
Scope: future HTTP API contract for tenant-safe CID AI job operations

Companion docs:
- `docs/architecture/cid_ai_job_repository_async_contract_v1.md`
- `docs/architecture/cid_ai_job_orchestration_service_contract_v1.md`
- `docs/architecture/cid_ai_job_accounting_gateway_async_contract_v1.md`
- `docs/architecture/cid_ai_job_reservation_linkage_contract_v1.md`
- `docs/architecture/cid_credit_ledger_idempotency_tenant_scope_contract_v1.md`
- `docs/architecture/cid_postgresql_only_policy_v1.md`

## 1. Purpose

This document defines the future API contract for CID AI jobs.

The contract is endpoint-level only. It does not implement routes, schemas, workers, frontend integration, migrations, or runtime behavior in this phase.

## 2. Audited Implementation Surface

Read-only audit performed before writing this contract:

- `src/services/ai_job_async_orchestration_service.py`
- `src/repositories/ai_job_repository.py`
- `src/services/ai_job_accounting_gateway.py`
- `src/routes/auth_routes.py`
- `src/dependencies/tenant_context.py`
- `src/models/billing.py`

Observed current service surface:

- `AIJobAsyncOrchestrationService.create_ai_job(session, request)`
- `AIJobAsyncOrchestrationService.estimate_ai_job(session, request)`
- `AIJobAsyncOrchestrationService.check_ai_job_credits(session, request)`
- `AIJobAsyncOrchestrationService.reserve_ai_job_credits(session, request)`
- `AIJobAsyncOrchestrationService.consume_ai_job_credits(session, request)`
- `AIJobAsyncOrchestrationService.release_ai_job_credits(session, request)`
- `AIJobAsyncOrchestrationService.estimate_credit_cost(...)`
- `AIJobAsyncOrchestrationService.check_credit_availability(...)`

Observed current repository surface:

- `AIJobRepository.create(job)`
- `AIJobRepository.get(organization_id, job_id)`
- `AIJobRepository.get_for_update(organization_id, job_id)`
- `AIJobRepository.save(job)`
- `AIJobRepository.find_by_idempotency_key(organization_id, idempotency_key)`

Required future service surface not yet observed:

- tenant-scoped read method for `GET /api/v1/ai-jobs/{job_id}` exposed through orchestration, not directly through repository from the endpoint
- tenant-scoped list method for `GET /api/v1/ai-jobs` exposed through orchestration
- tenant-scoped history method for `GET /api/v1/ai-jobs/{job_id}/history` exposed through orchestration

## 3. Global API Rules

- Endpoints must use `TenantContext` from `Depends(get_tenant_context)`.
- Endpoints must use `AsyncSession` from `Depends(get_db)`.
- Endpoints must call `AIJobAsyncOrchestrationService` as the only business boundary.
- Endpoints must not call `AIJobRepository` directly except through orchestration construction/wiring.
- Endpoints must not call `CreditLedgerService`, `CreditGateService`, or `AIJobCostingService` directly.
- `organization_id` never comes from the client body, path, query, or headers. It always comes from `TenantContext.organization_id`.
- `job_id` is always resolved tenant-scoped.
- There is no API or repository usage equivalent to `get(job_id)` without `organization_id`.
- PostgreSQL is the only contractual backend. Locking semantics require `SELECT ... FOR UPDATE` / `stmt.with_for_update()` through the repository mutation path.
- Frontend clients never calculate credits and never submit arbitrary ledger amounts. Any credit override fields documented below are internal/admin/service inputs until explicitly enabled by a future policy.
- Public frontend flows may create, estimate, check credits, reserve, read, list, and view history if authorized.
- Consume and release endpoints are internal/S2S/worker-controlled. They are not ordinary frontend actions.

## 4. Shared Response Shape

Minimum job response fields:

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
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`
- `output_asset_ids`
- `attempt_number`
- lifecycle timestamps available on `AIJob`
- `metadata`

Minimum mutation response fields:

- `job`
- `message`
- `transition` when a transition was applied
- `accounting` when an accounting boundary was invoked

The API may redact internal ledger details from public responses while preserving ids needed for traceability.

## 5. Error Mapping

Expected HTTP mapping:

- `400 Bad Request`: malformed payload, forbidden body fields, invalid idempotency payload, invalid operation request
- `401 Unauthorized`: missing/invalid authentication
- `402 Payment Required`: insufficient credits when the operation requires available credits
- `403 Forbidden`: tenant/account not authorized, missing write permission, insufficient plan permission, or non-internal caller attempting consume/release
- `404 Not Found`: tenant-scoped job lookup returns no row
- `409 Conflict`: idempotency conflict or invalid lifecycle transition
- `422 Unprocessable Entity`: schema validation failure
- `500 Internal Server Error`: unexpected orchestration/accounting failure without leaking internals

Implementation should map current service exceptions:

- `AIJobAsyncNotFoundError` -> `404`
- `AIJobAsyncInvalidStateError` -> `409`
- `AIJobAsyncIdempotencyConflictError` -> `409`
- `AIJobAsyncAccountingError` -> `400` or `409` depending on cause
- `AIJobAsyncOrchestrationError` -> `400` for caller errors, otherwise `500`

## 6. Endpoints

### 6.1 Create AI Job

Method/path: `POST /api/v1/ai-jobs`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`
- write permission may be required by future route policy

Body permitted:

- `operation_type`
- `project_id`
- `idempotency_key`
- `metadata`
- `provider_type`
- `provider_name`
- `workflow_id`
- `workflow_version`
- `workflow_hash`
- `model_name`
- `input_asset_ids`
- `output_asset_ids`

Fields prohibited:

- `organization_id`
- `status`
- `estimated_credits`
- `reserved_credits`
- `consumed_credits`
- `released_credits`
- ledger entry ids
- lifecycle timestamps
- arbitrary `user_id` unless a future admin-only policy allows it

Response minimum:

- `job`
- `message`

Errors:

- `400` malformed payload or forbidden field
- `401` unauthenticated
- `403` unauthorized tenant/account
- `409` conflicting idempotency key
- `422` schema validation failure

Idempotency:

- Supports client-provided `idempotency_key` scoped by `tenant.organization_id`.
- Replay with same canonical create payload returns the existing job.
- Replay with different payload returns `409`.

Service called:

- Existing: `AIJobAsyncOrchestrationService.create_ai_job(session, AIJobAsyncCreateRequest(...))`
- Endpoint constructs `AIJobAsyncCreateRequest.organization_id` from `tenant.organization_id` only.

### 6.2 Estimate AI Job

Method/path: `POST /api/v1/ai-jobs/{job_id}/estimate`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`

Body permitted:

- empty body for normal frontend use
- `estimated_credits` only for internal/admin testing policy if explicitly enabled later

Fields prohibited:

- `organization_id`
- `job_id` in body
- arbitrary ledger amount fields
- `reserved_credits`, `consumed_credits`, `released_credits`
- ledger entry ids

Response minimum:

- `job`
- `message`
- `transition`
- `accounting.estimated_credits`

Errors:

- `400` invalid estimate request
- `401` unauthenticated
- `403` unauthorized tenant/account
- `404` job not found in tenant
- `409` invalid state transition
- `422` schema validation failure

Idempotency:

- Not a ledger-mutating operation.
- Repeating the request should be safe if service state transition permits it; invalid repeat transitions return `409`.

Service called:

- Existing: `AIJobAsyncOrchestrationService.estimate_ai_job(session, AIJobAsyncEstimateRequest(...))`
- Endpoint passes `organization_id=tenant.organization_id` and path `job_id`.

### 6.3 Check AI Job Credits

Method/path: `POST /api/v1/ai-jobs/{job_id}/check-credits`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`

Body permitted:

- empty body for normal frontend use
- `estimated_credits` only for internal/admin testing policy if explicitly enabled later

Fields prohibited:

- `organization_id`
- `job_id` in body
- arbitrary `amount`
- ledger entry ids
- credit balance mutation fields

Response minimum:

- `job`
- `message`
- `transition`
- `accounting.available`
- `accounting.required_credits`

Errors:

- `400` invalid credit check request
- `401` unauthenticated
- `402` insufficient credits when the operation requires available credits
- `403` unauthorized tenant/account or insufficient plan permission
- `404` job not found in tenant
- `409` invalid state transition
- `422` schema validation failure

Idempotency:

- Not a ledger-mutating operation.
- Repeating the request should not create ledger entries.

Service called:

- Existing: `AIJobAsyncOrchestrationService.check_ai_job_credits(session, AIJobAsyncCreditCheckRequest(...))`
- Endpoint does not call `CreditGateService` directly.

### 6.4 Reserve AI Job Credits

Method/path: `POST /api/v1/ai-jobs/{job_id}/reserve`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`
- write permission required

Body permitted:

- `caller_key` optional for caller-level idempotency
- `estimated_credits` only for internal/admin testing policy if explicitly enabled later

Fields prohibited:

- `organization_id`
- `job_id` in body
- arbitrary `amount`
- `reservation_entry_id`
- `consume_entry_id`
- `release_entry_id`
- balance mutation fields

Response minimum:

- `job`
- `message`
- `transition`
- `accounting.ledger_entry_id`

Errors:

- `400` invalid reserve request
- `401` unauthenticated
- `402` insufficient credits
- `403` unauthorized tenant/account
- `404` job not found in tenant
- `409` invalid state transition or idempotency conflict
- `422` schema validation failure

Idempotency:

- Ledger idempotency key is built below the endpoint boundary by accounting gateway/service logic.
- Endpoint may pass `caller_key` but must not build ledger keys itself.
- Current gateway key shape observed: `ai_job:{organization_id}:{job_id}:reserve[:caller_key]`.

Service called:

- Existing: `AIJobAsyncOrchestrationService.reserve_ai_job_credits(session, AIJobAsyncReserveRequest(...))`
- Endpoint does not call `CreditLedgerService`, `CreditGateService`, or `AIJobCostingService` directly.

### 6.5 Consume AI Job Credits

Method/path: `POST /api/v1/ai-jobs/{job_id}/consume`

Auth/tenant context:

- Internal/S2S/worker-controlled only.
- Must use authenticated internal API key, worker credential, or equivalent future S2S policy.
- `tenant: TenantContext = Depends(get_tenant_context)` still provides `organization_id`.
- `db: AsyncSession = Depends(get_db)`.

Body permitted:

- `caller_key` optional for caller-level idempotency
- `actual_credits` only from trusted provider/worker accounting path, not ordinary frontend

Fields prohibited:

- `organization_id`
- `job_id` in body
- arbitrary frontend `amount`
- `reservation_entry_id` from client; it is read from the tenant-scoped job
- ledger entry ids

Response minimum:

- `job`
- `message`
- `transition`
- `accounting.ledger_entry_id`

Errors:

- `400` invalid consume request or missing reservation linkage
- `401` unauthenticated
- `403` caller is not internal/S2S/worker-controlled
- `404` job not found in tenant
- `409` invalid state transition or duplicate/conflicting idempotency
- `422` schema validation failure

Idempotency:

- Endpoint may pass `caller_key`.
- Current gateway key shape observed: `ai_job:{organization_id}:{job_id}:consume[:caller_key]`.
- Consume must use the job's existing `reservation_entry_id`; clients do not provide it.

Service called:

- Existing: `AIJobAsyncOrchestrationService.consume_ai_job_credits(session, AIJobAsyncConsumeRequest(...))`
- Endpoint does not call credit services directly.

### 6.6 Release AI Job Credits

Method/path: `POST /api/v1/ai-jobs/{job_id}/release`

Auth/tenant context:

- Internal/S2S/worker-controlled only.
- Must use authenticated internal API key, worker credential, or equivalent future S2S policy.
- `tenant: TenantContext = Depends(get_tenant_context)` still provides `organization_id`.
- `db: AsyncSession = Depends(get_db)`.

Body permitted:

- `caller_key` optional for caller-level idempotency
- `release_credits` only from trusted cancellation/failure/settlement path, not ordinary frontend

Fields prohibited:

- `organization_id`
- `job_id` in body
- arbitrary frontend `amount`
- `reservation_entry_id` from client; it is read from the tenant-scoped job
- ledger entry ids

Response minimum:

- `job`
- `message`
- `transition`
- `accounting.ledger_entry_id`

Errors:

- `400` invalid release request or missing reservation linkage
- `401` unauthenticated
- `403` caller is not internal/S2S/worker-controlled
- `404` job not found in tenant
- `409` invalid state transition or duplicate/conflicting idempotency
- `422` schema validation failure

Idempotency:

- Endpoint may pass `caller_key`.
- Current gateway key shape observed: `ai_job:{organization_id}:{job_id}:release[:caller_key]`.
- Release must use the job's existing `reservation_entry_id`; clients do not provide it.

Service called:

- Existing: `AIJobAsyncOrchestrationService.release_ai_job_credits(session, AIJobAsyncReleaseRequest(...))`
- Endpoint does not call credit services directly.

### 6.7 Get AI Job

Method/path: `GET /api/v1/ai-jobs/{job_id}`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`

Body permitted:

- none

Fields prohibited:

- request body
- `organization_id` query override

Response minimum:

- `job`

Errors:

- `401` unauthenticated
- `403` unauthorized tenant/account
- `404` job not found in tenant

Idempotency:

- Read-only operation; not applicable.

Service called or required future surface:

- Required future service surface: tenant-scoped `AIJobAsyncOrchestrationService` read method.
- Endpoint must not directly call `AIJobRepository.get(...)` unless this is only construction/wiring inside the orchestration boundary.

### 6.8 List AI Jobs

Method/path: `GET /api/v1/ai-jobs`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`

Query/body permitted:

- query filters: `status`, `project_id`, `operation_type`, `created_after`, `created_before`, `limit`, `cursor`
- no request body

Fields prohibited:

- `organization_id` query override
- direct user/tenant impersonation filters unless a future admin policy defines them

Response minimum:

- `items`
- `next_cursor`

Errors:

- `400` invalid filters
- `401` unauthenticated
- `403` unauthorized tenant/account
- `422` schema validation failure

Idempotency:

- Read-only operation; not applicable.

Service called or required future surface:

- Required future service surface: tenant-scoped `AIJobAsyncOrchestrationService` list method.
- Listing must filter by `tenant.organization_id` in the persistence query.

### 6.9 Get AI Job History

Method/path: `GET /api/v1/ai-jobs/{job_id}/history`

Auth/tenant context:

- `tenant: TenantContext = Depends(get_tenant_context)`
- `db: AsyncSession = Depends(get_db)`

Body permitted:

- none

Fields prohibited:

- request body
- `organization_id` query override

Response minimum:

- `job_id`
- `events`
- each event: `status`, `timestamp`, `actor_type`, `message`, relevant ledger/job ids when safe

Errors:

- `401` unauthenticated
- `403` unauthorized tenant/account
- `404` job not found in tenant

Idempotency:

- Read-only operation; not applicable.

Service called or required future surface:

- Required future service surface: tenant-scoped `AIJobAsyncOrchestrationService` history method.
- History retrieval must first resolve the job tenant-scoped.

## 7. Service Wiring Contract

Future route construction should wire dependencies in this shape:

```python
async def endpoint(
    ...,
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    request = AIJobAsync...Request(
        organization_id=tenant.organization_id,
        ...
    )
    result = await orchestration_service.method(db, request)
```

The endpoint must not pass an `organization_id` supplied by the client.

The endpoint must not compute credits. Credit calculations and ledger mutations remain below `AIJobAsyncOrchestrationService` through `AIJobAccountingGateway`.

## 8. Known Gap: Ledger Idempotency Scope

Current gap retained intentionally:

- `CreditLedgerEntry` still has `UniqueConstraint("idempotency_key")` globally.
- Tenant-scoped ledger idempotency using `organization_id + idempotency_key` requires a future model and Alembic phase.
- Endpoint implementation must not pretend this is solved.
- Until that future phase lands, endpoint idempotency should remain conservative and route implementations should preserve the gateway's organization-prefixed idempotency key shape.

Future phase:

- update model constraint
- add Alembic migration
- update ledger service lookup to include `organization_id`
- add tests for cross-tenant idempotency keys

## 9. Security Requirements

- Return `404` instead of cross-tenant visibility for unknown tenant-scoped jobs.
- Do not leak internal ledger/accounting stack traces.
- Do not expose unrestricted metadata writes to fields that affect accounting or routing.
- Require internal/S2S/worker auth for consume/release.
- Use PostgreSQL row locking for mutation paths via repository `get_for_update`.
- Use one `AsyncSession` through endpoint, orchestration, repository, and accounting gateway for transactional consistency.

## 10. Roadmap After This Contract

Recommended order:

1. `CID.SAAS.AI.JOBS.API.ENDPOINTS.IMPLEMENTATION.1`: implement endpoints and schemas against current/future service surface.
2. `CID.SAAS.AI.JOBS.WORKER.MOCK.1`: add mock worker path for internal consume/release without real providers.
3. `CID.SAAS.AI.JOBS.WORKER.REAL.1`: connect real worker/provider execution after mock contract is validated.
4. `CID.SAAS.AI.JOBS.FRONTEND.CONNECTED.1`: connect frontend to create/estimate/check/reserve/read/list/history only.
5. `CID.SAAS.STRIPE.CREDITS.PURCHASABLE.1`: add Stripe-backed purchasable credits after accounting and job flows are stable.

## 11. Non-Goals

- No route implementation in this phase.
- No worker implementation in this phase.
- No frontend changes in this phase.
- No Alembic/model changes in this phase.
- No Stripe or purchasable credit implementation in this phase.
- No direct ComfyUI runtime calls in this phase.
