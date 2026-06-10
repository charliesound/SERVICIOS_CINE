from __future__ import annotations

import os
import sys
import importlib.util
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)
os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)

from database import get_db
from dependencies.ai_job_worker_mock import get_ai_job_worker_mock_execution_service
from dependencies.tenant_context import get_tenant_context
from schemas.auth_schema import TenantContext
from services.ai_job_worker_mock_execution_service import (
    AIJobWorkerMockExecutionConflictError,
    AIJobWorkerMockExecutionError,
    AIJobWorkerMockExecutionFingerprintMismatchError,
    AIJobWorkerMockExecutionInProgressError,
    AIJobWorkerMockExecutionInvalidStateError,
    AIJobWorkerMockExecutionReplayError,
    AIJobWorkerMockExecutionResult,
)
from services.ai_job_worker_mock_service import AIJobWorkerMockResult

ROUTE_MODULE_PATH = SRC_DIR / "routes" / "internal_ai_job_worker_mock_routes.py"
spec = importlib.util.spec_from_file_location(
    "internal_ai_job_worker_mock_routes_under_test",
    ROUTE_MODULE_PATH,
)
assert spec is not None and spec.loader is not None
routes_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routes_module)

router = routes_module.router


class FakeWorkerMockExecutionService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def _worker_result(self, **overrides: object) -> AIJobWorkerMockResult:
        defaults: dict[str, object] = {
            "organization_id": "org-tenant",
            "job_id": "job-1",
            "mode": "success",
            "status": "consumed",
            "consumed_credits": 5,
            "released_credits": None,
            "consume_entry_id": "entry-consume-1",
            "release_entry_id": None,
            "output_metadata": {"asset_id": "asset-1"},
            "error_metadata": None,
        }
        defaults.update(overrides)
        return AIJobWorkerMockResult(**defaults)  # type: ignore[arg-type]

    async def execute(self, session, command):
        del session
        self.calls.append(("execute", command))
        if command.mode == "success":
            result = self._worker_result(
                mode="success",
                status="consumed",
                consumed_credits=getattr(command, "actual_credits", None) or 5,
            )
            return AIJobWorkerMockExecutionResult(
                result=result,
                replay=False,
                attempt_status="succeeded",
                execution_attempt_id=command.execution_attempt_id,
            )
        if command.mode == "failure":
            result = self._worker_result(
                mode="failure",
                status="released",
                released_credits=getattr(command, "release_credits", None) or 5,
                consumed_credits=None,
                consume_entry_id=None,
                release_entry_id="entry-release-1",
                output_metadata=None,
                error_metadata={"code": getattr(command, "mock_error_code", None)},
            )
            return AIJobWorkerMockExecutionResult(
                result=result,
                replay=False,
                attempt_status="failed",
                execution_attempt_id=command.execution_attempt_id,
            )
        if command.mode == "cancel":
            result = self._worker_result(
                mode="cancel",
                status="released",
                released_credits=getattr(command, "release_credits", None) or 3,
                consumed_credits=None,
                consume_entry_id=None,
                release_entry_id="entry-release-1",
                output_metadata=None,
                error_metadata=None,
            )
            return AIJobWorkerMockExecutionResult(
                result=result,
                replay=False,
                attempt_status="cancelled",
                execution_attempt_id=command.execution_attempt_id,
            )
        raise ValueError("unexpected mode in fake")


class FakeDirectWorkerMockService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    async def execute(self, session, command):
        del session
        self.calls.append(("execute", command))
        raise AssertionError("route must not call direct worker service")


class FailingWorkerMockExecutionService:
    def __init__(self, error: Exception) -> None:
        self._error = error
        self.calls: list[tuple[str, object]] = []

    async def execute(self, session, command):
        del session
        self.calls.append(("execute", command))
        raise self._error


class ReplayWorkerMockExecutionService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    async def execute(self, session, command):
        del session
        self.calls.append(("execute", command))
        return AIJobWorkerMockExecutionResult(
            result=AIJobWorkerMockResult(
                organization_id=command.organization_id,
                job_id=command.job_id,
                mode=command.mode,
                status="consumed",
                consumed_credits=8,
                consume_entry_id="entry-replayed-consume",
                output_metadata=None,
            ),
            replay=True,
            attempt_status="succeeded",
            execution_attempt_id=command.execution_attempt_id,
        )


@pytest.fixture
def fake_execution_service() -> FakeWorkerMockExecutionService:
    return FakeWorkerMockExecutionService()


def _tenant(auth_method: str = "internal_api_key", user_id: str = "user-1") -> TenantContext:
    return TenantContext(
        user_id=user_id,
        organization_id="org-tenant",
        plan="pro",
        role="producer",
        is_admin=False,
        auth_method=auth_method,
    )


def _app(
    execution_service: object,
    tenant: TenantContext | None = None,
) -> FastAPI:
    application = FastAPI()
    application.include_router(router)

    async def override_db():
        yield object()

    async def override_tenant():
        return tenant or _tenant()

    async def override_execution_service():
        return execution_service

    application.dependency_overrides[get_db] = override_db
    application.dependency_overrides[get_tenant_context] = override_tenant
    application.dependency_overrides[
        get_ai_job_worker_mock_execution_service
    ] = override_execution_service
    return application


@pytest.fixture
def app(fake_execution_service: FakeWorkerMockExecutionService) -> FastAPI:
    return _app(fake_execution_service)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def _valid_payload(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "mode": "success",
        "execution_attempt_id": "attempt-1",
    }
    payload.update(overrides)
    return payload


# ── Authorization tests ───────────────────────────────────────────────────


def test_rejects_jwt_normal_caller(
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    app = _app(fake_execution_service, tenant=_tenant(auth_method="jwt"))
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 403


def test_rejects_non_internal_auth_method(
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    app = _app(fake_execution_service, tenant=_tenant(auth_method="api_key"))
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 403


def test_accepts_internal_api_key(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(),
    )
    assert response.status_code == 200
    assert len(fake_execution_service.calls) == 1


def test_endpoint_calls_execution_wrapper(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(),
    )
    assert response.status_code == 200
    assert response.json()["attempt_status"] == "succeeded"


# ── Query / body safety tests ────────────────────────────────────────────


def test_rejects_organization_id_in_query(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        params={"organization_id": "org-forged"},
        json=_valid_payload(),
    )
    assert response.status_code == 422


def test_rejects_organization_id_in_body(client: TestClient) -> None:
    payload = _valid_payload()
    payload["organization_id"] = "org-forged"  # type: ignore[assignment]
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=payload,
    )
    assert response.status_code == 422


def test_rejects_requested_by_in_body(client: TestClient) -> None:
    payload = _valid_payload()
    payload["requested_by"] = "attacker"  # type: ignore[assignment]
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=payload,
    )
    assert response.status_code == 422


def test_job_id_in_body_rejected_by_schema(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    del fake_execution_service
    payload = _valid_payload()
    payload["job_id"] = "body-job"  # type: ignore[assignment]
    response = client.post(
        "/api/v1/internal/ai-jobs/job-path/mock-worker/execute",
        json=payload,
    )
    assert response.status_code == 422


def test_job_id_from_path_not_body(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-path/mock-worker/execute",
        json=_valid_payload(),
    )
    assert response.status_code == 200
    command = fake_execution_service.calls[-1][1]
    assert command.job_id == "job-path"
    assert command.organization_id == "org-tenant"


# ── Command construction tests ────────────────────────────────────────────


def test_builds_command_from_tenant_context(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(),
    )
    assert response.status_code == 200
    command = fake_execution_service.calls[-1][1]
    assert command.organization_id == "org-tenant"
    assert command.job_id == "job-1"
    assert command.execution_attempt_id == "attempt-1"
    assert command.mode == "success"


def test_requested_by_derived_from_tenant_user_id(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(),
    )
    assert response.status_code == 200
    command = fake_execution_service.calls[-1][1]
    assert command.requested_by == "user-1"


def test_requested_by_fallback_to_internal_trigger(
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    app = _app(
        fake_execution_service,
        tenant=_tenant(auth_method="internal_api_key", user_id=""),
    )
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 200
    command = fake_execution_service.calls[-1][1]
    assert command.requested_by == "internal_trigger"


# ── Flow tests ────────────────────────────────────────────────────────────


def test_success_flow(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(mode="success"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "success"
    assert body["status"] == "consumed"
    assert body["consumed_credits"] == 5
    assert body["consume_entry_id"] == "entry-consume-1"
    assert body["job_id"] == "job-1"
    assert body["organization_id"] == "org-tenant"
    assert body["replay"] is False
    assert body["attempt_status"] == "succeeded"


def test_terminal_replay_returns_200_with_replay_true() -> None:
    execution_service = ReplayWorkerMockExecutionService()
    app = _app(execution_service)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-replay/mock-worker/execute",
            json=_valid_payload(mode="success"),
        )
    assert response.status_code == 200
    body = response.json()
    assert body["replay"] is True
    assert body["attempt_status"] == "succeeded"
    assert body["job_id"] == "job-replay"
    assert body["consumed_credits"] == 8
    assert body["consume_entry_id"] == "entry-replayed-consume"
    assert len(execution_service.calls) == 1


def test_failure_flow(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(mode="failure", mock_error_code="test_error"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "failure"
    assert body["status"] == "released"
    assert body["released_credits"] == 5
    assert body["release_entry_id"] == "entry-release-1"
    assert body["job_id"] == "job-1"
    assert body["replay"] is False
    assert body["attempt_status"] == "failed"


def test_cancel_flow(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(mode="cancel"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "cancel"
    assert body["status"] == "released"
    assert body["released_credits"] == 3
    assert body["release_entry_id"] == "entry-release-1"
    assert body["replay"] is False
    assert body["attempt_status"] == "cancelled"


# ── Validation tests ──────────────────────────────────────────────────────


def test_invalid_mode_fails(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json={"mode": "other", "execution_attempt_id": "a"},
    )
    assert response.status_code == 422


def test_missing_execution_attempt_id_fails(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json={"mode": "success"},
    )
    assert response.status_code == 422


def test_empty_execution_attempt_id_fails(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json={"mode": "success", "execution_attempt_id": ""},
    )
    assert response.status_code == 422


def test_simulated_duration_ms_out_of_range_fails(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json={"mode": "success", "execution_attempt_id": "a", "simulated_duration_ms": 999999},
    )
    assert response.status_code == 422


def test_extra_fields_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json={"mode": "success", "execution_attempt_id": "a", "unknown_field": True},
    )
    assert response.status_code == 422


def test_credit_override_fields_pass_for_internal(
    client: TestClient,
    fake_execution_service: FakeWorkerMockExecutionService,
) -> None:
    response = client.post(
        "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
        json=_valid_payload(mode="success", actual_credits=10),
    )
    assert response.status_code == 200
    command = fake_execution_service.calls[-1][1]
    assert command.actual_credits == 10


# ── Error mapping tests ───────────────────────────────────────────────────


def test_worker_mock_error_maps_to_400() -> None:
    from services.ai_job_worker_mock_service import AIJobWorkerMockError

    failing = FailingWorkerMockExecutionService(AIJobWorkerMockError("bad command"))
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 400
    assert "bad command" in response.json()["detail"]


def test_settlement_error_maps_to_409() -> None:
    from services.ai_job_worker_mock_service import AIJobWorkerMockSettlementError

    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockSettlementError("settlement conflict")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409
    assert "settlement conflict" in response.json()["detail"]


def test_not_found_maps_to_404() -> None:
    from services.ai_job_async_orchestration_service import AIJobAsyncNotFoundError

    failing = FailingWorkerMockExecutionService(
        AIJobAsyncNotFoundError("AI job not found for organization org-tenant: job-x")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-x/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 404


def test_invalid_state_maps_to_409() -> None:
    from services.ai_job_async_orchestration_service import AIJobAsyncInvalidStateError

    failing = FailingWorkerMockExecutionService(
        AIJobAsyncInvalidStateError("invalid transition")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409


def test_orchestration_error_maps_to_400() -> None:
    from services.ai_job_async_orchestration_service import AIJobAsyncOrchestrationError

    failing = FailingWorkerMockExecutionService(AIJobAsyncOrchestrationError("bad request"))
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 400


def test_fingerprint_mismatch_maps_to_409() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionFingerprintMismatchError("internal fingerprint detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409
    assert response.json()["detail"] == "Execution attempt conflict"


def test_in_progress_maps_to_409() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionInProgressError("internal in-progress detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409
    assert response.json()["detail"] == "Execution attempt is in progress"


def test_invalid_stored_state_maps_to_409() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionInvalidStateError("internal invalid state detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409
    assert response.json()["detail"] == "Execution attempt state conflict"


def test_replay_reconstruction_error_maps_to_500() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionReplayError("internal replay detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 500
    assert response.json()["detail"] == "Execution attempt replay failed"


def test_generic_wrapper_conflict_maps_to_409() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionConflictError("internal conflict detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 409
    assert response.json()["detail"] == "Execution attempt conflict"


def test_generic_wrapper_error_maps_to_500() -> None:
    failing = FailingWorkerMockExecutionService(
        AIJobWorkerMockExecutionError("internal execution detail")
    )
    app = _app(failing)
    with TestClient(app) as c:
        response = c.post(
            "/api/v1/internal/ai-jobs/job-1/mock-worker/execute",
            json=_valid_payload(),
        )
    assert response.status_code == 500
    assert response.json()["detail"] == "Execution attempt failed"


# ── Isolation tests ───────────────────────────────────────────────────────


def test_router_has_no_forbidden_direct_dependencies() -> None:
    source = ROUTE_MODULE_PATH.read_text(encoding="utf-8")
    forbidden_terms = (
        "AsyncSessionLocal",
        "session.commit",
        "commit()",
        "CreditLedgerService",
        "CreditGateService",
        "AIJobAccountingGateway",
        "AIJobCostingService",
        "AIJobRepository",
        "AIJobWorkerMockService",
    )
    for term in forbidden_terms:
        assert term not in source, f"forbidden term found: {term}"


def test_router_include_in_schema_is_false() -> None:
    assert getattr(router, "include_in_schema", True) is False


def test_no_frontend_imports() -> None:
    source = ROUTE_MODULE_PATH.read_text(encoding="utf-8")
    assert "src_frontend" not in source
    assert "frontend" not in source


# ── Regression: existing route tests still importable ─────────────────────


def test_existing_ai_job_routes_module_is_importable() -> None:
    existing_spec = importlib.util.spec_from_file_location(
        "ai_job_routes_existing",
        SRC_DIR / "routes" / "ai_job_routes.py",
    )
    assert existing_spec is not None and existing_spec.loader is not None
    mod = importlib.util.module_from_spec(existing_spec)
    existing_spec.loader.exec_module(mod)
    assert hasattr(mod, "router")
