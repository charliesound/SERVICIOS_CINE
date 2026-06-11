# CID AI Job Cancellation API Contract v1

## Status

- Based on HEAD `b758879` (`feat: add CID AI job cancellation service phase 1`).
- Pre-route implementation document. This contract does not implement an endpoint.
- PostgreSQL-only. Do not introduce alternate database behavior.
- Service layer already exists: `AIJobAsyncOrchestrationService.request_cancel_ai_job()` with `AIJobAsyncCancelRequest`.
- Base lifecycle contract: `docs/architecture/cid_ai_job_cancellation_contract_v1.md`.

## Objective

Define how AI Job cancellation should be exposed through the API in a later phase without breaking tenant boundaries, permissions, request validation, or credit lifecycle guarantees.

The route must be a thin FastAPI adapter over `request_cancel_ai_job()`. It must not execute workers, create execution attempts, release credits, or implement queue cancellation.

## Real Patterns Found

### AI Job Routes

- Public AI Job routes live in `src/routes/ai_job_routes.py` with router prefix `/api/v1/ai-jobs`.
- The route module uses `get_db`, `get_tenant_context`, `require_write_permission`, and `get_ai_job_orchestration_service`.
- The route module maps orchestration exceptions through `_raise_http_from_error()`.
- Existing mutation response shape is `AIJobMutationResponse` from `src/schemas/ai_job_api_schema.py`.
- Existing action schemas use Pydantic `ConfigDict(extra="forbid")`.
- Existing route tests in `tests/unit/test_ai_job_routes.py` verify tenant-derived `organization_id`, path-derived `job_id`, body/query rejection for forged fields, and dependency-level permission behavior.

### Internal Worker Routes

- Internal mock worker routes live in `src/routes/internal_ai_job_worker_mock_routes.py` with prefix `/api/v1/internal/ai-jobs` and `include_in_schema=False`.
- Internal execution requires `auth_method == "internal_api_key"`.
- Internal route derives `requested_by` from `tenant.user_id` or falls back to `"internal_trigger"`.
- Internal route rejects `organization_id` in query and schema rejects forged body fields.
- Internal mock execution is not the target for this API contract; it remains a later worker/Phase 2 concern.

### Tenant And Project Access

- `get_tenant_context()` in `src/dependencies/tenant_context.py` builds `TenantContext` from token data and optional internal API key.
- `tenant.organization_id` is the only trusted source for `organization_id`.
- `require_write_permission()` delegates to `can_write_project()` in `src/services/tenant_access_service.py`.
- Write roles currently accepted by `can_write_project()` are global admin, admin, role `admin`, `owner`, `producer`, or `operator`.
- `validate_project_access()` checks `Project.id == project_id` and `Project.organization_id == tenant.organization_id`, returning 404 when not found.
- Project-scoped route modules such as `storyboard_routes.py` include `validate_project_access` on project-scoped endpoints and `require_write_permission` on mutating endpoints.

## Proposed Route

Use the existing public AI Job namespace:

```http
POST /api/v1/ai-jobs/{job_id}/cancel
```

Rationale:

- Existing public AI Job lifecycle actions already use `/api/v1/ai-jobs/{job_id}/<action>`.
- Cancellation is a user/system lifecycle intent, not a mock-worker execution command.
- The route should use the current `AIJobMutationResponse` pattern unless a later implementation explicitly introduces a narrower cancellation response schema.

Do not implement an internal worker cancel route in this phase. Worker settlement and credit release remain separate concerns.

## Authentication And Authorization

### Authentication

The route must depend on `get_tenant_context` through `require_write_permission`:

```python
tenant: TenantContext = Depends(require_write_permission)
```

This preserves the existing AI Job `reserve` pattern and mutating storyboard route pattern.

### Organization Boundary

- The route must pass `tenant.organization_id` into `AIJobAsyncCancelRequest.organization_id`.
- The route must never accept `organization_id` from request body, query, path, or headers.
- If a caller attempts `?organization_id=...`, reject with 422 using the same `_reject_forged_organization_query()` pattern used by AI Job list and internal mock routes.
- If a job is not found under `tenant.organization_id`, return 404. This includes tenant mismatch and avoids leaking cross-tenant job existence.

### Project Access

AI Jobs currently expose `project_id` as optional job metadata and list filter, but existing AI Job get/mutate routes do not validate `project_id` with `validate_project_access`.

Recommended Phase 2 policy:

- If the cancel endpoint is only `/api/v1/ai-jobs/{job_id}/cancel`, tenant isolation through `organization_id + job_id` is required and sufficient for Phase 2.
- If a future route includes project scope, for example `/api/projects/{project_id}/ai-jobs/{job_id}/cancel`, it must also use `validate_project_access` and ensure the loaded job belongs to that `project_id`.
- Do not accept `project_id` in the cancel body as an ownership guard.

### Permission

Required permission: write-equivalent.

Use `require_write_permission`, which currently allows:

- Global admin.
- Admin.
- Role `admin`.
- Role `owner`.
- Role `producer`.
- Role `operator`.

Read-only roles must receive 403.

## Request Payload

Add a schema in a later implementation, preferably in `src/schemas/ai_job_api_schema.py`:

```python
class AIJobCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(default=None, min_length=1, max_length=500)
    metadata: dict[str, Any] | None = None
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=120)
```

Field policy:

- `reason`: optional user/system reason, copied to service request `reason`.
- `metadata`: optional JSON-safe object, copied to service request `metadata`.
- `idempotency_key`: optional future extension. Phase 2 may accept it for traceability, but Phase 1 service does not use it. If accepted before service support exists, document it as informational only.
- `requested_by`: do not accept from public clients. Derive from `tenant.user_id` or use an internal fallback only for internal callers.
- `organization_id`: forbidden.
- `job_id`: forbidden in body; path is authoritative.
- Credit fields such as `release_credits`: forbidden in this public cancel route.

Recommended `requested_by` derivation:

```python
requested_by = tenant.user_id or "internal_trigger"
```

For public JWT users, `tenant.user_id` should normally be present.

## Response Payload

Recommended Phase 2 response can reuse `AIJobMutationResponse` for consistency:

```json
{
  "job": {
    "id": "job-id",
    "organization_id": "tenant-org-id",
    "status": "cancelled | cancel_requested",
    "cancel_requested_at": "timestamp | null",
    "cancelled_at": "timestamp | null",
    "metadata": {}
  },
  "message": "cancelled | cancel requested | AI job already cancelled | AI job cancellation already requested",
  "transition": {
    "from_status": "created | estimated | credit_checked | reserved | queued | running",
    "to_status": "cancelled | cancel_requested",
    "requires_release": false,
    "accounting_action": "none"
  },
  "accounting": null
}
```

If a dedicated response schema is introduced later, it should contain:

- `job_id`
- `organization_id`
- `status`
- `cancel_requested`
- `idempotent`
- `release_required`
- `release_pending`
- `message`
- `metadata` when safe and useful

Suggested booleans:

- `cancel_requested`: true when final status is `cancel_requested`.
- `idempotent`: true when service returns an already-cancelled or already-requested message without saving a new transition.
- `release_required`: true when status is `cancel_requested` and the job has reserved credits/reservation linkage.
- `release_pending`: false in Phase 2 API route because release is not performed by `request_cancel_ai_job()`.

## Error Mapping

Use the existing AI Job route mapping style.

| Service / Route Condition | HTTP | Rationale |
|---|---:|---|
| `AIJobAsyncNotFoundError` | 404 | Includes tenant mismatch without leaking existence. |
| `AIJobAsyncInvalidStateError` | 409 | The request is valid, but lifecycle state does not permit cancellation. Existing AI Job routes map invalid state to 409. |
| `AIJobAsyncAccountingError` | 400 | Existing AI Job mapping; not expected for Phase 2 cancellation. |
| `AIJobAsyncOrchestrationError` | 400 | Existing AI Job mapping for malformed orchestration input. |
| Pydantic validation error | 422 | Invalid request body shape or forbidden extra fields. |
| Missing/invalid auth | 401/403 | Existing dependency behavior. |
| Permission denied | 403 | `require_write_permission` behavior. |
| Forged `organization_id` query | 422 | Existing AI Job route safety pattern. |
| Unexpected exception | 500 | Log server-side; do not leak internals. |

## Semantics By Job State

| Current status | API result | HTTP |
|---|---|---:|
| `created` | Transition to `cancelled` | 200 |
| `estimated` | Transition to `cancelled` | 200 |
| `credit_checked` | Transition to `cancelled` | 200 |
| `reserved` | Transition to `cancel_requested` | 200 or 202 |
| `queued` | Transition to `cancel_requested` | 200 or 202 |
| `running` | Transition to `cancel_requested` | 200 or 202 |
| `cancel_requested` | Idempotent response, no new save | 200 |
| `cancelled` | Idempotent response, no new save | 200 |
| `succeeded` | Not cancelable | 409 |
| `partial_succeeded` | Not cancelable | 409 |
| `failed` | Not cancelable | 409 |
| `consume_pending` | Not cancelable | 409 |
| `consumed` | Not cancelable | 409 |
| `release_pending` | Not cancelable | 409 |
| `released` | Not cancelable | 409 |
| `retry_pending` | Not cancelable | 409 |
| `expired` | Not cancelable | 409 |

Preferred status code:

- Use 200 for all successful service returns to match existing AI Job mutation endpoints.
- 202 is acceptable for `reserved/queued/running -> cancel_requested` only if Phase 2 explicitly adopts asynchronous semantics. If 202 is adopted, tests and client documentation must distinguish direct cancellation from cooperative cancellation request.

## Credits

Phase 2 API must not perform real credit release if it only calls `request_cancel_ai_job()`.

- `created/estimated/credit_checked -> cancelled`: no reservation, no credit action.
- `reserved/queued/running -> cancel_requested`: reserved credits remain reserved until a later worker/accounting phase settles the job.
- No automatic refund is promised for consumed credits.
- Do not expose `release_credits` in the public cancel request.
- Idempotent ledger release remains a future phase and must be covered by separate tests before it is exposed.

## Concurrency

- The route must delegate mutation and locking to `AIJobAsyncOrchestrationService.request_cancel_ai_job()`.
- The service uses repository `get_for_update()` through `_load_job_for_mutation()`, so the route must not perform a separate read-modify-write path.
- Concurrent cancel requests for the same job should converge to one transition plus idempotent responses.
- The route must not create `AIJobExecutionAttempt` rows.
- The route must not call `AIJobWorkerMockExecutionService` or `AIJobWorkerMockService`.
- The route must not execute a real queue or worker.
- Controlled errors should leave the session usable; do not catch errors in a way that masks a broken transaction.

## Observability

Recommended logging in Phase 2 implementation:

- Logger name should follow existing module pattern, for example `servicios_cine.routes.ai_job`.
- Log cancellation attempts at info level with `job_id`, `organization_id`, `user_id`, final status, and idempotent/replay flag when available.
- Log invalid-state cancellations at warning level with `job_id`, `organization_id`, current status, and actor.
- Log unexpected exceptions at exception level and return a generic 500.
- Do not log secrets, raw tokens, full request headers, full metadata payloads, or sensitive user content.
- Preserve request correlation if request-id middleware/context is present.

Recommended audit metadata passed to service:

```python
AIJobAsyncCancelRequest(
    organization_id=tenant.organization_id,
    job_id=job_id,
    metadata=payload.metadata,
    requested_by=tenant.user_id or "internal_trigger",
    reason=payload.reason,
)
```

## Tests Recommended For Phase 2 Route Implementation

- `POST /api/v1/ai-jobs/{job_id}/cancel` on `created` returns 200 and status `cancelled`.
- Repeated cancel returns 200 with idempotent result and does not call `save()` again in the fake service/repository model.
- Cancel on `reserved` returns status `cancel_requested` and does not call worker or create attempts.
- Cancel on `running` returns status `cancel_requested` and does not call worker or create attempts.
- Cancel on `succeeded` returns 409.
- Cancel on `partial_succeeded` returns 409.
- Cancel on `failed` returns 409.
- Tenant mismatch returns 404.
- Body with `organization_id`, `job_id`, `requested_by`, `release_credits`, or unknown fields returns 422.
- Query with `organization_id` returns 422.
- Read-only permission returns 403.
- Missing auth returns 401.
- Route delegates to `AIJobAsyncOrchestrationService.request_cancel_ai_job()` with `organization_id` from tenant and `job_id` from path.
- Route does not import repositories, accounting gateway, worker mock service, or execution attempt repository.
- Route maps `AIJobAsyncInvalidStateError` to 409.

## Phase 2 Implementation Checklist

- Add `AIJobCancelRequest` to `src/schemas/ai_job_api_schema.py` with `extra="forbid"`.
- Import `AIJobAsyncCancelRequest` in `src/routes/ai_job_routes.py`.
- Add `POST /{job_id}/cancel` under router prefix `/api/v1/ai-jobs`.
- Use `tenant: TenantContext = Depends(require_write_permission)`.
- Reject forged `organization_id` query via `_reject_forged_organization_query(request)`.
- Derive `requested_by` from `tenant.user_id` or internal fallback.
- Call only `service.request_cancel_ai_job(db, AIJobAsyncCancelRequest(...))`.
- Return `_result_response(result)` unless a dedicated response schema is intentionally introduced.
- Extend `tests/unit/test_ai_job_routes.py` with route-level tests.
- Do not touch worker mock route, worker services, models, Alembic, Docker, frontend, or credit ledger release behavior.

## Next Phase

`CID.SAAS.AI.JOB.CANCELLATION.API.ROUTE.PHASE2.IMPLEMENTATION.1`
